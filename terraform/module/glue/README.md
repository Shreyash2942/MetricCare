# 🧬 AWS Glue Modules (MetricCare Lakehouse)

This directory contains all **AWS Glue-related Terraform modules** used to build the **MetricCare Data Lakehouse**.  
It provides the ETL foundation for transforming raw healthcare (FHIR) data into structured, queryable, and analytics-ready datasets across Bronze, Silver, and Gold layers.

---

## 📖 Overview

The Glue module suite automates the following key processes:

| Component | Description |
|------------|--------------|
| **Glue Catalog Database** | Defines metadata databases for Bronze, Silver, and Gold layers. |
| **Glue Job** | Executes PySpark-based ETL scripts to process and load datasets. |
| **Glue Workflow** | Orchestrates sequential job execution with defined dependencies. |

Together, these modules form the **ETL backbone** of the MetricCare Lakehouse — enabling automated, versioned, and queryable data transformations.

---

## 🗂️ Folder Structure

```bash
glue/
├── glue_catalog_database/     # Creates AWS Glue Databases for metadata storage
├── glue_job/                  # Defines and deploys ETL jobs (PySpark scripts in S3)
├── glue_workflow/             # Orchestrates ETL job execution via triggers
│
├── main.tf                    # (Optional) Wrapper to call submodules together
├── variables.tf               # (Optional) Common input variables (e.g., tags, IAM role)
├── outputs.tf                 # (Optional) Outputs consolidated from submodules
└── README.md                  # This documentation file
```

---

## ⚙️ Submodules Summary

| Submodule | Purpose |
|------------|----------|
| [`glue_catalog_database/`](./glue_catalog_database) | Creates AWS Glue databases for Bronze, Silver, and Gold data layers. |
| [`glue_job/`](./glue_job) | Deploys PySpark ETL jobs that load and transform data between layers. |
| [`glue_workflow/`](./glue_workflow) | Chains Glue jobs into orchestrated workflows using triggers and dependencies. |

---

## 🔁 Architecture Flow

```
       ┌──────────────────────────────────────────────┐
       │                AWS Glue Stack                │
       │──────────────────────────────────────────────│
       │                                              │
       │  Catalog Database ──→ ETL Jobs ──→ Workflow  │
       │  (Bronze/Silver/Gold)     (Transformation)   │
       │                                              │
       └──────────────────────────────────────────────┘
                      ▲                   ▲
                      │                   │
             Lambda / EventBridge     SNS Notifications
```

- **Glue Catalog Database**: Defines metadata for Hudi tables and partitions.  
- **Glue Jobs**: Execute data transformations using PySpark scripts stored in S3.  
- **Glue Workflow**: Ensures jobs run in sequence (Bronze → Silver → Gold).  
- **Lambda / EventBridge**: Triggers workflows automatically.  
- **SNS**: Sends notifications on success or failure.  

---

## 🧩 Example Combined Deployment

Here’s an example of how all Glue submodules can be invoked together in your root `main.tf`:

```hcl
module "glue_catalog_database" {
  source = "./module/glue/glue_catalog_database"
  databases = {
    bronze = "metriccare_bronze_db"
    silver = "metriccare_silver_db"
    gold   = "metriccare_gold_db"
  }
}

module "glue_job" {
  source   = "./module/glue/glue_job"
  role_arn = aws_iam_role.glue_job_role.arn
  temp_dir = "s3://metriccare-temp-dir/"
  jobs = {
    bronze = { name = "bronze_etl", script_path = "scripts/bronze_etl.py" }
    silver = { name = "silver_etl", script_path = "scripts/silver_etl.py" }
    gold   = { name = "gold_etl", script_path = "scripts/gold_etl.py" }
  }
}

module "glue_workflow" {
  source = "./module/glue/glue_workflow"
  workflow_name = "metriccare_etl_workflow"
  jobs = {
    bronze = module.glue_job.glue_job_names[0]
    silver = module.glue_job.glue_job_names[1]
    gold   = module.glue_job.glue_job_names[2]
  }
}
```

---

## 📤 Outputs and Integration

| Integration | Description |
|--------------|--------------|
| **Lambda Function** | Reads workflow name from environment variables (`GLUE_WORKFLOW_NAME`). |
| **EventBridge** | Triggers workflows on schedule or S3 events. |
| **Athena** | Queries data registered in Glue Catalog Databases. |
| **Power BI** | Consumes analytical datasets from Gold layer. |

---

## 🧠 Best Practices

- Maintain **consistent naming conventions**:  
  - Databases → `metriccare_<layer>_db`  
  - Jobs → `metriccare_<layer>_etl`  
  - Workflow → `metriccare_etl_workflow`  
- Store scripts in versioned S3 paths (`upload_scripts/`).  
- Enable **Hudi-based incremental ingestion** for all jobs.  
- Use **CloudWatch** for monitoring job and workflow metrics.  
- Tag all Glue resources with `Environment`, `Project`, and `Owner` identifiers.  

---

## 🔗 References

- [Terraform AWS Glue Catalog Database](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/glue_catalog_database)  
- [Terraform AWS Glue Job](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/glue_job)  
- [Terraform AWS Glue Workflow](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/glue_workflow)  
- [AWS Glue Documentation](https://docs.aws.amazon.com/glue/)  
- [AWS Glue and Athena Integration](https://docs.aws.amazon.com/athena/latest/ug/glue-best-practices.html)  

---

> 🧱 **Author:** Shreyash (Data Engineer)  
> 📚 *MetricCare – AWS Data Lakehouse for Healthcare Analytics*  
> 🔗 *Module: glue – Centralized ETL Orchestration using AWS Glue*
