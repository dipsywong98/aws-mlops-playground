import os
from pathlib import Path
from fixtures.fixtures import tmp_dir, train_parquet, validation_parquet  # noqa: F401
from pipelines.mnist.code.mnist import main as train_mnist


def test_mnist_train(tmp_dir, train_parquet, validation_parquet):  # noqa: F811
    assert not os.path.exists(os.path.join(tmp_dir, "processing/model"))

    # Run the training script
    train_mnist(
        train_dir=Path(train_parquet).parent,
        validation_dir=Path(validation_parquet).parent,
        model_dir=os.path.join(tmp_dir, "processing/model"),
        dry_run=True,
        epochs=1,
    )

    # Check if the model directory exists
    assert os.path.exists(os.path.join(tmp_dir, "processing/model"))

    # Check if the model file exists
    assert os.path.exists(os.path.join(tmp_dir, "processing/model/model.pth"))
    assert os.path.exists(os.path.join(tmp_dir, "processing/model/model.onnx"))


def test_mnist_train_real(tmp_dir, train_parquet, validation_parquet):  # noqa: F811
    assert not os.path.exists(os.path.join(tmp_dir, "processing/model"))

    # Run the training script
    train_mnist(
        train_dir=Path(train_parquet).parent,
        validation_dir=Path(validation_parquet).parent,
        model_dir=os.path.join(tmp_dir, "processing/model"),
        dry_run=False,
        epochs=10,
    )

    # Check if the model directory exists
    assert os.path.exists(os.path.join(tmp_dir, "processing/model"))

    # Check if the model file exists
    assert os.path.exists(os.path.join(tmp_dir, "processing/model/model.pth"))
    assert os.path.exists(os.path.join(tmp_dir, "processing/model/model.onnx"))
