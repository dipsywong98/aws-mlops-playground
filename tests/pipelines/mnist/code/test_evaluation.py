import json
from pipelines.mnist.code.evaluation import main as evaluate_output_accuracy
from fixtures.fixtures import tmp_dir, test_parquet, model_tar_gz  # noqa: F401
import os


def test_evaluation_output_accuracy(tmp_dir, test_parquet, model_tar_gz):  # noqa: F811
    output_dir = os.path.join(tmp_dir, "processing/evaluation")
    evaluate_output_accuracy(
        model_path=model_tar_gz,
        test_path=test_parquet,
        output_dir=output_dir,
        extract_path=tmp_dir,
    )
    evaluation_path = os.path.join(output_dir, "evaluation.json")
    result = json.loads(open(evaluation_path, "r").read())
    print(result)
    assert "accuracy" in result
    assert result["accuracy"]["value"] > 0
