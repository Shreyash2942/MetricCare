variable "glue_jobs" {
  type = map(object({
    script_path = string
    job_name= string
  }))                     # The type of the variable, in this case a string
  description = "The glue job name" # Description of what this variable represents
}

variable "s3_bucket" {
  type = string
  description = "S3 bucket name"
}

variable "iam_role" {
  type = string
  description = "Iam role ARN for glue job"
}

variable "script_location" {
  type = map(string)
  description = "Map of script names to upload s3 object"
}

variable "database_name" {
  type = string
  default = "database name for adding config "
}

variable "meta_table" {
  type = string
  default = "meta table name"
}

variable "config_file" {
  type = string
  default = "config file location for glue job"
}



