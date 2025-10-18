# ⚙️ AWS Glue Job Module

This module provisions one or more **AWS Glue ETL Jobs** that perform transformations across the MetricCare data lake layers (Bronze → Silver → Gold).  
Each Glue Job runs a **PySpark script stored in S3** to process FHIR datasets (Patients, Encounters, Conditions) into curated and analytics-ready CMS metric tables.

---

## 📖 Overview

| Component | Purpose |
|------------|----------|
| **Glue Job** | Executes a PySpark script to transform and load data. |
| **Job Bookmarking** | Enables incremental processing of new data only. |
| **IAM Role** | Grants Glue access to S3, Glue Catalog, and DynamoDB for metadata tracking. |
| **Glue Connection (optional)** | Defines data source connections (if applicable). |

---

## 🧩 Use Case in MetricCare Architecture

```
┌────────────┐     Extracted Data      ┌──────────────┐     Transformed Data     ┌──────────────────┐
│     S3     │ ─────────────────────► │   Glue Job    │ ─────────────────────► │ Glue Catalog DB  │
└────────────┘                        └──────────────┘                         └──────────────────┘
     ▲                                        │
     │                                        ▼
     │                          Processed Tables in Athena / Power BI
```

- **S3 → Glue Job:** Reads raw JSON/Parquet FHIR data.  
- **Glue Job → Catalog Database:** Registers Hudi tables for Bronze, Silver, and Gold layers.  
- **Athena / BI Tools:** Query and visualize CMS metrics (Mortality, Infection, Readmission, ALOS).

---

## 🗂️ Module Structure

```bash
glue_job/
├── main.tf         # Defines Glue job configurations and permissions
├── variables.tf    # Input variables (job name, script location, role, etc.)
└── outputs.tf      # Exports job name and ARN
```

---

## ⚙️ Example Usage

Here’s an example of how to define Glue jobs using this module in your Terraform root:

```hcl
module "glue_job" {
  source = "./module/glue/glue_job"

  jobs = {
    bronze = {
      name          = "metriccare_bronze_etl"
      script_path   = "scripts/bronze_etl.py"
      glue_version  = "4.0"
      max_retries   = 1
      timeout       = 20
      worker_type   = "G.1X"
      number_of_workers = 2
      description   = "Extracts raw FHIR data and loads to Bronze Hudi tables"
    }
    silver = {
      name          = "metriccare_silver_etl"
      script_path   = "scripts/silver_etl.py"
      glue_version  = "4.0"
      max_retries   = 1
      timeout       = 25
      worker_type   = "G.1X"
      number_of_workers = 2
      description   = "Transforms Bronze data into curated Silver tables"
    }
  }

  role_arn = aws_iam_role.glue_job_role.arn
  temp_dir = "s3://metriccare-temp-dir/"
  tags = {
    Environment = terraform.workspace
    Project     = "MetricCare"
  }
}
```

---

## 🔑 Key Variables

| Variable | Description | Type | Default |
|-----------|--------------|------|----------|
| `jobs` | Map of Glue job configurations (name, script path, version, etc.). | `map(any)` | `{}` |
| `role_arn` | IAM role ARN used by Glue jobs. | `string` | `null` |
| `temp_dir` | Temporary S3 location for job checkpoints and logs. | `string` | `null` |
| `default_arguments` | Map of additional arguments for Glue job execution. | `map(string)` | `{}` |
| `tags` | Tags applied to all Glue jobs. | `map(string)` | `{}` |

---

## 📤 Outputs

| Output | Description |
|---------|--------------|
| `glue_job_names` | List of created Glue job names. |
| `glue_job_arns` | List of Glue job ARNs. |

---

## 🧠 Best Practices

- Store all PySpark scripts in **S3 → upload_scripts/** for version control.  
- Use **`--enable-continuous-log-filter`** and **`--job-bookmark-option job-bookmark-enable`** in `default_arguments`.  
- Use **Hudi tables** for incremental updates and upserts.  
- Test PySpark jobs locally before uploading to S3.  
- Configure **worker_type = "G.1X" or G.2X"** based on data size.  
- Separate job roles and logs by environment (dev, prod).  

---

## 🧩 Testing the Module

To deploy and test your Glue jobs individually:

```bash
terraform init
terraform apply -target=module.glue_job -auto-approve
```

Verification steps:
1. Go to **AWS Glue Console → Jobs**.  
2. Confirm job creation and check script location in S3.  
3. Run the job manually or trigger it via **Glue Workflow / Lambda**.  
4. Validate registered tables in **Glue Catalog Database**.  

---

## 🔗 References

- [Terraform AWS Glue Job Resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/glue_job)  
- [AWS Glue Developer Guide – Jobs](https://docs.aws.amazon.com/glue/latest/dg/add-job.html)  
- [AWS Glue Job Bookmarking](https://docs.aws.amazon.com/glue/latest/dg/monitor-continuations.html)  
- [AWS Glue and Hudi Integration](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-hudi.html)  
- [AWS Glue Logging & Monitoring](https://docs.aws.amazon.com/glue/latest/dg/monitor-jobs.html)

---

> 🧱 **Author:** Shreyash (Data Engineer)  
> 📚 *MetricCare – AWS Data Lakehouse for Healthcare Analytics*  
> 🔗 *Module: glue_job – ETL Job Deployment for Bronze, Silver, and Gold Layers*
