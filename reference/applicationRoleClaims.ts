type JWTPayload = Record<string, unknown>;
export type ApplicationRoleCheckSuccess = {
  ok: true;
  claims: JWTPayload;
  roles: string[];
  requiredRole: string;
  matchedRole: string;
};

export type ApplicationRoleCheckFailure = {
  ok: false;
  status: number;
  error: string;
};

function normalizeRequiredRole(
  requiredRole: string
): string | null {
  const normalized =
    requiredRole.trim();

  return normalized.length > 0
    ? normalized
    : null;
}

function getRoles(
  claims: JWTPayload
): string[] {
  if (
    !Array.isArray(
      claims.roles
    )
  ) {
    return [];
  }

  return claims.roles.filter(
    (role): role is string =>
      typeof role === "string" &&
      role.length > 0
  );
}

export function authorizeApplicationAppRoleClaims(
  claims: JWTPayload,
  requiredRole: string
):
  | ApplicationRoleCheckSuccess
  | ApplicationRoleCheckFailure {
  const normalizedRole =
    normalizeRequiredRole(
      requiredRole
    );

  if (!normalizedRole) {
    return {
      ok: false,
      status: 500,
      error:
        "API route is missing required application app role configuration.",
    };
  }

  if (
    claims.scp !== undefined &&
    claims.scp !== null
  ) {
    return {
      ok: false,
      status: 403,
      error:
        "Delegated user tokens are not permitted for this application-only route.",
    };
  }

  const roles =
    getRoles(claims);

  if (
    !roles.includes(
      normalizedRole
    )
  ) {
    return {
      ok: false,
      status: 403,
      error:
        `Application token is missing required app role: ${normalizedRole}`,
    };
  }

  return {
    ok: true,
    claims,
    roles,
    requiredRole:
      normalizedRole,
    matchedRole:
      normalizedRole,
  };
}
