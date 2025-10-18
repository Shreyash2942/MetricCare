# 🧠 MetricCare Technical Architecture & Development Guide

This document provides a **comprehensive technical overview** of the MetricCare project — covering architecture, Terraform automation, AWS workflows, data pipeline design, and development standards.

---

## 🏗️ Project Architecture Overview

**MetricCare** is an end-to-end AWS Data Lakehouse solution for **healthcare analytics and CMS compliance**.  
It uses a modern data engineering stack to ingest, transform, and analyze FHIR-based healthcare data.

### 🔹 Core Components

| Layer | Services / Tools | Purpose |
|--------|------------------|----------|
| **Data Simulation** | Python, Faker, FHIR Resources | Generate synthetic Patient, Encounter, and Condition data. |
| **Data Lake** | Amazon S3 | Multi-zone data storage (Raw → Bronze → Silver → Gold). |
| **ETL & Processing** | AWS Glue (PySpark + Hudi) | Transform, cleanse, and aggregate data into CMS metrics. |
| **Orchestration** | AWS Lambda, EventBridge | Trigger workflows on schedule or new data events. |
| **Metadata & Tracking** | AWS Glue Catalog, DynamoDB | Store schema and track processed files. |
| **Monitoring & Alerts** | CloudWatch, SNS | Workflow monitoring and notification system. |
| **Analytics** | Athena, Power BI | Query and visualize CMS metrics. |

---

## ☁️ Infrastructure as Code (Terraform)

Terraform manages all infrastructure provisioning for MetricCare. Each AWS service is modularized for scalability and reusability.

### 🧩 Module Overview

| Module | Description |
|---------|--------------|
| `s3_bucket` | Provisions all S3 buckets for data lake zones. |
| `upload_scripts` | Uploads Glue and Lambda scripts to S3. |
| `glue_catalog_database` | Defines databases for Bronze, Silver, and Gold layers. |
| `glue_job` | Deploys ETL jobs for transformations. |
| `glue_workflow` | Orchestrates ETL jobs with triggers. |
| `lambda_function` | Triggers Glue workflows automatically. |
| `event_bridge` | Schedules workflow runs. |
| `dynemoDB` | Tracks incremental processing. |
| `aws_sns` | Sends workflow alerts. |

### ⚙️ Terraform Workflow

```bash
# Initialize Terraform
terraform init

# Create or switch workspace
terraform workspace new dev
terraform workspace select dev

# Plan and deploy
terraform plan
terraform apply -auto-approve

# Destroy environment
terraform destroy -auto-approve
```

**Key Practices:**
- Separate workspaces for `dev` and `prod` (no tfvars).  
- Remote backend in S3 for state management.  
- GitHub Actions handles automated plan/apply for approved merges.  

---

## 🧬 Data Simulation & ETL Design

### 1️⃣ Synthetic FHIR Data Generator
- Implemented in **Python** using `Faker` and HL7 FHIR R4 schema.  
- Generates **Patient**, **Encounter**, and **Condition** JSON datasets.  
- Each resource includes SNOMED-CT codes and logical timestamps.  

Output structure:
```
fhir_data/
├── json/
│   ├── patients/
│   ├── encounters/
│   └── conditions/
```

### 2️⃣ Glue ETL Architecture (Bronze → Silver → Gold)

| Layer | Purpose | Transformation Type |
|--------|----------|----------------------|
| **Bronze** | Stores raw, ingested JSON data. | Minimal parsing and Hudi table conversion. |
| **Silver** | Cleaned, deduplicated data. | Joins across Patient/Encounter/Condition. |
| **Gold** | Aggregated CMS metrics. | Derived metrics (Mortality, Infection, Readmission, ALOS). |

Each job uses **AWS Glue 4.0 (Spark 3.5)** with incremental **Hudi tables** for upserts.

---

## 🔄 AWS Orchestration Flow

### Workflow Sequence

```
S3 Upload → Lambda Trigger → Glue Workflow → Glue Jobs (Bronze → Silver → Gold)
                               │
                               ▼
                       SNS Notification
```

