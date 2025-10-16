# 🩺 Silver Layer – Patient FHIR Data Transformation (AWS Glue + Hudi)

This job is part of the **MetricCare Data Lakehouse Pipeline**, responsible for refining **FHIR-compliant Patient data** from the Bronze layer into the **Silver layer**.  
It performs light cleansing, normalization, and adds derived fields for analytics readiness.

---

## 🧩 Overview

The **Silver Patient Glue Job** performs the following key actions:

1. **Reads** Bronze patient data from Apache Hudi table (Glue Catalog).  
2. **Applies minimal transformations** for standardization and quality:
   - Converts `birthDate` and `deceasedDateTime` into proper date format.  
   - Derives a new human-readable `deceased_flag` ("Yes"/"No").  
3. **Writes cleaned data** into a Silver-level Apache Hudi table for downstream consumption.  
4. **Maintains incremental ingestion** using timestamp logs and Glue Catalog metadata.

---

## ⚙️ Architecture Flow

```
          +------------------------+
          | Bronze Hudi (Patient)  |
          | Raw FHIR-compliant Data|
          +-----------+------------+
                      |
                      v
        +-------------+-------------+
        | AWS Glue ETL (Silver Job) |
        | - Convert date fields     |
        | - Add deceased_flag       |
        | - Drop duplicates         |
        +-------------+-------------+
                      |
                      v
          +-----------+------------+
          | Silver Hudi Table      |
          | Cleaned & Ready for BI |
          +-----------+------------+
                      |
                      v
             +--------+--------+
             | AWS Glue Catalog |
             | Athena / Power BI |
             +------------------+
```

---

## 📂 Key Components

| Component | Description |
|------------|-------------|
| **AWS Glue Job** | Executes ETL transformation logic |
| **Apache Hudi** | Provides incremental storage with upserts |
| **AWS Glue Catalog** | Enables Athena queries over Silver tables |
| **Amazon S3** | Stores Silver-level Hudi tables |
| **AWS Glue Log Table** | Tracks incremental runs and ingestion time |

---

## 🧠 Silver Schema

| Column | Description |
|---------|-------------|
| `patient_id` | Unique FHIR patient ID |
| `gender` | Male/Female |
| `birthDate` | Converted to date format |
| `language` | Patient communication language |
| `hospital_name` | Managing organization |
| `is_deceased` | Boolean deceased flag |
| `deceased_flag` | Readable "Yes"/"No" version |
| `deceasedDateTime` | Converted to date format |
| `sourcename` | Source JSON path from Bronze layer |
| `precombine_ts` | Ingestion timestamp used for Hudi deduplication |

---

## 🚀 Hudi Configuration Summary

| Parameter | Description |
|------------|-------------|
| `hoodie.table.name` | Name of Silver Hudi table |
| `hoodie.datasource.write.operation` | Upsert for incremental processing |
| `hoodie.datasource.write.recordkey.field` | `patient_id` |
| `hoodie.datasource.write.precombine.field` | `precombine_ts` |
| `hoodie.datasource.write.partitionpath.field` | `hospital_name` |
| `hoodie.datasource.hive_sync.use_glue_catalog` | Syncs schema to Glue Catalog |

---

## 🧮 Incremental Ingestion Logic

1. Reads **last processed timestamp** from the Silver job log table.  
2. Filters Bronze data where `precombine_ts` > last processed time.  
3. Processes only **new or updated records**.  
4. Writes transformed data to Silver Hudi table and updates the timestamp log.

This ensures **idempotent** and **incremental** processing.

---

## 🧰 Dependencies

Install required packages before running locally or testing:

```bash
pip install boto3 pyspark awsglue
```

---

## 🔗 Useful AWS References

### 🔹 Apache Hudi
- [Hudi Overview](https://hudi.apache.org/docs/overview/)
- [Hudi + AWS Glue Integration](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-hudi.html)

### 🔹 AWS Glue
- [AWS Glue ETL Overview](https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html)
- [Glue Catalog & Athena Integration](https://docs.aws.amazon.com/athena/latest/ug/glue-best-practices.html)

### 🔹 AWS Data Lakehouse
- [AWS Lakehouse Reference Architecture](https://aws.amazon.com/solutions/guidance/lakehouse-architecture-on-aws/)

---

## ✅ Summary

This **Silver Patient job** standardizes the cleaned data from the Bronze layer, enabling reliable downstream analytics such as:

- Mortality rate aggregation  
- Readmission analysis  
- Patient demographics reporting  

---

**Author:** MetricCare Data Engineering Team  
📅 Last Updated: October 2025  
