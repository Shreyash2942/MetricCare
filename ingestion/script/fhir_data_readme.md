# 🧩 MetricCare – Synthetic FHIR Data Generator (Ingestion Layer)

This module generates and manages **synthetic, FHIR-compliant datasets** (Patient, Encounter, Condition) for ingestion into the **AWS Lakehouse (S3 → Glue → Hudi → Athena)** pipeline.  
It provides an end-to-end workflow for local or S3 output, parameterized simulation, and CMS-aligned metric generation.

---

## 🏗️ Folder Structure

```
ingestion/
│
├── script/
│   ├── config/
│   │   └── config_fhir.py                # Shared constants (hospitals, SNOMED, time config, etc.)
│   │
│   ├── patient/
│   │   └── generate_patient_fhir.py      # Generates FHIR Patient resources
│   │
│   ├── encounter/
│   │   └── generate_encounter_fhir.py    # Generates FHIR Encounter resources
│   │
│   ├── condition/
│   │   └── generate_condition_fhir.py    # Generates FHIR Condition resources
│   │
│   ├── cms_metric_data_simulator_v4.py   # Creates CMS-style datasets using FHIR structure
│   ├── generate_fhir_data.py             # Combines Patient, Encounter, Condition generation
│   ├── main_generate.py                  # Entry script (orchestrates generation + S3 upload)
│   │
│   ├── save_json.py                      # Saves data to local JSON structure
│   ├── upload_to_S3.py                   # Uploads generated JSON to AWS S3
│   ├── aws_credential.py                 # Loads credentials and validates S3 connection
│
└── fhir_data/
    └── json/
        ├── patient/
        ├── encounter/
        └── condition/
```

---

## ⚙️ Overview

Each component has a **specific role** in the ingestion workflow:

| Script | Purpose |
|--------|----------|
| `config_fhir.py` | Centralized configuration (hospitals, SNOMED codes, time settings, version metadata). |
| `generate_patient_fhir.py` | Generates synthetic FHIR `Patient` resources. |
| `generate_encounter_fhir.py` | Generates linked FHIR `Encounter` resources per patient. |
| `generate_condition_fhir.py` | Generates FHIR `Condition` resources (Mortality, Infection, Readmission). |
| `generate_fhir_data.py` | Creates a dataset of Patients + Encounters + Conditions. |
| `cms_metric_data_simulator_v4.py` | Simulates CMS metrics using realistic date and condition rules. |
| `save_json.py` | Saves dataset locally into structured folders. |
| `upload_to_S3.py` | Uploads datasets to your S3 bucket using `boto3`. |
| `aws_credential.py` | Loads credentials from `.env` and validates connection. |
| `main_generate.py` | Main driver script that runs the full pipeline. |

---

## 🧬 Workflow Summary

1. **Configuration Loaded**
   - All scripts import parameters from `config_fhir.py`
   - Defines hospitals, SNOMED codes, encounter types, and time settings.

2. **Patient Generation**
   - Each Patient record is realistic (age, gender, location, birth/death).

3. **Encounter Generation**
   - Each Patient has 1–n encounters with type, department, hospital.

4. **Condition Generation**
   - Assigns SNOMED-coded conditions (Death, Infection, Chronic, etc.).
   - Each Condition links to a valid Patient and Encounter.

5. **Simulation (CMS-Aligned)**
   - The `cms_metric_data_simulator_v4.py` script generates **Mortality**, **Infection**, **Readmission**, and **ALOS** data.
   - Includes configurable percentages (e.g., 10% mortality, 20% infection).

6. **Storage**
   - Data saved locally or uploaded to S3 (`fhir_data/json/...`).

---

## 🚀 Usage

### 🧱 Option 1: Basic Data Generation (Local)
```bash
python main_generate.py
```

- Generates `patients`, `encounters`, and `conditions` JSON files.
- Saves in:  
  `fhir_data/json/{resource}/resource_timestamp.json`

### ☁️ Option 2: Configured AWS Upload
Create a `.env` file named `aws_crendential.env`:
```
AWS_ACCESS_KEY=YOUR_ACCESS_KEY
AWS_SECRET_KEY=YOUR_SECRET_KEY
S3_BUCKET_NAME=your-bucket-name
```

Then run:
```bash
python main_generate.py
```
✅ The script validates your AWS credentials and uploads JSON data to:
```
s3://your-bucket-name/fhir_data/json/patient/
s3://your-bucket-name/fhir_data/json/encounter/
s3://your-bucket-name/fhir_data/json/condition/
```

---

## ⚙️ CMS Simulation Example

Run the advanced simulator for metric-specific generation:
```bash
python cms_metric_data_simulator_v4.py
```

**Example Input**
```
Enter number of patients (e.g., 500): 100
Enter year to simulate (e.g., 2023): 2023
Mortality percentage [10%]:
Infection percentage [20%]:
Readmission percentage [15%]:
ALOS percentage [100%]:
```

**Output**
```
─────────────────────────── SUMMARY ───────────────────────────
Year simulated:           2023
Total patients simulated: 100
Total encounters:         425
Total conditions:         320
───────────────────────────────────────────────────────────────
Mortality   : 10
Infection   : 20
Readmission : 15
ALOS        : 100
```

---

## 🧱 Example Output Schema (FHIR JSON)

**Patient Example**
```json
{
  "resourceType": "Patient",
  "id": "3f97d742-63c9-4931-a15f-80ffedaa0675",
  "gender": "female",
  "birthDate": "1973-08-11",
  "address": [{"city": "Charlotte", "state": "NC"}],
  "managingOrganization": {"reference": "Organization/org-metriccare"}
}
```

**Condition Example**
```json
{
  "resourceType": "Condition",
  "id": "0e31df71-962b-4dc9-91b7-39a3296ff57a",
  "code": {
    "coding": [{"code": "419620001", "display": "Death"}],
    "text": "Death"
  },
  "clinicalStatus": {"text": "resolved"},
  "note": [{"authorString": "category", "text": "Death"}]
}
```

---

## 🧰 Recommended Enhancements

| Category | Recommendation | Benefit |
|-----------|----------------|----------|
| ✅ Config Management | Use a `config.yaml` instead of `.py` for dynamic reloading | Enables runtime parameterization without code edits |
| 🗂️ Folder Structure | Move all generators under a common `fhir/` package | Easier imports and packaging |
| 🧪 Testing | Add pytest-based validation for JSON schema | Prevents invalid FHIR outputs |
| ☁️ AWS Integration | Use `boto3.resource('s3')` for managed sessions | Cleaner upload and retry management |
| 🧱 Metadata Tracking | Create `processed_files` DynamoDB table | Enables incremental Glue jobs |
| 🔄 CLI Interface | Add `argparse` flags (e.g., `--year`, `--upload`, `--count`) | Easier automation for CI/CD or AWS Lambda |

---

## 🧭 Example Future Structure

```
ingestion/
├── fhir/
│   ├── __init__.py
│   ├── patient.py
│   ├── encounter.py
│   ├── condition.py
│   ├── config.yaml
│   └── generator.py
│
├── io/
│   ├── local_writer.py
│   ├── s3_writer.py
│   ├── credential_loader.py
│
├── simulator/
│   ├── cms_simulator.py
│   ├── metrics.py
│
└── main.py
```

This refactor allows you to later deploy it as a **PyPI module** or use it within **AWS Glue Jobs** directly.
