mock_provider "azurerm" {}
mock_provider "azapi" {}
mock_provider "azuread" {}
variables {
  subscription_id                 = "00000000-0000-0000-0000-000000000001"
  tenant_id                       = "00000000-0000-0000-0000-000000000002"
  owner_object_id                 = "00000000-0000-0000-0000-000000000003"
  api_service_principal_object_id = "00000000-0000-0000-0000-000000000004"
  resource_group_name             = "rg-example-identity"
  environment                     = "lab"
  admin_app_role_id               = "00000000-0000-0000-0000-000000000005"
  supervisor_app_role_id          = "00000000-0000-0000-0000-000000000006"
  employee_app_role_id            = "00000000-0000-0000-0000-000000000007"
  hr_app_role_id                  = "00000000-0000-0000-0000-000000000008"
  payroll_app_role_id             = "00000000-0000-0000-0000-000000000009"
  sensitive_records_app_role_id   = "00000000-0000-0000-0000-000000000010"
}
run "trust_stays_off_and_worker_is_separate" {
  command = plan
  assert {
    condition     = length(azurerm_federated_identity_credential.github) == 0
    error_message = "Federation must stay opt-in."
  }
  assert {
    condition     = azurerm_user_assigned_identity.api.name != azurerm_user_assigned_identity.directory.name
    error_message = "Do not combine API and directory worker identities."
  }
  assert {
    condition     = length(azuread_group.workforce_payroll.owners) == 1
    error_message = "Payroll must retain an explicit owner."
  }
}
run "empty_federated_subject_is_rejected" {
  command = plan
  variables { enable_github_federation = true }
  expect_failures = [azurerm_federated_identity_credential.github[0]]
}
