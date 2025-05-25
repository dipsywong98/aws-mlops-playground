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
import typer
from sagemaker.workflow.conditions import ConditionLessThanOrEqualTo
from sagemaker.workflow.condition_step import ConditionStep
from sagemaker.workflow.functions import JsonGet
from sagemaker.workflow.model_step import ModelStep

from sagemaker.workflow.fail_step import FailStep
from sagemaker.workflow.functions import Join

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

    accuracy_threshold = ParameterFloat(name="AccuracyThreshold", default_value=6.0)
    model_package_group_name = f"MnistModelPackageGroupName"

    
    sklearn_processor = SKLearnProcessor(
        framework_version = "1.2-1",
        instance_type="ml.m5.large",
        instance_count=1,
        base_job_name="mnist-preprocess",
        role=role,
        sagemaker_session=pipeline_session,
        env={
            'SAGEMAKER_REQUIREMENTS': 'requirements.txt',
        },
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
        },
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
        env={
            'SAGEMAKER_REQUIREMENTS': 'requirements.txt',
        },
        tags=tags,
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

    from sagemaker.model_metrics import MetricsSource, ModelMetrics

    model_metrics = ModelMetrics(
        model_statistics=MetricsSource(
            s3_uri="{}/evaluation.json".format(
                step_eval.arguments["ProcessingOutputConfig"]["Outputs"][0]["S3Output"]["S3Uri"]
            ),
            content_type="application/json",
        )
    )
    from sagemaker.model import Model
    model = Model(
        image_uri=estimator.training_image_uri(),
        model_data=step_train.properties.ModelArtifacts.S3ModelArtifacts,
        sagemaker_session=PipelineSession(),
        role=role,
    )
    step_register = ModelStep(
        name="MnistRegisterModel",
        step_args=model.register(
            model_package_group_name=model_package_group_name,
            approval_status=model_approval_status,
            model_metrics=model_metrics,
        ),
    )

    cond_lte = ConditionLessThanOrEqualTo(
        left=JsonGet(
            step_name=step_eval.name,
            property_file=evaluation_report,
            json_path="regression_metrics.accuracy.value",
        ),
        right=accuracy_threshold,
    )

    step_fail = FailStep(
        name="MnistAccuracyFail",
        error_message=Join(on=" ", values=["Execution failed due to accuracy <", accuracy_threshold]),
    )

    step_cond = ConditionStep(
        name="MnistCondition",
        conditions=[cond_lte],
        if_steps=[step_register],
        else_steps=[step_fail],
    )

    pipeline_name = f"MNIST-Pipeline"
    pipeline = Pipeline(
        name=pipeline_name,
        parameters=[
            instance_type,
            model_approval_status,
            input_data,
            accuracy_threshold,
        ],
        steps=[step_process, step_train, step_eval, step_cond],
    )

    return pipeline


def main(
    input_data_uri = "s3://sagemaker-ap-southeast-2-993630082325/datasets/mnist/original",
    role = "arn:aws:iam::993630082325:role/service-role/AmazonSageMaker-ExecutionRole-20250516T191424",
    run_pipeline = False,
): 
    pipeline = get_pipeline(input_data_uri, role)
    pipeline.upsert(role_arn=role, tags=[{"Key": "Project", "Value": "MNIST"}])
    print(f"Pipeline {pipeline.name} created successfully.")
    if run_pipeline:
        print("Starting pipeline execution...")
        execution = pipeline.start()
        execution.wait()


if __name__ == "__main__":
    typer.run(main)