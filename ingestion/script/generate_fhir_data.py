"""generate_fhir_data.py"""
import json
import random
from datetime import datetime
from typing import List, Dict
from faker import Faker

# Import your three generator modules
from patient.generate_patient_fhir import generate_patient
from encounter.generate_encounter_fhir import generate_encounter
from condition.generate_condition_fhir import generate_condition

fake = Faker()

# Timestamp for filenames
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# Data store for all generated resources
data_store: Dict[str, List[Dict]] = {
    "patients": [],
    "encounters": [],
    "conditions": []
}


def generate_patient_data(num_patients: int, encounter_count: int, condition_count: int):
    """
    Generate linked FHIR resources (Patient, Encounter, Condition)
    for the specified number of patients.
    """
    for _ in range(num_patients):
        # ----------------------------
        # Generate Patient
        # ----------------------------
        patient = generate_patient()
        patient_id = patient.id
        data_store["patients"].append(json.loads(patient.model_dump_json(exclude_none=True)))

        # ----------------------------
        # Generate Encounters (linked to patient)
        # ----------------------------
        encounter_ids = []
        enc_count = random.randint(1, encounter_count)
        for _ in range(enc_count):
            encounter = generate_encounter(patient_id)
            encounter_ids.append(encounter.id)
            data_store["encounters"].append(json.loads(encounter.model_dump_json(exclude_none=True)))

        # ----------------------------
        # Generate Conditions (linked to patient & random encounter)
        # ----------------------------
        con_count = random.randint(1, condition_count)
        for _ in range(con_count):
            if encounter_ids:
                selected_encounter_id = random.choice(encounter_ids)
            else:
                # fallback if no encounter
                selected_encounter_id = str(fake.uuid4())

            condition = generate_condition(patient_id, selected_encounter_id)
            data_store["conditions"].append(json.loads(condition.model_dump_json(exclude_none=True)))

    return data_store


if __name__ == "__main__":
    # Example run: 5 patients, up to 3 encounters & 4 conditions each
    results = generate_patient_data(num_patients=5, encounter_count=3, condition_count=4)

    # Write each resource type to file for easy upload to S3
    for resource_type, records in results.items():
        file_name = f"{resource_type}_{timestamp}.json"
        print(f"Generated {len(records)} {resource_type} → {file_name}")
