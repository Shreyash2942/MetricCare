import json
import pprint
import uuid
import random
from faker import Faker
from datetime import timedelta, timezone

from fhir.resources.condition import Condition as FHIRCondition
from fhir.resources.reference import Reference
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.annotation import Annotation

#  Import shared configuration
from ingestion.script.config.config_fhir import SNOMED_CODES, CLINICAL_STATUSES, SEVERITIES, VERSION_INFO

fake = Faker()


def format_fhir_datetime(dt):
    """Format datetime consistently with milliseconds and Z suffix."""
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def generate_condition(patient_id: str, encounter_id: str) -> FHIRCondition:
    """Generates a FHIR-compliant Condition resource for a given patient encounter."""
    onset = fake.date_time_this_year(tzinfo=timezone.utc)
    abatement = onset + timedelta(days=random.randint(1, 5))

    # ----------------------------
    # Randomly pick SNOMED condition
    # ----------------------------
    code, name = random.choice(list(SNOMED_CODES.items()))

    # ----------------------------
    # Categorize by CMS metric type
    # ----------------------------
    if code == "419620001":
        category = "Death"
        metric_type = "Mortality Rate"
    elif code in ["91302008", "233604007", "68566005", "34014006", "22298006"]:
        category = "Infection"
        metric_type = "HAI Rate"
    elif code in ["44054006", "42343007", "13645005", "38341003", "195967001"]:
        category = "Chronic"
        metric_type = "Readmission/Comorbidity"
    else:
        category = "General"
        metric_type = "Non-Infection Analytics"

    # ----------------------------
    # Structured annotations (ICD-style metadata)
    # ----------------------------
    note_annotations = [
        Annotation(authorString="category", text=category),
        Annotation(authorString="type", text=name),
        Annotation(authorString="metric", text=metric_type),
        Annotation(authorString="severity", text=random.choice(SEVERITIES)),
        Annotation(authorString="version", text=VERSION_INFO["schema_version"])
    ]

    # ----------------------------
    # Construct the Condition resource
    # ----------------------------
    condition = FHIRCondition(
        resourceType="Condition",
        id=str(uuid.uuid4()),
        subject=Reference(reference=f"Patient/{patient_id}"),
        encounter=Reference(reference=f"Encounter/{encounter_id}"),
        clinicalStatus=CodeableConcept(text=random.choice(CLINICAL_STATUSES)),
        code=CodeableConcept(
            coding=[{"code": code, "display": name}],
            text=name
        ),
        onsetDateTime=format_fhir_datetime(onset),
        abatementDateTime=format_fhir_datetime(abatement),
        note=note_annotations
    )

    return condition


# ----------------------------
# Example standalone execution
# ----------------------------
if __name__ == "__main__":
    patient_id = uuid.uuid4()
    encounter_id = uuid.uuid4()

    condition = generate_condition(patient_id, encounter_id)
    print(" Generated Patient Condition FHIR Data:\n")
    pprint.pprint(json.loads(condition.model_dump_json(exclude_none=True)))
