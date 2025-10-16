# ⚙️ MetricCare – FHIR Configuration Module (`config_fhir.py`)

This module defines all **shared configuration constants** used across the FHIR data generation scripts in the MetricCare project.  
It centralizes hospital details, SNOMED codes, encounter settings, and version metadata — ensuring consistency across **Patient**, **Encounter**, **Condition**, and **Simulation** scripts.

---

## 🧩 Purpose

The `config_fhir.py` file acts as the **single source of truth** for FHIR dataset generation, ensuring that each resource (Patient, Encounter, Condition) uses:
- The same hospital and language references  
- CMS-aligned SNOMED CT condition codes  
- Standardized encounter types and departments  
- Version-controlled output settings  

This configuration is imported by:
- `generate_patient_fhir.py`
- `generate_encounter_fhir.py`
- `generate_condition_fhir.py`
- `cms_metric_data_simulator.py`

---

## 🏥 Hospital & Language Metadata

| Variable | Description |
|-----------|--------------|
| `HOSPITALS` | List of healthcare organizations available for `Patient.managingOrganization` and `Encounter.serviceProvider`. |
| `LANGUAGES` | Supported spoken languages for patient communication preferences. |

**Example:**
```python
HOSPITALS = [
    {"id": "org-metriccare", "name": "MetricCare General Hospital"},
    {"id": "org-northwell", "name": "Northwell Regional Hospital"},
    {"id": "org-mountainview", "name": "MountainView Healthcare"},
    {"id": "org-southern", "name": "Southern Valley Hospital"},
]
LANGUAGES = ["English", "Spanish", "French", "Hindi", "Mandarin", "Arabic"]
```

---

## ⚕️ Encounter Configuration

| Variable | Description |
|-----------|--------------|
| `ENCOUNTER_TYPES` | Encounter categories (Inpatient, Outpatient, Emergency, etc.) |
| `ENCOUNTER_STATUSES` | Valid FHIR encounter lifecycle statuses |
| `DEPARTMENTS` | Hospital departments for location and partitioning |
| `PARTICIPANT_ROLES` | Common staff roles involved in encounters |

**Used by:** `generate_encounter_fhir.py`

---

## 🧬 Condition Configuration (CMS-Aligned)

| Variable | Description |
|-----------|--------------|
| `SNOMED_CODES` | SNOMED CT codes aligned to CMS metrics (Mortality, HAI, Chronic, Readmission). |
| `CLINICAL_STATUSES` | Possible clinical statuses for a Condition resource. |
| `SEVERITIES` | Defines severity classification (mild, moderate, severe). |

### SNOMED Categories
| Category | Example Codes | Used For |
|-----------|----------------|-----------|
| ⚰️ **Death-related** | `419620001` | Mortality rate |
| 🦠 **Infection-related** | `91302008` (Sepsis), `233604007` (Pneumonia), `22298006` (Septicemia) | Hospital-Acquired Infection (HAI) |
| 💊 **Chronic conditions** | `44054006` (Diabetes), `42343007` (CHF), `13645005` (COPD) | Readmission & Comorbidity metrics |

**Used by:** `generate_condition_fhir.py`

---

## ⏱️ Time Settings

Defines the date simulation window and resource lifespan for temporal realism.

```python
TIME_SETTINGS = {
    "start_window": "-1y",    # Data within past year
    "max_encounter_days": 14, # Max hospital stay length
    "max_condition_days": 10  # Max duration of a condition
}
```

**Used by:** `cms_metric_data_simulator.py`

---

## 📦 Output Configuration

| Variable | Description |
|-----------|--------------|
| `JSON_DIR` | Local or S3 folder where generated FHIR JSON files are stored. |

Example:
```
s3://metriccare-dev/fhir_data/json/patient_20251012.json
```

---

## 🧾 Version Metadata

Version control for dataset reproducibility.

```python
VERSION_INFO = {
    "schema_version": "1.0",
    "author": "MetricCare Data Engineering Team",
    "project": "CMS Metrics Data Generator",
    "last_updated": "2025-10-12"
}
```

---

## 🔗 Integration Diagram

```
config_fhir.py
   ├── generate_patient_fhir.py      → Uses HOSPITALS, LANGUAGES
   ├── generate_encounter_fhir.py    → Uses ENCOUNTER_TYPES, STATUSES, DEPARTMENTS
   ├── generate_condition_fhir.py    → Uses SNOMED_CODES, CLINICAL_STATUSES
   └── cms_metric_data_simulator.py  → Uses TIME_SETTINGS, VERSION_INFO, JSON_DIR
```

---

## ✅ Example Usage

```python
from ingestion.script.config.config_fhir import SNOMED_CODES, HOSPITALS

print("Supported Hospitals:")
for hospital in HOSPITALS:
    print("-", hospital["name"])

print("\nDeath SNOMED Code:", SNOMED_CODES["419620001"])
```

**Output:**
```
Supported Hospitals:
- MetricCare General Hospital
- Northwell Regional Hospital
- MountainView Healthcare
- Southern Valley Hospital

Death SNOMED Code: Death
```

---

## 📚 Related Modules

| Script | Description |
|---------|--------------|
| `generate_patient_fhir.py` | Generates Patient FHIR JSON objects |
| `generate_encounter_fhir.py` | Generates Encounter FHIR JSON objects |
| `generate_condition_fhir.py` | Generates Condition FHIR JSON objects |
| `cms_metric_data_simulator.py` | Combines all three to simulate CMS metrics |
