import kagglehub
path = kagglehub.dataset_download("oddrationale/mnist-in-csv")
s3_bucket = "minist-15432"

print("Path to dataset files:", path)

# upload the dataset to S3
import boto3
import os


s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
)

s3_client.upload_file(
    Filename=os.path.join(path, "mnist_train.csv"),
    Bucket=s3_bucket,
    Key="mnist_train.csv"
)

s3_client.upload_file(
    Filename=os.path.join(path, "mnist_test.csv"),
    Bucket=s3_bucket,
    Key="mnist_test.csv"
)
