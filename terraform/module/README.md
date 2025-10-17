# 🧩 MetricCare Terraform Modules

This directory contains all **Terraform modules** used to provision the MetricCare AWS Data Lakehouse infrastructure.  
Each module defines a reusable building block representing a major AWS service such as S3, Lambda, Glue, DynamoDB, EventBridge, or SNS — all working together to automate data ingestion, ETL processing, and workflow orchestration.

---

## 📦 Module Overview

MetricCare’s Terraform layer uses **6 core AWS services**, each represented by one or more reusable modules.

| AWS Service | Use Case in MetricCare |
|--------------|------------------------|
| **Amazon S3** | Serves as the data lake storage for raw → bronze → silver → gold layers, and hosts ETL scripts/configuration files. |
| **AWS Lambda** | Automates Glue workflows by triggering ETL jobs when new data arrives in S3. |
| **AWS Glue** | Performs ETL processing, maintains Hudi tables, and organizes data into the Bronze, Silver, and Gold layers. |
| **Amazon DynamoDB** | Tracks processed files for incremental ingestion, ensuring idempotent ETL runs. |
| **Amazon SNS** | Sends notifications for Glue workflow success, failure, or error alerts. |
| **Amazon EventBridge** | Schedules recurring workflows and manages event-driven orchestration between services. |

> 💡 Each service has its own dedicated module folder (e.g., `glue/`, `s3/`, `lambda_function/`) containing Terraform definitions for related resources.

---

## 🗂️ Module Directory Structure

```bash
module/
│
├── aws_sns/                     # Notification system for Glue and Lambda events
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
│
├── dynemoDB/                    # Table for tracking processed files
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
│
├── event_bridge/                # Scheduler and event router for workflow automation
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
│
├── glue/                        # All Glue-related modules (database, jobs, workflows)
│   ├── glue_catalog_database/
│   ├── glue_job/
│   └── glue_workflow/
│
├── lambda_function/             # Lambda function to trigger Glue workflows
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
│
└── s3/                          # Data lake buckets and script uploads
    ├── s3_bucket/
    ├── upload_files/
    └── upload_scripts/
```

---

## ⚙️ Module Design Pattern

Each Terraform module follows a **consistent structure** for readability and reusability:

| File | Purpose |
|------|----------|
| `main.tf` | Contains the AWS resource definitions for the service. |
| `variables.tf` | Defines input variables required by the module. |
| `outputs.tf` | Exposes outputs such as ARNs, names, or IDs to parent modules. |

Example (Lambda Module Reference):

```hcl
module "lambda_function" {
  source              = "./module/lambda_function"
  function_name       = "trigger_glue_workflow"
  handler             = "myglueworkflow.lambda_handler"
  runtime             = "python3.12"
  s3_bucket           = var.lambda_script_bucket
  environment = {
    GLUE_WORKFLOW_NAME = var.glue_workflow_name
  }
}
```

> 🧠 Each module is self-contained, reusable across environments, and designed for workspace-based deployment.

---

## 🔄 How Modules Interact

```
┌────────────┐
│   S3       │  → Stores raw and transformed data (Bronze → Silver → Gold)
└────┬───────┘
     │
     ▼
┌────────────┐
│ Lambda     │  → Triggers Glue workflows when new data lands in S3
└────┬───────┘
     │
     ▼
┌────────────┐
│ Glue Jobs  │  → Transforms, cleans, and aggregates CMS metrics
└────┬───────┘
     │
     ▼
┌────────────┐
│ DynamoDB   │  → Tracks processed files for incremental updates
└────┬───────┘
     │
     ▼
┌────────────┐
│ SNS/EventBridge │ → Sends alerts & orchestrates periodic runs
└────────────────┘
```

---

## 🧩 Development Workflow

- **Test a single module:**
  ```bash
  terraform apply -target=module.lambda_function -auto-approve
  ```

- **Destroy a single module:**
  ```bash
  terraform destroy -target=module.lambda_function -auto-approve
  ```

- **Add a new module:**
  ```bash
  module "new_service" {
    source = "./module/new_service"
  }
  ```

> 🧩 This modular design allows independent development, testing, and deployment of each service component.

---

## 🧠 Best Practices

- Follow consistent **naming standards**: `metriccare_<service>_<env>`  
- Keep **provider versions pinned** (`version = "~> 6.12.0"`)  
- Avoid circular dependencies between modules  
- Export only required outputs (ARNs, IDs)  
- Test modules in isolation before integrating with main stack  

---

## 🧱 Future Enhancements

Planned or potential modules to expand functionality:
- `cloudwatch/` → Centralized monitoring and alerts for Glue & Lambda  
- `kms/` → Encryption key management for secure storage and data transfers  
- `redshift/` → Data warehouse integration for analytical workloads  
- `cloudtrail/` → Audit logging for infrastructure change tracking  

---

## 🔗 References

- [Terraform AWS Provider Docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)  
- [Terraform Modules Best Practices](https://developer.hashicorp.com/terraform/language/modules/develop)  
- [AWS Glue Documentation](https://docs.aws.amazon.com/glue/)  
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)  
- [Amazon S3 Documentation](https://docs.aws.amazon.com/s3/)  
- [Amazon DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)  
- [Amazon EventBridge Documentation](https://docs.aws.amazon.com/eventbridge/)  
- [Amazon SNS Documentation](https://docs.aws.amazon.com/sns/)

---

> 🧱 **Author:** Shreyash (Data Engineer)  
> 📚 *MetricCare – AWS Data Lakehouse for Healthcare Analytics*  
> 🔗 *Built with Terraform, AWS Glue, Lambda, S3, DynamoDB, EventBridge, and SNS*
