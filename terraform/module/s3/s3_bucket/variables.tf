variable "bucket_name" {
  description = "name of S3 bucket"
  type = string
}

variable "tag" {
  type = map(string)
  description = "Tags for the buckets"
}