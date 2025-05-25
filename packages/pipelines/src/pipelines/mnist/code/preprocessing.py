import os
import pathlib
import pandas as pd
import numpy as np


def ensure_parent_dir_exists(file_path):
    """Ensures that the parent directory of the given file path exists.
    If the parent directory does not exist, it is created.

    Args:
        file_path: The path to the file.
    """
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def save_as_parquet(np_array, file_path):
    """
    Save a numpy array as a parquet file.

    Args:
        np_array (np.ndarray): The numpy array to save.
        file_path (str): The path where the parquet file will be saved.
    """
    ensure_parent_dir_exists(file_path)
    df = pd.DataFrame(np_array)
    df.columns = df.columns.astype(str)
    df.to_parquet(file_path, index=False)
    print(f"Saved data to {file_path}")


def main(base_dir="/opt/ml/processing"):
    df = pd.read_parquet(
        f"{base_dir}/input/all.parquet",
    )

    # As there is no feature engineering required in mnist,
    # we can directly split the data into train, validation, and test sets.

    X = df.to_numpy()
    train, validation, test = np.split(X, [int(0.7 * len(X)), int(0.85 * len(X))])

    save_as_parquet(train, f"{base_dir}/train/train.parquet")
    save_as_parquet(validation, f"{base_dir}/validation/validation.parquet")
    save_as_parquet(test, f"{base_dir}/test/test.parquet")


if __name__ == "__main__":
    print(os.environ)
    main()
