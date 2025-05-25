# aws mlops playground

A POC of doing MLOps using AWS stuff

use S3 to serve training data

use AWS Model registry to register model

model CT(continuous training) pipeline:

Data preparation and validation -> Model training -> Model validation -> Model publishing and versioning -> Model serving

model update and data update should trigger the
