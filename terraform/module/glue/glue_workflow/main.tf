terraform {
  required_version = ">= 1.0.0" # Ensure that the Terraform version is 1.0.0 or higher

  required_providers {
    aws = {
      source = "hashicorp/aws" # Specify the source of the AWS provider
      version = "~> 6.12.0"        # Use a version of the AWS provider that is compatible with version
    }
  }
}

resource "aws_glue_workflow" "glue_workflow" {
  name = var.workflow_name
  #"${terraform.workspace}_mc_de_4_workflow
  description = "${terraform.workspace}_${var.workflow_name} project workflow Bronze -> silver -> Gold"
}