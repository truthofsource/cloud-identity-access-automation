import time, unittest
from cryptography.hazmat.primitives.asymmetric import rsa
from lab.domain import Directory, Denied, ISSUER, AUDIENCE, issue, verify


class IdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    def setUp(self):
        self.d = Directory()
        self.d.apply("join-1", "join", "employee-001", ["Viewer"], ["Admin"])
        self.c = {
            "iss": ISSUER,
            "aud": AUDIENCE,
            "tid": "tenant-lab",
            "sub": "employee-001",
            "roles": ["Viewer"],
            "exp": int(time.time()) + 60,
        }

    def tearDown(self):
        self.d.db.close()

    def token(self, **changes):
        return verify(
            issue(self.key, {**self.c, **changes}), {"lab-key": self.key.public_key()}
        )

    def test_duplicate_is_idempotent(self):
        self.assertEqual(
            self.d.apply("join-1", "join", "employee-001", ["Viewer"], ["Admin"])[
                "revision"
            ],
            1,
        )

    def test_request_key_conflict(self):
        with self.assertRaises(ValueError):
            self.d.apply("join-1", "move", "employee-001", ["Admin"], ["Admin"])

    def test_operator_requires_admin(self):
        with self.assertRaises(Denied):
            self.d.apply("move-1", "move", "employee-001", ["Admin"], ["Viewer"])

    def test_own_record(self):
        self.assertTrue(self.d.authorize(self.token(), "employee-001"))

    def test_cross_person(self):
        with self.assertRaises(Denied):
            self.d.authorize(self.token(), "employee-002")

    def test_wrong_audience(self):
        with self.assertRaises(Denied):
            self.token(aud="another-api")

    def test_expired(self):
        with self.assertRaises(Denied):
            self.token(exp=1)

    def test_future_token(self):
        with self.assertRaises(Denied):
            self.token(nbf=int(time.time()) + 100)

    def test_wrong_issuer(self):
        with self.assertRaises(Denied):
            self.token(iss="https://untrusted.example.invalid")

    def test_unsigned(self):
        with self.assertRaises(Denied):
            verify("e30.e30.", {"lab-key": self.key.public_key()})

    def test_wrong_signing_key(self):
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        with self.assertRaises(Denied):
            verify(issue(key, self.c), {"lab-key": self.key.public_key()})

    def test_role_removal_applies_before_token_expires(self):
        claims = self.token()
        self.d.apply("move-1", "move", "employee-001", ["Reviewer"], ["Admin"])
        with self.assertRaises(Denied):
            self.d.authorize(claims, "employee-001", "Viewer")

    def test_leaver_denies_saved_token(self):
        claims = self.token()
        self.d.apply("leave-1", "leave", "employee-001", [], ["Admin"])
        with self.assertRaises(Denied):
            self.d.authorize(claims, "employee-001")

    def test_inactive_cannot_move(self):
        self.d.apply("leave-1", "leave", "employee-001", [], ["Admin"])
        with self.assertRaises(ValueError):
            self.d.apply("move-1", "move", "employee-001", ["Admin"], ["Admin"])
