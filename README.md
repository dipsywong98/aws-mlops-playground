# aws mlops playground

A POC of doing MLOps using AWS stuff

use S3 to serve training data

use AWS Model registry to register model

model CT(continuous training) pipeline:

Data preparation and validation -> Model training -> Model validation -> Model publishing and versioning -> Model serving

aws lambda to serve model in offline manner, that is the download the entire model to run on browser

use vite+react+onnx-web to run the model on handwritten digits

deploy the website on cloudflare for simplicity
