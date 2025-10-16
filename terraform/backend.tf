terraform {
  backend "s3" {
    bucket         = "mcde4-tfstate"      # your S3 bucket for state
    key            = "terraform/global/terraform.tfstate"
    region         = "us-east-1"          # same region as S3 + DynamoDB
    dynamodb_table = "mcde4_tflocks"      # your DynamoDB table name
    encrypt        = true
  }
}
