import sys, boto3, json, logging
from datetime import datetime
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.window import Window
from pyspark.sql.functions import (
    current_timestamp, col, lit, concat, date_format,
    max as spark_max, datediff, lag, when, to_timestamp, to_date
)

# -------------------------------------------------
# Logging
# -------------------------------------------------
logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# -------------------------------------------------
# Glue job parameters
# -------------------------------------------------
args = getResolvedOptions(
    sys.argv,
    ["JOB_NAME", "bucket_name", "config_key", "job_section", "env", "database_name"]
)

bucket_name   = args["bucket_name"]
config_key    = args["config_key"]
job_section   = args["job_section"]
env           = args["env"]
database_name = args["database_name"]
job_name      = args["JOB_NAME"]

# -------------------------------------------------
# Load config.json from S3
# -------------------------------------------------
try:
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket_name, Key=config_key)
    config = json.loads(response["Body"].read().decode("utf-8"))

    job_config = config[job_section]
    table_name = job_config["table"]        # gold_readmission_rate
    log_table  = job_config["log_table"]    # gold_readmission_rate_log
    output_path = f"s3://{bucket_name}/{job_config['output_path']}"
    log_path    = f"s3://{bucket_name}/{job_config['log_path']}"

    glue = boto3.client("glue")
    logger.info(f"Loaded config for section={job_section}")
except Exception as e:
    logger.error(f"Failed to load config: {e}", exc_info=True)
    raise

# -------------------------------------------------
# Glue + Spark setup
# -------------------------------------------------
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(job_name, args)

# -------------------------------------------------
# Helper functions
# -------------------------------------------------
def hudi_options(table_name, database_name, recordkey, precombine, partition_key, output_path):
    return {
        "hoodie.table.name": table_name,
        "hoodie.database.name": database_name,
        "hoodie.datasource.write.operation": "upsert",
        "hoodie.datasource.write.storage.type": "COPY_ON_WRITE",
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
        "path": output_path,
    }

def write_dataframe(df, options, mode="append"):
    table = options["hoodie.table.name"]
    logger.info(f"Writing table {table} to {options['path']}")
    df.write.format("hudi").options(**options).mode(mode).save()
    logger.info(f"Successfully wrote {table}")

def table_exists(database, table):
    try:
        glue.get_table(DatabaseName=database, Name=table)
        return True
    except glue.exceptions.EntityNotFoundException:
        return False

# -------------------------------------------------
# Main Job Logic
# -------------------------------------------------
try:
    # --------------------------
    # Get last process time
    # --------------------------
    lastprocesstime = datetime(2000, 1, 1, 0, 0, 0)
    if table_exists(database_name, log_table):
        ts_df = glueContext.create_data_frame.from_catalog(
            database=database_name, table_name=log_table
        )
        val = (
            ts_df.filter(col("tablename") == table_name)
            .agg(spark_max("lastprocesstime").alias("max_ts"))
            .collect()[0]["max_ts"]
        )
        if val:
            lastprocesstime = val
    logger.info(f"Last process time for {table_name}: {lastprocesstime}")

    # --------------------------
    # Read Silver encounters
    # --------------------------
    encounters = glueContext.create_data_frame.from_catalog(
        database=database_name,
        table_name="silver_encounter"
    )

    # Normalize dates: cast to date type, format MM/dd/yyyy
    encounters = (
        encounters
        .withColumn("admission_date", to_timestamp(col("admission_date")))
        .withColumn("discharge_date", to_timestamp(col("discharge_date")))
        .withColumn("admission_date",
            to_date(date_format(col("admission_date"), "MM/dd/yyyy"), "MM/dd/yyyy"))
        .withColumn("discharge_date",
            to_date(date_format(col("discharge_date"), "MM/dd/yyyy"), "MM/dd/yyyy"))
    )

    # Filter inpatients
    encounters = encounters.filter(col("encounter_type") == "Inpatient")

    # --------------------------
    # Identify readmissions (no negatives)
    # --------------------------
    w = Window.partitionBy("patient_id").orderBy("admission_date")

    enriched = (
        encounters
        .withColumn("prev_discharge", lag("discharge_date").over(w))
        .withColumn(
            "days_since_last_discharge",
            when(
                (col("admission_date").isNotNull()) & (col("prev_discharge").isNotNull()),
                datediff(col("admission_date"), col("prev_discharge"))
            ).otherwise(lit(None))
        )
        .withColumn(
            "is_readmission_30d",
            when(
                (col("days_since_last_discharge").isNotNull()) &
                (col("days_since_last_discharge") >= 0) &
                (col("days_since_last_discharge") <= 30),
                lit(1)
            ).otherwise(lit(0))
        )
        .withColumn("discharge_monthyear", date_format(col("discharge_date"), "MM/yyyy"))
        .withColumn("record_timestamp", current_timestamp())
    )

    # --------------------------
    # Write record-level facts to Hudi
    # --------------------------
    gold_options = hudi_options(
        table_name=table_name,
        database_name=database_name,
        recordkey="encounter_id",
        precombine="record_timestamp",
        partition_key="discharge_monthyear",
        output_path=output_path
    )
    write_dataframe(enriched, gold_options)

    # --------------------------
    # Update job log
    # --------------------------
    timestamp_df = (
        spark.range(1)
        .withColumn("record_id",
            concat(lit(f"{table_name}/"), date_format(current_timestamp(), "yyyyMMdd_HHmmss")))
        .withColumn("tablename", lit(table_name))
        .withColumn("tabletype", lit("gold"))
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

    logger.info(f" {table_name} job completed successfully!")

except Exception as e:
    logger.error(f"Job failed: {e}", exc_info=True)
    raise
finally:
    job.commit()
    logger.info("Glue job committed ")
