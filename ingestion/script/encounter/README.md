# 🏥 MetricCare – FHIR Encounter Data Generator

This module generates **FHIR-style Encounter resources** using the `fhir.resources` library and `Faker`.  
It creates **synthetic, HIPAA-safe JSON files** that simulate hospital visit records for use in your **AWS Data Lakehouse** (S3 → Glue → Hudi → Athena).

---

## 📌 Overview

The generator produces **FHIR-compliant Encounter JSON objects** with randomized:
- Admission and discharge timestamps
- Encounter type (inpatient, outpatient, emergency, etc.)
- Departments and hospital units
- Attending practitioners
- Linked Patient references

Each Encounter is directly tied to a **FHIR Patient resource**, enabling metric calculations for:
**Average Length of Stay (ALOS)**, **Readmission Rate**, **Bed Occupancy**, and **Department Load**.

---

## ⚙️ Features

| Feature | Description |
|----------|--------------|
| ✅ **FHIR-style structure** | Based on HL7 FHIR `Encounter` resource |
| 🏥 **Realistic visit scenarios** | Includes inpatient, outpatient, emergency, and virtual encounters |
| 🧑‍⚕️ **Practitioner and location links** | Each record references a practitioner and hospital department |
| ⏱️ **Time-based periods** | Admission/discharge timestamps for ALOS and readmission tracking |
| 🌎 **Multiple hospital locations** | Randomly cycles through MetricCare facilities (Charlotte, Raleigh, Durham) |
| 💾 **AWS-ready** | Outputs JSON files ready for ingestion into S3 Bronze layer |

---

## 🧩 Data Model Summary

| Field | Example | Description |
|--------|----------|-------------|
| `id` | `"enc-001"` | Unique encounter identifier |
| `status` | `"finished"` | Current encounter state |
| `type.text` | `"Inpatient"` | Encounter category |
| `subject.reference` | `"Patient/pat-001"` | Links encounter to a patient |
| `actualPeriod.start` | `"2025-09-15T08:00:00Z"` | Admission timestamp |
| `actualPeriod.end` | `"2025-09-20T14:30:00Z"` | Discharge timestamp |
| `location.display` | `"ICU"` | Department/unit |
| `serviceProvider.display` | `"MetricCare Hospital - Charlotte"` | Hospital name |
| `participant.actor.reference` | `"Practitioner/<UUID>"` | Assigned physician or nurse |

---

## 🧮 CMS Metric Alignment

| CMS Metric | Derived From | Logic |
|-------------|--------------|-------|
| **Average Length of Stay (ALOS)** | `actualPeriod.start/end` | Average hospitalization duration |
| **Readmission Rate (30-Day)** | `subject.reference`, `actualPeriod.end` | Re-encounter within 30 days |
| **Bed Occupancy Rate** | `status`, `location.display` | Ratio of active encounters |
| **Departmental Load** | `location.display` | Track ICU, ER, and ward utilization |

---

## 🧰 Example JSON Output

```json
{
  "resourceType": "Encounter",                                 // Defines FHIR resource type
  "id": "enc-14fa5c72-18b4-4ad9-a06b-3c3df775b3a1",            // Unique encounter ID (primary key)
  "status": "finished",                                        // Encounter lifecycle state (used for occupancy metrics)
  "type": [ { "text": "Inpatient" } ],                         // Encounter category (e.g., Inpatient, Outpatient)
  "subject": { "reference": "Patient/2f43a8b7-01d9-4f36-b592-cb36a948fa53" },  // Patient FHIR reference
  "actualPeriod": {                                            // Admission/discharge timestamps (ALOS calculation)
    "start": "2025-09-15T08:00:00.000Z",                       // Admission time
    "end": "2025-09-20T14:30:00.000Z"                          // Discharge time
  },
  "location": [                                                // Encounter location section
    {
      "location": { "display": "ICU" },                        // Department/unit (used for Department Load metric)
      "period": {
        "start": "2025-09-15T08:00:00.000Z",                   // Location admission time
        "end": "2025-09-20T14:30:00.000Z"                      // Location discharge time
      }
    }
  ],
  "serviceProvider": { "display": "MetricCare Hospital - Charlotte" }, // Hospital name (regional CMS comparison)
  "participant": [                                             // Attending staff details
    {
      "type": [ { "text": "attending physician" } ],           // Role of practitioner
      "actor": { "reference": "Practitioner/df8a3f44-b3a7-48c1-a21b-9c6461b3b02d" }, // Practitioner reference
      "period": {
        "start": "2025-09-15T08:00:00.000Z",                   // Practitioner involvement start
        "end": "2025-09-20T14:30:00.000Z"                      // Practitioner involvement end
      }
    }
  ]
}
```

---

## 🪶 How It Fits in the Data Lakehouse

```
FHIR Generator → S3 (Bronze) → Glue (Bronze → Silver → Gold) → Athena → Power BI
```

- **Bronze Layer:** Raw Encounter JSON data written as Hudi tables  
- **Silver Layer:** Derived fields like `length_days`, `readmit_flag`, and department normalization  
- **Gold Layer:** Aggregated CMS metrics (mortality, readmission, ALOS, infection rate)  

---

## 🚀 Usage

```bash
python encounter_generator.py
```

Output:
```
Patient 'Encounter' data
{ JSON structure printed in console }
```

You can also batch-generate encounters by looping through Patient IDs and saving the output to JSON files or S3 paths such as:
```
s3://<your-bucket>/bronze/encounter/YYYY/MM/DD/
```

---

## 🧱 Integration Points

| Integration | Description |
|--------------|--------------|
| **Patient Generator** | Links via `subject.reference` |
| **Condition Generator** | Links via `encounter.reference` |
| **Glue Bronze Jobs** | Reads from S3 → writes to Hudi `bronze_encounter` |
| **DynamoDB Tracker** | Prevents reprocessing duplicate encounter files |
| **Athena** | Used for ALOS, readmission, and occupancy queries |

---

## 🧰 Dependencies

```bash
pip install faker fhir.resources
```

---

## 🧾 Deliverables

| File | Description |
|------|--------------|
| `encounter_generator.py` | Python script to generate Encounter JSON |
| `README.md` | Documentation (this file) |
| `sample_output.json` | Example Encounter dataset for testing |
| `bronze_encounter_glue.py` | AWS Glue ingestion script (optional) |

---

## ✅ Outcome

- Fully **FHIR-compliant Encounter data**
- Supports **CMS compliance metrics**
- Ready for ingestion into **AWS Glue ETL**
- Compatible with **Athena queries** and **Power BI dashboards**

---

🩺 *Part of the MetricCare Data Lakehouse – a FHIR-based CMS Metrics Platform*
