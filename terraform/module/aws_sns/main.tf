###############################################
# SNS Alert Module — Supports Multiple Emails
###############################################

# SNS Topic for alerts (environment-aware)
resource "aws_sns_topic" "this" {
  name = "${var.env_prefix}-alert-topic"
}

# Create subscriptions for each email/phone in the list
resource "aws_sns_topic_subscription" "subscribers" {
  for_each = toset(var.endpoints)

  topic_arn = aws_sns_topic.this.arn
  protocol  = var.protocol   # "email" or "sms"
  endpoint  = each.value
}

# Allow EventBridge to publish to this SNS topic
resource "aws_sns_topic_policy" "allow_eventbridge_publish" {
  arn    = aws_sns_topic.this.arn
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "events.amazonaws.com"
        },
        Action = "sns:Publish",
        Resource = aws_sns_topic.this.arn
      }
    ]
  })
}
