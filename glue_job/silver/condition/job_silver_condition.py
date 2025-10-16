import sys, boto3, json, logging
from datetime import datetime
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from awsglue.job import Job
from pyspark.context import SparkContext
from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    current_timestamp, col, split, to_date, lit, concat, regexp_replace,
    date_format, max as spark_max
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
    ['JOB_NAME', 'bucket_name', 'config_key', 'job_section', 'env', 'database_name']
)

bucket_name   = args['bucket_name']
config_key    = args['config_key']
job_section   = args['job_section']
env           = args['env']
database_name = args['database_name']
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
    input_path = f"s3://{bucket_name}/{input_location}"
    table_name = job_config["table"]
    log_table = job_config["log_table"]
    output_location = job_config["output_path"]
    output_path = f"s3://{bucket_name}/{output_location}"
    log_location = job_config["log_path"]
    log_path = f"s3://{bucket_name}/{log_location}"

    glue = boto3.client("glue")
    logger.info(f"✅ Loaded config for section={job_section} from s3://{bucket_name}/{config_key}")

except Exception as e:
    logger.error(f"❌ Failed to load config: {e}", exc_info=True)
    raise

# ----------------------------
# Glue Boilerplate
# ----------------------------
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(job_name, args)

# ----------------------------
# Helper Functions
# ----------------------------
def hudi_options(table_name, database_name, recordkey, precombine, partition_key, output_path):
    """HUDI Write Options"""
    return {
        "hoodie.table.name": table_name,
        "hoodie.database.name": database_name,
        "hoodie.datasource.write.storage.type": "COPY_ON_WRITE",
        "hoodie.datasource.write.operation": "upsert",
        "hoodie.datasource.write.recordkey.field": recordkey,
        "hoodie.datasource.write.precombine.field": precombine,
        "hoodie.datasource.write.partitionpath.field": partition_key,
        "hoodie.datasource.write.hive_style_partitioning": "true",
        "hoodie.datasource.write.schema.allow.auto.evolution": "true",
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
    """Write DataFrame to Hudi"""
    table = options["hoodie.table.name"]
    logger.info(f"▶ Writing table {table} to {options['path']}")
    df.write.format("hudi").options(**options).mode(mode).save()
    logger.info(f"✅ Successfully wrote table {table}")

def table_exists(database, table):
    """Check if Glue table exists"""
    try:
        glue.get_table(DatabaseName=database, Name=table)
        return True
    except glue.exceptions.EntityNotFoundException:
        return False

# ----------------------------
# Main Processing Logic
# ----------------------------
try:
    # 1️⃣ Get last processed timestamp
    lastprocesstime = datetime(2000, 1, 1, 0, 0, 0)
    if table_exists(database_name, log_table):
        ts_dyf = glueContext.create_data_frame.from_catalog(
            database=database_name,
            table_name=log_table
        )
        value = ts_dyf.filter(col("tablename") == table_name) \
                      .agg(spark_max("lastprocesstime")) \
                      .collect()[0][0]
        if value:
            lastprocesstime = value
    logger.info(f"🕒 Last process time for {table_name}: {lastprocesstime}")

    # 2️⃣ Read Bronze Condition table
    bronze_df = glueContext.create_data_frame.from_catalog(
        database=database_name,
        table_name="bronze_condition"
    ).filter(col("precombine_ts") > lastprocesstime)

    if bronze_df.count() == 0:
        logger.info("No new condition records to process.")
    else:
        logger.info(f"Processing {bronze_df.count()} new condition records...")

        # 3️⃣ Transformations — aligned with Bronze schema
        df = (
            bronze_df
            .withColumn("onset_date", to_date(regexp_replace(col("onset_time"), r"T.*", ""), "yyyy-MM-dd"))
            .withColumn("abatement_date", to_date(regexp_replace(col("recovery_time"), r"T.*", ""), "yyyy-MM-dd"))
            .withColumn("patient_id", split(col("patient_ref"), "/")[1])
            .withColumn("encounter_id", split(col("encounter_ref"), "/")[1])
            .withColumn("is_infectious", (col("category") == "Infection").cast("boolean"))
            .withColumn("is_chronic", (col("category") == "Chronic").cast("boolean"))
            .dropDuplicates(["condition_id"])
        )

        # 4️⃣ Select Silver Schema
        silver_df = df.select(
            col("condition_id"),
            col("patient_id"),
            col("encounter_id"),
            col("snomed_code"),
            col("condition_name"),
            col("category"),
            col("metric_type"),
            col("severity"),
            col("clinical_status"),
            col("onset_date"),
            col("abatement_date"),
            col("is_infectious"),
            col("is_chronic"),
            col("sourcename"),
            col("precombine_ts")
        )

        # 5️⃣ Write Silver Hudi Table
        silver_options = hudi_options(
            table_name=table_name,
            database_name=database_name,
            recordkey="condition_id",
            precombine="precombine_ts",
            partition_key="category",
            output_path=output_path
        )
        write_dataframe(silver_df, silver_options)

        # 6️⃣ Log processing timestamp
        timestamp_df = (
            spark.range(1)
            .withColumn("record_id", concat(lit(f"{table_name}/"), date_format(current_timestamp(), "yyyyMMdd_HHmmss")))
            .withColumn("tablename", lit(table_name))
            .withColumn("tabletype", lit("silver"))
            .withColumn("lastprocesstime", current_timestamp())
        )

        ts_options = hudi_options(
            table_name=log_table,
            database_name=database_name,
            recordkey="record_id",
            precombine="lastprocesstime",
            partition_key="tabletype",
            output_path=log_path
        )
        write_dataframe(timestamp_df, ts_options)

        logger.info(f"✅ Silver Condition Job {job_name} completed successfully")

except Exception as e:
    logger.error(f"❌ Job failed: {e}", exc_info=True)
    raise

finally:
    job.commit()
    logger.info("Glue job committed ✅")
