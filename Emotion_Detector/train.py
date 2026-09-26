"""
train.py
--------
Trains the emotion CNN and saves the best checkpoint. This is the ONLY
place training happens. Run it by hand when you want a new model:

    python train.py --data-dir ./data

NeoMind, monitor.py and model.py never import or run this file.

The dataset folder must directly contain one sub-folder per emotion, each
holding that emotion's images (torchvision ImageFolder layout):

    data/Angry/*.jpg   data/Fear/*.jpg   data/Happy/*.jpg   ...
"""

import argparse
import sys
import time
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset
from torchvision import datasets

from model import (
    CNN,
    DEFAULT_MODEL_PATH,
    IMG_SIZE,
    BASE_DIR,
    get_eval_transform,
    get_train_transform,
    save_checkpoint,
    select_device,
)


def parse_args():
    p = argparse.ArgumentParser(description="Train the NeoMind emotion detector.")
    p.add_argument("--data-dir", type=Path, default=BASE_DIR / "data",
                   help="Folder that directly contains one sub-folder per emotion (default: ./data)")
    p.add_argument("--output", type=Path, default=DEFAULT_MODEL_PATH,
                   help="Where to save the trained model (default: models/trained_model.pth)")
    p.add_argument("--epochs", type=int, default=30)
    p.add_argument("--batch-size", type=int, default=32)
    p.add_argument("--lr", type=float, default=0.001)
    p.add_argument("--val-split", type=float, default=0.2)
    p.add_argument("--num-workers", type=int, default=2,
                   help="DataLoader worker processes (original was 12, too many for most machines)")
    p.add_argument("--seed", type=int, default=42, help="Makes the train/validation split repeatable")
    p.add_argument("--patience", type=int, default=0,
                   help="Stop after this many epochs without validation improvement (0 = never stop early)")
    return p.parse_args()


def build_loaders(args, device):
    if not args.data_dir.is_dir():
        sys.exit(f"Dataset folder not found: {args.data_dir}\n"
                 "Unzip the dataset there, or pass --data-dir <folder>.")

    # Two views of the same folder: one with augmentation (training) and one
    # without (validation). The original notebook shared one dataset object,
    # so changing the validation transform also changed the training one.
    train_full = datasets.ImageFolder(args.data_dir, transform=get_train_transform(IMG_SIZE))
    val_full = datasets.ImageFolder(args.data_dir, transform=get_eval_transform(IMG_SIZE))

    class_names = train_full.classes
    if len(class_names) < 2:
        sys.exit(f"Found {len(class_names)} class folder(s) in {args.data_dir}; need at least 2.\n"
                 "--data-dir must be the folder that directly contains the emotion folders.")

    n = len(train_full)
    val_count = int(n * args.val_split)
    train_count = n - val_count
    if val_count < 1 or train_count < 1:
        sys.exit(f"Not enough images ({n}) for a {args.val_split:.0%} validation split.")

    generator = torch.Generator().manual_seed(args.seed)
    perm = torch.randperm(n, generator=generator).tolist()
    val_idx, train_idx = perm[:val_count], perm[val_count:]

    pin = device.type == "cuda"
    train_loader = DataLoader(Subset(train_full, train_idx), batch_size=args.batch_size,
                              shuffle=True, num_workers=args.num_workers, pin_memory=pin)
    val_loader = DataLoader(Subset(val_full, val_idx), batch_size=args.batch_size,
                            shuffle=False, num_workers=args.num_workers, pin_memory=pin)
    return train_loader, val_loader, class_names, train_count, val_count


def run_epoch(model, loader, criterion, device, optimizer=None):
    """One pass over `loader`. Trains if an optimizer is given, otherwise
    just evaluates. Returns (average loss, accuracy)."""
    training = optimizer is not None
    model.train(training)
    total_loss, correct, total = 0.0, 0, 0

    with torch.set_grad_enabled(training):
        for images, labels in loader:
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)

            if training:
                optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            if training:
                loss.backward()
                optimizer.step()

            total_loss += loss.item() * images.size(0)
            correct += (outputs.argmax(dim=1) == labels).sum().item()
            total += images.size(0)

    return total_loss / total, correct / total


def main():
    args = parse_args()
    torch.manual_seed(args.seed)
    device = select_device()

    train_loader, val_loader, class_names, train_count, val_count = build_loaders(args, device)

    print(f"Device: {device}")
    print(f"Dataset: {args.data_dir}")
    print(f"Classes ({len(class_names)}): {class_names}")
    print(f"Train images: {train_count}  Validation images: {val_count}")
    print(f"Model will be saved to: {args.output}")

    model = CNN(num_classes=len(class_names), img_size=IMG_SIZE).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)

    best_acc = 0.0
    epochs_without_improvement = 0

    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        train_loss, train_acc = run_epoch(model, train_loader, criterion, device, optimizer)
        val_loss, val_acc = run_epoch(model, val_loader, criterion, device)
        elapsed = time.time() - t0

        print(f"EPOCH {epoch}/{args.epochs}  train_loss={train_loss:.3f} train_acc={train_acc:.3f}  "
              f"val_loss={val_loss:.3f} val_acc={val_acc:.3f}  time={elapsed:.1f}s")

        if val_acc > best_acc:
            best_acc = val_acc
            epochs_without_improvement = 0
            save_checkpoint(model, class_names, IMG_SIZE, args.output)
            print(f"Saving the model with the best validation accuracy : {best_acc:.3f} to {args.output}")
        else:
            epochs_without_improvement += 1
            if args.patience and epochs_without_improvement >= args.patience:
                print(f"No improvement for {args.patience} epochs, stopping early.")
                break

    print(f"Training completed. Best validation accuracy: {best_acc:.3f}")
    print(f"Saved model: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
