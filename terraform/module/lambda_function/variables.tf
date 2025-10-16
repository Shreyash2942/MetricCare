variable "lmbd_name" {
  type = string                     # The type of the variable, in this case a string
  description = "The type of EC2 instance" # Description of what this variable represents
}

variable "lmbd_iam_role" {
  type = string
  description = "Iam role for lambda function"
}



variable "glue_workflow_name" {
  type = string
  description = "glue workflow name to be started"
}

variable "bucket_arn" {
  type = string
  description = "Aws S3 arn"
}

variable "bucket_id" {
  type = string
  description = "Bucket name"
}

variable "s3_prefix" {
  type = string
  description = "file path from the s3"
}

variable "lmbd_s3_buckt" {
  type = string
  description = "s3 bucket name for lambda function"
}
variable "lmbd_s3_key" {
  type = string
  description = "lambda script location on s3"
}

variable "lmbd_etags" {
  type = string
  description = "make change when we update on code"
}