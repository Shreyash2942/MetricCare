import json
import pprint
import uuid
import random
from faker import Faker
from datetime import datetime, timedelta, timezone, date

from fhir.resources.patient import Patient as FHIRPatient
from fhir.resources.address import Address
from fhir.resources.identifier import Identifier
from fhir.resources.meta import Meta
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.reference import Reference

# 🧱 Import shared config file
from ingestion.script.config.config_fhir import HOSPITALS, LANGUAGES, VERSION_INFO

fake = Faker()
DECEASED = [True, False, False]  # ~33% chance deceased

def generate_patient() -> FHIRPatient:
    """Generate a minimal FHIR-compliant Patient resource for CMS metric simulation."""
    patient_id = str(uuid.uuid4())
    birth_date = fake.date_of_birth(minimum_age=18, maximum_age=90)

    # ----------------------------
    # Deceased status simulation
    # ----------------------------
    is_deceased = random.choice(DECEASED)
    deceased_date = None

    if is_deceased:
        max_life_span_days = (date.today() - birth_date).days
        if max_life_span_days > 0:
            death_offset = random.randint(1, max_life_span_days)
            death_date = birth_date + timedelta(days=death_offset)
            deceased_date = datetime.combine(
                death_date, datetime.min.time(), tzinfo=timezone.utc
            ).isoformat()

    # ----------------------------
    # Random language & hospital assignment
    # ----------------------------
    selected_language = random.choice(LANGUAGES)
    selected_org = random.choice(HOSPITALS)

    # ----------------------------
    # Build FHIR Patient resource
    # ----------------------------
    patient = FHIRPatient(
        resourceType="Patient",
        id=patient_id,
        active=True,
        meta=Meta(
            versionId=VERSION_INFO["schema_version"],
            lastUpdated=datetime.now(timezone.utc).isoformat()
        ),
        identifier=[
            Identifier(
                use="usual",
                type=CodeableConcept(text="Medical Record Number"),
                system="MetricCare-MRN",
                value=f"MC-{random.randint(100000, 999999)}"
            )
        ],
        gender=random.choice(["male", "female"]),
        birthDate=birth_date.isoformat(),
        address=[
            Address(
                use="home",
                type="both",
                line=[fake.street_address()],
                city=fake.city(),
                state=fake.state_abbr(),
                country="USA"
            )
        ],
        communication=[
            {"language": {"text": selected_language}, "preferred": True}
        ],
        managingOrganization=Reference(
            reference=f"Organization/{selected_org['id']}",
            display=selected_org["name"]
        ),
        deceasedDateTime=deceased_date if is_deceased else None
    )

    return patient


# ----------------------------
# Example standalone execution
# ----------------------------
if __name__ == "__main__":
    patient = generate_patient()
    print("✅ CMS-Focused FHIR Patient Resource:\n")
    pprint.pprint(json.loads(patient.model_dump_json(exclude_none=True)))

    # Suggested S3 filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"patient_{timestamp}.json"
    print(f"\nSuggested file path: s3://metriccare-dev/bronze/patient/{file_name}")
