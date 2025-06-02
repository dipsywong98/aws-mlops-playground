import pandas as pd
from pipelines.mnist.code.preprocessing import main as preprocess
import os
from fixtures.fixtures import tmp_dir, all_parquet  # noqa: F401


def check_df(df: pd.DataFrame):
    size = 28*28
    assert len(df) > 0
    assert df.shape[1] == 785
    assert set(df['label'].value_counts().keys()) == set(range(10))
    assert df.iloc[:, :size].min().min() == 0.0
    assert df.iloc[:, :size].max().max() == 1.0
    assert df["label"].dtype == "int64"

def test_preprocessing_generate_train_test_validation_parquets(tmp_dir, all_parquet):  # noqa: F811
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

    check_df(train_df)
    check_df(validation_df)
    check_df(test_df)

    assert len(train_df) == 63000
    assert len(validation_df) == 3500
    assert len(test_df) == 3500
