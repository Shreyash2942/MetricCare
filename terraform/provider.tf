terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.12.0"   # or "= 6.12.0" if you want exactly
    }
  }
}

# AWS provider configuration
provider "aws" {
  region = var.aws_region
}
