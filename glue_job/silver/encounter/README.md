# 🏥 Silver Layer – Encounter FHIR Data Transformation (AWS Glue + Hudi)

This job is part of the **MetricCare Data Lakehouse Pipeline**, responsible for transforming **FHIR-compliant Encounter data** from the Bronze layer into the **Silver layer**.  
It applies essential data cleansing and enrichment to prepare the encounter data for downstream analytics.

---

## 🧩 Overview

The **Silver Encounter Glue Job** performs the following core operations:

1. **Reads** Encounter data from the Bronze Hudi table (registered in AWS Glue Catalog).  
2. **Standardizes timestamps** by converting `admission_time` and `discharge_time` to readable `date` format.  
3. **Extracts entity identifiers** from FHIR references (e.g., `patient_id`, `practitioner_id`).  
4. **Derives encounter duration** in days.  
5. **Writes cleaned and enriched data** into a Silver Hudi table, partitioned by hospital name.  
6. **Maintains incremental ingestion** using timestamp-based logging to ensure idempotency.

---

## ⚙️ Architecture Flow

```
          +--------------------------+
          | Bronze Encounter (Hudi)  |
          | Raw FHIR-compliant Data  |
          +------------+-------------+
                       |
                       v
         +-------------+-------------+
         | AWS Glue ETL (Silver Job) |
         | - Clean timestamps        |
         | - Extract IDs             |
         | - Compute duration days   |
         +-------------+-------------+
                       |
                       v
          +------------+------------+
          | Silver Encounter (Hudi) |
          | Clean & Enriched Schema |
          +------------+------------+
                       |
             +---------+---------+
             | AWS Glue Catalog  |
             | Athena / Power BI |
             +-------------------+
```

---

## 📂 Key Components

| Component | Description |
|------------|-------------|
| **AWS Glue Job** | Executes ETL logic for data standardization and transformation |
| **Apache Hudi** | Provides incremental data storage and ACID upserts |
| **AWS Glue Catalog** | Enables query access via Athena or BI tools |
| **Amazon S3** | Stores Silver-layer Hudi tables |
| **Glue Log Table** | Tracks last processing timestamp for incremental runs |

---

## 🧠 Silver Encounter Schema

| Column | Description |
|---------|-------------|
| `encounter_id` | Unique FHIR encounter ID |
| `patient_id` | Extracted from `Patient` reference |
| `practitioner_id` | Extracted from `Practitioner` reference |
| `status` | Encounter lifecycle status |
| `encounter_type` | Encounter category (Inpatient, Outpatient, etc.) |
| `department` | Department where encounter occurred |
| `participant_role` | Role of participant (Physician, Nurse, etc.) |
| `hospital_name` | Name of the managing organization |
| `admission_date` | Converted start date of encounter |
| `discharge_date` | Converted end date of encounter |
| `encounter_duration_days` | Derived from discharge - admission |
| `sourcename` | Input file path from Bronze layer |
| `precombine_ts` | Ingestion timestamp used by Hudi |

---

## 🚀 Hudi Configuration Summary

| Parameter | Description |
|------------|-------------|
| `hoodie.table.name` | Name of the Hudi Silver table |
| `hoodie.datasource.write.recordkey.field` | Primary key (`encounter_id`) |
| `hoodie.datasource.write.precombine.field` | Timestamp used for deduplication (`precombine_ts`) |
| `hoodie.datasource.write.partitionpath.field` | Partition by `hospital_name` |
| `hoodie.datasource.write.operation` | Set to `upsert` for incremental processing |
| `hoodie.datasource.hive_sync.use_glue_catalog` | Enables schema sync with Glue Catalog |

---

## 🧮 Incremental Ingestion Logic

1. Reads **last processed timestamp** from the Silver log table.  
2. Filters Bronze data where `precombine_ts` > last processed time.  
3. Processes only **new or updated encounter records**.  
4. Writes transformed results to the Silver table.  
5. Updates the log table to record the new `lastprocesstime`.

This design ensures **idempotent** and **incremental processing**, critical for large-scale ETL pipelines.

---

## 🧰 Dependencies

Install dependencies before running locally or testing:

```bash
pip install boto3 pyspark awsglue
```

---

## 🔗 Useful AWS References

### 🔹 Apache Hudi
- [Hudi Overview](https://hudi.apache.org/docs/overview/)
- [Using Hudi with AWS Glue](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-hudi.html)

### 🔹 AWS Glue
- [AWS Glue ETL Overview](https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html)
- [Glue Catalog and Athena Integration](https://docs.aws.amazon.com/athena/latest/ug/glue-best-practices.html)

### 🔹 AWS Data Lakehouse
- [Lakehouse Architecture on AWS](https://aws.amazon.com/solutions/guidance/lakehouse-architecture-on-aws/)

---

## ✅ Summary

The **Silver Encounter Job** provides standardized, analytics-ready encounter data that supports advanced healthcare insights, such as:

- **Encounter duration analysis** (Length of Stay)  
- **Department performance tracking**  
- **Physician and patient engagement metrics**  

---

**Author:** MetricCare Data Engineering Team  
📅 Last Updated: October 2025  
