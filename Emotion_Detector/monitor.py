"""
monitor.py
----------
Webcam inference for the emotion detector, wrapped in a simple focus
monitor.

Pipeline:

    webcam frame -> face_detector.detect_faces() -> largest face box
                 -> face_detector.crop_face()     -> face crop
                 -> model.preprocess_frame()      -> tensor
                 -> model(tensor)                 -> emotion + confidence
                 -> focus_monitor.FocusMonitor     -> focus_state, focus_score, ...

This file ONLY runs inference. It never trains anything and never
imports train.py — it loads whatever checkpoint train.py already saved
to models/trained_model.pth (or a path you pass explicitly) and
classifies faces found in webcam frames with it.

Run with:

    python monitor.py
    python monitor.py --model ./models/trained_model.pth --camera 0
    python monitor.py --min-face 25              # pick up farther faces
    python monitor.py --distraction-threshold 5  # more tolerant of brief look-aways

Press 'q' in the window to quit.

Standalone dev tool for testing the detector (and now the focus
monitor) in isolation — not wired into NeoMind's FastAPI backend yet.
That's a later phase.
"""

import argparse
import sys
from pathlib import Path

import cv2
import torch

from face_detector import DEFAULT_MIN_FACE, crop_face, detect_faces, load_face_detector
from focus_monitor import DEFAULT_DISTRACTION_THRESHOLD, FocusMonitor
from model import DEFAULT_MODEL_PATH, load_model, preprocess_frame, select_device

BOX_COLOR = (0, 255, 0)         # green — a face is present
NO_FACE_COLOR = (0, 165, 255)   # amber — brief absence, not (yet) a distraction
DISTRACTED_COLOR = (0, 0, 255)  # red — prolonged absence, counted as a distraction
PANEL_TEXT_COLOR = (255, 255, 255)

STATE_COLORS = {
    "focused": BOX_COLOR,
    "no_face": NO_FACE_COLOR,
    "distracted": DISTRACTED_COLOR,
}


def parse_args():
    p = argparse.ArgumentParser(description="Run webcam face + emotion inference with a trained model.")
    p.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH,
                    help="Path to a trained checkpoint (default: models/trained_model.pth)")
    p.add_argument("--camera", type=int, default=0, help="OpenCV camera index (default: 0)")
    p.add_argument("--min-face", type=int, default=DEFAULT_MIN_FACE,
                    help=f"Smallest face width/height to detect, in pixels (default: {DEFAULT_MIN_FACE}). "
                         "Lower this if faces farther from the camera aren't being picked up.")
    p.add_argument("--distraction-threshold", type=float, default=DEFAULT_DISTRACTION_THRESHOLD,
                    help=f"Seconds of continuous face absence before it counts as a distraction "
                         f"(default: {DEFAULT_DISTRACTION_THRESHOLD}). A brief look-away shorter than "
                         "this never increments distraction_count.")
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


def _draw_status_panel(frame, snapshot):
    """Small status block, bottom-left, showing the focus_monitor's
    output. Kept separate from the top-left "No face detected" notice
    and the per-face label so none of them overlap."""
    h = frame.shape[0]
    state = snapshot["focus_state"]
    color = STATE_COLORS.get(state, PANEL_TEXT_COLOR)

    lines = [
        (f"Focus: {state.upper()}  Score: {snapshot['focus_score']:.1f}", color),
        (f"Distractions: {snapshot['distraction_count']}  "
         f"({snapshot['total_distraction_time']:.1f}s)", PANEL_TEXT_COLOR),
        (f"Monitored: {snapshot['total_monitored_time']:.1f}s", PANEL_TEXT_COLOR),
    ]
    y = h - 15 - (len(lines) - 1) * 25
    for text, text_color in lines:
        cv2.putText(frame, text, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
        y += 25


def run(model_path: Path, camera_index: int, min_face: int, distraction_threshold: float) -> int:
    device = select_device()

    try:
        model, class_names, img_size = load_model(model_path, device)
    except (FileNotFoundError, ValueError) as e:
        print(str(e))
        return 1

    face_detector = load_face_detector()
    focus_monitor = FocusMonitor(distraction_threshold=distraction_threshold)

    print(f"Loaded model ({len(class_names)} classes: {class_names}) on {device}")
    print(f"Distraction threshold: {distraction_threshold}s of continuous face absence")
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

            # max_faces=1: this pipeline is one face in, one prediction
            # out. detect_faces() already returns the largest box first,
            # so this keeps whichever face is closest/most prominent if
            # more than one is in frame.
            boxes = detect_faces(frame, face_detector, min_face_size=min_face, max_faces=1)
            emotion_label = None

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
                        emotion_label = class_names[idx.item()]

                    _draw_label(frame, box, f"{emotion_label} {confidence.item():.2f}")

            # face_detected reflects whether a face was FOUND, regardless
            # of whether classification also ran -- that's the signal the
            # focus monitor cares about. emotion is purely supplementary:
            # never read back into focus_state/focus_score/distraction_count.
            snapshot = focus_monitor.update(face_detected=bool(boxes), emotion=emotion_label)
            _draw_status_panel(frame, snapshot)

            cv2.imshow("Emotion Detector (q to quit)", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        webcam.release()
        cv2.destroyAllWindows()

    return 0


if __name__ == "__main__":
    args = parse_args()
    sys.exit(run(args.model, args.camera, args.min_face, args.distraction_threshold))
