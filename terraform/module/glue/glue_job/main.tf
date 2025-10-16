terraform {
  required_version = ">= 1.0.0" # Ensure that the Terraform version is 1.0.0 or higher

  required_providers {
    aws = {
      source = "hashicorp/aws" # Specify the source of the AWS provider
      version = "~> 6.12.0"        # Use a version of the AWS provider that is compatible with version
    }
  }
}


resource "aws_glue_job" "etl_jobs" {
  for_each = var.glue_jobs
  name     ="${terraform.workspace}-${each.value.job_name}"
  role_arn = var.iam_role

  command {
    name = "glueetl"
    python_version = "3"
    script_location = var.script_location[each.value.job_name]
  }

  default_arguments = {
    "--enable-metrics"                  = "true"   # Enable Glue job metrics (basic execution stats in CloudWatch)
    "--enable-job-insights"             = "true"   # Enable Job Observability metrics (runtime insights, executor/data movement details)
    "--enable-spark-ui"                 = "true"   # Enable Spark UI (view DAGs & stages in Glue Studio)
    "--spark-event-logs-path"           = "s3://${var.s3_bucket}/glue_assiets/spark-logs/" # S3 path for Spark UI event logs
    "--enable-continuous-cloudwatch-log"= "true"   # Stream job logs continuously to CloudWatch (real-time logging)
    "--enable-continuous-log-filter"    = "true"   # Apply filters to CloudWatch logs (reduce noise like DEBUG spam)
    "--enable-spark-ui-metrics"         = "true"   # Enable Spark UI metrics (standard Spark metrics dashboards)
    "--enable-glue-datacatalog"         = "true"   # Use Glue Data Catalog as Hive Metastore (for Spark SQL/Hive queries)
    "--additional-python-modules"       = "pyathena" # Install extra Python module(s) at runtime (e.g., PyAthena)
    "--Tempdir"                         = "s3://${var.s3_bucket}/glue_assiets/temp_glue_job" # Temporary S3 dir for Glue job intermediates


    #hudi configuration
    "--datalake-formats" = "hudi"
    "--conf": "spark.serializer=org.apache.spark.serializer.KryoSerializer"

    # Config job parameters
    "--bucket_name"   = var.s3_bucket
    "--config_key"    = var.config_file
    "--job_section"   = each.value.job_name
    "--env"           = terraform.workspace
    "--database_name" = var.database_name
    "--meta_table"    = var.meta_table

  }

  max_retries = 0
  glue_version = "5.0"
  number_of_workers = 10
  worker_type = "G.1X"
  timeout = 480 #job time out in minutes


}