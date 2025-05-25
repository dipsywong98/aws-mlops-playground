import pandas as pd
import numpy as np

def main():
    base_dir = "/opt/ml/processing"

    df = pd.read_parquet(
        f"{base_dir}/input/all.parquet",
    )

    # As there is no feature engineering required in mnist,
    # we can directly split the data into train, validation, and test sets.

    X = df.to_numpy()
    train, validation, test = np.split(X, [int(0.7 * len(X)), int(0.85 * len(X))])


    pd.DataFrame(train).to_parquet(f"{base_dir}/train/train.parquet", header=False, index=False)
    pd.DataFrame(validation).to_parquet(
        f"{base_dir}/validation/validation.parquet", header=False, index=False
    )
    pd.DataFrame(test).to_parquet(f"{base_dir}/test/test.parquet", header=False, index=False)

if __name__ == "__main__":
    main()