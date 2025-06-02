import argparse
import os
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.optim.lr_scheduler import StepLR
from torch.utils.data import Dataset


class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.dropout1 = nn.Dropout(0.25)
        self.dropout2 = nn.Dropout(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = F.relu(x)
        x = self.conv2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        output = F.log_softmax(x, dim=1)
        return output


def train(log_interval, dry_run, model, device, train_loader, optimizer, epoch):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % log_interval == 0:
            print(
                "Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}".format(
                    epoch,
                    batch_idx * len(data),
                    len(train_loader.dataset),
                    100.0 * batch_idx / len(train_loader),
                    loss.item(),
                )
            )
            if dry_run:
                break


def validation(model, device, validation_loader):
    model.eval()
    validation_loss = 0
    correct = 0
    with torch.no_grad():
        for data, target in validation_loader:
            data, target = data.to(device), target.to(device)
            output = model(data)
            validation_loss += F.nll_loss(
                output, target, reduction="sum"
            ).item()  # sum up batch loss
            pred = output.argmax(
                dim=1, keepdim=True
            )  # get the index of the max log-probability
            correct += pred.eq(target.view_as(pred)).sum().item()

    validation_loss /= len(validation_loader.dataset)

    print(
        "\nvalidation set: Average loss: {:.4f}, Accuracy: {}/{} ({:.0f}%)\n".format(
            validation_loss,
            correct,
            len(validation_loader.dataset),
            100.0 * correct / len(validation_loader.dataset),
        )
    )


class MnistDataset(Dataset):
    def __init__(self, data_file):
        self.data = pd.read_parquet(data_file)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        image = self.data.iloc[idx, :-
                               1].values.reshape(1, 28, 28).astype("float32")
        label = self.data.iloc[idx, -1]
        return torch.tensor(image), torch.tensor(label)


def main(batch_size=64,
         validation_batch_size=1000,
         epochs=14,
         lr=1,
         gamma=0.7,
         no_accel=False,
         dry_run=False,
         seed=1,
         log_interval=10,
         save_model=True,
         output_data_dir=os.environ.get("SM_OUTPUT_DATA_DIR"),
         model_dir=os.environ.get("SM_MODEL_DIR"),
         train_dir=os.environ.get("SM_CHANNEL_TRAIN"),
         validation_dir=os.environ.get("SM_CHANNEL_VALIDATION"),
         ):
    use_accel = not no_accel and torch.accelerator.is_available()

    torch.manual_seed(seed)

    if use_accel:
        device = torch.accelerator.current_accelerator()
    else:
        device = torch.device("cpu")

    train_kwargs = {"batch_size": batch_size}
    validation_kwargs = {"batch_size": validation_batch_size}
    if use_accel:
        accel_kwargs = {"num_workers": 1, "pin_memory": True, "shuffle": True}
        train_kwargs.update(accel_kwargs)
        validation_kwargs.update(accel_kwargs)

    dataset1 = MnistDataset(os.path.join(train_dir, "train.parquet"))
    dataset2 = MnistDataset(os.path.join(
        validation_dir, "validation.parquet"))

    train_loader = torch.utils.data.DataLoader(dataset1, **train_kwargs)
    validation_loader = torch.utils.data.DataLoader(
        dataset2, **validation_kwargs)

    model = Net().to(device)
    optimizer = optim.Adadelta(model.parameters(), lr=lr)

    scheduler = StepLR(optimizer, step_size=1, gamma=gamma)
    for epoch in range(1, epochs + 1):
        train(log_interval, dry_run, model, device, train_loader, optimizer, epoch)
        validation(model, device, validation_loader)
        scheduler.step()

    output_dir = model_dir
    os.makedirs(output_dir, exist_ok=True)
    torch.save(model.state_dict(), f"{output_dir}/model.pth")
    example_inputs = (torch.randn(1, 1, 28, 28),)
    onnx_program = torch.onnx.export(model, example_inputs, dynamo=True)
    onnx_program.optimize()
    onnx_program.save(f"{output_dir}/model.onnx")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PyTorch MNIST Example")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=64,
        metavar="N",
        help="input batch size for training (default: 64)",
    )
    parser.add_argument(
        "--validation-batch-size",
        type=int,
        default=1000,
        metavar="N",
        help="input batch size for validationing (default: 1000)",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=14,
        metavar="N",
        help="number of epochs to train (default: 14)",
    )
    parser.add_argument(
        "--lr",
        type=float,
        default=1.0,
        metavar="LR",
        help="learning rate (default: 1.0)",
    )
    parser.add_argument(
        "--gamma",
        type=float,
        default=0.7,
        metavar="M",
        help="Learning rate step gamma (default: 0.7)",
    )
    parser.add_argument("--no-accel", action="store_true",
                        help="disables accelerator")
    parser.add_argument(
        "--dry-run", action="store_true", help="quickly check a single pass"
    )
    parser.add_argument(
        "--seed", type=int, default=1, metavar="S", help="random seed (default: 1)"
    )
    parser.add_argument(
        "--log-interval",
        type=int,
        default=10,
        metavar="N",
        help="how many batches to wait before logging training status",
    )
    parser.add_argument(
        "--save-model",
        action="store_true",
        default=True,
        help="For Saving the current Model",
    )
    parser.add_argument(
        "--output-data-dir", type=str, default=os.environ["SM_OUTPUT_DATA_DIR"]
    )
    parser.add_argument("--model-dir", type=str,
                        default=os.environ["SM_MODEL_DIR"])
    parser.add_argument("--train", type=str,
                        default=os.environ["SM_CHANNEL_TRAIN"])
    parser.add_argument(
        "--validation", type=str, default=os.environ["SM_CHANNEL_VALIDATION"]
    )
    args = parser.parse_args()
    main(
        batch_size=args.batch_size,
        validation_batch_size=args.validation_batch_size,
        epochs=args.epochs,
        lr=args.lr,
        gamma=args.gamma,
        no_accel=args.no_accel,
        dry_run=args.dry_run,
        seed=args.seed,
        log_interval=args.log_interval,
        save_model=args.save_model,
        output_data_dir=args.output_data_dir,
        model_dir=args.model_dir,
        train_dir=args.train,
        validation_dir=args.validation
    )
