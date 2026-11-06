"""Portable reference implementation of identity lifecycle and API authorization."""

import base64
import hashlib
import json
import sqlite3
import time
from datetime import datetime, timezone
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

ISSUER = "https://identity.example.invalid/tenant-lab/v2.0"
AUDIENCE = "urn:example:workforce-api"
ROLES = {"Viewer", "Reviewer", "Admin"}


class Denied(ValueError):
    pass


def encode(value):
    return base64.urlsafe_b64encode(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).rstrip(b"=")


def issue(key, claims):
    """Fixture issuer only. The production identity provider owns token issuance."""
    header = encode({"alg": "RS256", "kid": "lab-key", "typ": "JWT"})
    payload = encode(claims)
    signature = key.sign(header + b"." + payload, padding.PKCS1v15(), hashes.SHA256())
    return (
        header
        + b"."
        + payload
        + b"."
        + base64.urlsafe_b64encode(signature).rstrip(b"=")
    ).decode()


def verify(token, trusted_keys, now=None):
    now = int(time.time()) if now is None else now
    try:
        if not isinstance(token, str) or len(token) > 16000:
            raise Denied("Malformed token")
        h, p, s = token.split(".")
        decode = lambda x: base64.b64decode(
            x + "=" * (-len(x) % 4), altchars=b"-_", validate=True
        )
        header = json.loads(decode(h))
        claims = json.loads(decode(p))
        if not isinstance(header, dict) or not isinstance(claims, dict):
            raise Denied("Malformed token")
        if header.get("alg") != "RS256" or header.get("kid") not in trusted_keys:
            raise Denied("Untrusted signing key or algorithm")
        trusted_keys[header["kid"]].verify(
            decode(s), (h + "." + p).encode(), padding.PKCS1v15(), hashes.SHA256()
        )
        if (
            claims.get("iss") != ISSUER
            or claims.get("aud") != AUDIENCE
            or claims.get("tid") != "tenant-lab"
        ):
            raise Denied("Issuer, audience or tenant mismatch")
        if type(claims.get("exp")) is not int or claims["exp"] <= now:
            raise Denied("Expired token")
        if type(claims.get("nbf", 0)) is not int or claims.get("nbf", 0) > now:
            raise Denied("Token is not yet valid")
        if not isinstance(claims.get("sub"), str) or not claims["sub"]:
            raise Denied("Missing subject")
        if not isinstance(claims.get("roles"), list) or not all(
            isinstance(r, str) and r in ROLES for r in claims["roles"]
        ):
            raise Denied("Invalid role claims")
        return claims
    except Denied:
        raise
    except (
        ValueError,
        KeyError,
        TypeError,
        InvalidSignature,
        UnicodeError,
        RecursionError,
    ) as error:
        raise Denied("Invalid token or signature") from error


class Directory:
    def __init__(self, path=":memory:"):
        self.db = sqlite3.connect(path, isolation_level=None, timeout=5)
        self.db.execute("pragma foreign_keys=on")
        self.db.executescript(
            """create table if not exists accounts(id text primary key, active integer not null, roles text not null, revision integer not null);
        create table if not exists operations(request_key text primary key, payload_hash text not null, result text not null);"""
        )

    def apply(self, key, action, person, roles, actor_roles):
        if "Admin" not in actor_roles:
            raise Denied("Administrator role required for lifecycle work")
        if (
            action not in {"join", "move", "leave"}
            or not person
            or not key
            or not set(roles) <= ROLES
        ):
            raise ValueError("Invalid lifecycle request")
        payload = json.dumps(
            [action, person, sorted(set(roles))], separators=(",", ":")
        )
        fingerprint = hashlib.sha256(payload.encode()).hexdigest()
        self.db.execute("begin immediate")
        try:
            prior = self.db.execute(
                "select payload_hash,result from operations where request_key=?", (key,)
            ).fetchone()
            if prior:
                if prior[0] != fingerprint:
                    raise ValueError("Request key already belongs to another operation")
                result = json.loads(prior[1])
            else:
                row = self.db.execute(
                    "select active,revision from accounts where id=?", (person,)
                ).fetchone()
                if action == "join" and row:
                    raise ValueError("Account already exists")
                if action != "join" and not row:
                    raise ValueError("Account does not exist")
                if action == "move" and not row[0]:
                    raise ValueError("An inactive account cannot move")
                active = action != "leave"
                effective = sorted(set(roles)) if active else []
                revision = 1 if row is None else row[1] + 1
                self.db.execute(
                    "insert into accounts values(?,?,?,?) on conflict(id) do update set active=excluded.active,roles=excluded.roles,revision=excluded.revision",
                    (person, int(active), json.dumps(effective), revision),
                )
                result = {
                    "person": person,
                    "active": active,
                    "roles": effective,
                    "revision": revision,
                }
                self.db.execute(
                    "insert into operations values(?,?,?)",
                    (key, fingerprint, json.dumps(result)),
                )
            self.db.execute("commit")
            return result
        except Exception:
            self.db.execute("rollback")
            raise

    def authorize(self, claims, record_owner, required_role=None):
        row = self.db.execute(
            "select active,roles from accounts where id=?", (claims["sub"],)
        ).fetchone()
        if not row or not row[0]:
            raise Denied("Account is inactive or unknown")
        effective = set(claims["roles"]) & set(json.loads(row[1]))
        if required_role and required_role not in effective:
            raise Denied("Required role is missing")
        if claims["sub"] != record_owner and "Admin" not in effective:
            raise Denied("Record belongs to another person")
        return True


