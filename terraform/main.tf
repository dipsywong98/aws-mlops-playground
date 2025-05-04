terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }

  required_version = ">= 0.14.9"
}

provider "aws" {
  profile = "default"
  region  = "us-east-1"
}

resource "aws_instance" "app_server" {
  ami           = "ami-097947612b141c026"
  subnet_id     = "subnet-02d9a4ed897161023"
  instance_type = "t2.micro"

  tags = {
    Name = "Batman"
  }
}