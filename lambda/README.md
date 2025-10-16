# ⚙️ AWS Lambda – Glue Workflow Trigger

## 🧩 Purpose

This Lambda function automates the **execution of AWS Glue Workflows** used in the MetricCare Lakehouse pipeline.  
It ensures that ETL jobs (Bronze → Silver → Gold) start automatically when new data arrives in S3 or when scheduled through EventBridge.

---

## 🧠 Function Overview

- **Validates Workflow Status:**  
  Before triggering, it checks recent Glue workflow runs to ensure none are already `RUNNING`, `WAITING`, or `STOPPING`.

- **Starts New Workflow Run:**  
  If the workflow is idle, it triggers a new run using the AWS Glue API (`start_workflow_run()`).

- **Returns Execution Metadata:**  
  Outputs JSON with workflow name, run ID, trigger source, and success/failure status.

- **Error Handling:**  
  Logs and returns detailed messages if permissions, configuration, or Glue service errors occur.

---

## ‼️ Why It’s Important

This Lambda is the **orchestration bridge** between data ingestion (S3) and ETL processing (Glue).  
It helps ensure:
- Automated pipeline execution without manual intervention  
- No overlapping workflow runs (avoiding data duplication or corruption)  
- Consistent data refresh cycles across environments (dev/prod)

---

## ⚙️ Environment Configuration

| Variable | Description | Example |
|-----------|--------------|----------|
| `GLUE_WORKFLOW_NAME` | The name of the Glue Workflow to start | `metriccare_etl_workflow` |

**Required IAM Permissions:**
```json
{
  "Action": [
    "glue:GetWorkflowRuns",
    "glue:StartWorkflowRun"
  ],
  "Effect": "Allow",
  "Resource": "*"
}
```

---

## 🚀 Deployment Instructions (Terraform)

When deploying via Terraform:

1. **Ensure your Python file exists**  
   ```bash
   lambda_glue_trigger.py
   ```

2. **Create a deployment package (.zip)**  
   ```bash
   zip function.zip lambda_glue_trigger.py
   ```

3. **Reference in Terraform configuration**
   ```hcl
   resource "aws_lambda_function" "metriccare_trigger" {
     function_name = "metriccare-glue-trigger"
     runtime       = "python3.12"
     handler       = "lambda_glue_trigger.lambda_handler"
     filename      = "function.zip"
     role          = aws_iam_role.lambda_glue_role.arn

     environment {
       variables = {
         GLUE_WORKFLOW_NAME = "metriccare_etl_workflow"
       }
     }
   }
   ```

---

## 🪶 Typical Trigger Sources

- **S3 ObjectCreated events:** When new JSON data (Patient, Encounter, Condition) is uploaded  
- **EventBridge schedule:** Timed Glue job refresh  
- **Manual invocation:** Through AWS Console, API Gateway, or CLI

---

## 📊 Integration Flow

```
S3 (Bronze Data) → Lambda Trigger → Glue Workflow (Bronze → Silver → Gold) → Athena/Power BI
```

---

## 🧾 Summary

✅ Automates Glue Workflow execution  
✅ Prevents duplicate runs  
✅ Integrates seamlessly with S3 and EventBridge  
✅ Essential for MetricCare’s ETL orchestration layer  

---

**Maintainer:** Shreyash  
**Project:** MetricCare Data Lakehouse  
**Version:** 1.0.0  
**License:** MIT
