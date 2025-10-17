# 🧠 Amazon DynamoDB Module

This module provisions an **Amazon DynamoDB table** used to track processed files and metadata for incremental ingestion within the **MetricCare Data Lakehouse**.  
It ensures ETL jobs are idempotent — meaning the same data file is not processed more than once — and maintains a persistent metadata log for Glue workflows.

---

## 📖 Overview

| Component | Purpose |
|------------|----------|
| **DynamoDB Table** | Stores metadata about processed files (e.g., file name, timestamp, job status). |
| **Primary Key (file_id)** | Ensures unique identification of each processed file. |
| **TTL (optional)** | Automatically expires old metadata entries after a retention period. |
| **IAM Policy** | Grants Glue and Lambda read/write access to the DynamoDB table. |

---

## 🧩 Use Case in MetricCare Architecture

The DynamoDB module acts as a **metadata ledger** for file ingestion across data lake layers.

```
┌────────────┐          ┌──────────────┐          ┌──────────────┐
│    S3      │ ───────► │   Glue Job   │ ───────► │  DynamoDB    │
└────────────┘          └──────────────┘          └──────────────┘
        │                        │                        │
        │                        ▼                        │
        │           Marks file as processed               │
        └─────────────────────────────────────────────────┘
```

- **Glue → DynamoDB:** Updates the table once a file is processed.  
- **Lambda → DynamoDB:** Reads entries to skip already processed files.  
- **Athena / Monitoring:** Can query table for ingestion audit reports.

---

## 🗂️ Module Structure

```bash
dynemoDB/
├── main.tf         # Creates DynamoDB table, IAM policy, and optional TTL settings
├── variables.tf    # Input variables (table name, attributes, tags)
└── outputs.tf      # Exports table name and ARN
```

---

## ⚙️ Example Usage

Example usage from your root `main.tf` file:

```hcl
module "dynemoDB" {
  source            = "./module/dynemoDB"
  table_name        = "metriccare_processed_files"
  hash_key          = "file_id"
  read_capacity     = 5
  write_capacity    = 5
  ttl_attribute     = "expiration_time"
  enable_ttl        = true
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
| `table_name` | Name of the DynamoDB table. | `string` | `"metriccare_processed_files"` |
| `hash_key` | Primary key attribute name. | `string` | `"file_id"` |
| `read_capacity` | Read capacity units (RCU). | `number` | `5` |
| `write_capacity` | Write capacity units (WCU). | `number` | `5` |
| `enable_ttl` | Whether to enable time-to-live (TTL) for records. | `bool` | `false` |
| `ttl_attribute` | Attribute used for TTL expiration. | `string` | `"expiration_time"` |
| `tags` | Map of resource tags. | `map(string)` | `{}` |

---

## 📤 Outputs

| Output | Description |
|---------|--------------|
| `table_name` | Name of the created DynamoDB table. |
| `table_arn` | ARN of the DynamoDB table. |

---

## 🧠 Best Practices

- Use **unique file identifiers** (`file_id`) to ensure idempotent ingestion.  
- Enable **TTL** for retention-based cleanup in dev/test environments.  
- Grant only **specific service principals** (Glue, Lambda) access to write.  
- Use **CloudWatch metrics** to monitor consumed capacity and throttling.  
- Consider **on-demand billing mode** if ingestion volume is unpredictable.

---

## 🧩 Testing the Module

Run this module independently to confirm table creation and IAM policies:

```bash
terraform init
terraform apply -target=module.dynemoDB -auto-approve
```

Then verify in the AWS Console:
- Navigate to **DynamoDB → Tables → metriccare_processed_files**.  
- Check table schema, TTL, and tags.  

---

## 🔗 References

- [Terraform AWS DynamoDB Resource](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/dynamodb_table)  
- [AWS DynamoDB Developer Guide](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html)  
- [DynamoDB TTL Documentation](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/TTL.html)  
- [AWS Glue and DynamoDB Integration](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-dynamodb.html)

---

> 🧱 **Author:** Shreyash (Data Engineer)  
> 📚 *MetricCare – AWS Data Lakehouse for Healthcare Analytics*  
> 🔗 *Module: dynemoDB – Incremental Metadata Tracking for ETL Workflows*
