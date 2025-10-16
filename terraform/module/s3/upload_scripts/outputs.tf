# Map of job_name => S3 key (path inside bucket)
output "script_keys" {
  description = "S3 object keys where scripts are uploaded"
  value = {
    for k, v in aws_s3_object.upload_script :
    var.scripts[k].job_name => v.key
  }
}

# Map of job_name => full S3 URI
output "script_locations" {
  description = "Full S3 URI for each uploaded script"
  value = {
    for k, v in aws_s3_object.upload_script :
    var.scripts[k].job_name => "s3://${v.bucket}/${v.key}"
  }
}

