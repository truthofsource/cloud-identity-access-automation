# Implementation walkthrough

A healthcare-services workforce platform needed one sign-in layer and a reliable way to grant, change and revoke staff access without giving the business API broad directory-write permissions.

## 1. Trace sign-in

The browser requests an access token for the API, not an ID token intended for its own UI. The API checks signature, trusted issuer, tenant, audience and time claims before using roles.

## 2. Follow a joiner

A privileged operator submits a specific employee/access change. A durable request key prevents repeating the same local operation. In the source platform a separate worker applies narrow directory changes and records readback.

## 3. Try the negative paths

The demo rejects a wrong audience, expired token and cross-person read. Moving removes effective access even before the old token expires; leaving blocks the saved token.

## 4. Review the cloud adapter boundary

The demo issuer is ephemeral and local. Real Graph reconciliation must handle timeouts with unknown outcomes by reading state before retrying; a local transaction cannot roll back an external directory change.

## Read the implementation

Start with [the domain module](../lab/domain.py), then [its tests](../tests/test_domain.py). The [dashboard report](../lab/demo.py) runs the same implementation; it does not substitute static success labels. `python -B -m lab demo` exits with an error if a demonstration assertion fails.

## Discuss the result

Describe the business problem first, the trust boundary second and the observed result third. Claim only the evidence in the validation record. A portable reference test is useful evidence of code behavior; it is not live-provider acceptance.

## Commands for this walkthrough

Start from the repository root. Run the working identity and lifecycle reference and its tests:

```bash
python -B -m unittest discover -s tests -v
python -B -m lab demo
```

Then follow the commands beside each [proof section](../README.md#proof-it-works). The [full command reference](COMMANDS.md) explains prerequisites, expected outcomes and which additional procedures have not been run.

## Follow the actual implementation

Read [the implemented path](IMPLEMENTATION.md), then [the selected source](../reference/) and original tests. The loopback workbench remains a portable local reference. It does not replay provider operations or prove a fresh hosted deployment.
