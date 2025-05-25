import pandas as pd
from pipelines.mnist.code.preprocessing import main as preprocess
import os
import shutil
from pathlib import Path


def test_preprocessing_generate_train_test_validation_parquets():
    # clean tmp directory that store data
    tmp_dir = Path("/tmp/mnist")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    # copy fixture from fixture/tmp to tmp
    current_dir = Path(__file__).parent
    fixture_dir = os.path.join(current_dir, "fixtures")
    # copy all.parquet to /tmp/mnist/processing/input
    os.makedirs(tmp_dir, exist_ok=True)
    os.makedirs(os.path.join(tmp_dir, "processing/input"), exist_ok=True)
    shutil.copy(
        os.path.join(fixture_dir, "all.parquet"),
        os.path.join(tmp_dir, "processing/input/all.parquet"),
    )

    # assert directory not exists
    assert not os.path.exists(os.path.join(tmp_dir, "processing/train"))
    assert not os.path.exists(os.path.join(tmp_dir, "processing/test"))
    assert not os.path.exists(os.path.join(tmp_dir, "processing/validation"))

    # run the preprocessing script
    preprocess(os.path.join(tmp_dir, "processing"))

    assert os.path.exists(os.path.join(tmp_dir, "processing/train"))
    assert os.path.exists(os.path.join(tmp_dir, "processing/test"))
    assert os.path.exists(os.path.join(tmp_dir, "processing/validation"))

    # assert train.parquet, validation.parquet, test.parquet exists
    assert os.path.exists(os.path.join(tmp_dir, "processing/train/train.parquet"))
    assert os.path.exists(
        os.path.join(tmp_dir, "processing/validation/validation.parquet")
    )
    assert os.path.exists(os.path.join(tmp_dir, "processing/test/test.parquet"))

    # assert train.parquet, validation.parquet, test.parquet are pd dataframes of len
    train_df = pd.read_parquet(os.path.join(tmp_dir, "processing/train/train.parquet"))
    validation_df = pd.read_parquet(
        os.path.join(tmp_dir, "processing/validation/validation.parquet")
    )
    test_df = pd.read_parquet(os.path.join(tmp_dir, "processing/test/test.parquet"))

    assert len(train_df) > 0
    assert len(validation_df) > 0
    assert len(test_df) > 0
    # assert train_df, validation_df, test_df are pd dataframes of shape (n, 785)
    assert train_df.shape[1] == 785
    assert validation_df.shape[1] == 785
    assert test_df.shape[1] == 785
