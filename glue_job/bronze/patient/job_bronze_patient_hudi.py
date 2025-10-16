import sys, json, boto3, logging
from datetime import datetime

from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    current_timestamp, col, to_date, input_file_name,
    lit, concat, date_format, when
)

# ----------------------------
# Logging Setup
# ----------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ----------------------------
# Glue Job Params
# ----------------------------
args = getResolvedOptions(
    sys.argv,
    ['JOB_NAME', 'bucket_name', 'config_key', 'job_section', 'env', 'database_name', 'meta_table']
)
job_name = args['JOB_NAME']
bucket_name = args['bucket_name']
config_key = args['config_key']
job_section = args['job_section']       # "patients"
env = args['env']
database_name = args['database_name']
meta_table = args['meta_table']

# ----------------------------
# Load Config from S3
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

    logger.info(f"✅ Loaded config for section={job_section} from s3://{bucket_name}/{config_key}")

except Exception as e:
    logger.error(f"❌ Failed to load config: {e}", exc_info=True)
    raise

# ----------------------------
# Glue Context
# ----------------------------
sc = SparkContext.getOrCreate()
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
# Helper Functions
# ----------------------------
def list_all_s3_files(bucket: str, prefix: str) -> list:
    """List all JSON files in the given S3 prefix"""
    s3 = boto3.client("s3")
    resp = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return [f"s3://{bucket}/{obj['Key']}" for obj in resp.get("Contents", [])]

def hudi_options(table_name: str, database_name: str, recordkey: str,
                 precombine: str, partition_key: str, output_path: str) -> dict:
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
    table = options["hoodie.table.name"]
    logger.info(f"▶ Writing table {table} to {options['path']}")
    df.write.format("hudi").options(**options).mode(mode).save()
    logger.info(f"✅ Successfully wrote table {table}")

# ----------------------------
# Main Logic
# ----------------------------
try:
    all_files = list_all_s3_files(bucket_name, input_location)
    processed_files = get_processed_files(table_name)
    new_files = [f for f in all_files if f not in processed_files]

    if not new_files:
        logger.info("No new patient files to process. Exiting job.")
    else:
        logger.info(f"Found {len(new_files)} new patient files")

        # Read JSON files
        df = (
            spark.read.option("multiLine", "True").json(new_files)
            .withColumn("birthDate", to_date("birthDate", "yyyy-MM-dd"))
            .withColumn("sourcename", input_file_name())
            .withColumn("precombine_ts", current_timestamp())
        )

        # Handle deceased patients
        if "deceasedDateTime" in df.columns:
            df = df.withColumn(
                "is_deceased",
                when(col("deceasedDateTime").isNotNull(), lit(True)).otherwise(lit(False))
            )
        else:
            df = df.withColumn("deceasedDateTime", lit(None).cast("string")) \
                   .withColumn("is_deceased", lit(False))

        # Flatten FHIR Patient schema
        flat_df = df.select(
            col("id").alias("patient_id"),
            col("gender"),
            col("birthDate"),
            col("communication")[0]["language"]["text"].alias("language"),
            col("managingOrganization")["display"].alias("hospital_name"),
            col("is_deceased"),
            col("deceasedDateTime"),
            col("sourcename"),
            col("precombine_ts")
        ).dropDuplicates(["patient_id"])

        # Write Patient data to Hudi
        patient_hudi_conf = hudi_options(
            table_name=table_name,
            database_name=database_name,
            recordkey="patient_id",
            precombine="precombine_ts",
            partition_key="hospital_name",
            output_path=output_path
        )
        write_dataframe(flat_df, patient_hudi_conf)

        # Log table entry
        timestamp_df = (
            spark.range(1)
            .withColumn("record_id", concat(lit(f"{table_name}/"), date_format(current_timestamp(), "yyyyMMdd_HHmmss")))
            .withColumn("tablename", lit(table_name))
            .withColumn("tabletype", lit("bronze"))
            .withColumn("lastprocesstime", current_timestamp())
            .withColumn("column_count", lit(len(flat_df.columns)))
        )

        log_hudi_conf = hudi_options(
            table_name=log_table,
            database_name=database_name,
            recordkey="record_id",
            precombine="lastprocesstime",
            partition_key="tabletype",
            output_path=log_path
        )
        write_dataframe(timestamp_df, log_hudi_conf)

        # Update DynamoDB processed file list
        update_processed_files(table_name, new_files)
        logger.info(f"✅ Glue job {job_name} completed successfully.")

except Exception as e:
    logger.error(f"❌ Glue job {job_name} failed: {e}", exc_info=True)
    raise
finally:
    job.commit()
    logger.info("Glue job committed ✅")
