"""
cms_metric_data_simulator_v4.py
-------------------------------------------------
MetricCare CMS Metric Data Simulator (Config-Integrated + Time-Series)
Generates FHIR-style Patient, Encounter, and Condition data
for Mortality, Infection, Readmission, and ALOS metrics.

✅ Features
- Integrates config_fhir.py for SNOMED codes, time settings, and metadata
- Flexible year selection (e.g., 2019–2025)
- Prevents unrealistic datasets (no pre-birth, negative intervals, or future deaths)
- Infection onset ≥ 48h after admission
- Readmission occurs 5–30 days after discharge
- Configurable metric percentages
-------------------------------------------------
"""

import json
import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Set
from faker import Faker

# ------------------------------
# Import shared configuration
# ------------------------------
from ingestion.script.config.config_fhir import (
    SNOMED_CODES,
    CLINICAL_STATUSES,
    SEVERITIES,
    TIME_SETTINGS,
    VERSION_INFO,
)

# ------------------------------
# Import FHIR generators
# ------------------------------
try:
    from patient.generate_patient_fhir import generate_patient
    from encounter.generate_encounter_fhir import generate_encounter
    from condition.generate_condition_fhir import generate_condition
except Exception:
    from generate_patient_fhir import generate_patient  # type: ignore
    from generate_encounter_fhir import generate_encounter  # type: ignore
    from generate_condition_fhir import generate_condition  # type: ignore

# ------------------------------
# Optional AWS helpers
# ------------------------------
try:
    from aws_credential import aws_credential
    from upload_to_S3 import save_json_to_s3
    AWS_AVAILABLE = True
except Exception:
    AWS_AVAILABLE = False

from fhir.resources.condition import Condition as FHIRCondition
from fhir.resources.reference import Reference
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.annotation import Annotation

fake = Faker()

# ------------------------------------------------------------------
# Utilities
# ------------------------------------------------------------------
def fmt(dt: datetime) -> str:
    """FHIR-style ISO format with ms and Z suffix."""
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def random_date_in_year(year: int) -> datetime:
    start = datetime(year, 1, 1, tzinfo=timezone.utc)
    end = datetime(year + 1, 1, 1, tzinfo=timezone.utc)
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds()) - 1))


def clamp_after_birth(birth_date_iso: str, candidate_dt: datetime, min_age_years: int = 18) -> datetime:
    birth = datetime.fromisoformat(birth_date_iso)
    if birth.tzinfo is None:
        birth = birth.replace(tzinfo=timezone.utc)
    min_dt = birth + timedelta(days=min_age_years * 365)
    return candidate_dt if candidate_dt >= min_dt else min_dt + timedelta(days=random.randint(0, 365))


def build_condition(patient_id: str, encounter_id: str, code: str, display: str,
                    category: str, metric: str,
                    onset: datetime, abatement: datetime) -> FHIRCondition:
    annotations = [
        Annotation(authorString="category", text=category),
        Annotation(authorString="type", text=display),
        Annotation(authorString="metric", text=metric),
        Annotation(authorString="severity", text=random.choice(SEVERITIES)),
        Annotation(authorString="version", text=VERSION_INFO["schema_version"]),
    ]
    return FHIRCondition(
        resourceType="Condition",
        id=str(uuid.uuid4()),
        subject=Reference(reference=f"Patient/{patient_id}"),
        encounter=Reference(reference=f"Encounter/{encounter_id}"),
        clinicalStatus=CodeableConcept(text=random.choice(CLINICAL_STATUSES)),
        code=CodeableConcept(coding=[{"code": code, "display": display}], text=display),
        onsetDateTime=fmt(onset),
        abatementDateTime=fmt(abatement),
        note=annotations,
    )


def pick_indices(total: int, pct: float) -> Set[int]:
    count = max(0, min(total, round(total * (pct / 100.0))))
    return set(random.sample(range(total), count)) if count > 0 else set()

