# Identity evidence and detection boundaries

Entra `AuditLogs` and interactive `SigninLogs` use an existing native tenant route to the hub security workspace. They do not use the application's custom HTTP/operations tables or collector identity. Configuration, a table name, actual arrivals and useful incident rules are separate acceptance steps.

November 14 read-only verification observed 34 audit and 20 interactive sign-in records over seven days. Other inspected noninteractive, service-principal and managed-identity sign-in categories were not enabled and had no rows. These counts do not establish unique users, a complete authentication audit or a cost forecast.

The existing Azure Activity rule observes successful Azure resource role-assignment additions/removals. Its privileged label does not mean every selected role is privileged, and it is not complete coverage of Entra directory-role changes or authentication threats. No new identity rule was enabled by the collection verification.

ClickOps: inspect the tenant diagnostic category selection and destination, then query `AuditLogs` and `SigninLogs` in the authorized hub security workspace. Avoid exporting names, IPs, claims or complete sign-in records into public screenshots. Native collection and the separate [application/operations security project](https://github.com/truthofsource/azure-sentinel-detection-and-incident-response) retain different sources, grants and schemas.

Before expansion, review useful detections, premium eligibility, source volume, retention, privacy and analyst workload. More categories can add cost and noise; an enabled route without a useful response process is not full identity-security coverage. This public project does not deploy or alter that native route.
