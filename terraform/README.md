# 🏗️ MetricCare Terraform Infrastructure

This directory provisions the **AWS Data Lakehouse infrastructure** for the MetricCare project using **Terraform**.  
It automates the creation of compute, storage, and orchestration layers used across:
- `lambda/` → Event-driven Glue triggers  
- `glue_job/` → ETL transformations (Bronze → Silver → Gold)  
- `fhir_data/` → Synthetic FHIR datasets used for CMS metrics  

---

## 📦 Overview

| Component | AWS Service | Purpose |
|------------|--------------|----------|
| 🪣 **S3 Buckets** | Amazon S3 | Stores raw → bronze → silver → gold FHIR datasets |
| ⚙️ **Glue Jobs & Workflow** | AWS Glue | Runs ETL pipelines and manages job dependencies |
| 🧠 **DynamoDB Table** | Amazon DynamoDB | Tracks processed files for incremental ingestion |
| 🧩 **Lambda Function** | AWS Lambda | Triggers Glue Workflow on new S3 data arrival |
| 🔔 **SNS + EventBridge** | AWS SNS / EventBridge | Notification and orchestration for job events |
| 🔐 **IAM Roles & Policies** | AWS IAM | Grants least-privilege access to each service |

---

## 🗂️ Terraform Project Structure

```bash
terraform/
│
├── backend.tf                # Defines remote backend (S3 + DynamoDB) for Terraform state
├── main.tf                   # Root module calling all submodules (S3, Glue, Lambda, etc.)
├── provider.tf               # AWS provider configuration and version locking
├── variables.tf              # Shared variable definitions for all modules
├── terraform.tfstate         # Local state file (only if remote backend not configured)
├── terraform.tfstate.backup  # Local backup of the state file
├── README.md                 # This documentation file
│
├── awscredentials/
│   └── credentials            # Stores AWS CLI credentials (for local dev use only)
│
└── module/
    ├── aws_sns/               # Creates SNS topics/subscriptions for notifications
    ├── dynemoDB/              # Creates DynamoDB table for processed_files metadata
    ├── event_bridge/          # Defines EventBridge rules for workflow scheduling
    ├── glue/
    │   ├── glue_catalog_database/   # Creates Glue databases for bronze/silver/gold tables
    │   ├── glue_job/                # Deploys ETL Glue Jobs (PySpark scripts)
    │   └── glue_workflow/           # Creates Glue Workflows + triggers between jobs
    ├── lambda_function/      # Deploys Lambda for workflow orchestration
    └── s3/
        ├── s3_bucket/        # Creates data lake buckets (raw → bronze → silver → gold)
        ├── upload_files/     # Uploads config/data files to S3 during provisioning
        └── upload_scripts/   # Uploads Lambda & Glue scripts to corresponding S3 paths
```

---

## 🚀 Deploying with Terraform Workspaces

This project uses **Terraform Workspaces** to manage environments (e.g., `dev`, `prod`).

```bash
terraform init
terraform workspace new dev
terraform workspace select dev
terraform plan
terraform apply -auto-approve
```

> 🧩 Each workspace maintains isolated state, allowing you to deploy multiple environments using the same Terraform codebase.

---

## 🧩 Running or Destroying Specific Modules

You can apply or destroy **individual modules** instead of the entire stack.

### ▶️ Apply a Specific Module
```bash
terraform apply -target=module.lambda_function -auto-approve
```

### 💣 Destroy a Specific Module
```bash
terraform destroy -target=module.lambda_function -auto-approve
```

> ⚠️ Use targeted commands for testing only. For production, always run full `plan/apply` for dependency consistency.

---

## 💥 Destroying the Entire Infrastructure

To remove **all resources** in the current workspace:

```bash
terraform destroy -auto-approve
```

If managing multiple environments:

```bash
terraform workspace select dev
terraform destroy -auto-approve
```

> 🧹 This ensures a clean teardown of all resources in that workspace while preserving remote state in S3/DynamoDB.

---

## 🧠 Design Principles

- **Modular Architecture:** Each AWS service lives in an independent module.  
- **Workspace Isolation:** Environments (`dev`, `prod`) use workspaces instead of `.tfvars`.  
- **Least-Privilege IAM:** Policies grant only necessary permissions.  
- **Version Locking:** AWS provider pinned to `~> 6.12.0`.  
- **Automation-Ready:** EventBridge + Lambda enable serverless orchestration.  
- **State Safety:** Remote backend protects against conflicting deployments.  

---

## 🔗 Additional Resources

### 🧰 Terraform
- [Terraform Downloads](https://developer.hashicorp.com/terraform/downloads)  
- [Terraform CLI Documentation](https://developer.hashicorp.com/terraform/cli)  
- [Terraform AWS Provider Reference](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)  
- [Terraform Remote State (S3 Backend)](https://developer.hashicorp.com/terraform/language/settings/backends/s3)  

### ☁️ AWS CLI & Configuration
- [AWS CLI Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)  
- [AWS CLI Configuration Files](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)  
- [AWS IAM User Guide](https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html)  

### 🧩 AWS Service Docs
- [AWS Glue Documentation](https://docs.aws.amazon.com/glue/)  
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)  
- [Amazon EventBridge Documentation](https://docs.aws.amazon.com/eventbridge/)  
- [AWS SNS Documentation](https://docs.aws.amazon.com/sns/)  
- [Amazon DynamoDB Documentation](https://docs.aws.amazon.com/dynamodb/)  
- [Amazon S3 Documentation](https://docs.aws.amazon.com/s3/)

---

> 🧱 **Author:** Shreyash (Data Engineer)  
> 📚 *MetricCare – AWS Data Lakehouse for Healthcare Analytics*  
> 🔗 *Built with Terraform, AWS Glue, Lambda, S3, DynamoDB, EventBridge, and SNS*
