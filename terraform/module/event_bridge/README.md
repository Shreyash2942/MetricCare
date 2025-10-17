# ⏰ Amazon EventBridge Module

This module provisions **Amazon EventBridge rules and targets** that automate workflow scheduling and event-driven orchestration within the **MetricCare Data Lakehouse**.  
EventBridge is used to trigger AWS Glue workflows or Lambda functions on a time-based schedule (e.g., daily ETL refresh) or in response to specific AWS events (e.g., new S3 data uploads).

---

## 📖 Overview

| Component | Purpose |
|------------|----------|
| **EventBridge Rule** | Defines the event pattern or schedule (e.g., CRON expression, S3 event, or custom event). |
| **EventBridge Target** | Specifies which AWS service to invoke (Glue Workflow, Lambda, SNS, etc.). |
| **IAM Role / Policy** | Grants EventBridge permission to invoke the configured target services. |

---

## 🧩 Use Case in MetricCare Architecture

The EventBridge module enables both **scheduled and reactive workflows**, ensuring MetricCare’s pipelines run reliably and automatically.

```
┌──────────────┐      Triggers      ┌──────────────┐      Starts      ┌──────────────┐
│  EventBridge │ ─────────────────► │   Lambda     │ ───────────────► │   Glue Job   │
└──────────────┘                    └──────────────┘                  └──────────────┘
       ▲
       │
       │
   (CRON / S3 Event)
```

- **Scheduled Events:** Runs nightly ETL jobs at defined CRON intervals.  
- **S3 Events:** Starts workflows automatically when new FHIR data lands.  
- **SNS Integration:** Sends alerts if scheduled workflows fail or skip runs.

---

## 🗂️ Module Structure

```bash
event_bridge/
├── main.tf         # Defines EventBridge rules, schedules, and targets
├── variables.tf    # Input variables (event name, schedule, target ARN)
└── outputs.tf      # Exports rule name, ARN, and target details
```

---

## ⚙️ Example Usage

Below is an example configuration to trigger a Lambda function once per day at midnight UTC:

```hcl
module "event_bridge" {
  source              = "./module/event_bridge"
  rule_name           = "metriccare-daily-trigger"
  schedule_expression = "cron(0 0 * * ? *)" # Every day at 00:00 UTC
  target_arn          = module.lambda_function.lambda_arn
  description         = "Triggers the Glue workflow Lambda every day at midnight"
  is_enabled          = true
  tags = {
    Environment = terraform.workspace
    Project     = "MetricCare"
  }
}
```

> 💡 You can also configure event patterns (instead of schedules) to trigger workflows when specific AWS events occur — such as new S3 objects or SNS notifications.

---

## 🔑 Key Variables

| Variable | Description | Type | Default |
|-----------|--------------|------|----------|
| `rule_name` | Name of the EventBridge rule. | `string` | `"metriccare-etl-scheduler"` |
| `description` | Description of the rule. | `string` | `null` |
| `schedule_expression` | CRON or rate expression for scheduling. | `string` | `"rate(24 hours)"` |
| `event_pattern` | JSON pattern for event-based triggers. | `string` | `null` |
| `target_arn` | ARN of the target resource (Lambda, Glue, SNS). | `string` | `null` |
| `is_enabled` | Whether the rule is active. | `bool` | `true` |
| `tags` | Key-value pairs of tags. | `map(string)` | `{}` |

---

## 📤 Outputs

| Output | Description |
|---------|--------------|
| `rule_name` | Name of the created EventBridge rule. |
| `rule_arn` | ARN of the rule. |
| `target_arn` | Target ARN linked to the rule. |

---

## 🧠 Best Practices

- Use **CRON expressions** for predictable schedule intervals.  
- Keep **one rule per workflow** to simplify debugging and monitoring.  
- Integrate with **SNS** for success/failure alerts.  
- Use **CloudWatch Logs** to track rule invocations and target responses.  
- Tag each rule by environment and project (`metriccare_dev`, `metriccare_prod`).  

---

## 🧩 Testing the Module

Run this module independently to verify your EventBridge rule setup:

```bash
terraform init
terraform apply -target=module.event_bridge -auto-approve
```

You can test triggering manually:
```bash
aws events put-events --entries file://test_event.json
```

> Check CloudWatch Logs for Lambda or Glue invocations triggered by EventBridge.

---

## 🧩 Example Event Pattern (Optional)

To trigger the workflow when new data lands in S3:

```hcl
event_pattern = jsonencode({
  "source" : ["aws.s3"],
  "detail-type" : ["AWS API Call via CloudTrail"],
  "detail" : {
    "eventName" : ["PutObject"],
    "requestParameters" : {
      "bucketName" : ["metriccare-raw-data"]
    }
  }
})
```

---

## 🔗 References

- [Terraform AWS EventBridge Rule](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_rule)  
- [Terraform AWS EventBridge Target](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudwatch_event_target)  
- [AWS EventBridge Developer Guide](https://docs.aws.amazon.com/eventbridge/latest/userguide/what-is-amazon-eventbridge.html)  
- [CRON Expressions for EventBridge](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-create-rule-schedule.html)  
- [AWS CLI – Put Events](https://docs.aws.amazon.com/cli/latest/reference/events/put-events.html)

---

> 🧱 **Author:** Shreyash (Data Engineer)  
> 📚 *MetricCare – AWS Data Lakehouse for Healthcare Analytics*  
> 🔗 *Module: event_bridge – Workflow Scheduling and Orchestration*
