import os
from pathlib import Path
import shutil

import pytest


fixture_dir = Path(__file__).parent


@pytest.fixture
def tmp_dir():
    tmp_dir = Path("/tmp/mnist")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    # copy all.parquet to /tmp/mnist/processing/input
    os.makedirs(tmp_dir, exist_ok=True)
    yield tmp_dir


@pytest.fixture
def all_parquet(tmp_dir):
    os.makedirs(os.path.join(tmp_dir, "processing/input"), exist_ok=True)
    dest = os.path.join(tmp_dir, "processing/input/all.parquet")
    shutil.copy(
        os.path.join(fixture_dir, "all.parquet"),
        dest,
    )
    return dest


@pytest.fixture
def test_parquet(tmp_dir):
    os.makedirs(os.path.join(tmp_dir, "processing/test"), exist_ok=True)
    dest = os.path.join(tmp_dir, "processing/test/test.parquet")
    shutil.copy(
        os.path.join(fixture_dir, "test.parquet"),
        dest,
    )
    return dest


@pytest.fixture
def train_parquet(tmp_dir):
    os.makedirs(os.path.join(tmp_dir, "processing/train"), exist_ok=True)
    dest = os.path.join(tmp_dir, "processing/train/train.parquet")
    shutil.copy(
        os.path.join(fixture_dir, "train.parquet"),
        dest,
    )
    return dest


@pytest.fixture
def validation_parquet(tmp_dir):
    os.makedirs(os.path.join(tmp_dir, "processing/validation"), exist_ok=True)
    dest = os.path.join(tmp_dir, "processing/validation/validation.parquet")
    shutil.copy(
        os.path.join(fixture_dir, "validation.parquet"),
        dest,
    )
    return dest


@pytest.fixture
def model_tar_gz(tmp_dir):
    os.makedirs(os.path.join(tmp_dir, "processing/model"), exist_ok=True)
    dest = os.path.join(tmp_dir, "processing/model/model.tar.gz")
    shutil.copy(
        os.path.join(fixture_dir, "model.tar.gz"),
        dest,
    )
    return dest
