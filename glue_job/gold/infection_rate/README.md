# Gold Layer – Infection Rate | AWS Glue + Hudi + Athena

This job computes the **Infection Rate** for healthcare quality monitoring under CMS metrics.  
It identifies infection-related conditions (e.g., sepsis, pneumonia, UTI, etc.) from the Silver layer and calculates infection rates by ICD-10/SNOMED code and condition type.

---

## Overview

The **Gold Infection Rate Job** performs the following operations:

1. Reads condition data from `silver_condition` (Hudi table via AWS Glue Catalog).  
2. Filters incremental records based on `precombine_ts`.  
3. Classifies conditions as **Infectious** or **Non-Infectious** using the `infection_flag`.  
4. Aggregates results by `icd10_code` and `condition_name`.  
5. Calculates the infection rate as the percentage of infection-related cases.  
6. Writes the results to a Gold Hudi table and updates the ETL log.

---

## CMS Infection Rate Formula

```
Infection Rate (%) = (Number of infection-related cases ÷ Total patient cases) × 100
```

**Infection-related conditions** include sepsis, pneumonia, urinary tract infection, clostridium difficile colitis, septicemia, and similar hospital-acquired infections (HAIs).

---

## Gold Table Schema

| Column | Description |
|---------|-------------|
| `icd10_code` | ICD-10 or SNOMED condition code |
| `condition_name` | Clinical description of the condition |
| `condition_type` | Infectious or Non-Infectious |
| `total_patients` | Number of unique patients with this condition |
| `infection_cases` | Number of cases flagged as infection-related |
| `infection_rate_percent` | Calculated infection rate (%) |
| `record_timestamp` | Timestamp of ETL run |

**Partitioned by:** `condition_type`  
**Primary Key:** `icd10_code`  
**Precombine Field:** `record_timestamp`

---

## Transformation Logic

| Step | Description |
|------|-------------|
| 1 | Read `silver_condition` table via AWS Glue Catalog |
| 2 | Filter only new data (based on `precombine_ts`) |
| 3 | Create `condition_type` = Infectious if `infection_flag` = 1 |
| 4 | Aggregate per `icd10_code` and `condition_name` |
| 5 | Compute infection rate = (infection_cases ÷ total_patients) × 100 |
| 6 | Write Gold table and update log table |

---

## Athena Validation Queries

### 1. Verify Gold Table Content
```sql
SELECT 
    icd10_code,
    condition_name,
    condition_type,
    total_patients,
    infection_cases,
    ROUND(infection_rate_percent, 2) AS infection_rate_percent
FROM gold_infection_rate
ORDER BY infection_rate_percent DESC;
```

### 2. Calculate Overall Infection Rate
```sql
SELECT 
    ROUND(SUM(infection_cases) * 100.0 / SUM(total_patients), 2) AS overall_infection_rate
FROM gold_infection_rate
WHERE condition_type = 'Infectious';
```

### 3. Compare Infection vs Non-Infection Categories
```sql
SELECT 
    condition_type,
    COUNT(DISTINCT icd10_code) AS total_conditions,
    ROUND(SUM(infection_cases) * 100.0 / SUM(total_patients), 2) AS avg_infection_rate
FROM gold_infection_rate
GROUP BY condition_type;
```

### 4. Patient-Level Verification (Silver Data)
```sql
SELECT 
    patientid,
    icd10_code,
    condition_name,
    infection_flag,
    CASE WHEN infection_flag = 1 THEN 'Infectious' ELSE 'Non-Infectious' END AS condition_type
FROM silver_condition
LIMIT 50;
```

---

## Hudi Configuration Summary

| Parameter | Description |
|------------|-------------|
| `hoodie.table.name` | `gold_infection_rate` |
| `hoodie.datasource.write.recordkey.field` | `icd10_code` |
| `hoodie.datasource.write.precombine.field` | `record_timestamp` |
| `hoodie.datasource.write.partitionpath.field` | `condition_type` |
| `hoodie.datasource.hive_sync.use_glue_catalog` | Enables Glue & Athena integration |

---

## Visualization Ideas

Once the Gold table is registered in the Glue Catalog, it can be visualized in **Power BI**, **QuickSight**, or **Athena** dashboards.

**Suggested KPIs:**
- Average Infection Rate by Condition Type  
- Top 10 Infection Conditions (highest infection_rate_percent)  
- Infection Rate by Hospital Department or Region (if available)  
- Year-over-Year or Monthly Trend of Infection Rates  

**Example Metric**
```sql
SELECT
    condition_name,
    ROUND(infection_rate_percent, 2) AS infection_rate
FROM gold_infection_rate
WHERE condition_type = 'Infectious'
ORDER BY infection_rate DESC
LIMIT 10;
```

---

## Useful References

- [Apache Hudi Documentation](https://hudi.apache.org/docs/overview/)
- [AWS Glue Hudi Integration](https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-hudi.html)
- [Athena Querying Hudi Tables](https://docs.aws.amazon.com/athena/latest/ug/hudi-queries.html)
- [CMS Healthcare-Associated Infections (HAI)](https://www.cms.gov/Medicare/Quality-Initiatives-Patient-Assessment-Instruments/HospitalQualityInits/HospitalHCAHPS)
- [CDC HAI Metrics](https://www.cdc.gov/hai/surveillance/index.html)

---

**Author:** MetricCare Data Engineering Team  
Last Updated: October 2025
