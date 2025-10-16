resource "aws_dynamodb_table" "workflow_metadata" {
  name         = "${terraform.workspace}_${var.project_name}_workflow_metadata"
  billing_mode = "PAY_PER_REQUEST"

  # Keys
  hash_key  = "dataset"   # Partition key
  range_key = "filename"  # Sort key

  attribute {
    name = "dataset"
    type = "S"
  }

  attribute {
    name = "filename"
    type = "S"
  }

  tags = {
    Project     = var.project_name
  }
}
