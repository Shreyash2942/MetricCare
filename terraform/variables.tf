#------------Aws region--------------#
variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

# ----------------- S3 Bucket ----------------- #

variable "bucket_name" {
  default = "mcde4-sp"
}

variable "tag" {
  default = {
    name        = "mcde4-sp-dev"
    Project     = "MC-DE-4"
    owner       = "Shreyash"
    createdby   = "terraform"
  }
}

# ----------------- Uploading Config File ----------------- #
variable "config_file" {
  default = {
      source_location = "../config/config.json"
      s3_location     = "config/config.json"
  }
}

#--------------------creating dynemoDB table--------------------#
variable "project_name" {
  description = "Project name for resource naming and tagging"
  type        = string
  default     = "mc_de_4"
}

# ----------------- IAM Roles ----------------- #
variable "iam_role" {
  # Glue IAM role (workspace specific if you suffix them)
  default = "arn:aws:iam::259524131933:role/service-role/AWSGlueServiceRole-metriccare"
}

variable "lmbd_iam_role" {
  # Lambda IAM role (workspace specific if you suffix them)
  default = "arn:aws:iam::259524131933:role/service-role/my-job-role-cn7zdaxh"
}


# ----------------- Uploading Glue Job Scripts ----------------- #
variable "scripts" {
  default = {
    bronze_condition = {
      script_path = "../glue_job/bronze/condition/job_bronze_condition_hudi.py"
      job_name    = "job_bronze_condition_hudi"
    }
    bronze_encounter = {
      script_path = "../glue_job/bronze/encounter/job_bronze_encounter_hudi.py"
      job_name    = "job_bronze_encounter_hudi"
    }
    bronze_patient = {
      script_path = "../glue_job/bronze/patient/job_bronze_patient_hudi.py"
      job_name    = "job_bronze_patient_hudi"
    }

    silver_condition = {
      script_path = "../glue_job/silver/condition/job_silver_condition.py"
      job_name    = "job_silver_condition"
    }
    silver_encounter = {
      script_path = "../glue_job/silver/encounter/job_silver_encounter.py"
      job_name    = "job_silver_encounter"
    }
    silver_patient = {
      script_path = "../glue_job/silver/patient/job_silver_patient.py"
      job_name    = "job_silver_patient"
    }
    gold_infection_rate={
      script_path="../glue_job/gold/infection_rate/job_gold_infection_rate.py"
      job_name="job_gold_infection_rate"
    }
    gold_mortality_rate={
      script_path="../glue_job/gold/mortality_rate/job_gold_mortality_rate.py"
      job_name="job_gold_mortality_rate"
    }
    gold_readmission_rate={
      script_path="../glue_job/gold/readmission_rate/job_gold_readmission_rate.py"
      job_name="job_gold_readmission_rate"
    }
  }

}

# ----------------- Glue Catalog Database ----------------- #
variable "glue_database_name" {
  default = "mcde4_sp"
}

variable "glue_database_location" {
  default = "hudi_database/database"
}

# ----------------- Glue Workflow ----------------- #
variable "workflow_name" {
  default = "mc_de_4_workflow"
}

variable "bronze_job_name" {
  default = {
    bronze_condition = "job_bronze_condition_hudi"
    bronze_encounter = "job_bronze_encounter_hudi"
    bronze_patient   = "job_bronze_patient_hudi"
  }
}

variable "silver_job_name" {
  default = {
    silver_condition = "job_silver_condition"
    silver_encounter = "job_silver_encounter"
    silver_patient   = "job_silver_patient"
  }
}

variable "gold_job_name" {
  default = {
    gold_inflation_rate="job_gold_infection_rate"
    gold_mortality_rate="job_gold_mortality_rate"
    job_gold_readmission_rate="job_gold_readmission_rate"
  }
}

# ----------------- Lambda Function ----------------- #
variable "lambda_function_name" {
  default = "lambda_mcde4_sp"
}

variable "lambda_script" {
  default = {
    lambda_glue = {
      script_path = "../lambda/lambda_function.zip"
      job_name    = "lambda_glue"
    }
  }
}

# ----------------- S3 Prefix for Data ----------------- #
variable "s3_prefix" {
  default = "fhir_data/json/patient"
}

# ----------------- SNS Alerts (Multiple Recipients) ----------------- #

variable "sns_protocol" {
  description = "Protocol for SNS alert subscriptions (email or sms)"
  type        = string
  default     = "email"
}

variable "sns_endpoints" {
  description = "List of recipients for SNS alerts (email addresses or phone numbers)"
  type        = list(string)

  # Example defaults (override per environment in tfvars)
  default = [
    "shreyash@takeo.com",
    "teamlead@example.com",
    "opsengineer@example.com"
  ]
}

