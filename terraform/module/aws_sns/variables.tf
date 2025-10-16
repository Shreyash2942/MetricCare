##########################
# SNS Alert Module Inputs
##########################

variable "env_prefix" {
  type        = string
  description = "Environment prefix (e.g., dev, prod)"
}

variable "protocol" {
  type        = string
  description = "SNS protocol type (email or sms)"
  default     = "email"
}

variable "endpoints" {
  type        = list(string)
  description = "List of email addresses or phone numbers for alerts"
  default     = []
}
