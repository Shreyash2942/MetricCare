"""aws_credential.py"""
import os
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from dotenv import load_dotenv

load_dotenv(dotenv_path='aws_crendential.env')


def aws_credential():
    # # Prompt user for AWS credentials and S3 details
    aws_access_key = os.getenv("AWS_ACCESS_KEY")
    aws_secret_key =os.getenv("AWS_SECRET_KEY")
    bucket_name =os.getenv("S3_BUCKET_NAME")
    bucket_path = "test/output/"



    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key
        )
        # Test credentials by listing buckets (but not printing them)
        s3.list_buckets()
        print("AWS credentials are valid.")
        return bucket_name,bucket_path,s3

    except NoCredentialsError:
        print("Invalid AWS credentials.")
        exit(1)
    except ClientError as e:
        print(f"AWS error: {e}")
        exit(1)


if __name__=="__main__":
    aws_credential()