# 📤 AWS S3 Upload Scripts Module

This module automates the upload of **Lambda and Glue job scripts** to the designated S3 bucket used in the MetricCare Data Lakehouse.  
It ensures all ETL and orchestration scripts are versioned, environment-specific, and available for deployment through Terraform workflows.

---

## 📖 Overview

| Component | Purpose |
|------------|----------|
| **Lambda Scripts** | Python functions that trigger Glue workflows or monitor S3 events. |
| **Glue Scripts** | PySpark ETL scripts responsible for transforming and loading healthcare data. |
| **S3 Upload Automation** | Uploads all necessary script files to S3 as part of the Terraform apply process. |

---

## 🧩 Use Case in MetricCare Architecture

```
┌────────────────────┐
│  Local Scripts     │
│ (Lambda + Glue)    │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Terraform Module   │  → Uploads →  S3: upload_scripts/
└────────────────────┘
          │
          ▼
┌────────────────────┐
│ AWS Glue + Lambda  │ ← Reads from → S3 paths
└────────────────────┘
```

- **Terraform → S3:** Uploads scripts to the specified S3 bucket during infrastructure provisioning.  
- **Lambda / Glue:** Fetches the latest script version from S3 at runtime.  

---

## 🗂️ Module Structure

```bash
upload_scripts/
├── main.tf         # Uses aws_s3_object to upload files to S3
├── variables.tf    # Input variables for source and destination paths
└── outputs.tf      # Exports uploaded object keys and locations
```

---

## ⚙️ Example Usage

Here’s an example configuration from your Terraform root module:

```hcl
module "upload_scripts" {
  source = "./module/s3/upload_scripts"

  bucket_name = "metriccare-upload-scripts"
  upload_file = {
    lambda_trigger = {
      s3_location     = "lambda/myglueworkflow.zip"
      source_location = "../lambda/myglueworkflow.zip"
    }
    glue_bronze = {
      s3_location     = "glue/scripts/bronze_etl.py"
      source_location = "../glue_job/scripts/bronze_etl.py"
    }
    glue_silver = {
      s3_location     = "glue/scripts/silver_etl.py"
      source_location = "../glue_job/scripts/silver_etl.py"
    }
    glue_gold = {
      s3_location     = "glue/scripts/gold_etl.py"
      source_location = "../glue_job/scripts/gold_etl.py"
    }
  }

  tags = {
    Environment = terraform.workspace
    Project     = "MetricCare"
  }
}
```

> 🧩 This module ensures your Lambda and Glue jobs always use the **latest uploaded script versions** during deployment.

---

## 🔑 Key Variables

| Variable | Description | Type | Default |
|-----------|--------------|------|----------|
| `bucket_name` | Target S3 bucket for uploading files. | `string` | n/a |
| `upload_file` | Map of files to upload (S3 key + local source path). | `map(object({ s3_location = string, source_location = string }))` | `{}` |
| `tags` | Resource tags for all uploaded objects. | `map(string)` | `{}` |

---

## 📤 Outputs

| Output | Description |
|---------|--------------|
| `uploaded_files` | List of successfully uploaded S3 object keys. |
| `bucket_name` | Name of the target bucket where files were uploaded. |

---

## 🧠 Best Practices

- Keep **script paths consistent** (`lambda/`, `glue/scripts/`).  
- Maintain **versioned ZIPs or scripts** for traceability.  
- Use Terraform **workspaces** for environment isolation (e.g., dev/prod).  
- Validate the `source_location` path before apply to prevent broken uploads.  
- Enable **S3 versioning** on the upload bucket to retain script history.  

---

## 🧩 Testing the Module

Run the module independently to verify file uploads:

```bash
terraform init
terraform apply -target=module.upload_scripts -auto-approve
```

Verification steps:
1. Open **AWS S3 Console → metriccare-upload-scripts**.  
2. Confirm files exist under the correct prefixes (`lambda/`, `glue/scripts/`).  
3. Check versioning and metadata tags.  

---

## 🔗 References

- [Terraform AWS S3 Object Resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_object)  
- [AWS S3 Console](https://console.aws.amazon.com/s3/)  
- [AWS Glue Documentation](https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html)  
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)

---

> 🧱 **Author:** Shreyash (Data Engineer)  
> 📚 *MetricCare – AWS Data Lakehouse for Healthcare Analytics*  
> 🔗 *Module: upload_scripts – Automated Script Deployment for Glue & Lambda*
