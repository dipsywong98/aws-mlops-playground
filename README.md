# aws mlops playground

An end to end PoC project and devcontainer of doing MLOps using AWS stuff - sagemaker, S3, lambda, etc

## The project - MNIST playground

A minimalistic project that can demo all the basic requirements of ML lifecycle:

preparation and validation of data -> training -> evaluation -> registration -> serve model

- [x] UI that download ONNX MNIST classifier models, and do adhoc handwritting digit recognition, simulates offline model usage in Goodnotes
- [x] MNIST data from pytorch to kick start training and preupload to S3 as a single parquet file, to simulate a raw input from data pipeline
- Sagemaker pipeline that consist of the following steps
    - [x] preprocess: split data into training, validation and test (TODO: validate the data distribution to minimize bias)
    - [x] training: load the training and validation data, use pytorch CNN to train a model, export a pytorch pt format and ONNX format file
    - [x] evaluation: load the test data and pytorch model, ensure the accuracy reach a baseline
    - [x] registration: wait for manual approval and register the model as ready for production
    - [x] approval for deployment: only approved model is searchable from UI
- Lambdas
    - [x] endpoint for UI to download models
    - [x] endpoint to list models
- Github action
    - [x] automated test to verify the scripts used inside sagemaker pipeline and lambda is valid
    - [x] automated deployment to upload and run sagemaker pipeline upon test pass and code change
    - [x] automated deployment of aws lambda functions
    - [x] automated deployment of the web
- [ ] Write up on decisions and challenges in the PoC
- [ ] TBD - build docker image, more tests on the pipeline


## Folder structure

```
├── .devcontainer
├── .github/workflows # workflows to run lint, test, terraform, and pipeline, web deployment
├── iam # json file of aws iam policy. manually set up on UI and potentially can use terraform to automate, 
│         need to check if that is secure
├── packages
│   ├── experiments # some experiments to verify concept locally or to prepare data to s3
│   ├── functions # uv workspace that contains lambda functions,
│   │   │           currently terraform is picking a single python file to deploy, need to check how to scale that,
│   │   │           may check building docker image. so this is not really a package
│   │   └── src
│   │       └── functions
│   │           └── get_models
│   └── pipelines # uv workspace that contains sagemaker pipeline definition
│       └── src
│           └── pipelines # pipeline that build different kinds of model
│               └── mnist
│                   ├── code # code that run on sagemaker
│                   └── pipeline.py # the actual pipeline definition
├── terraform # terraform that deploy changes to aws
├── tests
│   └── pipelines
│       └── mnist
│           └── code # we should test the sagemaker step is working before deploying it
│               └── fixtures # data that required in tests
└── web # react app that download model and do model inferrence
```
