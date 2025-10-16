terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.12.0"
    }
  }
}
resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name
  force_destroy = true
  tags = var.tag
}