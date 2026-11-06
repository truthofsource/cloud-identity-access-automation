variable "subscription_id" { type = string }
variable "location" {
  type    = string
  default = "eastus2"
}
variable "resource_group_name" { type = string }
variable "tags" {
  type    = map(string)
  default = { environment = "lab", owner = "engineering", cost_center = "training", managed_by = "terraform" }
}

variable "owner_object_id" {
  type = string
}

variable "group_display_names" {
  type        = map(string)
  default     = {}
  description = "Existing environment-specific Entra group names; empty entries use the module defaults."
}

variable "payroll_group_description" {
  type        = string
  default     = null
  description = "Existing Payroll group description when it differs from the module default."
}

variable "api_service_principal_object_id" {
  type = string
}

variable "admin_app_role_id" {
  type = string
}

variable "payroll_app_role_id" {
  type = string
}

variable "supervisor_app_role_id" {
  type = string
}

variable "employee_app_role_id" {
  type = string
}

variable "hr_app_role_id" {
  type = string
}

variable "sensitive_records_app_role_id" {
  type = string
}

variable "environment" { type = string }

variable "tenant_id" { type = string }
variable "enable_github_federation" {
  type    = bool
  default = false
}
variable "github_oidc_subject" {
  type    = string
  default = ""
}
