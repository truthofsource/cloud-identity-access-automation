# Operations and troubleshooting

**Terms used here:** A digest is a file or container fingerprint used to confirm the exact version. An artifact is a file produced for a release, such as an application ZIP or container image.

## Start and stop

Run unit tests, then start the loopback dashboard with `python -B -m lab serve`. Stop with Ctrl+C. Each demonstration uses disposable test-only state; running it twice does not send messages or change a cloud resource.

## Diagnose by failure stage

| Symptom | Check and next action |
| --- | --- |
| Token rejected | Check the API audience, tenant, issuer and token lifetime. Do not paste the token into logs or public JWT decoders. |
| Role changed but access persists | Compare current membership, app-role assignment, token issue time and application state. Group membership and app roles are different objects. |
| Lifecycle request times out | Read the stored request and directory state before retrying. A timeout is not proof that no change occurred. |
| Worker cannot change membership | Inspect only the worker identity and exact Graph grant. Do not grant directory-write access to the business API to make the error disappear. |

## Cleanup

Default demos use managed temporary directories and close their own database handles. Do not run blanket recursive cleanup against a shared checkout. Inspect `git status --short --ignored`, stop the local server and remove only artifacts you created. Cloud resource cleanup is a separate reviewed operation and is never triggered by this repository's CI.

## Evidence to keep

Retain source commit, test command/exit status, tool versions and safe error stage. For a real release, also retain exact package/image digest and the restored operating state. Do not retain credentials, bearer tokens or employee data in public artifacts.
