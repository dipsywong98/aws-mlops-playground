import json
import boto3
import tarfile

import botocore

s3_client = boto3.client('s3')
sm_client = boto3.client('sagemaker')

def parse_s3_url(s3_url):
    """
    Parse the S3 URL to extract bucket name and object key.
    """
    if not s3_url.startswith("s3://"):
        raise ValueError("Invalid S3 URL format. It should start with 's3://'.")
    
    parts = s3_url[5:].split('/', 1)  # Split after 's3://'
    if len(parts) != 2:
        raise ValueError("Invalid S3 URL format. It should contain a bucket and a key.")
    
    bucket_name = parts[0]
    object_key = parts[1]
    
    return bucket_name, object_key

def check_file_exists(bucket_name, object_key):
    try:
        s3_client.head_object(Bucket=bucket_name, Key=object_key)
        return True  # File exists
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            return False  # File does not exist
        else:
            raise e

def extract_reupload_model(bucket_name, tarfile_object_key, onnxfile_boject_key):
    local_tar_path = '/tmp/model.tar.gz'
    s3_client.download_file(bucket_name, tarfile_object_key, local_tar_path)

    # Extract model.onnx
    with tarfile.open(local_tar_path, 'r:gz') as tar:
        tar.extract('model.onnx', path='/tmp')

    s3_client.upload_file('/tmp/model.onnx', bucket_name, onnxfile_boject_key)


def lambda_handler(event, context):
    body = json.loads(event['body'])
    ModelPackageName = body.get('ModelPackageName')
    if not ModelPackageName:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'ModelPackageName is required'})
        }
    try:
        res = sm_client.describe_model_package(
            ModelPackageName=ModelPackageName
        )
    except Exception as e:
        print(f"Error describing model package: {e}")
        return {
            'statusCode': 404,
            'body': "Model package not found"
        }
    
    # s3://sagemaker-ap-southeast-2-993630082325/models/mnist/pipelines-q7lwddalt01t-MINIST-Train-5sHsaJrZoO/output/model.tar.gz
    tarfile_s3_url = res["InferenceSpecification"]["Containers"][0]["ModelDataUrl"]
    onnxfile_s3_url = tarfile_s3_url.replace("model.tar.gz", "model.onnx")

    _, tarfile_object_key = parse_s3_url(tarfile_s3_url)
    bucket_name, onnx_object_key = parse_s3_url(onnxfile_s3_url)

    if not check_file_exists(bucket_name, onnx_object_key):
        extract_reupload_model(bucket_name, tarfile_object_key, onnx_object_key)

    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': onnx_object_key},
        ExpiresIn=3600  # URL expires in 1 hour
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({'download_url': presigned_url})
    }
