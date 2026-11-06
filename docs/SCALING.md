# Scaling, strengths and tradeoffs

**Terms used here:** A managed identity lets an Azure service request access without storing a password in the application. OIDC lets trusted systems exchange proof of identity; the release pipeline uses it to request short-lived Azure access.

## When the workload grows

Use bounded queue batches, per-person serialization and tenant-aware request IDs used to avoid repeating the same action. Put durable intents and provider receipts in a transactional datastore. Cache public signing keys with rotation support; do not cache employee revocation indefinitely. Separate provisioning, access review and password reset privileges. Measure queue age, unknown outcomes and reconciliation errors before increasing concurrency.

## Design choices

| Choice | Strength, weakness and tradeoff |
| --- | --- |
| Separate worker identity | Limits range of systems a failure could affect and makes permissions easier to review. Adds another deployment, queue and operating procedure. |
| Current-state authorization | Stops stale token roles from retaining application access. Adds a datastore dependency and a cache-invalidation decision. |
| Managed identity / OIDC | Avoids long-lived cloud keys. Exact trust subjects, permissions limited to the required resources and recovery paths still need review. |
| SQLite reference adapter | Makes failure cases easy to run without a tenant. It does not prove Graph permission scope, PIM eligibility or Entra policy behavior. |

## Operating measures

Measure throughput, oldest pending work, duplicate/rejected operations, failure stage and recovery duration. Tie alerts to an operator action. Do not infer service availability from an old successful import or infer delivery from provider acceptance.

Start with measured load and an explicit service objective. Increase concurrency only after checking provider quotas, database contention, per-person ordering and recovery behavior. Horizontal scaling requires a shared durable store; independent in-memory or SQLite processes are not a distributed coordination system.
