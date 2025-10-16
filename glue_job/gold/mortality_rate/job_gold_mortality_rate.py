import sys, boto3, json, logging
from datetime import datetime
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import (
    current_date, col, lit, concat, date_format, to_date,
    max as spark_max, datediff, when, year, month
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
    table_name = job_config["table"]
    log_table  = job_config["log_table"]
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
def hudi_options(table_name, database_name, recordkey, precombine, output_path):
    return {
        "hoodie.table.name": table_name,
        "hoodie.database.name": database_name,
        "hoodie.datasource.write.operation": "upsert",
        "hoodie.datasource.write.storage.type": "COPY_ON_WRITE",
        "hoodie.datasource.write.recordkey.field": recordkey,
        "hoodie.datasource.write.precombine.field": precombine,
        "hoodie.datasource.write.hive_style_partitioning": "false",
        "hoodie.datasource.write.schema.allow.auto.evolution": "true",
        "hoodie.datasource.hive_sync.enable": "true",
        "hoodie.datasource.hive_sync.use_glue_catalog": "true",
        "hoodie.datasource.hive_sync.database": database_name,
        "hoodie.datasource.hive_sync.table": table_name,
        "hoodie.datasource.hive_sync.mode": "hms",
        "hoodie.datasource.hive_sync.use_jdbc": "false",
        "path": output_path
    }

def write_dataframe(df, options, mode="append"):
    """Write dataframe to Hudi"""
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
    # Get last process date
    # --------------------------
    lastprocessdate = datetime(2000, 1, 1).date()
    if table_exists(database_name, log_table):
        ts_df = glueContext.create_data_frame.from_catalog(
            database=database_name, table_name=log_table
        )
        val = (ts_df.filter(col("tablename") == table_name)
                    .agg(spark_max("lastprocessdate").alias("max_date"))
                    .collect()[0]["max_date"])
        if val:
            lastprocessdate = val
    logger.info(f"Last process date for {table_name}: {lastprocessdate}")

    # --------------------------
    # Read silver layer tables
    # --------------------------
    silver_patients = glueContext.create_data_frame.from_catalog(
        database=database_name, table_name="silver_patients"
    )
    silver_conditions = glueContext.create_data_frame.from_catalog(
        database=database_name, table_name="silver_condition"
    )
    silver_encounters = glueContext.create_data_frame.from_catalog(
        database=database_name, table_name="silver_encounter"
    )

    # Convert timestamps → date
    silver_patients = silver_patients.withColumn("deceaseddatetime", to_date(col("deceaseddatetime")))
    silver_encounters = silver_encounters.withColumn("discharge_date", to_date(col("discharge_date"))) \
                                         .withColumn("admission_date", to_date(col("admission_date")))

    # --------------------------
    # Join Patient + Encounter + Condition
    # --------------------------
    joined_df = (
        silver_encounters.filter(col("encounter_type") == "Inpatient")
        .join(silver_patients, "patient_id", "inner")
        .join(silver_conditions, "patient_id", "left")
        .select(
            silver_patients["patient_id"],
            silver_patients["deceaseddatetime"],
            silver_encounters["encounter_id"],
            silver_encounters["hospital_name"],
            silver_encounters["department"],
            silver_encounters["discharge_date"],
            silver_encounters["admission_date"],
            silver_conditions["snomed_code"],
            silver_conditions["condition_name"]
        )
    )

    # --------------------------
    # Derive mortality fields (no negative dates)
    # --------------------------
    enriched_df = (
        joined_df
        .withColumn("days_to_death", datediff(col("deceaseddatetime"), col("discharge_date")))
        .withColumn(
            "death_within_30days",
            when(
                (col("deceaseddatetime").isNotNull()) &
                (col("discharge_date").isNotNull()) &
                (col("days_to_death") >= 0) &
                (col("days_to_death") <= 30),
                lit(1)
            ).otherwise(lit(0))
        )
        .withColumn("year", year(col("discharge_date")))
        .withColumn("month", month(col("discharge_date")))
        .withColumn("record_date", current_date())
    )

    # Filter out invalid negative death dates
    enriched_df = enriched_df.filter(
        (col("days_to_death").isNull()) | (col("days_to_death") >= 0)
    )

    # --------------------------
    # Write to Gold Hudi table
    # --------------------------
    gold_options = hudi_options(
        table_name=table_name,
        database_name=database_name,
        recordkey="encounter_id",
        precombine="record_date",
        output_path=output_path
    )
    write_dataframe(enriched_df, gold_options)

    # --------------------------
    # Update job log (date-based)
    # --------------------------
    log_df = spark.range(1).withColumn(
        "record_id", concat(lit(f"{table_name}/"), date_format(current_date(), "yyyyMMdd"))
    ).withColumn("tablename", lit(table_name)) \
     .withColumn("tabletype", lit("gold")) \
     .withColumn("lastprocessdate", current_date())

    log_options = hudi_options(
        table_name=log_table,
        database_name=database_name,
        recordkey="record_id",
        precombine="lastprocessdate",
        output_path=log_path
    )
    write_dataframe(log_df, log_options)

    logger.info(f"{table_name} job completed successfully!")

except Exception as e:
    logger.error(f"Job failed: {e}", exc_info=True)
    raise
finally:
    job.commit()
    logger.info("Glue job committed.")
