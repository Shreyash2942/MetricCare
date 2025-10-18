# 🪣 Amazon S3 Bucket Module

This module provisions the **Amazon S3 buckets** that form the backbone of the MetricCare Data Lakehouse.  
Each bucket represents a logical data zone — from raw ingestion to analytics-ready datasets — ensuring data lineage and lifecycle consistency across the pipeline.

---

## 📖 Overview

| Bucket | Purpose |
|---------|----------|
| **Raw** | Stores unprocessed synthetic FHIR JSON data (Patient, Encounter, Condition). |
| **Bronze** | Stores ingested data converted to Hudi-managed Parquet format. |
| **Silver** | Stores curated, cleaned, and structured data for analytics. |
| **Gold** | Stores aggregated and metric-level data (Mortality, Infection, Readmission, ALOS). |
| **Scripts / Configs** | Hosts Glue and Lambda deployment packages and configuration files. |

---

## 🧩 Use Case in MetricCare Architecture

```
        ┌──────────────────────────────────────────────┐
        │                AWS S3 Buckets                │
        │──────────────────────────────────────────────│
        │   Raw Data  →  Bronze  →  Silver  →  Gold    │
        │    (FHIR)      (Hudi)     (Clean)   (Metrics)│
        │──────────────────────────────────────────────│
        │  upload_scripts/ → Glue & Lambda packages     │
        │  upload_files/   → Config JSONs, mappings     │
        └──────────────────────────────────────────────┘
```

- **Glue Jobs:** Read/write to these buckets during ETL.  
- **Lambda:** Monitors bucket events to trigger Glue workflows.  
- **Athena / Power BI:** Query Gold-layer tables for reporting.  

---

## 🗂️ Module Structure

```bash
s3_bucket/
├── main.tf         # Defines multiple S3 buckets with tags, policies, and versioning
├── variables.tf    # Input variables (bucket names, versioning, encryption)
└── outputs.tf      # Exports bucket ARNs and names
```

---

## ⚙️ Example Usage

Here’s how this module can be invoked from your Terraform root:

```hcl
module "s3_bucket" {
  source = "./module/s3/s3_bucket"

  buckets = {
    raw     = "metriccare-raw-data"
    bronze  = "metriccare-bronze-data"
    silver  = "metriccare-silver-data"
    gold    = "metriccare-gold-data"
    scripts = "metriccare-upload-scripts"
  }

  enable_versioning = true
  enable_encryption = true
  force_destroy     = false

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
| `buckets` | Map of bucket names (raw, bronze, silver, gold, scripts). | `map(string)` | `{}` |
| `enable_versioning` | Enables S3 versioning. | `bool` | `true` |
| `enable_encryption` | Enables AES-256 server-side encryption. | `bool` | `true` |
| `force_destroy` | Deletes all objects on `terraform destroy`. | `bool` | `false` |
| `tags` | Common resource tags. | `map(string)` | `{}` |

---

## 📤 Outputs

| Output | Description |
|---------|--------------|
| `bucket_names` | List of created bucket names. |
| `bucket_arns` | List of corresponding bucket ARNs. |

---

## 🧠 Best Practices

- **Versioning:** Keep enabled for rollback and auditing.  
- **Encryption:** Use AES-256 or KMS for secure storage.  
- **Naming Convention:**  
  - `metriccare-raw-data`  
  - `metriccare-bronze-data`  
  - `metriccare-silver-data`  
  - `metriccare-gold-data`  
- **Access Control:** Restrict public access and enforce IAM-based access.  
- **Lifecycle Rules:** (Optional) Add lifecycle policies to transition old data to Glacier.  
- **Cross-Region Replication:** Consider enabling for disaster recovery.  

---

## 🧩 Testing the Module

Deploy and validate S3 buckets:

```bash
terraform init
terraform apply -target=module.s3_bucket -auto-approve
```

Verification steps:
1. Open **AWS S3 Console → Buckets**.  
2. Confirm all MetricCare buckets are created.  
3. Verify versioning and encryption under bucket properties.  
4. Upload test data or scripts to validate paths.  

---

## 🔗 References

- [Terraform AWS S3 Bucket Resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket)  
- [Terraform S3 Bucket Versioning](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_versioning)  
- [Terraform S3 Bucket Server-Side Encryption](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/s3_bucket_server_side_encryption_configuration)  
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/index.html)  
- [AWS S3 Best Practices](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)

---

> 🧱 **Author:** Shreyash (Data Engineer)  
> 📚 *MetricCare – AWS Data Lakehouse for Healthcare Analytics*  
> 🔗 *Module: s3_bucket – Foundation Storage Layer for ETL Pipelines*
