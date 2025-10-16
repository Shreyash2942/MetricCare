# ⚰️ Gold Layer – Mortality Rate (30-Day) | AWS Glue + Hudi + Athena

This job computes **30-day post-discharge mortality rates** per hospital and department,  
based on CMS-aligned definitions and standardized FHIR data from the Silver Layer.

It integrates **Silver Patient**, **Silver Encounter**, and **Silver Condition** tables  
to identify valid deaths occurring within 30 days after hospital discharge.

---

## 🧩 Overview

The **Gold Mortality Rate Job** performs the following core tasks:

1. **Reads** cleaned datasets from Silver Hudi tables (`silver_patients`, `silver_encounter`, `silver_condition`).
2. **Joins** patient and encounter data to detect discharges and corresponding deaths.
3. **Applies CMS rule** — death occurs **within 30 days** after discharge.
4. **Filters out invalid or negative intervals** (death date before discharge).
5. **Derives key metrics** like `death_within_30days` and `days_to_death`.
6. **Writes** results to the **Gold Mortality Hudi table (`gold_mortality_rate`)**.
7. **Logs** job execution metadata to `gold_mortality_rate_log` for auditing.

---

## ⚙️ CMS Mortality Formula

```
Mortality Rate (%) =
    (Deaths within 30 days of discharge ÷ Total inpatient discharges) × 100
```

### Inclusion Criteria:
- Encounter type = **Inpatient**
- Valid discharge date
- `deceasedDateTime` is not null
- `datediff(deceasedDateTime, discharge_date)` between **0 and 30 days**

---

## 🧠 Gold Table Schema

| Column | Description |
|---------|-------------|
| `patient_id` | Unique patient identifier |
| `encounter_id` | Encounter identifier |
| `hospital_name` | Hospital or organization name |
| `department` | Hospital department name |
| `discharge_date` | Patient discharge date |
| `admission_date` | Patient admission date |
| `deceaseddatetime` | Date of death (from Patient resource) |
| `days_to_death` | Number of days between discharge and death |
| `death_within_30days` | 1 = death ≤ 30 days after discharge |
| `year` | Year extracted from discharge date |
| `month` | Month extracted from discharge date |
| `record_date` | Date when the gold job executed |

**Primary Key:** `encounter_id`  
**Precombine Field:** `record_date`  
**Partitioning:** None (flat table structure)

---

## 🧮 Transformation Logic

| Step | Description |
|------|-------------|
| 1️⃣ | Read all silver tables from AWS Glue Catalog |
| 2️⃣ | Filter only `Inpatient` encounters |
| 3️⃣ | Join `silver_patients`, `silver_encounter`, `silver_condition` |
| 4️⃣ | Convert timestamp fields to date (`to_date`) |
| 5️⃣ | Compute `days_to_death = datediff(deceaseddatetime, discharge_date)` |
| 6️⃣ | Mark `death_within_30days = 1` if 0 ≤ days_to_death ≤ 30 |
| 7️⃣ | Filter out negative death intervals (`days_to_death < 0`) |
| 8️⃣ | Write clean results to `gold_mortality_rate` table |
| 9️⃣ | Append run audit info to `gold_mortality_rate_log` |

---

## 🧾 Athena Validation Queries

### 🔹 1. Validate Non-Negative Death Dates
```sql
SELECT *
FROM gold_mortality_rate
WHERE days_to_death < 0;
-- Expect: 0 records
```

### 🔹 2. Check Mortality Counts by Hospital
```sql
SELECT 
    hospital_name,
    COUNT(*) AS total_cases,
    SUM(death_within_30days) AS deaths_within_30days,
    ROUND(SUM(death_within_30days) * 100.0 / COUNT(*), 2) AS mortality_rate_30d
FROM gold_mortality_rate
GROUP BY hospital_name
ORDER BY mortality_rate_30d DESC;
```

### 🔹 3. Department-Level Breakdown
```sql
SELECT 
    hospital_name,
    department,
    SUM(death_within_30days) AS deaths_within_30days,
    COUNT(*) AS total_cases,
    ROUND(SUM(death_within_30days) * 100.0 / COUNT(*), 2) AS mortality_rate_30d
FROM gold_mortality_rate
GROUP BY hospital_name, department
ORDER BY mortality_rate_30d DESC;
```

### 🔹 4. Verify Valid Intervals
```sql
SELECT patient_id, discharge_date, deceaseddatetime, days_to_death
FROM gold_mortality_rate
WHERE deceaseddatetime IS NOT NULL
ORDER BY days_to_death ASC;
```

---

## 🧩 Hudi Configuration Summary

| Parameter | Description |
|------------|-------------|
| `hoodie.table.name` | `gold_mortality_rate` |
| `hoodie.datasource.write.recordkey.field` | `encounter_id` |
| `hoodie.datasource.write.precombine.field` | `record_date` |
| `hoodie.datasource.hive_sync.use_glue_catalog` | Enables Glue/Athena sync |
| `hoodie.datasource.write.storage.type` | `COPY_ON_WRITE` |
| `hoodie.datasource.write.hive_style_partitioning` | Disabled (flat table) |

---

## 📊 Power BI / QuickSight Integration

The Gold Mortality Rate table can be queried via **Athena** and visualized in dashboards.

### Suggested KPIs:
- **30-Day Mortality Rate (%)** per hospital  
- **Department-level mortality trends**  
- **Monthly trend (based on `year` + `month` fields)**  

### Suggested Visuals:
- Bar chart: Mortality Rate by Department  
- KPI card: Total 30-Day Mortality Rate  
- Table: Patient-level view with `days_to_death`

---

## 🔍 Data Quality Rules Enforced

| Rule | Description |
|------|-------------|
| ✅ Chronological | `discharge_date < deceaseddatetime` |
| ✅ Mortality Window | `days_to_death` between 0–30 days |
| ✅ Encounter Filter | Includes only Inpatient encounters |
| ✅ Date Integrity | All datetime fields converted to `date` type |
| ✅ Flat Schema | No partitioning or nested date fields |

---

## 🔗 References

### 🔹 Apache Hudi
- [Apache Hudi Documentation](https://hudi.apache.org/docs/overview/)
- [Hudi with AWS Glue](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-hudi.html)

### 🔹 AWS Glue + Athena
- [AWS Glue Developer Guide](https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html)
- [Query Hudi Tables in Athena](https://docs.aws.amazon.com/athena/latest/ug/hudi.html)

### 🔹 CMS Mortality Measure
- [CMS Hospital Mortality Measures](https://qualitynet.cms.gov/inpatient/measures/mortality)

---

**Author:** MetricCare Data Engineering Team  
📅 **Last Updated:** October 2025  
