import sys, boto3, json, logging
from datetime import datetime
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import DataFrame
from pyspark.sql.functions import (
    current_timestamp, col, to_date, regexp_replace,
    when, lit, concat, date_format, max as spark_max
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
    table_name = job_config["table"]
    log_table = job_config["log_table"]
    output_location = job_config["output_path"]
    log_location = job_config["log_path"]

    input_path = f"s3://{bucket_name}/{input_location}"
    output_path = f"s3://{bucket_name}/{output_location}"
    log_path = f"s3://{bucket_name}/{log_location}"

    glue = boto3.client("glue")
    logger.info(f"✅ Loaded config for section={job_section} from s3://{bucket_name}/{config_key}")

except Exception as e:
    logger.error(f"❌ Failed to load config: {e}", exc_info=True)
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
# Helper Functions
# ----------------------------
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

def table_exists(database, table):
    """Check if Glue table exists"""
    try:
        glue.get_table(DatabaseName=database, Name=table)
        return True
    except glue.exceptions.EntityNotFoundException:
        return False

# ----------------------------
# Main Processing
# ----------------------------
try:
    # 1️⃣ Get last process time from Silver job’s log
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
    logger.info(f"Last process time for {table_name}: {lastprocesstime}")

    # 2️⃣ Read Bronze patients
    bronze_df = glueContext.create_data_frame.from_catalog(
        database=database_name,
        table_name="bronze_patients"
    ).filter(col("precombine_ts") > lastprocesstime)

    if bronze_df.count() == 0:
        logger.info("No new patient records to process from Bronze layer.")
    else:
        logger.info(f"Processing {bronze_df.count()} new patient records from Bronze layer.")

        # 3️⃣ Clean and minimal transformations
        silver_df = (
            bronze_df
            .withColumn("birthDate", to_date(col("birthDate"), "yyyy-MM-dd"))
            .withColumn("deceasedDateTime", to_date(regexp_replace(col("deceasedDateTime"), r"T.*", ""), "yyyy-MM-dd"))
            .withColumn("deceased_flag", when(col("is_deceased") == True, lit("Yes")).otherwise(lit("No")))
            .dropDuplicates(["patient_id"])
        )

        # 4️⃣ Select Silver schema
        silver_df = silver_df.select(
            col("patient_id"),
            col("gender"),
            col("birthDate"),
            col("language"),
            col("hospital_name"),
            col("is_deceased"),
            col("deceased_flag"),
            col("deceasedDateTime"),
            col("sourcename"),
            col("precombine_ts")
        )

        # 5️⃣ Write to Silver Hudi table
        silver_options = hudi_options(
            table_name=table_name,
            database_name=database_name,
            recordkey="patient_id",
            precombine="precombine_ts",
            partition_key="hospital_name",
            output_path=output_path
        )
        write_dataframe(silver_df, silver_options)

        # 6️⃣ Write timestamp log
        timestamp_df = spark.range(1).withColumn(
            "record_id", concat(lit(f"{table_name}/"), date_format(current_timestamp(), "yyyyMMdd_HHmmss"))
        ).withColumn("tablename", lit(table_name)) \
         .withColumn("tabletype", lit("silver")) \
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

        logger.info(f"✅ Silver Patient Job {job_name} completed successfully")

except Exception as e:
    logger.error(f"❌ Glue job {job_name} failed: {e}", exc_info=True)
    raise
finally:
    job.commit()
    logger.info("Glue job committed ✅")
