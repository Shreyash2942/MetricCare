# 📁 AWS S3 Upload Files Module

This module automates the upload of **configuration files, metadata, or sample input datasets** to an S3 bucket in the MetricCare Data Lakehouse.  
It ensures that all required resources — such as `config.json`, `metric_mapping.json`, or `sample_FHIR_data.json` — are always available for Glue and Lambda processing.

---

## 📖 Overview

| Component | Purpose |
|------------|----------|
| **Configuration Files** | Define dynamic job settings, paths, and metadata for Glue ETL. |
| **Metadata / JSON Files** | Provide synthetic FHIR data or schema mapping information. |
| **Upload Automation** | Ensures these files are uploaded to S3 via Terraform during deployment. |

---

## 🧩 Use Case in MetricCare Architecture

```
┌────────────────────┐
│ Local Configs &    │
│ Sample Data Files  │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Terraform Module   │  → Uploads →  S3: upload_files/
└────────────────────┘
          │
          ▼
┌────────────────────┐
│ AWS Glue & Lambda  │ ← Reads from → S3 config paths
└────────────────────┘
```

- **Terraform → S3:** Uploads configuration and resource files to the target bucket.  
- **Glue Jobs:** Read configs to control ETL parameters (paths, table names, etc.).  
- **Lambda:** Reads configuration metadata before triggering workflows.

---

## 🗂️ Module Structure

```bash
upload_files/
├── main.tf         # Uploads files to S3 using aws_s3_object
├── variables.tf    # Defines file mappings and target bucket
└── outputs.tf      # Exports uploaded file keys and bucket info
```

---

## ⚙️ Example Usage

Example configuration from the Terraform root module:

```hcl
module "upload_files" {
  source = "./module/s3/upload_files"

  bucket_name = "metriccare-upload-scripts"
  upload_file = {
    config = {
      s3_location     = "configs/config.json"
      source_location = "../config/config.json"
    }
    mapping = {
      s3_location     = "configs/metric_mapping.json"
      source_location = "../config/metric_mapping.json"
    }
    sample_data = {
      s3_location     = "fhir_data/json/patients/sample_patients.json"
      source_location = "../data/patients/sample_patients.json"
    }
  }

  tags = {
    Environment = terraform.workspace
    Project     = "MetricCare"
  }
}
```

> 💡 This module helps maintain environment-specific configuration consistency across Glue and Lambda components.

---

## 🔑 Key Variables

| Variable | Description | Type | Default |
|-----------|--------------|------|----------|
| `bucket_name` | Target S3 bucket for uploads. | `string` | n/a |
| `upload_file` | Map of files to upload (S3 key + local source path). | `map(object({ s3_location = string, source_location = string }))` | `{}` |
| `tags` | Tags to apply to uploaded files. | `map(string)` | `{}` |

---

## 📤 Outputs

| Output | Description |
|---------|--------------|
| `uploaded_files` | List of uploaded S3 object keys. |
| `bucket_name` | Name of the target S3 bucket. |

---

## 🧠 Best Practices

- Store configuration files under a clear prefix (`configs/`, `fhir_data/`).  
- Use Terraform workspaces to maintain **environment-specific configs** (dev, prod).  
- Validate file paths before deployment to prevent broken uploads.  
- Enable **S3 versioning** for config change tracking.  
- Keep sensitive information (e.g., credentials) **outside JSON configs**.  

---

## 🧩 Testing the Module

To test the module independently:

```bash
terraform init
terraform apply -target=module.upload_files -auto-approve
```

Verification steps:
1. Open **AWS S3 Console → metriccare-upload-scripts → configs/**  
2. Confirm uploaded files and verify metadata tags.  
3. Check that Glue/Lambda jobs can reference these files.

---

## 🔗 References

- [Terraform AWS S3 Object Resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_object)  
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)  
- [AWS Glue Configuration Management](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-glue-arguments.html)  
- [AWS Lambda Environment Configuration](https://docs.aws.amazon.com/lambda/latest/dg/configuration-envvars.html)

---

> 🧱 **Author:** Shreyash (Data Engineer)  
> 📚 *MetricCare – AWS Data Lakehouse for Healthcare Analytics*  
> 🔗 *Module: upload_files – Config & Metadata File Upload Automation*
