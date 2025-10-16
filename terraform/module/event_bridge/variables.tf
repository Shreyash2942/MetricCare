##########################
# Variables for Event Hub
##########################

variable "env_prefix" {
  type        = string
  description = "Environment prefix (e.g., dev, prod)"
}

variable "sns_topic_arn" {
  type        = string
  description = "SNS Topic ARN where alerts will be sent"
}

variable "glue_job_names" {
  type        = list(string)
  description = "List of Glue job names to monitor for failure"
}
