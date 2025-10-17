# 🧩 AWS Lambda Function Module

This module provisions an **AWS Lambda function** that orchestrates the MetricCare ETL workflow by triggering **AWS Glue Workflows** whenever new data is uploaded to S3 or on a scheduled basis via EventBridge.  
The Lambda function acts as the **automation brain** of the data lakehouse, connecting event-driven and scheduled pipelines.

---

## 📖 Overview

| Component | Purpose |
|------------|----------|
| **Lambda Function** | Executes orchestration logic (e.g., start Glue Workflow). |
| **IAM Role & Policies** | Grants Lambda permission to invoke Glue, access S3, and read logs. |
| **Environment Variables** | Configurable parameters like workflow name, environment, and bucket. |
| **S3 Source** | Stores the Lambda deployment package (ZIP) uploaded via Terraform. |

---

## 🧩 Use Case in MetricCare Architecture

```
┌────────────┐        New Data        ┌──────────────┐       Starts        ┌──────────────┐
│     S3     │ ────────────────────► │   Lambda     │ ─────────────────► │   Glue Job   │
└────────────┘                       └──────────────┘                    └──────────────┘
       ▲                                     │
       │                                     ▼
       │                          Sends alerts via SNS/EventBridge
       │
   (FHIR JSON Upload)
```

- **S3 → Lambda:** Triggered by new data uploads.  
- **Lambda → Glue:** Starts Glue Workflow (Bronze → Silver → Gold ETL).  
- **EventBridge → Lambda:** Executes scheduled workflow runs.  
- **Lambda → SNS:** Sends job status or error alerts.

---

## 🗂️ Module Structure

```bash
lambda_function/
├── main.tf         # Defines Lambda function, IAM role, and environment variables
├── variables.tf    # Input variables (function name, handler, runtime, etc.)
└── outputs.tf      # Exports Lambda ARN and IAM role
```

---

## ⚙️ Example Usage

Below is an example of how to call this module in your Terraform root:

```hcl
module "lambda_function" {
  source              = "./module/lambda_function"
  function_name       = "metriccare_trigger_glue"
  handler             = "myglueworkflow.myglueworkflow"
  runtime             = "python3.12"
  s3_bucket           = var.lambda_script_bucket
  s3_key              = "lambda/myglueworkflow.zip"
  environment = {
    GLUE_WORKFLOW_NAME = "hudi_to_silver_shreyash"
    LOG_LEVEL          = "INFO"
  }
  timeout             = 60
  memory_size         = 256
  tags = {
    Environment = terraform.workspace
    Project     = "MetricCare"
  }
}
```

> ⚡ Make sure the Lambda deployment ZIP file is uploaded to S3 before running `terraform apply`.

---

## 🔑 Key Variables

| Variable | Description | Type | Default |
|-----------|--------------|------|----------|
| `function_name` | Name of the Lambda function. | `string` | `"metriccare_trigger_glue"` |
| `handler` | Entry point (e.g., `file_name.handler_function`). | `string` | `"lambda_function.lambda_handler"` |
| `runtime` | Lambda runtime environment. | `string` | `"python3.12"` |
| `s3_bucket` | S3 bucket containing the Lambda ZIP file. | `string` | `null` |
| `s3_key` | Key (path) to the Lambda ZIP in S3. | `string` | `null` |
| `timeout` | Timeout (in seconds) for the function. | `number` | `60` |
| `memory_size` | Memory allocation for Lambda. | `number` | `256` |
| `environment` | Map of environment variables passed to Lambda. | `map(string)` | `{}` |
| `tags` | Common tags applied to resources. | `map(string)` | `{}` |

---

## 📤 Outputs

| Output | Description |
|---------|--------------|
| `lambda_arn` | ARN of the created Lambda function. |
| `lambda_name` | Name of the function. |
| `lambda_role_arn` | IAM Role ARN associated with the Lambda function. |

---

## 🧠 Best Practices

- Use **versioned ZIP deployments** to maintain reproducibility.  
- Store all Lambda scripts in a dedicated S3 prefix (`upload_scripts/`).  
- Grant **least-privilege IAM policies** — only Glue, S3, and CloudWatch Logs access.  
- Enable **CloudWatch logging** for observability.  
- Keep **timeout < 5 minutes**; Glue handles long ETL operations.  
- Use **environment variables** for workflow names instead of hardcoding them.

---

## 🧩 Testing the Module

To validate deployment:

```bash
terraform init
terraform apply -target=module.lambda_function -auto-approve
```

Then verify:

- In AWS Console → Lambda → **metriccare_trigger_glue**
- Check **Environment variables** and **Execution role**.
- Trigger test events manually from S3 or EventBridge.

---

## 🧩 Example Lambda Script Reference

The associated Python script (uploaded via S3) might look like this:

```python
import boto3
import os

glue = boto3.client("glue")

def lambda_handler(event, context):
    workflow_name = os.environ["GLUE_WORKFLOW_NAME"]
    print(f"Starting Glue Workflow: {workflow_name}")
    glue.start_workflow_run(Name=workflow_name)
    return {"status": "Workflow Triggered"}
```

---

## 🔗 References

- [Terraform AWS Lambda Resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_function)  
- [Terraform Lambda Permissions](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/lambda_permission)  
- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)  
- [AWS Glue Workflow Integration](https://docs.aws.amazon.com/glue/latest/dg/orchestrate-workflow.html)  
- [EventBridge and Lambda Integration](https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-targets-lambda.html)

---

> 🧱 **Author:** Shreyash (Data Engineer)  
> 📚 *MetricCare – AWS Data Lakehouse for Healthcare Analytics*  
> 🔗 *Module: lambda_function – Event-Driven Orchestration for Glue Workflows*
