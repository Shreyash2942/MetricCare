# 🧬 Bronze Layer – Condition FHIR Data Ingestion (AWS Glue + Hudi)

This script is part of the **MetricCare Data Lakehouse Pipeline**, responsible for ingesting **FHIR-compliant Condition data** into the **Bronze Layer** on AWS using **AWS Glue**, **Apache Hudi**, and **Amazon DynamoDB** for incremental ingestion tracking.

---

## 🧩 Overview

The Bronze Condition job processes **FHIR Condition JSON files** stored in Amazon S3 and performs the following key tasks:

1. **Reads JSON data** generated from the MetricCare FHIR Data Generator.
2. **Flattens the nested FHIR structure** to extract key condition-related attributes.
3. **Adds ingestion metadata** fields:
   - `sourcename` → source file path from S3  
   - `precombine_ts` → ingestion timestamp (used for deduplication)
4. **Writes data into an Apache Hudi table** (COPY_ON_WRITE mode).
5. **Logs processing metadata** (column count, last processed time) into a Hudi log table.
6. **Updates DynamoDB meta table** to record processed files, enabling incremental ingestion.

---

## ⚙️ Architecture Flow

```
          +--------------------------+
          | FHIR JSON (Condition)    |
          | Stored in S3 Input Path  |
          +------------+-------------+
                       |
                       v
         +-------------+-------------+
         | AWS Glue ETL (Bronze Job) |
         |  - Flatten FHIR JSON      |
         |  - Extract SNOMED Codes   |
         |  - Add Metadata Fields    |
         +-------------+-------------+
                       |
                       v
          +------------+------------+
          | Apache Hudi Bronze Table|
          | Partitioned by Status   |
          +------------+------------+
                       |
             +---------+---------+
             | AWS Glue Catalog |
             | Athena Queryable |
             +------------------+
                       |
          +------------+------------+
          | DynamoDB Meta Table     |
          | Tracks processed files  |
          +--------------------------+
```

---

## 📂 Key Components

| Component | Description |
|------------|-------------|
| **AWS Glue Job** | Runs ETL logic to parse and flatten FHIR Condition JSON data |
| **Apache Hudi** | Provides incremental and upsert capabilities for data lake storage |
| **AWS Glue Catalog** | Maintains schema registry for querying in Athena |
| **Amazon DynamoDB** | Tracks processed files to enable idempotent ingestion |

---

## 🧠 Extracted Schema

| Column | Description |
|---------|-------------|
| `condition_id` | Unique identifier for each condition |
| `patient_ref` | FHIR reference to the related Patient |
| `encounter_ref` | FHIR reference to associated Encounter |
| `snomed_code` | SNOMED CT code for condition classification |
| `condition_name` | Human-readable name for the condition |
| `clinical_status` | Active / Resolved / Recurrence / Remission |
| `onset_time` | Timestamp when condition was identified |
| `recovery_time` | Timestamp when condition resolved |
| `category` | Category of condition (Death, Infection, Chronic) |
| `metric_type` | CMS Metric classification (Mortality Rate, HAI, etc.) |
| `severity` | Condition severity (Mild / Moderate / Severe) |
| `version` | FHIR condition data schema version |
| `sourcename` | Source JSON file path in S3 |
| `precombine_ts` | Ingestion timestamp used for Hudi deduplication |

---

## 🚀 Hudi Configuration Summary

| Parameter | Description |
|------------|-------------|
| `hoodie.table.name` | Name of the Hudi table (bronze_condition) |
| `hoodie.datasource.write.recordkey.field` | Primary key (`condition_id`) |
| `hoodie.datasource.write.precombine.field` | Timestamp for deduplication (`precombine_ts`) |
| `hoodie.datasource.write.partitionpath.field` | Partitioned by `clinical_status` |
| `hoodie.datasource.write.operation` | Upsert mode for incremental loads |
| `hoodie.datasource.hive_sync.use_glue_catalog` | Enables Glue Catalog sync for Athena |

---

## 🧮 Incremental Ingestion Workflow

1. Lists all JSON files from S3 input prefix.  
2. Queries DynamoDB to find previously processed files.  
3. Filters new/unprocessed files.  
4. Transforms and loads new files into Bronze Hudi table.  
5. Updates DynamoDB with filenames to avoid duplicates.

This design ensures **safe, idempotent re-runs** and consistent data lake ingestion.

---

## 🧰 Dependencies

Before testing or deploying locally, install the following libraries:

```bash
pip install boto3 pyspark awsglue
```

---

## 🔗 Useful AWS References

### 🔹 Apache Hudi
- [Hudi Documentation](https://hudi.apache.org/docs/overview/)
- [Using Apache Hudi with AWS Glue](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-hudi.html)

### 🔹 AWS Glue
- [AWS Glue ETL Overview](https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html)
- [Glue + Hudi Catalog Integration](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-hudi.html#aws-glue-programming-etl-hudi-catalog)

### 🔹 Amazon DynamoDB
- [DynamoDB Core Concepts](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html)
- [Using Boto3 with DynamoDB](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html)

### 🔹 AWS Data Lakehouse
- [Lakehouse Architecture on AWS](https://aws.amazon.com/solutions/guidance/lakehouse-architecture-on-aws/)

---

## ✅ Summary

This **Bronze Condition Glue Job** establishes the foundation for healthcare quality metrics and CMS analytics.  
It provides structured, queryable condition-level data to support:

- Mortality and infection rate analysis  
- Chronic condition tracking  
- Readmission and severity-based quality metrics  

---

**Author:** MetricCare Data Engineering Team  
📅 Last Updated: October 2025  
