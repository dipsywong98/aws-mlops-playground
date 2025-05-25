import boto3
import botocore


def lambda_handler(event, context):
    print(f'boto3 version: {boto3.__version__}')
    print(f'botocore version: {botocore.__version__}')
    sm_client = boto3.client("sagemaker")
    model_package_group_name = "MnistModelPackageGroupName"
    return sm_client.list_model_packages(ModelPackageGroupName=model_package_group_name, ModelApprovalStatus="Approved")
