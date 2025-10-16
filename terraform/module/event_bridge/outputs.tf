output "event_rule_name" {
  description = "EventBridge rule name for Glue job failure alerts"
  value       = aws_cloudwatch_event_rule.this.name
}
