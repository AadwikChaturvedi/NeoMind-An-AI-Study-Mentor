"""
monitor.py
----------
Webcam inference for the emotion detector.

Pipeline (this is the whole point of this phase — the model NEVER sees
a raw, undetected frame anymore):

    webcam frame -> face_detector.detect_faces() -> largest face box
                 -> face_detector.crop_face()     -> face crop
                 -> model.preprocess_frame()      -> tensor
                 -> model(tensor)                 -> emotion + confidence

This file ONLY runs inference. It never trains anything and never
imports train.py — it loads whatever checkpoint train.py already saved
to models/trained_model.pth (or a path you pass explicitly) and
classifies faces found in webcam frames with it.

Run with:

    python monitor.py
    python monitor.py --model ./models/trained_model.pth --camera 0
    python monitor.py --min-face 25   # detect smaller/farther faces

Press 'q' in the window to quit.

Standalone dev tool for testing the detector in isolation — not wired
into NeoMind's FastAPI backend yet. That's a later phase.
"""

import argparse
import sys
from pathlib import Path

import cv2
import torch

from face_detector import DEFAULT_MIN_FACE, crop_face, detect_faces, load_face_detector
from model import DEFAULT_MODEL_PATH, load_model, preprocess_frame, select_device

BOX_COLOR = (0, 255, 0)
NO_FACE_COLOR = (0, 165, 255)  # amber — distinct from a found-face box at a glance


def parse_args():
    p = argparse.ArgumentParser(description="Run webcam face + emotion inference with a trained model.")
    p.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH,
                    help="Path to a trained checkpoint (default: models/trained_model.pth)")
    p.add_argument("--camera", type=int, default=0, help="OpenCV camera index (default: 0)")
    p.add_argument("--min-face", type=int, default=DEFAULT_MIN_FACE,
                    help=f"Smallest face width/height to detect, in pixels (default: {DEFAULT_MIN_FACE}). "
                         "Lower this if faces farther from the camera aren't being picked up.")
    return p.parse_args()


def _draw_no_face_notice(frame):
    cv2.putText(frame, "No face detected", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, NO_FACE_COLOR, 2)


def _draw_face_box(frame, box):
    x, y, w, h = box
    cv2.rectangle(frame, (x, y), (x + w, y + h), BOX_COLOR, 2)


def _draw_label(frame, box, text):
    x, y, w, h = box
    # Label sits just above the box; if the box is right at the top edge,
    # drop the label just inside it instead of letting it run off-screen.
    label_y = y - 10 if y - 10 > 15 else y + 20
    cv2.putText(frame, text, (x, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, BOX_COLOR, 2)


def run(model_path: Path, camera_index: int, min_face: int) -> int:
    device = select_device()

    try:
        model, class_names, img_size = load_model(model_path, device)
    except (FileNotFoundError, ValueError) as e:
        print(str(e))
        return 1

    face_detector = load_face_detector()

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

            # max_faces=1: this phase's pipeline is one face in, one
            # prediction out (see the module docstring). detect_faces()
            # already returns the largest box first, so this keeps
            # whichever face is closest/most prominent if more than one
            # is in frame.
            boxes = detect_faces(frame, face_detector, min_face_size=min_face, max_faces=1)

            if not boxes:
                _draw_no_face_notice(frame)
            else:
                box = boxes[0]
                _draw_face_box(frame, box)

                face_crop = crop_face(frame, box)
                # crop_face() only returns None for a box clamped to
                # nothing at the frame edge — rare, but skip classifying
                # a frame like that rather than feeding the model an
                # empty image. The box still gets drawn above either way.
                if face_crop is not None and face_crop.size > 0:
                    tensor = preprocess_frame(face_crop, img_size).to(device)

                    with torch.no_grad():
                        outputs = model(tensor)
                        probs = torch.nn.functional.softmax(outputs, dim=1)
                        confidence, idx = torch.max(probs, dim=1)
                        label = class_names[idx.item()]

                    _draw_label(frame, box, f"{label} {confidence.item():.2f}")

            cv2.imshow("Emotion Detector (q to quit)", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        webcam.release()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    args = parse_args()
    sys.exit(run(args.model, args.camera, args.min_face))
