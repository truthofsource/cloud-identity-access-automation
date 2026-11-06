resource "azuread_group" "workforce_admins" {
  display_name     = lookup(var.group_display_names, "admins", "example-workforce-admins-${var.environment}")
  description      = "workforce platform administrators for the example workforce platform ${var.environment} environment."
  security_enabled = true

  owners = [
    var.owner_object_id
  ]
}

resource "azuread_app_role_assignment" "workforce_admins_api_admin" {
  app_role_id         = var.admin_app_role_id
  principal_object_id = azuread_group.workforce_admins.object_id
  resource_object_id  = var.api_service_principal_object_id
}

resource "azuread_group" "workforce_supervisors" {
  display_name     = lookup(var.group_display_names, "supervisors", "grp-example-workforce-supervisors-${var.environment}")
  description      = "workforce platform supervisors for the example workforce platform ${var.environment} environment."
  security_enabled = true

  owners = [
    var.owner_object_id
  ]
}

resource "azuread_group" "workforce_employees" {
  display_name     = lookup(var.group_display_names, "employees", "grp-example-workforce-employees-${var.environment}")
  description      = "workforce platform employees for the example workforce platform ${var.environment} environment."
  security_enabled = true

  owners = [
    var.owner_object_id
  ]
}

resource "azuread_group" "workforce_hr" {
  display_name     = lookup(var.group_display_names, "hr", "grp-example-workforce-hr-${var.environment}")
  description      = "workforce platform HR users for the example workforce platform ${var.environment} environment."
  security_enabled = true

  owners = [
    var.owner_object_id
  ]
}

resource "azuread_group" "workforce_payroll" {
  display_name     = lookup(var.group_display_names, "payroll", "grp-example-workforce-payroll-${var.environment}")
  description      = coalesce(var.payroll_group_description, "workforce platform payroll users for the example workforce platform ${var.environment} environment.")
  security_enabled = true
  owners           = [var.owner_object_id]
  lifecycle {
    prevent_destroy = true
  }
}

resource "azuread_app_role_assignment" "workforce_payroll_api_payroll" {
  app_role_id         = var.payroll_app_role_id
  principal_object_id = azuread_group.workforce_payroll.object_id
  resource_object_id  = var.api_service_principal_object_id
}

resource "azuread_app_role_assignment" "workforce_supervisors_api_supervisor" {
  app_role_id         = var.supervisor_app_role_id
  principal_object_id = azuread_group.workforce_supervisors.object_id
  resource_object_id  = var.api_service_principal_object_id
}

resource "azuread_app_role_assignment" "workforce_employees_api_employee" {
  app_role_id         = var.employee_app_role_id
  principal_object_id = azuread_group.workforce_employees.object_id
  resource_object_id  = var.api_service_principal_object_id
}

resource "azuread_app_role_assignment" "workforce_hr_api_hr" {
  app_role_id         = var.hr_app_role_id
  principal_object_id = azuread_group.workforce_hr.object_id
  resource_object_id  = var.api_service_principal_object_id
}

resource "azuread_group" "workforce_sensitive_records" {
  display_name     = lookup(var.group_display_names, "sensitive_records", "grp-example-workforce-sensitive-onboarding-${var.environment}")
  description      = "workforce platform users approved for explicitly audited sensitive onboarding data access."
  security_enabled = true

  owners = [
    var.owner_object_id
  ]
}

resource "azuread_app_role_assignment" "workforce_sensitive_records_api_sensitive_records" {
  app_role_id         = var.sensitive_records_app_role_id
  principal_object_id = azuread_group.workforce_sensitive_records.object_id
  resource_object_id  = var.api_service_principal_object_id
}
