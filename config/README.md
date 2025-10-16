# 📁 MetricCare Data Lakehouse – Job Configuration (`config.json`)

This configuration file defines **input/output paths**, **target tables**, and **log tracking tables** for all **AWS Glue jobs** in the MetricCare Lakehouse pipeline.  
It provides a **single source of truth** for Glue job parameters — used by both Terraform and Glue ETL scripts to maintain consistent naming and structure across all data layers.

---

## 🧩 Purpose

The `config.json` file centralizes key Glue job settings:

- ✅ Defines source (`input_path`) and destination (`output_path`) folders.  
- ✅ Specifies database table names for each processing layer.  
- ✅ Tracks logs and job execution via `log_path` and `log_table`.  
- ✅ Ensures consistent file structure across Patient, Encounter, and Condition datasets.

This configuration is uploaded to S3 during Terraform deployment and consumed by each Glue job to dynamically load parameters.

---

## ⚙️ JSON Structure Overview

Each key corresponds to a **specific Glue job**, such as:
```json
"job_bronze_patient_hudi": {
  "input_path": "fhir_data/json/patients/",
  "output_path": "database/bronzetable/patients",
  "log_path": "database/log_tables/bronze_patient_logs",
  "table": "bronze_patients",
  "log_table": "bronze_patient_log"
}
```

| Field | Description |
|--------|--------------|
| **input_path** | Path to source JSON files (FHIR data from ingestion). |
| **output_path** | Target location for processed data in S3. |
| **log_path** | Location where Glue writes job execution metadata. |
| **table** | Name of the target data table in Glue/Hudi. |
| **log_table** | Audit table for job logs (used for incremental tracking). |

---

## 🪣 Pathing Convention

All folders and tables follow the **Medallion Architecture (Bronze → Silver → Gold)** pattern.

```
fhir_data/json/<resource>        → Raw JSON input (Patient, Encounter, Condition)
database/bronzetable/<resource>  → Cleaned & structured Hudi tables
database/silvertable/<resource>  → Normalized tables for metric computation
database/gold_table/<metric>     → Aggregated metric-level data
database/log_tables/<layer>_*    → Job audit and process logs
```

---

## 🥉 Bronze Layer – Raw Ingestion

| Job | Input | Output | Table | Log Table |
|------|--------|----------|----------|-------------|
| **job_bronze_condition_hudi** | `fhir_data/json/conditions/` | `database/bronzetable/conditions` | `bronze_condition` | `bronze_condition_log` |
| **job_bronze_encounter_hudi** | `fhir_data/json/encounters/` | `database/bronzetable/encounters` | `bronze_encounter` | `bronze_encounter_log` |
| **job_bronze_patient_hudi** | `fhir_data/json/patients/` | `database/bronzetable/patients` | `bronze_patients` | `bronze_patient_log` |

**Purpose:**  
Stores ingested FHIR data (Patient, Encounter, Condition) as **Hudi copy-on-write tables** in raw form.  
Minimal transformation, schema validation, and ingestion timestamp added.

---

## 🥈 Silver Layer – Cleansing & Normalization

| Job | Input | Output | Table | Log Table |
|------|--------|----------|----------|-------------|
| **job_silver_condition** | `fhir_data/json/conditions/` | `database/silvertable/conditions` | `silver_condition` | `silver_condition_log` |
| **job_silver_encounter** | `fhir_data/json/encounters/` | `database/silvertable/encounters` | `silver_encounter` | `silver_encounter_log` |
| **job_silver_patient** | `fhir_data/json/patients/` | `database/silvertable/patients` | `silver_patients` | `silver_patient_log` |

**Purpose:**  
Performs data standardization:
- Flattens nested JSON (FHIR resources)  
- Parses and validates timestamps  
- Derives helper columns (e.g., `length_days`, `is_death`, `is_infection`)  
- Removes redundant or null fields  

---

## 🥇 Gold Layer – Metric Aggregation

| Job | Input | Output | Table | Log Table |
|------|--------|----------|----------|-------------|
| **job_gold_infection_rate** | *Derived from Silver layer* | `database/gold_table/infection_rate` | `gold_infection_rate` | `gold_infection_log` |
| **job_gold_mortality_rate** | *Derived from Silver layer* | `database/gold_table/mortality_rate` | `gold_mortality_rate` | `gold_mortality_rate_log` |
| **job_gold_readmission_rate** | *Derived from Silver layer* | `database/gold_table/readmission_rate` | `gold_readmission_rate` | `gold_readmission_rate_log` |

**Purpose:**  
Aggregates data into **CMS-aligned compliance metrics**:
- 🧬 **Infection Rate** — (Infections ÷ Encounters × 1000)  
- ⚰️ **Mortality Rate** — (Deaths ÷ Discharges × 100)  
- 🔁 **Readmission Rate** — (Re-admissions ÷ Discharges × 100)

Gold tables are **partitioned by department or month** for Power BI analytics.

---

## 🧾 Log Tables

Each job writes to a corresponding **log table** under `database/log_tables/` for auditing.

| Log Table | Description |
|-------------|--------------|
| `bronze_*_log` | Tracks raw ingestion success/failure |
| `silver_*_log` | Records cleansing and normalization job runs |
| `gold_*_log` | Logs metric computation results (aggregations) |

**Columns typically include:**
```
log_id, job_name, status, start_time, end_time, record_count, error_message
```

---

## 🔗 Integration with AWS Glue Jobs

Each Glue ETL script (e.g., `job_bronze_condition_hudi.py`) reads parameters dynamically:
```python
import json, boto3
config = json.load(open("config/config.json"))
params = config["job_bronze_condition_hudi"]

input_path  = params["input_path"]
output_path = params["output_path"]
log_table   = params["log_table"]
```

✅ This enables **config-driven automation** — one script can run across multiple environments simply by pointing to different `config.json` files.

---

## ☁️ Typical S3 Structure

```
s3://mcde4-sp/
│
├── config/config.json
├── database/
│   ├── bronzetable/
│   ├── silvertable/
│   ├── gold_table/
│   └── log_tables/
└── fhir_data/
    └── json/
        ├── patients/
        ├── encounters/
        └── conditions/
```

---

## ✅ Best Practices

| Recommendation | Benefit |
|----------------|----------|
| Keep all job parameters centralized in `config.json` | Avoids code duplication |
| Version the file in Git and S3 | Enables reproducibility and rollback |
| Sync `config.json` during Terraform apply | Ensures Glue jobs read the latest paths |
| Maintain naming consistency across layers | Simplifies Glue workflow chaining |
| Add environment suffix (`-dev`, `-prod`) in future configs | Isolates deployments safely |
