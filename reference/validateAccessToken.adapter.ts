import type { HttpRequest } from "@azure/functions";
import {
  createRemoteJWKSet,
  jwtVerify,
  type JWTPayload,
  type JWTVerifyGetKey,
} from "jose";

type ValidTokenResult = {
  ok: true;
  claims: JWTPayload;
};

type InvalidTokenResult = {
  ok: false;
  status: number;
  error: string;
};

const jwksCache = new Map<string, JWTVerifyGetKey>();

function getRequiredEnv(name: string): string {
  const value = process.env[name];

  if (!value) {
    throw new Error(`Missing required app setting: ${name}`);
  }

  return value;
}

function getJwksForTenant(tenantId: string): JWTVerifyGetKey {
  const cached = jwksCache.get(tenantId);

  if (cached) {
    return cached;
  }

  const jwks = createRemoteJWKSet(
    new URL(`https://login.microsoftonline.com/${tenantId}/discovery/v2.0/keys`)
  );

  jwksCache.set(tenantId, jwks);

  return jwks;
}

function getBearerToken(request: HttpRequest): string | null {
  const authorization = request.headers.get("authorization");

  if (!authorization) {
    return null;
  }

  const [scheme, token] = authorization.split(" ");

  if (scheme?.toLowerCase() !== "bearer" || !token) {
    return null;
  }

  return token;
}

function hasRequiredScope(claims: JWTPayload, requiredScope: string): boolean {
  const scopeClaim = claims.scp;

  if (typeof scopeClaim !== "string") {
    return false;
  }

  return scopeClaim.split(" ").includes(requiredScope);
}

export async function validateAccessToken(
  request: HttpRequest
): Promise<ValidTokenResult | InvalidTokenResult> {
  let tenantId: string;
  let apiClientId: string;
  let apiAudience: string;
  let requiredScope: string;

  try {
    tenantId = getRequiredEnv("ENTRA_TENANT_ID");
    apiClientId = getRequiredEnv("ENTRA_API_CLIENT_ID");
    apiAudience = getRequiredEnv("ENTRA_API_AUDIENCE");
    requiredScope = getRequiredEnv("ENTRA_REQUIRED_SCOPE");
  } catch (error) {
    const message = error instanceof Error ? error.message : "Auth configuration error";

    return {
      ok: false,
      status: 500,
      error: message,
    };
  }

  const token = getBearerToken(request);

  if (!token) {
    return {
      ok: false,
      status: 401,
      error: "Missing or invalid Authorization bearer token.",
    };
  }

  const issuer = `https://login.microsoftonline.com/${tenantId}/v2.0`;
  const audiences = [apiClientId, apiAudience];

  try {
    const { payload } = await jwtVerify(token, getJwksForTenant(tenantId), {
      issuer,
      audience: audiences,
    });

    if (payload.tid !== tenantId) {
      return {
        ok: false,
        status: 401,
        error: "Token tenant does not match expected tenant.",
      };
    }

    if (!hasRequiredScope(payload, requiredScope)) {
      return {
        ok: false,
        status: 403,
        error: `Token is missing required scope: ${requiredScope}`,
      };
    }

    return {
      ok: true,
      claims: payload,
    };
  } catch {
    return {
      ok: false,
      status: 401,
      error: "Invalid or expired access token.",
    };
  }
}
