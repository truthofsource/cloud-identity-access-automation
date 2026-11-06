# Terraform infrastructure

Entra security groups and API app-role assignments, separate API/directory/deployment managed identities, and an optional exact-subject GitHub federated credential.

These configurations adapt the same resource boundaries used in the author's workforce/operations platform. Names and input examples are neutral; no environment state, backend, import block, secret or production identifier is included. Each folder is a standalone reference root, not a command to adopt an existing production resource into new state.

## Code map

| File | Purpose |
| --- | --- |
| [groups.tf](groups.tf) | Six owned security groups and their existing API role assignments; the Payroll group retains deletion protection. |
| [main.tf](main.tf) | Distinct API and directory identities plus a separate deployment identity. Optional OIDC trust stays off. |
| [variables.tf](variables.tf) | Explicit tenant/subscription, owner, existing API principal and role IDs. No password or client secret. |
| [tests/identity.tftest.hcl](tests/identity.tftest.hcl) | Mock plans verify separate identities, explicit ownership and rejection of empty federation trust. |
| [versions.tf](versions.tf) | Exact provider versions; lock file records provider checksums. |
| [example inputs](example.tfvars.example) | Reviewable inputs with placeholders; never actual tenant values. |

## Validate locally without a cloud deployment

```bash
terraform init -backend=false
terraform fmt -check -recursive
terraform validate
terraform test
```

The `.tftest.hcl` files use mock providers and plan commands. They do not authenticate to Azure, create resources or mutate Entra. Provider initialization downloads provider packages; it is not an infrastructure deployment. No automatic Terraform apply is included in GitHub Actions. The existing workflow remains manual-only to avoid unnecessary Actions usage.

The `.tfvars.example` file is not loaded automatically. It contains placeholders and is not ready for a real plan. Leave real `.tfvars`, backend/state, saved plans and credentials outside Git. If you separately deploy a lab, review exact subscription/tenant, names, complete saved plan, permissions, network route, costs and cleanup first. Use a protected remote backend with Entra authentication; this public root deliberately supplies no organization backend.

## Integration boundaries

The Entra app registration, API role definitions, tenant consent, Microsoft Graph application grants and actual worker package are external. This root does not add members, reset passwords or grant directory-write access. The supplied role IDs must belong to the supplied API service principal; verify that relationship before a real apply.

## Security and activation

Federation is disabled by default. Before enabling it, inspect the exact OIDC subject emitted for the intended GitHub repository/environment. Newer immutable subject formats mean the legacy repository-name pattern must not be assumed. The deployer receives no Azure deployment role automatically. Graph permissions must be separately reviewed on the directory worker, never inferred from the identity resource.

## Cost, retention and cleanup

Managed identities and groups alone do not run application compute. Entra licensing and governance features depend on the tenant. This example neither buys a license nor commissions PIM, Conditional Access or password resets.

Mock-test cleanup is entirely local. A real destroy is a separate reviewed action against the correct lab state; never run it against copied production state or shared resources. Payroll deletion protection in the identity example intentionally prevents a casual destroy of that group. Retire grants/trust and inventory retained recovery artifacts before removing a real lab.

## Strengths and tradeoffs

Existing app registrations keep the example focused on the access boundary, but require deliberate integration inputs. A separate worker reduces business-API privilege at the cost of an additional identity and deployment to operate.

## Resource inventory

| Terraform resource type | Local name | Definition |
| --- | --- | --- |
| `azuread_group` | `workforce_admins` | [groups.tf](groups.tf) |
| `azuread_app_role_assignment` | `workforce_admins_api_admin` | [groups.tf](groups.tf) |
| `azuread_group` | `workforce_supervisors` | [groups.tf](groups.tf) |
| `azuread_group` | `workforce_employees` | [groups.tf](groups.tf) |
| `azuread_group` | `workforce_hr` | [groups.tf](groups.tf) |
| `azuread_group` | `workforce_payroll` | [groups.tf](groups.tf) |
| `azuread_app_role_assignment` | `workforce_payroll_api_payroll` | [groups.tf](groups.tf) |
| `azuread_app_role_assignment` | `workforce_supervisors_api_supervisor` | [groups.tf](groups.tf) |
| `azuread_app_role_assignment` | `workforce_employees_api_employee` | [groups.tf](groups.tf) |
| `azuread_app_role_assignment` | `workforce_hr_api_hr` | [groups.tf](groups.tf) |
| `azuread_group` | `workforce_sensitive_records` | [groups.tf](groups.tf) |
| `azuread_app_role_assignment` | `workforce_sensitive_records_api_sensitive_records` | [groups.tf](groups.tf) |
| `azurerm_resource_group` | `lab` | [main.tf](main.tf) |
| `azurerm_user_assigned_identity` | `api` | [main.tf](main.tf) |
| `azurerm_user_assigned_identity` | `directory` | [main.tf](main.tf) |
| `azurerm_user_assigned_identity` | `deployer` | [main.tf](main.tf) |
| `azurerm_federated_identity_credential` | `github` | [main.tf](main.tf) |

## Official references

- [Terraform test command and mock providers](https://developer.hashicorp.com/terraform/cli/commands/test)
- [AzureRM provider documentation](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)
- [Azure Registry repository permissions](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-rbac-abac-repository-permissions)

See [project architecture](../docs/ARCHITECTURE.md) and [validation evidence](../docs/VALIDATION.md) for the separate application/reference boundaries.
