resource "azurerm_resource_group" "lab" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

# Separate identities: the public API must not inherit directory-write grants.
resource "azurerm_user_assigned_identity" "api" {
  name                = "id-example-business-api"
  resource_group_name = azurerm_resource_group.lab.name
  location            = var.location
  tags                = var.tags
}
resource "azurerm_user_assigned_identity" "directory" {
  name                = "id-example-directory-worker"
  resource_group_name = azurerm_resource_group.lab.name
  location            = var.location
  tags                = var.tags
}
resource "azurerm_user_assigned_identity" "deployer" {
  name                = "id-example-deployer"
  resource_group_name = azurerm_resource_group.lab.name
  location            = var.location
  tags                = var.tags
}
resource "azurerm_federated_identity_credential" "github" {
  count                     = var.enable_github_federation ? 1 : 0
  name                      = "github-reviewed-environment"
  user_assigned_identity_id = azurerm_user_assigned_identity.deployer.id
  issuer                    = "https://token.actions.githubusercontent.com"
  audience                  = ["api://AzureADTokenExchange"]
  subject                   = var.github_oidc_subject
  lifecycle {
    precondition {
      condition     = length(trimspace(var.github_oidc_subject)) > 0 && !strcontains(var.github_oidc_subject, "*")
      error_message = "Provide the exact observed and reviewed GitHub OIDC subject; wildcards are not allowed."
    }
  }
}
output "api_identity_id" { value = azurerm_user_assigned_identity.api.id }
output "directory_identity_id" { value = azurerm_user_assigned_identity.directory.id }
