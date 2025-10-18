# 🧱 MetricCare Terraform Infrastructure – Module Index

This repository defines the **Infrastructure as Code (IaC)** foundation for the **MetricCare AWS Data Lakehouse** using **Terraform**.  
Each module in this structure is designed for **modularity, reusability, and environment-specific deployments** (via Terraform workspaces).

---

## 🌐 Overview

MetricCare’s Terraform setup provisions an **end-to-end AWS data engineering platform**, including:
- **S3** for data lake storage (Raw → Bronze → Silver → Gold)
- **Glue** for ETL pipelines and metadata management
- **Lambda** for orchestration and workflow triggers
- **EventBridge** for scheduled and event-driven automation
- **SNS** for notifications and alerts
- **DynamoDB** for incremental ingestion tracking

All components are fully integrated and tagged for environment consistency (`dev`, `test`, `prod`).

---

## 📂 Folder Structure

```bash
terraform/
├── main.tf
├── variables.tf
├── outputs.tf
├── provider.tf
├── backend.tf
│
├── module/
│   ├── aws_sns/
│   ├── dynemoDB/
│   ├── event_bridge/
│   ├── lambda_function/
│   ├── glue/
│   │   ├── glue_catalog_database/
│   │   ├── glue_job/
│   │   ├── glue_workflow/
│   ├── s3/
│   │   ├── s3_bucket/
│   │   ├── upload_scripts/
│   │   ├── upload_files/
│   └── README.md
│
└── README.md
```

---

## 🧩 Module Documentation Index

| Category | Module | Description |
|-----------|---------|--------------|
| **Core Infrastructure** | [Terraform Root README](./README.md) | Project setup, workspace usage, AWS CLI configuration. |
| **Modules Overview** | [Module Summary](./module/README.md) | Explains folder structure and design principles. |
| **S3 Layer** | [Root S3 Module](./module/s3/README.md) | Foundation data storage layer (Raw → Bronze → Silver → Gold). |
|  | [S3 Bucket](./module/s3/s3_bucket/README.md) | Creates all environment-specific buckets. |
|  | [Upload Scripts](./module/s3/upload_scripts/README.md) | Uploads Lambda & Glue scripts to S3. |
|  | [Upload Files](./module/s3/upload_files/README.md) | Uploads config and metadata JSONs. |
| **Glue Layer** | [Root Glue Module](./module/glue/README.md) | Metadata management and ETL orchestration. |
|  | [Glue Catalog Database](./module/glue/glue_catalog_database/README.md) | Defines Bronze/Silver/Gold databases. |
|  | [Glue Job](./module/glue/glue_job/README.md) | Deploys PySpark ETL jobs. |
|  | [Glue Workflow](./module/glue/glue_workflow/README.md) | Orchestrates Glue jobs in sequence. |
| **Orchestration & Automation** | [Lambda Function](./module/lambda_function/README.md) | Orchestrates Glue workflows and handles triggers. |
|  | [EventBridge](./module/event_bridge/README.md) | Automates workflows with CRON or event rules. |
|  | [AWS SNS](./module/aws_sns/README.md) | Sends alerts for job success/failure. |
|  | [DynamoDB](./module/dynemoDB/README.md) | Tracks processed files for incremental ingestion. |

---

## ⚙️ Deployment Workflow

### 1️⃣ Initialize Terraform
```bash
terraform init
```

### 2️⃣ Select Environment
```bash
terraform workspace new dev
terraform workspace select dev
```

### 3️⃣ Plan and Apply Infrastructure
```bash
terraform plan
terraform apply -auto-approve
```

### 4️⃣ Destroy Environment (if needed)
```bash
terraform destroy -auto-approve
```

---

## 🧠 Design Highlights

- **Workspace-Based Environments:** Simplified dev/prod isolation without separate `.tfvars`.  
- **Modular Architecture:** Each AWS service is isolated into reusable modules.  
- **Version Control Integration:** All scripts, configs, and state managed through Git + S3 backend.  
- **CI/CD Ready:** Compatible with GitHub Actions or AWS CodePipeline for automation.  
- **Security First:** Enforced IAM least-privilege, encryption, and no public access for S3.  

---

## 📤 Outputs & Integrations

| Integration | Description |
|--------------|--------------|
| **Glue Jobs** | ETL scripts read/write S3 data and register tables in Glue Catalog. |
| **Lambda** | Orchestrates workflows and triggers Glue jobs. |
| **EventBridge** | Automates job scheduling and event-based triggers. |
| **DynamoDB** | Tracks processed files to prevent duplicates. |
| **SNS** | Sends alerts on job completion or failure. |
| **Athena / Power BI** | Access analytics-ready data from Gold layer. |

---

## 🔗 References

- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)  
- [Terraform Modules Best Practices](https://developer.hashicorp.com/terraform/language/modules/develop)  
- [AWS Data Lake Architecture](https://aws.amazon.com/big-data/datalakes-and-analytics/)  
- [AWS Glue Documentation](https://docs.aws.amazon.com/glue/)  
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)  
- [AWS S3 Security Guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)

---

> 🧱 **Author:** Shreyash (Data Engineer)  
> 📚 *MetricCare – AWS Data Lakehouse for Healthcare Analytics*  
> 🔗 *Terraform Infrastructure – Modular, Scalable, and Cloud-Native*
