output "bronze_trigger_name" {
  description = "Bronze Glue trigger name"
  value       = aws_glue_trigger.glue_job_bronze.name
}

output "silver_trigger_name" {
  description = "Silver Glue trigger name"
  value       = aws_glue_trigger.glue_job_silver
}

output "workflow_name" {
  description = "The Glue workflow name"
  value       = aws_glue_workflow.glue_workflow.name
}
