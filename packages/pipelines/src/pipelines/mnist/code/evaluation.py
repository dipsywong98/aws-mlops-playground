from importlib import import_module
import json
import os
import pathlib
import tarfile

import torch


try:
    from inference import model_fn
    from mnist import MnistDataset, Net
except ImportError:
    from .inference import model_fn
    from .mnist import MnistDataset, Net


def test(model, device, test_loader):
    model.eval()
    total = 0.0
    correct = 0.0
    with torch.no_grad():
        for data, target in test_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            pred = output.argmax(
                dim=1, keepdim=True
            )  # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()
            total += target.size(0)

    return correct / total


def main(
    model_path="/opt/ml/processing/model/model.tar.gz",
    test_path="/opt/ml/processing/test/test.parquet",
    output_dir="/opt/ml/processing/evaluation",
    extract_path=".",
    use_accel=torch.accelerator.is_available(),
    batch_size=1000,
):
    if use_accel:
        device = torch.accelerator.current_accelerator()
    else:
        device = torch.device("cpu")

    with tarfile.open(model_path) as tar:
        tar.extractall(path=extract_path)

    model: Net = model_fn(extract_path, None)

    test_kwargs = {"batch_size": batch_size}
    test_dataset = MnistDataset(test_path)

    test_loader = torch.utils.data.DataLoader(test_dataset, **test_kwargs)

    report_dict = {
        "accuracy": {"value": test(model, device, test_loader)},
    }

    pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)

    evaluation_path = f"{output_dir}/evaluation.json"
    with open(evaluation_path, "w") as f:
        f.write(json.dumps(report_dict))


if __name__ == "__main__":
    main()