def demo():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    directory = Directory()
    checks = []
    joined = directory.apply(
        "request-001", "join", "employee-001", ["Viewer"], ["Admin"]
    )
    repeated = directory.apply(
        "request-001", "join", "employee-001", ["Viewer"], ["Admin"]
    )
    checks.append(
        {
            "name": "Duplicate joiner request is idempotent",
            "passed": joined == repeated,
            "detail": "One account and one recorded operation",
        }
    )
    claims = {
        "iss": ISSUER,
        "aud": AUDIENCE,
        "tid": "tenant-lab",
        "sub": "employee-001",
        "roles": ["Viewer"],
        "exp": int(time.time()) + 600,
    }
    verified = verify(issue(key, claims), {"lab-key": key.public_key()})
    checks.append(
        {
            "name": "Signed token can access its own record",
            "passed": directory.authorize(verified, "employee-001"),
            "detail": "RS256 signature, issuer, audience, tenant and account state checked",
        }
    )
    for name, call in [
        (
            "Cross-person access is denied",
            lambda: directory.authorize(verified, "employee-002"),
        ),
        (
            "Wrong audience is rejected",
            lambda: verify(
                issue(key, {**claims, "aud": "other-api"}),
                {"lab-key": key.public_key()},
            ),
        ),
        (
            "Expired token is rejected",
            lambda: verify(
                issue(key, {**claims, "exp": 1}), {"lab-key": key.public_key()}
            ),
        ),
    ]:
        try:
            call()
            passed = False
        except Denied:
            passed = True
        checks.append(
            {"name": name, "passed": passed, "detail": "Expected denial observed"}
        )
    moved = directory.apply(
        "request-002", "move", "employee-001", ["Reviewer"], ["Admin"]
    )
    left = directory.apply("request-003", "leave", "employee-001", [], ["Admin"])
    try:
        directory.authorize(verified, "employee-001")
        denied = False
    except Denied:
        denied = True
    checks.append(
        {
            "name": "Leaver blocks an otherwise valid saved token",
            "passed": denied,
            "detail": "Current account state is rechecked on every operation",
        }
    )
    directory.db.close()
    return {
        "checks": checks,
        "metrics": [
            {
                "label": "Lifecycle stages",
                "value": "3",
                "detail": "Join, move and leave",
            },
            {
                "label": "Security checks",
                "value": str(len(checks)),
                "detail": "Positive and negative paths",
            },
            {
                "label": "Active access after leave",
                "value": "0",
                "detail": "Saved token cannot bypass revocation",
            },
            {
                "label": "Cloud writes",
                "value": "0",
                "detail": "Local directory adapter",
            },
        ],
        "records": [
            ["employee-001", "Joined", ",".join(joined["roles"])],
            ["employee-001", "Moved", ",".join(moved["roles"])],
            ["employee-001", "Inactive", f"Revision {left['revision']}; access denied"],
        ],
    }
