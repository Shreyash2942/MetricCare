output "job_names" {
  description = "List of Glue job names created"
  value       = [for job in aws_glue_job.etl_jobs : job.name]
}

output "job_arns" {
  description = "List of Glue job ARNs created"
  value       = [for job in aws_glue_job.etl_jobs : job.arn]
}