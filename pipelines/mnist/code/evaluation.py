import argparse
import json
import os
import pathlib
import pickle
import tarfile

import joblib
import numpy as np
import pandas as pd
import torch
from inference import model_fn


from mnist import MnistDataset, Net



def test(model, device, test_loader):
    model.eval()
    total = 0.0
    correct = 0.0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            pred = output.argmax(dim=1, keepdim=True)  # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()
            total += target.size(0)

    return correct / total


if __name__ == "__main__":
    use_accel = torch.accelerator.is_available()
    batch_size = 1000

    if use_accel:
        device = torch.accelerator.current_accelerator()
    else:
        device = torch.device("cpu")
    model_path = f"/opt/ml/processing/model/model.tar.gz"
    with tarfile.open(model_path) as tar:
        tar.extractall(path=".")

    model: Net = model_fn(".")

    test_path = "/opt/ml/processing/test/test.parquet"
    df = pd.read_parquet(test_path)

    y_test = df.iloc[:, 0].to_numpy()
    df.drop(df.columns[0], axis=1, inplace=True)


    
    test_kwargs = {'batch_size': batch_size}
    test_dataset = MnistDataset("/opt/ml/processing/test/test.parquet")

    test_loader = torch.utils.data.DataLoader(test_dataset,**test_kwargs)

    report_dict = {
        "accuracy ": test(model, device, test_loader),
    }

    output_dir = "/opt/ml/processing/evaluation"
    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)

    evaluation_path = f"{output_dir}/evaluation.json"
    with open(evaluation_path, "w") as f:
        f.write(json.dumps(report_dict))