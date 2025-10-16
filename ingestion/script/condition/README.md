# 🧬 MetricCare – FHIR Condition Data Generator

This module generates **FHIR-style Condition resources** using the `fhir.resources` library and `Faker`.  
It produces **synthetic, CMS-aligned diagnosis data** linked to `Patient` and `Encounter` resources for downstream **ETL processing (Bronze → Silver → Gold)** in the **MetricCare Data Lakehouse**.

---

## 📌 Overview

The generator produces **FHIR-compliant Condition JSON objects** that capture:
- Clinical diagnoses using **SNOMED CT codes**
- CMS metric categories (Mortality, Infection, Chronic)
- Referential links to **Patient** and **Encounter**
- Structured annotations describing **category, type, metric, severity**

Each record is unique, randomized, and ready for ingestion into your **AWS Data Lakehouse (S3 → Glue → Hudi → Athena)** pipeline.

---

## ⚙️ Features

| Feature | Description |
|----------|--------------|
| ✅ **FHIR-style JSON** | Lightweight and ETL-friendly Condition resource |
| 🧠 **CMS-mapped SNOMED codes** | Supports mortality, infection, and chronic conditions |
| 🔗 **Linked to Patient & Encounter** | Referential integrity across datasets |
| 🧾 **Structured annotations** | Stored as key-value pairs for easy parsing in Glue |
| 🧩 **ETL-ready fields** | Matches schema used in Bronze, Silver, and Gold stages |
| 💾 **Synthetic, HIPAA-safe** | No PHI; fully Faker-generated data |

---

## 🧾 Example Output

```jsonc
{
  "resourceType": "Condition",                 // FHIR resource type
  "id": "d6a909de-5c7c-41c4-b0db-0d4a942d354b", // Unique identifier
  "subject": { "reference": "Patient/pat-841212b9-bd20-41ee-b03e-8b654c3a2f6c" }, // Linked patient
  "encounter": { "reference": "Encounter/enc-6fa30a07-c7a2-4cd3-8f94-b239f16db3b8" }, // Linked encounter
  "clinicalStatus": { "text": "active" },      // Current condition status
  "code": {
    "coding": [{ "code": "233604007", "display": "Pneumonia" }],
    "text": "Pneumonia"                        // SNOMED condition name
  },
  "onsetDateTime": "2025-08-14T09:32:12.441Z", // Condition onset timestamp
  "abatementDateTime": "2025-08-17T09:32:12.441Z", // Condition resolution timestamp
  "note": [
    { "authorString": "category", "text": "Infection" },
    { "authorString": "type", "text": "Pneumonia" },
    { "authorString": "metric", "text": "HAI Rate" },
    { "authorString": "severity", "text": "moderate" }
  ]
}
```

---

## 🧩 Annotation Field Breakdown

| authorString | Example Value | Description | Used For |
|---------------|----------------|--------------|-----------|
| `category` | Infection / Death / Chronic / General | Condition classification | CMS metric grouping |
| `type` | Pneumonia, Sepsis, Diabetes, etc. | SNOMED display name | Metric-specific logic |
| `metric` | HAI Rate / Mortality Rate / Readmission Rate | CMS metric indicator | Gold-layer aggregations |
| `severity` | mild / moderate / severe | Clinical severity level | Advanced analytics |

---

## 🩺 CMS Metric Alignment

| Category | Example Condition | SNOMED Code | Metric |
|-----------|------------------|--------------|---------|
| ⚰️ **Death** | Death | 419620001 | Mortality Rate |
| 🩸 **Infection** | Pneumonia, Sepsis, UTI | 233604007, 91302008, 68566005 | HAI Rate |
| 💊 **Chronic** | Diabetes, Hypertension, COPD | 44054006, 38341003, 13645005 | Readmission / Comorbidity |
| 💉 **General** | Pressure ulcer | 399211009 | Non-Infection Analytics |

---

## 🧱 Data Lakehouse Integration

| Layer | Action | Output Table |
|--------|---------|---------------|
| 🥉 **Bronze** | Ingest raw JSONs from S3 | `bronze_condition` |
| 🥈 **Silver** | Clean and derive flags (`is_death`, `is_infection`, `is_chronic`) | `silver_condition` |
| 🥇 **Gold** | Aggregate CMS metrics | `gold_mortality_rate`, `gold_hai_rate`, `gold_readmission_rate` |

Derived Silver Layer Fields:
```text
is_death      → category = 'Death'
is_infection  → category = 'Infection'
is_chronic    → category = 'Chronic'
length_days   → abatement - onset
```

---

## 📤 Output Path Structure

```
s3://<bucket-name>/bronze/condition/YYYY/MM/DD/condition_<timestamp>.json
```

Each file contains multiple condition records linked to Patients and Encounters.

---

## ⚙️ Usage

1. **Run generator script**
   ```bash
   python fhir_condition_generator.py
   ```
2. **Preview output**
   - Prints formatted JSON to console  
3. **Save or upload**
   - Writes `condition_sample.json` (ready for S3 Bronze path)

---

## ✅ Deliverables

| File | Description |
|------|--------------|
| `fhir_condition_generator.py` | Generates CMS-aligned Condition resources |
| `README.md` | Documentation and field reference |
| `bronze_condition.py` | Glue job for raw ingestion |
| `silver_condition.py` | Data cleansing and classification |
| `gold_hai_rate.py`, `gold_mortality_rate.py` | Aggregation scripts for metrics |
