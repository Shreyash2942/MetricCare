#creating s3 bucket
module "s3_bucket" {
  source = "./module/s3/s3_bucket"
  bucket_name = "${terraform.workspace}-${var.bucket_name}"
  tag = var.tag
}
module "upload_files" {
  source = "./module/s3/upload_files"
  bucket_name = module.s3_bucket.bucket_id
  upload_file = var.config_file
  depends_on = [module.s3_bucket]
}
#uploading script
module "upload_script" {
  source = "./module/s3/upload_scripts"
  bucket_name = module.s3_bucket.bucket_id
  scripts = merge(var.scripts,var.lambda_script) #
  depends_on = [module.s3_bucket]
}

module "glue_catalog_database" {
  source = "./module/glue/glue_catalog_database"
  database_location = var.glue_database_location
  database_name     = "${terraform.workspace}_${var.glue_database_name}"
  description_database = "Glue catalog database for ${terraform.workspace} environment"
}

#-------------- creating dynemoDB -------------
module "dynamodb_metadata" {
  source       = "./module/dynemoDB"
  project_name = var.project_name
}

#------------------creating glue jobs------------
module "glue_job" {
  source = "./module/glue/glue_job"
  glue_jobs = var.scripts
  iam_role = var.iam_role
  s3_bucket = module.s3_bucket.bucket_id
  config_file = module.upload_files.uploaded_file.key
  database_name = module.glue_catalog_database.database_name
  script_location = module.upload_script.script_locations
  meta_table = module.dynamodb_metadata.workflow_metadata_table_name
  depends_on = [module.upload_script,module.glue_catalog_database]
}

#---------------Creating glue workflow------------------#

module "glue_work_flow" {
  source = "./module/glue/glue_workflow"
  bronze_job = var.bronze_job_name
  silver_job = var.silver_job_name
  gold_job = var.gold_job_name
  depends_on = [module.glue_job]
  workflow_name = "${terraform.workspace}_${var.workflow_name}"
}

#----------------Creating lambda function ------------------------------

module "lambda_function" {
  source             = "./module/lambda_function"
  bucket_arn         = module.s3_bucket.bucket_arn
  bucket_id          = module.s3_bucket.bucket_id
  glue_workflow_name = module.glue_work_flow.workflow_name
  lmbd_iam_role      = var.lmbd_iam_role
  lmbd_name          = var.lambda_function_name
  s3_prefix          = var.s3_prefix

  lmbd_s3_buckt      = module.s3_bucket.bucket_id
  lmbd_s3_key        = module.upload_script.script_keys["lambda_glue"]
  lmbd_etags         = filemd5(var.lambda_script["lambda_glue"].script_path)

  depends_on = [module.upload_script,module.glue_work_flow]
}

#########################################
# SNS Topic + Multi-Subscriber Alerts
#########################################

module "sns_alert" {
  source     = "./module/aws_sns"
  env_prefix = terraform.workspace
  protocol   = var.sns_protocol
  endpoints  = var.sns_endpoints
}

#########################################
# EventBridge Rule for Glue Job Failures
#########################################

module "eventbridge_rule" {
  source          = "./module/event_bridge"
  env_prefix      = terraform.workspace
  sns_topic_arn   = module.sns_alert.sns_topic_arn
  glue_job_names  = module.glue_job.job_names
}
