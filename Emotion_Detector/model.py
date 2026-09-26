"""
model.py
--------
Model definition, preprocessing and checkpoint loading for the NeoMind
emotion detector.

Shared by train.py (training) and monitor.py (webcam inference), so both
use exactly the same architecture and the same preprocessing. Importing
this module has no side effects: no training, no dataset access, no file
writes.

Checkpoint format (unchanged from the original Colab notebook):
    {"model_state": state_dict, "class_names": [...], "img_size": 64}
"""

from pathlib import Path

import torch
import torch.nn as nn
from torchvision import transforms

IMG_SIZE = 64
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL_PATH = BASE_DIR / "models" / "trained_model.pth"


class CNN(nn.Module):
    """The original 3-block CNN, layer for layer. For IMG_SIZE=64 the
    flattened feature size is 64 * 8 * 8 = 4096, exactly as before."""

    def __init__(self, num_classes, img_size=IMG_SIZE):
        super().__init__()
        if img_size % 8 != 0:
            raise ValueError("img_size must be divisible by 8 (three 2x2 poolings).")

        self.features = nn.Sequential(
            nn.Conv2d(3, 16, kernel_size=3, padding=1),
            nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(16, 32, kernel_size=3, padding=1),
            nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(), nn.MaxPool2d(2),
        )

        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * (img_size // 8) ** 2, 128),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(128, num_classes),
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


def get_train_transform(img_size=IMG_SIZE):
    """Training transform: same as the original plus Grayscale(3), which is
    a no-op for grayscale images and makes colour webcam frames match the
    grayscale training data."""
    return transforms.Compose([
        transforms.Grayscale(num_output_channels=3),
        transforms.Resize((img_size, img_size)),
        transforms.RandomHorizontalFlip(),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])


def get_eval_transform(img_size=IMG_SIZE):
    """Validation / inference transform: identical to training but with no
    random flip, so results are deterministic. The original notebook used
    the flip here by mistake."""
    return transforms.Compose([
        transforms.Grayscale(num_output_channels=3),
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize(IMAGENET_MEAN, IMAGENET_STD),
    ])


def select_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def save_checkpoint(model, class_names, img_size=IMG_SIZE, path=DEFAULT_MODEL_PATH):
    """Writes the trained model in the checkpoint format described above.
    Creates the parent folder if needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_state": model.state_dict(),
            "class_names": list(class_names),
            "img_size": img_size,
        },
        path,
    )


def load_model(path=DEFAULT_MODEL_PATH, device=None):
    """Loads a trained model for inference.

    Returns (model, class_names, img_size). The model is on `device` and in
    eval mode. Rebuilds the network from the checkpoint alone, so no dataset
    is needed. Raises FileNotFoundError with a clear hint if the file is
    missing; it never trains anything.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(
            f"No trained model found at {path}. "
            "Train one first with: python train.py --data-dir <dataset folder>"
        )

    device = torch.device(device) if device is not None else select_device()
    # weights_only=True: the checkpoint holds only tensors, strings and ints,
    # so there's no reason to allow arbitrary pickled code.
    checkpoint = torch.load(path, map_location=device, weights_only=True)

    missing = {"model_state", "class_names", "img_size"} - set(checkpoint)
    if missing:
        raise ValueError(f"{path} is not a valid checkpoint (missing: {sorted(missing)}).")

    class_names = list(checkpoint["class_names"])
    img_size = int(checkpoint["img_size"])

    model = CNN(num_classes=len(class_names), img_size=img_size).to(device)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()
    return model, class_names, img_size


def preprocess_frame(frame_bgr, img_size=IMG_SIZE):
    """Converts a single OpenCV BGR frame (a H x W x 3 numpy array) into a
    normalized, batched tensor using the exact same pipeline as
    get_eval_transform() — just starting from an in-memory frame instead
    of a file path, so a webcam frame is preprocessed identically to a
    training image.

    cv2 and PIL are imported here rather than at module level, so
    importing model.py (e.g. from train.py, or later from the FastAPI
    backend) never requires OpenCV or Pillow — only monitor.py, which
    actually touches a webcam, needs them.
    """
    import cv2
    from PIL import Image

    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(rgb)
    tensor = get_eval_transform(img_size)(image)
    return tensor.unsqueeze(0)
