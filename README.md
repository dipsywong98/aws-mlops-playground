# aws mlops playground

A POC and devcontainer of doing MLOps using AWS stuff - sagemaker, S3, lambda, etc

use S3 to serve training data

use AWS Model registry to register model

model CT(continuous training) pipeline:

Data preparation and validation -> Model training -> Model validation -> Model publishing and versioning -> Model serving

aws lambda to serve model in offline manner, that is to download the entire model to run on browser

use terraform to deploy aws lambda

use vite+react+onnx-web to run the model on handwritten digits - list approved models, choose and download one, run the model on browser

deploy the website somewhere

## Folder structure

```
├── .devcontainer
├── .github/workflows # workflows to run lint, test, terraform, and pipeline, web deployment
├── iam # json file of aws iam policy. manually set up on UI and potentially can use terraform to automate, need to check if that is secure
├── packages
│   ├── functions # uv workspace that contains lambda functions, currently terraform is picking a single python file to deploy, need to check how to scale that, may check building docker image. so this is not really a package
│   │   └── src
│   │       └── functions
│   │           └── get_models
│   └── pipelines # uv workspace that contains sagemaker pipeline definition
│       └── src
│           └── pipelines # pipeline that build different kinds of model
│               └── mnist
│                   ├── code # code that run on sagemaker
│                   ├── data # data that used locally, move away later
│                   ├── legacy_experiments # move away later
│                   ├── explore_data.ipynb # to prepare data for training and upload to s3, move away later
│                   └── pipeline.py # the actual pipeline definition
├── terraform # terraform that deploy changes to aws
├── tests
│   └── pipelines
│       └── mnist
│           └── code # we should test the sagemaker step is working before deploying it
│               └── fixtures # data that required in tests
└── web # react app that download model and do model inferrence
```
