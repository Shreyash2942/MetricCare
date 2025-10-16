import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

import boto3
import os
import shutil
from pyspark.sql import SparkSession

data_store = {"patients": [], "encounters": [], "conditions": []}
parquet_data_store = {"patients": [], "encounters": [], "conditions": []}

# Constants
bucket_name = "mc-de-4-takeo-project"
json_folder = "json"
processed_prefix_base = "processed_json"
s3 = boto3.client("s3")


# ---- Helper: List JSON files from S3 ----
def list_s3_json_files(bucket, prefix):
    paginator = s3.get_paginator("list_objects_v2")
    page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)

    json_files = []
    for page in page_iterator:
        for obj in page.get("Contents", []):
            key = obj["Key"]
            if key.endswith(".json") and not key.endswith("/"):
                json_files.append(key.split("/")[-1])  # just file name
    return json_files


# ---- Helper: Move S3 file ----
def move_s3_file(bucket, source_key, destination_key):
    s3.copy_object(
        Bucket=bucket,
        CopySource={'Bucket': bucket, 'Key': source_key},
        Key=destination_key
    )
    s3.delete_object(Bucket=bucket, Key=source_key)
    print(f"Moved: s3://{bucket}/{source_key} → s3://{bucket}/{destination_key}")


# ---- Main Conversion Function ----
def convert_into_parquet(spark):

    for folder_name in data_store:
        s3_prefix = f"{json_folder}/{folder_name}/"
        file_list = list_s3_json_files(bucket_name, s3_prefix)
        data_store[folder_name] = file_list

        for json_file_name in file_list:
            print("\nFile name:", json_file_name)

            s3_file_path = f"s3a://{bucket_name}/{s3_prefix}{json_file_name}"

            df = spark.read.option("multiline", "True").json(s3_file_path)

            # Save to S3 in Parquet format
            parquet_filename = json_file_name.replace(".json", ".parquet")
            s3_output_path = f"s3a://{bucket_name}/FHIR_data/{folder_name}/{parquet_filename}"
            df.write.mode("overwrite").parquet(s3_output_path)
            print(f"Written to S3: {s3_output_path}")

            parquet_data_store[folder_name].append(parquet_filename)

            # Move JSON file in S3 to "processed/" location
            source_key = f"{s3_prefix}{json_file_name}"
            destination_key = f"{processed_prefix_base}/{folder_name}/{json_file_name}"
            move_s3_file(bucket_name, source_key, destination_key)


sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

##calling parquet function
convert_into_parquet(spark)

job.commit()









