"""main_generate.py"""
import os

from generate_fhir_data import generate_patient_data
from aws_credential import aws_credential
from upload_to_S3 import save_json_to_s3
from save_json import save_json_to_local


# Configuration
num_patients=10
encounters_per_patient=4
condition_per_patient=3

def main():
    data_store=generate_patient_data(num_patients,encounters_per_patient,condition_per_patient)
    #save_json_to_local(data_store)
    print("\nSummary of Generated Files")
    # save_json_to_file(data_store)

    #AWS credential for uploading data into S3
    print("--------AWS Validation-----------")
    bucket_name,bucket_path,s3=aws_credential()

    save_json_to_s3(data_store,bucket_name,s3)
    ...

if __name__=="__main__":
    main()