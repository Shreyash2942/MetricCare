import sys, boto3, json, logging
from datetime import datetime
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    current_timestamp, col, input_file_name, concat, lit, date_format
)

# ----------------------------
# Setup Logging
# ----------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ----------------------------
# Glue job params
# ----------------------------
args = getResolvedOptions(
    sys.argv,
    ['JOB_NAME', 'bucket_name', 'config_key', 'job_section', 'env', 'database_name', 'meta_table']
)

bucket_name   = args['bucket_name']
config_key    = args['config_key']
job_section   = args['job_section']
env           = args['env']
database_name = args['database_name']
meta_table    = args['meta_table']
job_name      = args['JOB_NAME']

# ----------------------------
# Load config.json from S3
# ----------------------------
try:
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket_name, Key=config_key)
    config = json.loads(response['Body'].read().decode('utf-8'))

    job_config = config[job_section]
    input_location = job_config["input_path"]
    table_name = job_config["table"]
    log_table = job_config["log_table"]
    output_location = job_config["output_path"]
    log_location = job_config["log_path"]

    input_path = f"s3://{bucket_name}/{input_location}"
    output_path = f"s3://{bucket_name}/{output_location}"
    log_path = f"s3://{bucket_name}/{log_location}"

    logger.info(f"Loaded config for {job_section} from s3://{bucket_name}/{config_key}")

except Exception as e:
    logger.error(f"Failed to load config: {e}", exc_info=True)
    raise

# ----------------------------
# Glue boilerplate
# ----------------------------
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(job_name, args)

# ----------------------------
# DynamoDB Setup
# ----------------------------
dynamodb = boto3.resource("dynamodb")
ddb_table = dynamodb.Table(meta_table)

def get_processed_files(dataset: str):
    resp = ddb_table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key("dataset").eq(dataset)
    )
    return [item["filename"] for item in resp.get("Items", [])]

def update_processed_files(dataset: str, files: list):
    now = datetime.utcnow().isoformat()
    with ddb_table.batch_writer() as batch:
        for f in files:
            batch.put_item(Item={
                "dataset": dataset,
                "filename": f,
                "date": now
            })

# ----------------------------
# Helper functions
# ----------------------------
def list_all_s3_files(bucket: str, prefix: str) -> list:
    """Return all S3 object URIs under a given prefix."""
    s3 = boto3.client("s3")
    resp = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return [f"s3://{bucket}/{obj['Key']}" for obj in resp.get("Contents", [])]

def hudi_options(table_name, database_name, recordkey, precombine, partition_key, output_path):
    """HUDI write options"""
    return {
        "hoodie.table.name": table_name,
        "hoodie.database.name": database_name,
        "hoodie.datasource.write.storage.type": "COPY_ON_WRITE",
        "hoodie.datasource.write.operation": "upsert",
        "hoodie.datasource.write.recordkey.field": recordkey,
        "hoodie.datasource.write.precombine.field": precombine,
        "hoodie.datasource.write.partitionpath.field": partition_key,
        "hoodie.datasource.write.hive_style_partitioning": "true",
        "hoodie.datasource.hive_sync.enable": "true",
        "hoodie.datasource.hive_sync.use_glue_catalog": "true",
        "hoodie.datasource.hive_sync.database": database_name,
        "hoodie.datasource.hive_sync.table": table_name,
        "hoodie.datasource.hive_sync.partition_fields": partition_key,
        "hoodie.datasource.hive_sync.mode": "hms",
        "hoodie.datasource.hive_sync.use_jdbc": "false",
        "path": output_path
    }

def write_dataframe(df: DataFrame, options: dict, mode: str = "append"):
    """Writes DataFrame into Hudi table"""
    table = options["hoodie.table.name"]
    logger.info(f"▶ Writing table {table} to {options['path']}")
    df.write.format("hudi").options(**options).mode(mode).save()
    logger.info(f" Successfully wrote table {table}")

# ----------------------------
# Main Processing
# ----------------------------
try:
    all_files = list_all_s3_files(bucket_name, input_location)
    processed_files = get_processed_files(table_name)
    new_files = [f for f in all_files if f not in processed_files]

    if not new_files:
        logger.info("No new encounter files to process. Exiting job.")
    else:
        logger.info(f"Found {len(new_files)} new encounter files")

        # Read encounter JSONs
        df = (
            spark.read.option("multiLine", "True").json(new_files)
            .withColumn("sourcename", input_file_name())
            .withColumn("precombine_ts", current_timestamp())
        )

        # Flatten FHIR Encounter structure
        flat_df = df.select(
            col("id").alias("encounter_id"),
            col("status"),
            col("type")[0]["text"].alias("encounter_type"),
            col("subject")["reference"].alias("patient_ref"),
            col("actualPeriod")["start"].alias("admission_time"),
            col("actualPeriod")["end"].alias("discharge_time"),
            col("location")[0]["location"]["display"].alias("department"),
            col("participant")[0]["type"][0]["text"].alias("participant_role"),
            col("participant")[0]["actor"]["reference"].alias("practitioner_ref"),
            col("serviceProvider")["display"].alias("hospital_name"),
            col("sourcename"),
            col("precombine_ts")
        ).dropDuplicates(["encounter_id"])

        # Write Encounter data to Hudi
        encounter_hudi_conf = hudi_options(
            table_name=table_name,
            database_name=database_name,
            recordkey="encounter_id",
            precombine="precombine_ts",
            partition_key="hospital_name",
            output_path=output_path
        )
        write_dataframe(flat_df, encounter_hudi_conf)

        # Log metadata table
        timestamp_df = (
            spark.range(1)
            .withColumn("record_id", concat(lit(f"{table_name}/"), date_format(current_timestamp(), "yyyyMMdd_HHmmss")))
            .withColumn("tablename", lit(table_name))
            .withColumn("tabletype", lit("bronzeencounter"))
            .withColumn("lastprocesstime", current_timestamp())
            .withColumn("column_count", lit(len(flat_df.columns)))
        )

        log_conf = hudi_options(
            table_name=log_table,
            database_name=database_name,
            recordkey="record_id",
            precombine="lastprocesstime",
            partition_key="tabletype",
            output_path=log_path
        )
        write_dataframe(timestamp_df, log_conf)

        # Update DynamoDB
        update_processed_files(table_name, new_files)
        logger.info(f"✅ Encounter Bronze Job {job_name} completed successfully.")

except Exception as e:
    logger.error(f"Glue job {job_name} failed: {e}", exc_info=True)
    raise
finally:
    job.commit()
    logger.info("Glue job committed ")
