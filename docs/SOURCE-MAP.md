# Source map and deliberate adaptations

**Terms used here:** A JWT is a token format. The server must verify the token and its permissions before trusting it.

The selected implementation was reviewed November 6, 2026. Hashes identify private source inputs without publishing that private repository or its history. Example identities and labels preserve comparisons, not live authorization.

| Public file | Original implementation area | Adaptation |
| --- | --- | --- |
| [reference/directoryWorkerBoundary.ts](../reference/directoryWorkerBoundary.ts) | `apps/api/src/provisioning/directoryWorkerBoundary.ts` | Neutral example identifiers/labels; portable dependency boundary |
| [reference/directoryWorkerBoundary.test.ts](../reference/directoryWorkerBoundary.test.ts) | `apps/api/src/provisioning/directoryWorkerBoundary.test.ts` | Neutral example identifiers/labels; portable dependency boundary |
| [reference/applicationRoleClaims.ts](../reference/applicationRoleClaims.ts) | `apps/api/src/auth/requireApplicationAppRole.ts` | Extract actual pure claim-authorization functions; replace SDK payload type with structural type; neutral role names |
| [reference/applicationRoleClaims.test.ts](../reference/applicationRoleClaims.test.ts) | `apps/api/src/auth/requireApplicationAppRole.test.ts` | Neutral example identifiers/labels; portable dependency boundary |
| [reference/staffAccess.ts](../reference/staffAccess.ts) | `apps/api/src/auth/staffAccess.ts` | Extract actual pure current-account eligibility predicate; omit database adapter |
| [reference/staffAccess.test.ts](../reference/staffAccess.test.ts) | `apps/api/src/auth/staffAccess.test.ts` | Keep first original predicate test; omit Azure/database route integration test |
| [reference/validateAccessToken.adapter.ts](../reference/validateAccessToken.adapter.ts) | `apps/api/src/auth/validateAccessToken.ts` | Neutral example identifiers/labels; logic retained |

The remote token-validation adapter is included for inspection but not invoked by default tests. Its `jose`/Azure types need the original integration environment. Claim checks operate on already-verified claims and are not standalone JWT validation. Worker host/role prefixes use examples consistently.

[Machine source hashes](source-map.json) · [Validation and limits](VALIDATION.md)

The source map records where the Terraform and other reference files came from. The reusable examples still need their own connection tests and are not complete copies of the deployed setup.
