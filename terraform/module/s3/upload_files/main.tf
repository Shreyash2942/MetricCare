terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.12.0"
    }
  }
}

resource "aws_s3_object" "upload_file" {
  bucket = var.bucket_name
  key    = var.upload_file.s3_location
  source = var.upload_file.source_location
  etag   = filemd5(var.upload_file.source_location)
}