# 🧬 Silver Layer – Condition FHIR Data Transformation (AWS Glue + Hudi)

This job is part of the **MetricCare Data Lakehouse Pipeline**, responsible for transforming **FHIR-compliant Condition data** from the Bronze layer into the **Silver layer**.  
It applies CMS-specific data enrichment and standardization to support metrics like mortality rate, infection rate, and chronic condition tracking.

---

## 🧩 Overview

The **Silver Condition Glue Job** performs the following key operations:

1. **Reads** FHIR Condition data from the Bronze Hudi table (via AWS Glue Catalog).  
2. **Cleanses and standardizes** datetime fields (`onsetDateTime`, `abatementDateTime`).  
3. **Extracts IDs** from FHIR references (`Patient`, `Encounter`).  
4. **Derives flags** like `is_infectious` and `is_chronic` based on the `category` field.  
5. **Writes processed data** into a Silver Hudi table, partitioned by `category`.  
6. **Maintains incremental ingestion** using timestamp-based logs for idempotent updates.

---

## ⚙️ Architecture Flow

```
          +--------------------------+
          | Bronze Condition (Hudi)  |
          | Raw FHIR JSON Data       |
          +------------+-------------+
                       |
                       v
         +-------------+-------------+
         | AWS Glue ETL (Silver Job) |
         | - Date normalization      |
         | - ID extraction           |
         | - Category flags          |
         +-------------+-------------+
                       |
                       v
          +------------+------------+
          | Silver Condition (Hudi) |
          | CMS-Ready, Clean Schema |
          +------------+------------+
                       |
             +---------+---------+
             | AWS Glue Catalog  |
             | Athena / Power BI |
             +-------------------+
```

---

## 🧠 Silver Schema

| Column | Description |
|---------|-------------|
| `condition_id` | Unique FHIR condition ID |
| `patient_id` | Extracted from `Patient` reference |
| `encounter_id` | Extracted from `Encounter` reference |
| `snomed_code` | SNOMED CT code identifier |
| `condition_name` | Human-readable name of the condition |
| `category` | Death / Infection / Chronic / General |
| `metric_type` | CMS metric classification (Mortality, HAI, etc.) |
| `severity` | Clinical severity (Mild, Moderate, Severe) |
| `clinical_status` | FHIR status (Active, Resolved, etc.) |
| `onset_date` | Converted onset date |
| `abatement_date` | Converted recovery date |
| `is_infectious` | True if infection-related |
| `is_chronic` | True if chronic condition |
| `sourcename` | Input JSON path from S3 |
| `precombine_ts` | Ingestion timestamp for Hudi deduplication |

---

## 🚀 Hudi Configuration Summary

| Parameter | Description |
|------------|-------------|
| `hoodie.table.name` | Name of Silver Hudi table |
| `hoodie.datasource.write.recordkey.field` | Primary key (`condition_id`) |
| `hoodie.datasource.write.precombine.field` | Deduplication timestamp (`precombine_ts`) |
| `hoodie.datasource.write.partitionpath.field` | Partition by `category` |
| `hoodie.datasource.write.operation` | Upsert for incremental processing |
| `hoodie.datasource.hive_sync.use_glue_catalog` | Enables Glue Catalog integration |

---

## 🧮 Incremental Ingestion Logic

1. Retrieves **last process timestamp** from the Silver job log table.  
2. Filters Bronze data using `precombine_ts > lastprocesstime`.  
3. Transforms only **new or modified records**.  
4. Writes the output into the Silver Hudi table.  
5. Updates log table with the new `lastprocesstime` for future runs.

This ensures **idempotent**, **incremental**, and **fault-tolerant** processing.

---

## 🧰 Dependencies

Install dependencies before testing or deploying locally:

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
- [AWS Lakehouse Architecture Reference](https://aws.amazon.com/solutions/guidance/lakehouse-architecture-on-aws/)

---

## ✅ Summary

The **Silver Condition Job** transforms CMS-aligned FHIR Condition data into a clean, analytics-ready dataset, enabling healthcare analytics such as:

- **Mortality and infection rate computation**  
- **Chronic condition monitoring**  
- **Comorbidity and risk analytics**  
- **Quality and performance metrics for CMS compliance**  

---

**Author:** MetricCare Data Engineering Team  
📅 Last Updated: October 2025  