### Key Automations
- **Lambda** detects new S3 uploads and triggers Glue workflows.  
- **EventBridge** executes scheduled runs (daily/hourly).  
- **SNS** alerts for success/failure.  
- **DynamoDB** stores metadata of processed files for idempotent processing.  

---

## 📊 Analytics Layer

- **Athena** queries data directly from S3 (via Glue Catalog).  
- **Power BI** connects to Athena for visual analytics.  
- Metrics displayed: Mortality Rate, Infection Rate, Readmission Rate, ALOS.  

Sample visualization ideas:
- Donut chart for infection rate by SNOMED code.  
- Bar chart for readmission by hospital.  
- Line chart for mortality trend by year.  

---

## 🚀 CI/CD Deployment Flow

### GitHub Actions Workflow

| Stage | Task |
|--------|------|
| **Plan** | Runs `terraform plan` on pull requests. |
| **Apply** | Runs `terraform apply` on main merges (with approval). |
| **Destroy** | Manual workflow for resource cleanup. |

### Key Files
```
.github/workflows/
└── ci-cd.yml
```

Actions include:
- Auto-format & lint Terraform code.  
- Validate configuration syntax.  
- Upload plan summary to PR comment.  

---

## 🪣 Environment Management

Each workspace maps to an isolated environment:

| Workspace | Environment | Description |
|------------|--------------|-------------|
| `dev` | Development | Testing zone with synthetic data. |
| `prod` | Production | Final deployment for analytics use. |

### Environment Variables
```bash
export AWS_PROFILE=metriccare-dev
export AWS_REGION=us-east-1
```

---

## 🔍 Monitoring & Logging

| Service | Purpose |
|----------|----------|
| **CloudWatch Logs** | Captures job execution logs (Lambda & Glue). |
| **Glue Job Metrics** | Job run counts, duration, and failure rate. |
| **SNS Alerts** | Notifies via email or Slack integration. |
| **Athena Queries** | Used to validate data accuracy and freshness. |

---

## 🧩 Development Standards

| Category | Standard |
|-----------|-----------|
| **Terraform Modules** | Each service is isolated with `main.tf`, `variables.tf`, and `outputs.tf`. |
| **Naming Convention** | Use `metriccare_<layer>_<component>` pattern. |
| **IAM Roles** | Apply least-privilege principle. |
| **S3 Structure** | Maintain zone segregation (Raw/Bronze/Silver/Gold). |
| **Glue Scripts** | Commented, modularized, and version-controlled in `glue_job/`. |
| **Python Code** | Use docstrings, type hints, and PEP8 compliance. |

---

## 🧠 Best Practices & Troubleshooting

### ✅ Best Practices
- Enable versioning and encryption for all S3 buckets.  
- Test Glue jobs locally using `pytest` or AWS Glue Studio.  
- Use Terraform’s `-target` flag for incremental resource deployment.  
- Monitor Glue job failures through SNS and CloudWatch alerts.  
- Commit infrastructure changes only via PR (never directly to main).  

### ⚠️ Common Issues

| Issue | Cause | Resolution |
|--------|--------|-------------|
| Workflow not triggering | Lambda permission or EventBridge rule misconfigured. | Check Lambda IAM and event source ARN. |
| Glue job stuck in “RUNNING” | Data skew or missing bookmark. | Clear job bookmarks and retry. |
| S3 upload not detected | Missing event notification. | Recheck S3 → Lambda event mapping. |

---

## 🧾 References

- AWS Glue Developer Guide: [https://docs.aws.amazon.com/glue/](https://docs.aws.amazon.com/glue/)  
- AWS Lambda Documentation: [https://docs.aws.amazon.com/lambda/](https://docs.aws.amazon.com/lambda/)  
- Terraform AWS Provider: [https://registry.terraform.io/providers/hashicorp/aws/latest/docs](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)  
- Apache Hudi Integration: [https://hudi.apache.org/](https://hudi.apache.org/)  
- HL7 FHIR Specification: [https://hl7.org/fhir/](https://hl7.org/fhir/)

---

> 🧱 **Author:** Shreyash Patel  
> 💼 *AWS Data Engineer | Cloud & Healthcare Analytics*  
> 🔗 *Project: MetricCare – AWS Healthcare Data Lakehouse*
