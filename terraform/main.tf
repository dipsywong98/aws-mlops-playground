terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  required_version = ">= 1.12.1"
}

provider "aws" {
  # profile = "default"
  region  = "ap-southeast-2"
}

data "archive_file" "sagemaker_list_models_lambda_file" {
  type        = "zip"
  source_file = "../packages/functions/src/functions/list_models.py"
  output_path = "/tmp/sagemaker_list_models_lambda_file.zip"
}

resource "aws_lambda_function" "sagemaker_list_models_lambda" {
  function_name = "sagemaker_list_models_lambda"
  role          = "arn:aws:iam::993630082325:role/lambda_sagemaker_role"
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.12"
  filename      = data.archive_file.sagemaker_list_models_lambda_file.output_path
  source_code_hash = data.archive_file.sagemaker_list_models_lambda_file.output_base64sha256
}

resource "aws_lambda_permission" "allow_invoke" {
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.sagemaker_list_models_lambda.function_name
  principal     = "apigateway.amazonaws.com"
}

# resource "aws_instance" "app_server" {
#   ami           = "ami-097947612b141c026"
#   subnet_id     = "subnet-02d9a4ed897161023"
#   instance_type = "t2.micro"

#   tags = {
#     Name = "Batman"
#   }
# }