# ------------------------------------------------------------------
# Metric Simulations
# ------------------------------------------------------------------
def simulate_mortality(patient: dict, data_store: Dict, summary: Dict, year: int):
    patient_id = patient["id"]
    adm1 = random_date_in_year(year)
    dis1 = adm1 + timedelta(days=random.randint(1, TIME_SETTINGS.get("max_encounter_days", 7)))
    enc1 = generate_encounter(patient_id)
    enc1.actualPeriod.start = adm1
    enc1.actualPeriod.end = dis1
    data_store["encounters"].append(json.loads(enc1.model_dump_json(exclude_none=True)))

    adm2 = dis1 + timedelta(days=random.randint(5, 30))
    dis2 = adm2 + timedelta(days=random.randint(1, 7))
    enc2 = generate_encounter(patient_id)
    enc2.actualPeriod.start = adm2
    enc2.actualPeriod.end = dis2
    data_store["encounters"].append(json.loads(enc2.model_dump_json(exclude_none=True)))

    death_dt = dis2 + timedelta(days=random.randint(1, 30))
    death_dt = clamp_after_birth(patient["birthDate"], death_dt)
    if death_dt.year > datetime.now().year:
        death_dt = datetime(year, 12, 31, tzinfo=timezone.utc)

    cond = build_condition(patient_id, enc2.id, "419620001", SNOMED_CODES["419620001"],
                           "Death", "Mortality Rate (30-day)", dis2, death_dt)
    data_store["conditions"].append(json.loads(cond.model_dump_json(exclude_none=True)))
    patient["deceasedDateTime"] = fmt(death_dt)

    summary["patients"]["mortality"].add(patient_id)
    summary["conditions"]["mortality"] += 1


def simulate_infection(patient: dict, data_store: Dict, summary: Dict, year: int):
    patient_id = patient["id"]
    adm = random_date_in_year(year)
    los = random.randint(3, TIME_SETTINGS.get("max_encounter_days", 10))
    dis = adm + timedelta(days=los)
    enc = generate_encounter(patient_id)
    enc.actualPeriod.start = adm
    enc.actualPeriod.end = dis
    data_store["encounters"].append(json.loads(enc.model_dump_json(exclude_none=True)))

    infection_codes = {k: v for k, v in SNOMED_CODES.items() if k in ["91302008", "233604007", "68566005", "34014006", "22298006"]}
    code, name = random.choice(list(infection_codes.items()))
    onset = adm + timedelta(hours=random.randint(48, los * 24 - 12))
    abatement = min(onset + timedelta(days=random.randint(1, TIME_SETTINGS.get("max_condition_days", 5))), dis)

    cond = build_condition(patient_id, enc.id, code, name, "Infection", "HAI Rate", onset, abatement)
    data_store["conditions"].append(json.loads(cond.model_dump_json(exclude_none=True)))

    summary["patients"]["infection"].add(patient_id)
    summary["conditions"]["infection"] += 1


def simulate_readmission(patient: dict, data_store: Dict, summary: Dict, year: int):
    patient_id = patient["id"]
    adm1 = random_date_in_year(year)
    dis1 = adm1 + timedelta(days=random.randint(2, 6))
    adm2 = dis1 + timedelta(days=random.randint(5, 30))
    dis2 = adm2 + timedelta(days=random.randint(2, 6))
    enc1 = generate_encounter(patient_id)
    enc2 = generate_encounter(patient_id)
    enc1.actualPeriod.start = adm1
    enc1.actualPeriod.end = dis1
    enc2.actualPeriod.start = adm2
    enc2.actualPeriod.end = dis2
    data_store["encounters"] += [json.loads(enc1.model_dump_json(exclude_none=True)),
                                 json.loads(enc2.model_dump_json(exclude_none=True))]

    cond = build_condition(patient_id, enc2.id, "R-READMIT", "30-day Readmission",
                           "Readmission", "Readmission Rate (30-day)", adm2, dis2)
    data_store["conditions"].append(json.loads(cond.model_dump_json(exclude_none=True)))

    summary["patients"]["readmission"].add(patient_id)
    summary["conditions"]["readmission"] += 1


