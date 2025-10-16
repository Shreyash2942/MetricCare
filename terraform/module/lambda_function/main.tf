terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws" # Specify the source of the AWS provider
      version = "~> 6.12.0"        # Use a version of the AWS provider that is compatible with version
    }
  }
}

resource "aws_lambda_function" "this" {
  function_name = "${terraform.workspace}_${var.lmbd_name}"
  role          = var.lmbd_iam_role
  handler = "lambda_function.lambda_handler"
  runtime = "python3.9"

  #lambda code s3 location
  s3_bucket = var.lmbd_s3_buckt
  s3_key = var.lmbd_s3_key
  source_code_hash = var.lmbd_etags

  environment {
    variables = {
      GLUE_WORKFLOW_NAME=var.glue_workflow_name
    }
  }

}

# S3 invoke
resource "aws_lambda_permission" "allow_s3" {
  statement_id = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.this.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = var.bucket_arn
}

#s3 bucket notification
resource "aws_s3_bucket_notification" "s3_to_lambda" {
  bucket = var.bucket_id
  lambda_function {
    lambda_function_arn = aws_lambda_function.this.arn
    events = ["s3:ObjectCreated:*"]
    filter_prefix = var.s3_prefix
    filter_suffix       = ".json"
  }

  depends_on = [aws_lambda_permission.allow_s3]
}