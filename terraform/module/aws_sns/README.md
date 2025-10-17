# 🔔 AWS SNS Module

This module provisions an **Amazon Simple Notification Service (SNS)** topic and optional subscriptions used for real-time notifications within the **MetricCare Data Lakehouse**.  
It enables cross-service communication and event alerts for Glue workflows, Lambda functions, and EventBridge rules.

---

## 📖 Overview

| Component | Purpose |
|------------|----------|
| **SNS Topic** | Central notification channel for ETL job success, failure, or alert events. |
| **SNS Subscriptions** | (Optional) Email, Lambda, or SQS endpoints that receive messages. |
| **IAM Policies** | Grants publish permissions to AWS Glue, Lambda, and EventBridge. |

---

## 🧩 Use Case in MetricCare Architecture

The SNS module is responsible for distributing system-level notifications and pipeline events across the MetricCare environment.

```
┌────────────┐       Job Status      ┌────────────┐
│  AWS Glue  │ ────────────────────► │    SNS     │
└────────────┘                       └─────┬──────┘
                                          │
                                          ▼
                              ┌─────────────────────┐
                              │ Lambda / Email / SQS│
                              └─────────────────────┘
```

- **Glue → SNS:** Publishes messages when ETL jobs or workflows complete or fail.  
- **Lambda → SNS:** Sends notifications when triggered by new S3 data or errors.  
- **EventBridge → SNS:** Routes scheduled or rule-based alerts.

---

## 🗂️ Module Structure

```bash
aws_sns/
├── main.tf         # Defines SNS topic, subscriptions, and IAM policies
├── variables.tf    # Input variables (topic name, email endpoints, etc.)
└── outputs.tf      # Exports topic ARN and subscription details
```

---

## ⚙️ Example Usage

Below is an example of how this module can be invoked inside your root `main.tf`:

```hcl
module "aws_sns" {
  source       = "./module/aws_sns"
  topic_name   = "metriccare-alerts"
  subscriptions = [
    {
      protocol = "email"
      endpoint = "alerts@metriccare.io"
    }
  ]
}
```

> 💡 You can also attach Lambda or SQS subscriptions by changing the `protocol` and `endpoint` values.

---

## 🔑 Key Variables

| Variable | Description | Type | Default |
|-----------|--------------|------|----------|
| `topic_name` | Name of the SNS topic to create. | `string` | `"metriccare-alerts"` |
| `subscriptions` | List of subscription objects (protocol + endpoint). | `list(object)` | `[]` |
| `tags` | Common tags to apply to the SNS resources. | `map(string)` | `{}` |
| `policy_json` | Optional custom access policy for publishing. | `string` | `null` |

---

## 📤 Outputs

| Output | Description |
|---------|--------------|
| `sns_topic_arn` | ARN of the created SNS topic. |
| `sns_topic_name` | Name of the SNS topic. |
| `sns_subscription_arns` | List of created subscription ARNs. |

---

## 🧠 Best Practices

- Use **topic naming convention:** `metriccare-<env>-alerts` for consistency across environments.  
- Limit `Publish` permissions to trusted AWS services (Glue, Lambda).  
- Use **email confirmation** for verified recipients in dev/test environments.  
- For production, integrate SNS with **AWS Lambda or SQS** to automate event handling.  
- Enable **CloudWatch metrics** on SNS topics for delivery tracking and failures.

---

## 🧩 Testing the Module

Apply this module independently to validate SNS creation and subscription delivery:

```bash
terraform init
terraform apply -target=module.aws_sns -auto-approve
```

You can confirm subscription emails by checking your inbox for AWS confirmation links.

---

## 🔗 References

- [Terraform AWS SNS Module Docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/sns_topic)  
- [AWS SNS Developer Guide](https://docs.aws.amazon.com/sns/latest/dg/welcome.html)  
- [AWS SNS Subscription Protocols](https://docs.aws.amazon.com/sns/latest/dg/sns-delivery-protocols.html)  
- [AWS SNS Access Policy Examples](https://docs.aws.amazon.com/sns/latest/dg/sns-access-policy-use-cases.html)

---

> 🧱 **Author:** Shreyash (Data Engineer)  
> 📚 *MetricCare – AWS Data Lakehouse for Healthcare Analytics*  
> 🔗 *Module: aws_sns – Event Notifications for Glue and Lambda Workflows*
