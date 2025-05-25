import pandas as pd
from pipelines.mnist.code.preprocessing import main as preprocess
import os
from fixtures.fixtures import *


def test_preprocessing_generate_train_test_validation_parquets(tmp_dir, all_parquet):
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
