##########################
# SNS Alert Module Outputs
##########################

output "sns_topic_arn" {
  description = "ARN of the SNS topic used for alerts"
  value       = aws_sns_topic.this.arn
}

output "sns_topic_name" {
  description = "SNS topic name"
  value       = aws_sns_topic.this.name
}
