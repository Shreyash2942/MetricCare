# 🏗️ MetricCare Terraform Module

This directory provisions all **AWS infrastructure** for the MetricCare Data Lakehouse using **Terraform**.  
It connects with the `lambda/` and `glue_job/` folders at the project root to automate the deployment of data and compute resources.

---

## 📦 Overview

| Component | AWS Service | Purpose |
|------------|--------------|----------|
| 🪣 **S3 Buckets** | Amazon S3 | Stores raw → bronze → silver → gold FHIR data |
| ⚙️ **Glue Jobs & Workflow** | AWS Glue | ETL orchestration for CMS metrics |
| 🧠 **DynamoDB Table** | DynamoDB | Tracks processed files for incremental ingestion |
| 🧩 **Lambda Function** | AWS Lambda | Triggers Glue Workflow when new data lands in S3 |
| 🔔 **SNS + EventBridge** | AWS SNS/EventBridge | Alerts for job success/failure |
| 🔐 **IAM Roles & Policies** | AWS IAM | Grants permissions for all components |

---

## 🗂️ Project Structure

At the project root:

```
MetricCare/
├── terraform/         # Infrastructure as Code (this folder)
├── lambda/            # Contains myglueworkflow.py (trigger Lambda)
├── glue_job/          # Bronze/Silver/Gold Glue ETL scripts
├── fhir_data/         # FHIR patient/encounter/condition generators
├── docs/              # Architecture and implementation docs
└── README.md          # Main project overview
```

Inside the Terraform module:

```
terraform/
├── main.tf
├── backend.tf
├── provider.tf
├── variables.tf
├── output.tf
│
├── module/
│   ├── s3/
│   ├── glue/
│   ├── lambda_function/
│   ├── dynemoDB/
│   ├── event_bridge/
│   └── aws_sns/
│
└── awscredentials/credentials   # ⚠️ For local runs only — exclude from Git
```

---

## ⚙️ How It Works

1. **Lambda** (`../lambda/myglueworkflow.py`) is zipped and deployed via Terraform.
2. **S3** buckets and **DynamoDB** table are created for data storage and tracking.
3. **Glue modules** provision catalog, jobs, and workflows.
4. **SNS/EventBridge** handle notifications on job success or failure.
5. **Workspaces** manage `dev`, `prod`, etc., automatically.

---

## 🚀 Deployment with Workspaces

```bash
cd terraform
terraform init

# create/select environment
terraform workspace new dev
terraform workspace select dev

# plan & apply
terraform plan
terraform apply -auto-approve

# (optional) destroy
terraform destroy -auto-approve
```

Each workspace maintains isolated backend state (S3 + DynamoDB).

---

## 🪄 Lambda Packaging

Before running `terraform apply`, zip your Lambda trigger:

```bash
cd ../lambda
zip -r ../terraform/module/lambda_function/myglueworkflow.zip myglueworkflow.py
```

Terraform automatically uploads it to AWS Lambda.

---

## 📤 Outputs

| Output | Description |
|---------|-------------|
| `bucket_name` | Main data bucket |
| `workflow_name` | Glue Workflow name |
| `lambda_arn` | ARN of deployed Lambda |
| `config_file_path` | S3 path to uploaded config JSON |

---

## 🧰 Requirements

| Tool | Minimum Version |
|-------|-----------------|
| Terraform | ≥ 1.6.0 |
| AWS CLI | ≥ 2.15 |
| Python | ≥ 3.12 |
| Boto3 | Built into Lambda runtime |

---

## 🧩 Notes

- All sensitive credentials in `terraform/awscredentials/` should be **excluded from Git**:
  ```bash
  echo "terraform/awscredentials/" >> .gitignore
  ```
- The main project `README.md` should describe how Terraform integrates with Lambda and Glue jobs.

---

**Author:** MetricCare Data Engineering Team  
**Purpose:** Automate infrastructure provisioning for AWS-based CMS metrics pipeline.
