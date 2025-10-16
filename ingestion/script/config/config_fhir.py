"""
config_fhir.py
-------------------------------------
Shared configuration file for FHIR resource generation (MetricCare Project).
Used by:
  - generate_patient_fhir.py
  - generate_encounter_fhir.py
  - generate_condition_fhir.py
  - cms_metric_data_simulator.py
"""

# 🏥 Hospital Organizations (shared across Patient & Encounter)
HOSPITALS = [
    {"id": "org-metriccare", "name": "MetricCare General Hospital"},
    {"id": "org-northwell", "name": "Northwell Regional Hospital"},
    {"id": "org-mountainview", "name": "MountainView Healthcare"},
    {"id": "org-southern", "name": "Southern Valley Hospital"},
]

# 🌎 Supported Languages (used in Patient resource)
LANGUAGES = ["English", "Spanish", "French", "Hindi", "Mandarin", "Arabic"]

# ⚕️ Encounter-related fields
ENCOUNTER_TYPES = ["Inpatient", "Outpatient", "Emergency", "Home", "Virtual"]
ENCOUNTER_STATUSES = [
    "planned", "arrived", "in-progress", "onleave", "finished",
    "cancelled", "entered-in-error", "unknown"
]
DEPARTMENTS = ["ICU", "Emergency", "Cardiology", "General Ward", "Surgery"]
PARTICIPANT_ROLES = [
    "attending physician", "consulting physician", "referring physician", "nurse", "therapist"
]

# 🧬 CMS-aligned SNOMED Codes (for Condition resource)
# These codes drive metrics like Mortality, Infection, Readmission, and Chronic Comorbidity.
SNOMED_CODES = {
    # ⚰️ Death-related (Mortality metric)
    "419620001": "Death",

    # 🦠 Infection-related (HAI metrics)
    "91302008": "Sepsis",
    "233604007": "Pneumonia",
    "68566005": "Urinary tract infection",
    "34014006": "Clostridium difficile colitis",
    "22298006": "Septicemia",

    # 💊 Chronic / Non-infection conditions (for comorbidity & readmission metrics)
    "44054006": "Diabetes mellitus",
    "42343007": "Congestive heart failure",
    "13645005": "Chronic obstructive pulmonary disease",
    "38341003": "Hypertension",
    "195967001": "Asthma"
}

# 🩺 Clinical metadata fields
CLINICAL_STATUSES = ["active", "resolved", "recurrence", "inactive", "remission"]
SEVERITIES = ["mild", "moderate", "severe"]

# ⚙️ Global Time Configuration (optional)
# Defines the relative simulation window for all resource timestamps.
TIME_SETTINGS = {
    "start_window": "-1y",    # simulate data within the past year
    "max_encounter_days": 14, # max duration of hospital stay
    "max_condition_days": 10  # max duration for a clinical condition
}

# 📦 JSON output and S3 folder structure
JSON_DIR = "fhir_data/json"   # base local folder or S3 prefix for all generated datasets

# 🧾 Metadata for file versioning
VERSION_INFO = {
    "schema_version": "1.0",
    "author": "MetricCare Data Engineering Team",
    "project": "CMS Metrics Data Generator",
    "last_updated": "2025-10-12"
}
