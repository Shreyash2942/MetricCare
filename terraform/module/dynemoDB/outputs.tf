output "workflow_metadata_table_name" {
  description = "DynamoDB metadata table name"
  value       = aws_dynamodb_table.workflow_metadata.name
}

output "workflow_metadata_table_arn" {
  description = "DynamoDB metadata table ARN"
  value       = aws_dynamodb_table.workflow_metadata.arn
}
