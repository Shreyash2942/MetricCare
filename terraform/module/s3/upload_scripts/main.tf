terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.12.0"
    }
  }
}

resource "aws_s3_object" "upload_script" {
  for_each = var.scripts
  bucket = var.bucket_name
  key = "${replace(each.value.script_path,"../","" )}"  #destination on s3
  source = each.value.script_path#source file location
  etag = filemd5(each.value.script_path)
}

