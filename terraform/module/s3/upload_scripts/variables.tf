variable "bucket_name" {
  type = string                     # The type of the variable, in this case a string
  description = "Id of the bucket" # Description of what this variable represents
}

variable "scripts" {
  description = "Map of Glue scripts with local path and job name"
  type = map(object({
    script_path = string
    job_name    = string
  }))
}

