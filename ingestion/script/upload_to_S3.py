"""upload_to_S3.py"""
import json
from datetime import datetime
from typing import Dict, List
import os
from botocore.exceptions import ClientError, NoCredentialsError

json_dir="fhir_data/json"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

def save_json_to_s3(data_store,bucket_name,s3) -> None:
    # create directory and subdirectory
    for category in data_store:
        print(f"This {category} saved in following location")
        print(f"Location : {bucket_name}/{json_dir}/{category}/")
        json_s3(
            data_store[category],
            category,
            f"{category}_{timestamp}.json",
            bucket_name,
            s3
        )
def json_s3(data: List[Dict], folder_name: str, filename: str,bucket_name,s3_client):
    """Saves JSON data to a specified subfolder and records file metadata."""

    bucket_path=os.path.join(json_dir,folder_name,filename)

    try:
        json_data = json.dumps(data, indent=2)
        s3_key = bucket_path.strip('/').replace("\\", "/")
        s3_client.put_object(Body=json_data, Bucket=bucket_name, Key=s3_key)

        #file_size_kb = round(os.path.getsize(bucket_path) / 1024, 2)
        print(f"File: {os.path.basename(bucket_path)}")
        #print(f"Size: {file_size_kb} KB \n")
        print(f"Data uploaded successfully to s3://{bucket_name}/{s3_key}")

    except NoCredentialsError:
        print("AWS credentials not found.")
    except ClientError as e:
        print(f"Failed to upload data: {e}")








