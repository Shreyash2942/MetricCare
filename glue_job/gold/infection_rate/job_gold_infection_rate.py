import sys, boto3, json, logging
from datetime import datetime
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    current_timestamp, col, lit, concat, date_format,
    countDistinct, sum as spark_sum, max as spark_max, when
)

# -------------------------------------------------
# Logging setup
# -------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# -------------------------------------------------
# Glue job parameters
# -------------------------------------------------
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

# -------------------------------------------------
# Load config.json from S3
# -------------------------------------------------
try:
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket_name, Key=config_key)
    config = json.loads(response['Body'].read().decode('utf-8'))

    job_config = config[job_section]
    table_name = job_config["table"]        # gold_infection_rate
    log_table  = job_config["log_table"]    # gold_infection_rate_log
    output_path = f"s3://{bucket_name}/{job_config['output_path']}"
    log_path    = f"s3://{bucket_name}/{job_config['log_path']}"

    glue = boto3.client("glue")
    logger.info(f"Loaded configuration for section={job_section}")

except Exception as e:
    logger.error(f"Failed to load configuration: {e}", exc_info=True)
    raise

# -------------------------------------------------
# Glue + Spark Setup
# -------------------------------------------------
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(job_name, args)

# -------------------------------------------------
# Helper Functions
# -------------------------------------------------
def hudi_options(table_name, database_name, recordkey, precombine, partition_key, output_path):
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
    """Write dataframe to Hudi"""
    table = options["hoodie.table.name"]
    logger.info(f"Writing table {table} to {options['path']}")
    df.write.format("hudi").options(**options).mode(mode).save()
    logger.info(f"Successfully wrote table {table}")

def table_exists(database, table):
    """Check if Glue table exists"""
    try:
        glue.get_table(DatabaseName=database, Name=table)
        return True
    except glue.exceptions.EntityNotFoundException:
        return False

# -------------------------------------------------
# Main Job Logic
# -------------------------------------------------
try:
    # Step 1: Get last process time from log table
    lastprocesstime = datetime(2000, 1, 1, 0, 0, 0)
    if table_exists(database_name, log_table):
        ts_df = glueContext.create_data_frame.from_catalog(
            database=database_name, table_name=log_table
        )
        value = ts_df.filter(col("tablename") == table_name) \
                     .agg(spark_max("lastprocesstime")) \
                     .collect()[0][0]
        if value:
            lastprocesstime = value

    logger.info(f"Last process time for {table_name}: {lastprocesstime}")

    # Step 2: Read Silver Condition Table
    silver_conditions = glueContext.create_data_frame.from_catalog(
        database=database_name,
        table_name="silver_condition"
    )

    # Process only new or updated records
    silver_conditions = silver_conditions.filter(col("precombine_ts") > lastprocesstime)

    if silver_conditions.count() == 0:
        logger.info("No new condition records to process. Exiting.")
    else:
        logger.info(f"Processing {silver_conditions.count()} new condition records...")

        # Step 3: Add classification column
        silver_conditions = silver_conditions.withColumn(
            "condition_type",
            when(col("is_infectious") == True, lit("Infectious")).otherwise(lit("Non-Infectious"))
        )

        # Step 4: Compute Infection Metrics for all SNOMED codes
        total_patients = silver_conditions.select("patient_id").distinct().count()
        logger.info(f"Total unique patients in dataset: {total_patients}")

        infection_agg = (
            silver_conditions
            .groupBy("snomed_code", "condition_name", "condition_type")
            .agg(
                countDistinct("patient_id").alias("patients_with_condition"),
                spark_sum(when(col("is_infectious") == True, 1).otherwise(0)).alias("infection_cases")
            )
            .withColumn("total_patients", lit(total_patients))
            .withColumn(
                "infection_rate_percent",
                when(col("total_patients") > 0,
                     (col("infection_cases") * 100.0 / col("total_patients")))
                .otherwise(lit(0.0))
            )
            .withColumn(
                "infection_rate_per_1000",
                when(col("total_patients") > 0,
                     (col("infection_cases") * 1000.0 / col("total_patients")))
                .otherwise(lit(0.0))
            )
            .withColumn("record_timestamp", current_timestamp())
        )

        gold_df = infection_agg.select(
            "snomed_code",
            "condition_name",
            "total_patients",
            "infection_cases",
            "infection_rate_percent",
            "infection_rate_per_1000",
            "record_timestamp",
            "condition_type"
        )

        # Step 5: Write Gold Hudi Table
        gold_options = hudi_options(
            table_name=table_name,
            database_name=database_name,
            recordkey="snomed_code",
            precombine="record_timestamp",
            partition_key="condition_type",
            output_path=output_path
        )
        write_dataframe(gold_df, gold_options)

        # Step 6: Write Log Entry
        timestamp_df = spark.range(1).withColumn(
            "record_id", concat(lit(f"{table_name}/"), date_format(current_timestamp(), "yyyyMMdd_HHmmss"))
        ).withColumn("tablename", lit(table_name)) \
         .withColumn("tabletype", lit("gold")) \
         .withColumn("lastprocesstime", current_timestamp())

        ts_options = hudi_options(
            table_name=log_table,
            database_name=database_name,
            recordkey="record_id",
            precombine="lastprocesstime",
            partition_key="tabletype",
            output_path=log_path
        )
        write_dataframe(timestamp_df, ts_options)

        logger.info(f"{table_name} job completed successfully!")

except Exception as e:
    logger.error(f"Job failed: {e}", exc_info=True)
    raise
finally:
    job.commit()
    logger.info("Glue job committed successfully.")