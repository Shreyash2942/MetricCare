terraform {
  required_version = ">= 1.0.0" # Ensure that the Terraform version is 1.0.0 or higher

  required_providers {
    aws = {
      source = "hashicorp/aws" # Specify the source of the AWS provider
      version = "~> 6.12.0"        # Use a version of the AWS provider that is compatible with version
    }
  }
}

resource "aws_glue_catalog_database" "this" {
  name = var.database_name
  description = var.description_database
  location_uri = var.database_location
}