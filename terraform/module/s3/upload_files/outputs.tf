# -----------------------------
# Output for Single Uploaded File
# -----------------------------

output "uploaded_file" {
  description = "Details of the uploaded file in S3."
  value = {
    bucket = aws_s3_object.upload_file.bucket
    key    = aws_s3_object.upload_file.key
    etag   = aws_s3_object.upload_file.etag
    url    = "s3://${aws_s3_object.upload_file.bucket}/${aws_s3_object.upload_file.key}"
  }
}
