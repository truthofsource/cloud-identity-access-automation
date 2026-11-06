import assert from "node:assert/strict";
import test from "node:test";

import {
  authorizeApplicationAppRoleClaims,
} from "./applicationRoleClaims.ts";

const ingestionRole =
  "Workforce.IngestionWriter";

test(
  "accepts an application token with the exact ingestion app role",
  () => {
    const result =
      authorizeApplicationAppRoleClaims(
        {
          tid:
            "tenant-id",
          aud:
            "api-audience",
          roles: [
            ingestionRole,
          ],
        },
        ingestionRole
      );

    assert.equal(
      result.ok,
      true
    );

    if (result.ok) {
      assert.deepEqual(
        result.roles,
        [ingestionRole]
      );
    }
  }
);

test(
  "rejects a delegated token even if it also carries the ingestion role",
  () => {
    const result =
      authorizeApplicationAppRoleClaims(
        {
          roles: [
            ingestionRole,
          ],
          scp:
            "access_as_user",
        },
        ingestionRole
      );

    assert.deepEqual(
      result,
      {
        ok: false,
        status: 403,
        error:
          "Delegated user tokens are not permitted for this application-only route.",
      }
    );
  }
);

test(
  "rejects an application token without the exact ingestion role",
  () => {
    const result =
      authorizeApplicationAppRoleClaims(
        {
          roles: [
            "Workforce.Admin",
          ],
        },
        ingestionRole
      );

    assert.equal(
      result.ok,
      false
    );

    if (!result.ok) {
      assert.equal(
        result.status,
        403
      );
    }
  }
);

test(
  "fails closed on missing route role configuration",
  () => {
    const result =
      authorizeApplicationAppRoleClaims(
        {
          roles: [
            ingestionRole,
          ],
        },
        "  "
      );

    assert.equal(
      result.ok,
      false
    );

    if (!result.ok) {
      assert.equal(
        result.status,
        500
      );
    }
  }
);
