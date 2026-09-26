"""
monitor.py
----------
Webcam inference for the emotion detector.

This file ONLY runs inference. It never trains anything and never
imports train.py — it loads whatever checkpoint train.py already saved
to models/trained_model.pth (or a path you pass explicitly) and
classifies webcam frames with it.

Run with:

    python monitor.py
    python monitor.py --model ./models/trained_model.pth --camera 0

Press 'q' in the window to quit.

Standalone dev tool for testing the detector in isolation — not wired
into NeoMind's FastAPI backend yet. That's a later phase.
"""

import argparse
import sys
from pathlib import Path

import cv2
import torch

from model import DEFAULT_MODEL_PATH, load_model, preprocess_frame, select_device


def parse_args():
    p = argparse.ArgumentParser(description="Run webcam inference with a trained emotion model.")
    p.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH,
                    help="Path to a trained checkpoint (default: models/trained_model.pth)")
    p.add_argument("--camera", type=int, default=0, help="OpenCV camera index (default: 0)")
    return p.parse_args()


def run(model_path: Path, camera_index: int) -> int:
    device = select_device()

    try:
        model, class_names, img_size = load_model(model_path, device)
    except (FileNotFoundError, ValueError) as e:
        print(str(e))
        return 1

    print(f"Loaded model ({len(class_names)} classes: {class_names}) on {device}")
    print("Starting webcam — press 'q' to quit.")

    webcam = cv2.VideoCapture(camera_index)
    if not webcam.isOpened():
        print(f"Couldn't open webcam at index {camera_index}.")
        return 1

    try:
        while True:
            ret, frame = webcam.read()
            if not ret:
                print("Webcam stopped returning frames.")
                break

            tensor = preprocess_frame(frame, img_size).to(device)

            with torch.no_grad():
                outputs = model(tensor)
                probs = torch.nn.functional.softmax(outputs, dim=1)
                confidence, idx = torch.max(probs, dim=1)
                label = class_names[idx.item()]

            cv2.putText(frame, f"{label} {confidence.item():.2f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            cv2.imshow("Emotion Detector (q to quit)", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        webcam.release()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    args = parse_args()
    sys.exit(run(args.model, args.camera))
