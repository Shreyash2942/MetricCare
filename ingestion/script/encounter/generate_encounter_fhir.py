import json
import pprint
import uuid
import random
from faker import Faker
from datetime import timedelta, timezone

from fhir.resources.encounter import Encounter as FHIREncounter
from fhir.resources.encounter import EncounterParticipant, EncounterLocation
from fhir.resources.period import Period
from fhir.resources.reference import Reference
from fhir.resources.codeableconcept import CodeableConcept

# 🧱 Import shared config file
from ingestion.script.config.config_fhir import (
    ENCOUNTER_TYPES,
    ENCOUNTER_STATUSES,
    PARTICIPANT_ROLES,
    DEPARTMENTS,
    HOSPITALS,
    VERSION_INFO
)

fake = Faker()


def format_fhir_datetime(dt):
    """Format datetime consistently with milliseconds and Z suffix."""
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def generate_encounter(patient_id: str) -> FHIREncounter:
    """Generates a FHIR-compliant Encounter resource for a given patient."""

    # ----------------------------
    # Temporal fields (Admission & Discharge)
    # ----------------------------
    admission = fake.date_time_this_decade(tzinfo=timezone.utc)
    discharge = admission + timedelta(days=random.randint(1, 7))

    # ----------------------------
    # Encounter participant (attending or consulting clinician)
    # ----------------------------
    participant = EncounterParticipant(
        type=[CodeableConcept(text=random.choice(PARTICIPANT_ROLES))],
        period=Period(
            start=format_fhir_datetime(admission),
            end=format_fhir_datetime(discharge)
        ),
        actor=Reference(reference=f"Practitioner/{uuid.uuid4()}")
    )

    # ----------------------------
    # CMS-aligned encounter attributes
    # ----------------------------
    encounter_type = random.choice(ENCOUNTER_TYPES)
    department = random.choice(DEPARTMENTS)
    selected_org = random.choice(HOSPITALS)

    location = EncounterLocation(
        location=Reference(display=department),
        period=Period(
            start=format_fhir_datetime(admission),
            end=format_fhir_datetime(discharge)
        )
    )

    # ----------------------------
    # Construct FHIR Encounter resource
    # ----------------------------
    encounter = FHIREncounter(
        resourceType="Encounter",
        id=str(uuid.uuid4()),
        status=random.choice(ENCOUNTER_STATUSES),
        subject=Reference(reference=f"Patient/{patient_id}"),
        actualPeriod=Period(start=admission, end=discharge),
        type=[CodeableConcept(text=encounter_type)],
        participant=[participant],
        location=[location],
        serviceProvider=Reference(
            reference=f"Organization/{selected_org['id']}",
            display=selected_org["name"]
        )
    )

    return encounter


# ----------------------------
# Example standalone execution
# ----------------------------
if __name__ == "__main__":
    encounter = generate_encounter(str(uuid.uuid4()))
    print("✅ Patient 'Encounter' Data:\n")
    pprint.pprint(json.loads(encounter.model_dump_json(exclude_none=True)))
