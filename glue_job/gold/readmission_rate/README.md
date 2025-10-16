# 🔁 Gold Layer – 30-Day Readmission Rate | AWS Glue + Hudi + Athena

This job calculates the **30-day hospital readmission rate** — one of the key CMS quality metrics — using inpatient encounter data from the Silver layer.  
It identifies patients readmitted within 30 days of discharge and aggregates the results by hospital and department.

---

## 🧩 Overview

The **Gold Readmission Rate Job** performs the following key operations:

1. **Reads** inpatient data from `silver_encounter` (Hudi table via Glue Catalog).  
2. **Sorts** patient encounters chronologically.  
3. **Calculates** the time difference between each discharge and the next admission.  
4. **Flags readmissions** where the next admission occurs ≤ 30 days after discharge.  
5. **Aggregates** results by hospital and department.  
6. **Writes** a Gold Hudi table with readmission statistics.  
7. **Updates** the job log for incremental processing.

---

## ⚙️ CMS Readmission Formula

\`\`\`
Readmission Rate (%) =
    (Number of patients readmitted within 30 days after discharge ÷
     Total inpatient discharges) × 100
\`\`\`

**Conditions:**
- Only **Inpatient** encounters are considered.  
- Exclude same-day or overlapping discharges/admissions.  
- Readmission = next admission within **30 days** after discharge.

---

## 🧠 Gold Schema

| Column | Description |
|---------|-------------|
| `hospital_name` | Name of hospital or managing organization |
| `department` | Clinical department of the encounter |
| `total_discharges` | Total inpatient discharges |
| `readmissions_within_30d` | Number of patients readmitted within 30 days |
| `readmission_rate_30d` | Calculated CMS readmission rate (%) |
| `record_timestamp` | ETL run timestamp |

**Partitioned by:** `department`  
**Primary Key:** `hospital_name`  
**Precombine Field:** `record_timestamp`

---

## 🧮 Transformation Logic

| Step | Description |
|------|-------------|
| 1️⃣ | Read Inpatient encounters from Silver Hudi table |
| 2️⃣ | Partition data by `patient_id` and order by `admission_date` |
| 3️⃣ | Use `lag(discharge_date)` to calculate gap from last encounter |
| 4️⃣ | Flag `is_readmission = 1` if days between encounters ≤ 30 |
| 5️⃣ | Aggregate by hospital and department |
| 6️⃣ | Compute `readmission_rate_30d` (%) and write to Gold table |

---

## 🧾 Athena Validation Queries

### 🔹 1. Verify Table Content
\`\`\`sql
SELECT 
    hospital_name,
    department,
    total_discharges,
    readmissions_within_30d,
    ROUND(readmission_rate_30d, 2) AS readmission_rate_30d
FROM gold_readmission_rate
ORDER BY hospital_name, department;
\`\`\`

### 🔹 2. Compute Overall Readmission Rate
```sql
SELECT 
    ROUND(SUM(readmissions_within_30d) * 100.0 / SUM(total_discharges), 2) AS overall_readmission_rate_30d,
    COUNT(DISTINCT hospital_name) AS total_hospitals
FROM gold_readmission_rate;
```

### 🔹 3. Verify Patient-Level Readmissions (Crosscheck)
```sql
SELECT 
    patient_id,
    hospital_name,
    department,
    admission_date,
    discharge_date,
    LAG(discharge_date) OVER (PARTITION BY patient_id ORDER BY admission_date) AS prev_discharge_date,
    date_diff('day', LAG(discharge_date) OVER (PARTITION BY patient_id ORDER BY admission_date), admission_date) AS days_since_last_discharge
FROM silver_encounter
WHERE encounter_type = 'Inpatient'
ORDER BY patient_id, admission_date;
```

### 🔹 4. Filter Actual Readmissions (≤ 30 days)
```sql
SELECT *
FROM (
  SELECT 
      patient_id,
      hospital_name,
      department,
      admission_date,
      discharge_date,
      date_diff('day', LAG(discharge_date) OVER (PARTITION BY patient_id ORDER BY admission_date), admission_date) AS days_since_last_discharge
  FROM silver_encounter
  WHERE encounter_type = 'Inpatient'
)
WHERE days_since_last_discharge BETWEEN 1 AND 30;
```

---

## 🧩 Hudi Configuration Summary

| Parameter | Description |
|------------|-------------|
| `hoodie.table.name` | `gold_readmission_rate` |
| `hoodie.datasource.write.recordkey.field` | `hospital_name` |
| `hoodie.datasource.write.precombine.field` | `record_timestamp` |
| `hoodie.datasource.write.partitionpath.field` | `department` |
| `hoodie.datasource.hive_sync.use_glue_catalog` | Enables Glue & Athena sync |

---

## 📊 Integration with Dashboards

Once written and synced with AWS Glue Catalog, this table can be visualized in **Power BI** or **QuickSight** using Athena as a source.

**Suggested Visuals:**
- Line chart: Readmission Rate (%) over time  
- Bar chart: Hospital vs Readmission Rate (%)  
- KPI: Overall 30-Day Readmission Rate

**Example KPI**
\`\`\`
Overall Readmission Rate = (SUM(readmissions_within_30d) / SUM(total_discharges)) * 100
\`\`\`

---

## 🔗 Useful References

### 🔹 Apache Hudi
- [Apache Hudi Documentation](https://hudi.apache.org/docs/overview/)
- [Using Hudi with AWS Glue](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-hudi.html)

### 🔹 AWS Glue & Athena
- [AWS Glue ETL Overview](https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html)
- [Athena + Glue Integration](https://docs.aws.amazon.com/athena/latest/ug/glue-best-practices.html)

### 🔹 CMS Measure References
- [CMS Hospital Readmission Reduction Program (HRRP)](https://www.cms.gov/medicare/medicare-fee-for-service-payment/acuteinpatientpps/readmissions-reduction-program)

---

**Author:** MetricCare Data Engineering Team  
📅 Last Updated: October 2025  
