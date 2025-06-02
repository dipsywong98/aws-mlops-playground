import os
import pandas as pd
from sklearn.model_selection import train_test_split


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

    size = 28 * 28
    # ensure the data columns is of type float
    # df = df.astype('Float32')
    # df.iloc[:, :size] = df.iloc[:, :size].astype('Float32')
    # ensure the input data is normalized
    df.iloc[:, :size] = (df.iloc[:, :size] - df.iloc[:, :size].min().min()) / (df.iloc[:, :size].max().max() - df.iloc[:, :size].min().min())

    # As there is no feature engineering required in mnist,
    # we can directly split the data into train, validation, and test sets.


    # Stratified split into 90%, 5%, and 5%
    train_df, temp_df = train_test_split(df, test_size=0.1, stratify=df['label'], random_state=42)
    val_df, test_df = train_test_split(temp_df, test_size=0.5, stratify=temp_df['label'], random_state=42)

    print(train_df['label'].value_counts())  # Check distribution
    print(val_df['label'].value_counts())  # Check distribution
    print(test_df['label'].value_counts())  # Check distribution

    save_as_parquet(train_df, f"{base_dir}/train/train.parquet")
    save_as_parquet(val_df, f"{base_dir}/validation/validation.parquet")
    save_as_parquet(test_df, f"{base_dir}/test/test.parquet")


if __name__ == "__main__":
    print(os.environ)
    main()
