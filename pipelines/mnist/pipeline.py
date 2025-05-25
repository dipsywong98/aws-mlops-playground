import os
from sagemaker.workflow.pipeline_context import PipelineSession
from sagemaker.workflow.pipeline import Pipeline
from datetime import datetime
from sagemaker.workflow.parameters import (
    ParameterInteger,
    ParameterString,
    ParameterFloat,
)
from sagemaker.inputs import TrainingInput
from sagemaker.workflow.steps import TrainingStep, ProcessingStep
from sagemaker.sklearn.processing import SKLearnProcessor
from sagemaker.pytorch import PyTorch
from sagemaker.pytorch.processing import PyTorchProcessor
from sagemaker.processing import ProcessingInput, ProcessingOutput
from sagemaker.workflow.properties import PropertyFile

tags = [{"Key": "Project", "Value": "MNIST"}, {"Key": "Commit", "Value": "MNIST"}]


def get_pipeline(input_data_uri, role):
    pipeline_session = PipelineSession()
    pipeline_root_dir = os.path.dirname(__file__)

    instance_type = ParameterString(name="TrainingInstanceType", default_value="ml.m5.large")
    model_approval_status = ParameterString(
        name="ModelApprovalStatus", default_value="PendingManualApproval"
    )
    input_data = ParameterString(
        name="InputData",
        default_value=input_data_uri,
    )

    mse_threshold = ParameterFloat(name="MseThreshold", default_value=6.0)

    
    sklearn_processor = SKLearnProcessor(
        framework_version = "1.2-1",
        instance_type="ml.m5.large",
        instance_count=1,
        base_job_name="mnist-preprocess",
        role=role,
        sagemaker_session=pipeline_session,
    )

    step_process = ProcessingStep(
        name="MnistProcess",
        processor=sklearn_processor,
        inputs=[
            ProcessingInput(source=input_data, destination="/opt/ml/processing/input"),
        ],
        outputs=[
            ProcessingOutput(output_name="train", source="/opt/ml/processing/train"),
            ProcessingOutput(output_name="validation", source="/opt/ml/processing/validation"),
            ProcessingOutput(output_name="test", source="/opt/ml/processing/test"),
        ],
        code=os.path.join(pipeline_root_dir, "code/preprocessing.py"),
    )

    estimator = PyTorch(
        entry_point="mnist.py",
        source_dir=os.path.join(pipeline_root_dir, "code"),
        role=role,
        framework_version="2.6",
        py_version="py312",
        instance_count=1,
        train_instance_type="ml.m5.large",
        hyperparameters={"epochs": 1},
        output_path="s3://sagemaker-ap-southeast-2-993630082325/models/mnist",
        env={
            'SAGEMAKER_REQUIREMENTS': 'requirements.txt',
        }
    )

    step_train = TrainingStep(
        name="MINIST-Train",
        estimator=estimator,
        inputs={
            "train": TrainingInput(
                s3_data=step_process.properties.ProcessingOutputConfig.Outputs["train"].S3Output.S3Uri,
            ),
            "validation": TrainingInput(
                s3_data=step_process.properties.ProcessingOutputConfig.Outputs[
                    "validation"
                ].S3Output.S3Uri,
            ),
        },
    )

    model_evaluator = PyTorchProcessor(
        framework_version="2.6",
        py_version="py312",
        instance_type="ml.m5.large",
        instance_count=1,
        base_job_name="script-abalone-eval",
        role=role,
        sagemaker_session=pipeline_session,
    )

    evaluation_report = PropertyFile(
        name="EvaluationReport", output_name="evaluation", path="evaluation.json"
    )
    step_eval = ProcessingStep(
        name="MnistEval",
        processor=model_evaluator,
        property_files=[evaluation_report],
        inputs=[
            ProcessingInput(
                source=step_train.properties.ModelArtifacts.S3ModelArtifacts,
                destination="/opt/ml/processing/model",
            ),
            ProcessingInput(
                source=step_process.properties.ProcessingOutputConfig.Outputs["test"].S3Output.S3Uri,
                destination="/opt/ml/processing/test",
            ),
        ],
        outputs=[
            ProcessingOutput(output_name="evaluation", source="/opt/ml/processing/evaluation"),
        ],
        code=os.path.join(pipeline_root_dir, "code/evaluation.py"),
    )

    pipeline_name = f"MNIST-Pipeline"
    pipeline = Pipeline(
        name=pipeline_name,
        parameters=[
            instance_type,
            model_approval_status,
            input_data,
            mse_threshold,
        ],
        steps=[step_process, step_train, step_eval],
    )

    return pipeline

if __name__ == "__main__":
    
    input_data_uri = "s3://sagemaker-ap-southeast-2-993630082325/datasets/mnist/original"
    role = "arn:aws:iam::993630082325:role/service-role/AmazonSageMaker-ExecutionRole-20250516T191424"
    pipeline = get_pipeline(input_data_uri, role)
    pipeline.upsert(role_arn=role, tags=[{"Key": "Project", "Value": "MNIST"}])
    
    print(f"Pipeline {pipeline.name} created successfully.")