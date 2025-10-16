variable "bucket_name" {
  type        = string
  description = "Name of the S3 bucket where the file will be uploaded."
}

variable "upload_file" {
  description = "Details of the file to upload to S3."
  type = object({
    source_location = string
    s3_location     = string
  })
}
