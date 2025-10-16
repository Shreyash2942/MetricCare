# 🧱 MetricCare Infrastructure Configuration (`config.tf`)

This configuration defines all **Terraform variables** used to deploy the **MetricCare AWS Data Lakehouse** — including S3 buckets, Glue jobs, IAM roles, DynamoDB, Lambda triggers, and SNS alerts.  
It allows the same infrastructure code to be reused across **dev**, **test**, and **prod** environments by changing variable files (`*.tfvars`) or module inputs.

---

## ⚙️ Overview

| Category | Purpose |
|-----------|----------|
| **AWS Region & Tags** | Define base deployment region and metadata for resource tagging. |
| **S3 Configuration** | Manage the main storage bucket for Glue jobs, configurations, and data. |
| **Glue Job Scripts** | Define all script paths and job names for Bronze, Silver, and Gold layers. |
| **Glue Catalog & Workflow** | Manage Glue database, workflow orchestration, and job linking. |
| **IAM Roles** | Provide role ARNs for Glue and Lambda jobs. |
| **Lambda Functions** | Define Lambda code artifacts and names. |
| **DynamoDB** | Store incremental metadata (`processed_files`). |
| **SNS Alerts** | Configure alert recipients and protocols (email/SMS). |
| **S3 Prefixes** | Standardize storage paths for FHIR data. |

---

## 🗺️ Deployment Flow

```
Terraform Module
     │
     ├── config.tf      → Defines variables (this file)
     ├── main.tf        → Creates S3, Glue, DynamoDB, Lambda, SNS
     ├── outputs.tf     → Exports resource ARNs and names
     └── *.tfvars       → Environment overrides (dev, prod)
```

---

## 🧩 Variable Reference

### 🌍 AWS & Project Metadata

| Variable | Default | Description |
|-----------|----------|-------------|
| `aws_region` | `"us-east-1"` | AWS region for deployment |
| `bucket_name` | `"mcde4-sp"` | S3 bucket for all project data |
| `project_name` | `"mc_de_4"` | Used for naming conventions |
| `tag` | `{ name, Project, owner, createdby }` | Resource tagging block |

---

### 🪣 S3 & Config Files

| Variable | Description |
|-----------|-------------|
| `config_file` | Uploads the `config/config.json` file to S3 for reference |
| `s3_prefix` | Base folder structure for all ingested JSON files (default `fhir_data/json/patient`) |

**Example Path Structure:**
```
s3://mcde4-sp/fhir_data/json/patient/patient_20251015.json
```

---

### 🔐 IAM Roles

| Variable | Default | Used For |
|-----------|----------|----------|
| `iam_role` | `AWSGlueServiceRole-metriccare` | Glue jobs and workflow |
| `lmbd_iam_role` | `my-job-role-cn7zdaxh` | Lambda S3 → Glue trigger |

---

### 🧱 Glue Scripts & Jobs

| Layer | Variable Key | Job Name | Description |
|--------|---------------|-----------|--------------|
| Bronze | `bronze_condition`, `bronze_encounter`, `bronze_patient` | e.g. `job_bronze_condition_hudi` | Raw ingestion with Hudi |
| Silver | `silver_condition`, `silver_encounter`, `silver_patient` | e.g. `job_silver_condition` | Data cleansing & normalization |
| Gold | `gold_infection_rate`, `gold_mortality_rate`, `gold_readmission_rate` | e.g. `job_gold_infection_rate` | Aggregated CMS metric calculations |

---

### 🧩 Glue Database & Workflow

| Variable | Default | Description |
|-----------|----------|-------------|
| `glue_database_name` | `"mcde4_sp"` | Logical database for Hudi tables |
| `glue_database_location` | `"hudi_database/database"` | S3 path for Glue Catalog data |
| `workflow_name` | `"mc_de_4_workflow"` | Central workflow to link Bronze → Silver → Gold |

---

### ⚡ Lambda Functions

| Variable | Description |
|-----------|-------------|
| `lambda_function_name` | `"lambda_mcde4_sp"` |
| `lambda_script` | Points to packaged Lambda zip that triggers Glue workflow on S3 events. |

**Example Workflow:**
```
S3 Upload (bronze/patient/*.json)
       ↓
Lambda Trigger (lambda_mcde4_sp)
       ↓
Glue Workflow (mc_de_4_workflow)
```

---

### 🔔 SNS Alerts

| Variable | Default | Description |
|-----------|----------|-------------|
| `sns_protocol` | `"email"` | Notification protocol (email or sms) |
| `sns_endpoints` | `["shreyash@takeo.com", "teamlead@example.com", "opsengineer@example.com"]` | Alert recipients |

Triggered on:
- Glue job failure or timeout  
- Workflow completion notifications  
- Lambda errors

---

### 🧾 DynamoDB Table

| Variable | Description |
|-----------|-------------|
| `project_name` | Used to name DynamoDB table for incremental metadata tracking. |

**Example Table:**
```
Table Name: processed_files_mc_de_4
Partition Key: s3_key
Attributes: etag, status, timestamp
```

---

## 🧠 Usage Example

**Terraform Apply (Dev environment)**
```bash
terraform init
terraform plan -var-file="env/dev.tfvars"
terraform apply -var-file="env/dev.tfvars"
```

**Sample `dev.tfvars`**
```hcl
aws_region     = "us-east-1"
bucket_name    = "mcde4-dev"
project_name   = "mc_de_4_dev"
workflow_name  = "mc_de_4_dev_workflow"

sns_endpoints = [
  "devops@metriccare.com",
  "admin@metriccare.com"
]
```

---

## ✅ Deployment Outcome

After successful deployment, Terraform will provision:

| Component | Description |
|------------|-------------|
| **S3 Bucket** | Stores raw FHIR JSON, Glue scripts, configs |
| **DynamoDB Table** | Tracks processed files |
| **Glue Jobs & Workflow** | Orchestrates Bronze → Silver → Gold data processing |
| **Lambda Function** | Automates Glue trigger on new S3 uploads |
| **SNS Topic** | Sends email alerts on failures |
| **IAM Roles & Policies** | Grants least-privilege access for all services |

---

## 🔒 Security & Governance

- All S3 buckets use **SSE-KMS encryption**.  
- IAM roles follow **least privilege principle**.  
- All notifications routed via **AWS SNS**.  
- Configuration files (`config.json`) versioned and stored in S3 for auditability.
