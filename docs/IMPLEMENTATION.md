# Identity Boundaries from the Operational Platform

Microsoft Entra is the sign-in layer for the React/Node.js operational application. The bearer-token adapter verifies issuer/audience/tenant and delegated scope before server-side business authorization. Pure application-only route logic separately rejects delegated tokens and requires an exact application role.

The business API has a different identity and responsibility from the non-HTTP directory worker. Actual worker code checks both its execution role and the dedicated Function host name before allowing directory writes. Provisioning requires the exact saved Microsoft object ID, not account selection by an email-name resemblance. A host-name check is an additional boundary, not a replacement for managed identity and Graph/RBAC permissions.

Current staff eligibility rejects suspended, inactive and ambiguously linked employees even if an earlier token still contains a role. Unbound HR/Admin accounts are intentionally permitted by the predicate when not suspended. Exact-person/assignment checks remain part of individual routes. The extracted predicate does not claim to execute the database lookup.

This is Azure/Entra implementation evidence. It does not claim deployed AWS federation, PIM, FIDO2, Access Reviews or Entitlement Management merely because those are IAM capabilities. Password-reset automation remains outside the accepted public demonstration.

## Actual source and adaptations

Read [the source map](SOURCE-MAP.md) and [machine provenance](source-map.json) for every extracted implementation file.

## Dedicated recovery case study

The [backup and recovery project](https://github.com/truthofsource/azure-backup-and-recovery) goes deeper into key-version coverage, backup receipts, isolated recovery and data/file/state dependencies. Application artifact rollback and data recovery solve different problems.