def simulate_alos(patient: dict, data_store: Dict, summary: Dict, year: int):
    patient_id = patient["id"]
    for _ in range(random.randint(1, 3)):
        adm = random_date_in_year(year)
        dis = adm + timedelta(days=random.randint(1, TIME_SETTINGS.get("max_encounter_days", 14)))
        enc = generate_encounter(patient_id)
        enc.actualPeriod.start = adm
        enc.actualPeriod.end = dis
        data_store["encounters"].append(json.loads(enc.model_dump_json(exclude_none=True)))
    summary["patients"]["alos"].add(patient_id)

# ------------------------------------------------------------------
# Dataset Generator
# ------------------------------------------------------------------
def generate_cms_dataset(num_patients: int,
                         base_year: int = datetime.now().year,
                         mortality_pct: float = 10.0,
                         infection_pct: float = 20.0,
                         readmission_pct: float = 15.0,
                         alos_pct: float = 100.0) -> Dict[str, list]:

    data_store = {"patients": [], "encounters": [], "conditions": []}
    summary = {
        "patients": {"mortality": set(), "infection": set(), "readmission": set(), "alos": set()},
        "conditions": {"mortality": 0, "infection": 0, "readmission": 0},
    }

    for _ in range(num_patients):
        p = generate_patient()
        data_store["patients"].append(json.loads(p.model_dump_json(exclude_none=True)))

    idx_mortality = pick_indices(num_patients, mortality_pct)
    idx_infection = pick_indices(num_patients, infection_pct)
    idx_readmit = pick_indices(num_patients, readmission_pct)
    idx_alos = pick_indices(num_patients, alos_pct)

    for i, patient in enumerate(data_store["patients"]):
        if i in idx_alos:
            simulate_alos(patient, data_store, summary, base_year)
        if i in idx_infection:
            simulate_infection(patient, data_store, summary, base_year)
        if i in idx_readmit:
            simulate_readmission(patient, data_store, summary, base_year)
        if i in idx_mortality:
            simulate_mortality(patient, data_store, summary, base_year)

    print("\n─────────────────────────── SUMMARY ───────────────────────────")
    print(f"Year simulated:           {base_year}")
    print(f"Total patients simulated: {len(data_store['patients'])}")
    print(f"Total encounters:         {len(data_store['encounters'])}")
    print(f"Total conditions:         {len(data_store['conditions'])}")
    print("───────────────────────────────────────────────────────────────")

    for key, val in summary["patients"].items():
        print(f"{key.capitalize():<12}: {len(val)}")

    return data_store

# ------------------------------------------------------------------
# CLI Entry Point
# ------------------------------------------------------------------
def main():
    print("\nMetricCare — CMS Metric Dataset Simulator (v4 – Config Integrated)")
    print("=====================================================================")
    try:
        num_patients = int(input("Enter number of patients (e.g., 500): ").strip())
    except Exception:
        num_patients = 100

    try:
        base_year = int(input("Enter year to simulate (e.g., 2022): ").strip())
    except Exception:
        base_year = datetime.now().year

    def get_pct(prompt, default):
        try:
            val = input(f"{prompt} [{default}%]: ").strip()
            return float(val) if val != "" else default
        except Exception:
            return default

    mortality_pct = get_pct("Mortality percentage", 10.0)
    infection_pct = get_pct("Infection percentage", 20.0)
    readmission_pct = get_pct("Readmission percentage", 15.0)
    alos_pct = get_pct("ALOS percentage", 100.0)

    dataset = generate_cms_dataset(
        num_patients=num_patients,
        base_year=base_year,
        mortality_pct=mortality_pct,
        infection_pct=infection_pct,
        readmission_pct=readmission_pct,
        alos_pct=alos_pct
    )

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    # filename = f"cms_dataset_{base_year}_{ts}.json"
    # with open(filename, "w", encoding="utf-8") as f:
    #     json.dump(dataset, f, ensure_ascii=False)
    # print(f"\n Dataset saved: {filename}")

    if AWS_AVAILABLE:
        try:
            bucket_name, bucket_path, s3_client = aws_credential()
            print("\nUploading dataset to AWS S3...")
            save_json_to_s3(dataset, bucket_name, s3_client)
            print(f"Upload complete: s3://{bucket_name}/{bucket_path}")
        except Exception as e:
            print(f"[WARN] AWS upload skipped or failed: {e}")


if __name__ == "__main__":
    main()
