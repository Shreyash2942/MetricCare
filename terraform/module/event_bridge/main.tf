###############################################
# EventBridge (Event Hub) for Glue Job Failures
###############################################
terraform {
  required_version = ">= 1.0.0" # Ensure that the Terraform version is 1.0.0 or higher

  required_providers {
    aws = {
      source = "hashicorp/aws" # Specify the source of the AWS provider
      version = "~> 6.12.0"        # Use a version of the AWS provider that is compatible with version
    }
  }
}
resource "aws_cloudwatch_event_rule" "this" {
  name        = "${var.env_prefix}-glue-failure-rule"
  description = "Trigger when specified Glue jobs fail in ${var.env_prefix} environment"

  event_pattern = jsonencode({
    "source"       : ["aws.glue"],
    "detail-type"  : ["Glue Job State Change"],
    "detail"       : {
      "state"    : ["FAILED"],
      "jobName"  : var.glue_job_names
    }
  })
}

# EventBridge target that sends events to your existing SNS topic
resource "aws_cloudwatch_event_target" "sns_target" {
  rule      = aws_cloudwatch_event_rule.this.name
  arn       = var.sns_topic_arn
}

