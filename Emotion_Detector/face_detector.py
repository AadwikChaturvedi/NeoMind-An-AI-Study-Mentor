"""
face_detector.py
----------------
Lightweight face detection for the emotion pipeline, using the Haar
cascade that ships inside OpenCV itself — no extra download, no extra
framework, and it runs comfortably on CPU.

Only depends on OpenCV. Nothing here imports torch or the emotion
model, so it can be imported and tested on its own (and reused later
by the FastAPI backend).

Pipeline role:

    frame -> detect_faces() -> boxes -> crop_face() -> face crop
                                                        |
                             model.preprocess_frame() <-+

Known limit: the frontal-face cascade only finds faces that look
roughly at the camera. A face turned well to the side, tilted a lot, or
looking down at a desk usually comes back as "no face" — which is
useful to know later, when "no face" starts to mean something for focus
tracking.
"""

import os

import cv2

CASCADE_FILE = "haarcascade_frontalface_default.xml"

# Detection runs on a downscaled grayscale copy of the frame. Haar cost
# grows with pixel count, so a 1280x720 webcam is shrunk to 640 wide
# before searching, then the boxes are scaled back up to the original
# frame. 640x480 webcams are left alone.
DETECT_MAX_WIDTH = 640

# Smallest face to look for, in pixels of the ORIGINAL frame. On a
# 640x480 webcam a face at roughly arm's length is 150-200 px wide and
# one at ~3 m is around 40 px. Smaller than this is mostly noise and
# slows the search down.
DEFAULT_MIN_FACE = 40

# Standard Haar search settings. Lower MIN_NEIGHBORS finds more faces
# but adds false positives; higher does the opposite.
SCALE_FACTOR = 1.1
MIN_NEIGHBORS = 5

# Extra margin kept around each detected box when cropping, as a
# fraction of the box size. Haar boxes are tight around the face; a
# little context gets the crop closer to how the training faces are
# framed. A tuning knob, not a magic number.
CROP_PADDING = 0.10


def load_face_detector():
    """Loads OpenCV's bundled frontal-face Haar cascade.

    Raises FileNotFoundError with a clear message if the cascade file
    can't be loaded (an empty CascadeClassifier fails silently
    otherwise, and detection would just never find anything).
    """
    path = os.path.join(cv2.data.haarcascades, CASCADE_FILE)
    detector = cv2.CascadeClassifier(path)
    if detector.empty():
        raise FileNotFoundError(
            f"Couldn't load OpenCV's face cascade at {path}. "
            "Try reinstalling opencv-python."
        )
    return detector


def detect_faces(frame_bgr, detector, min_face_size=DEFAULT_MIN_FACE, max_faces=None):
    """Finds faces in a BGR frame.

    Returns a list of (x, y, w, h) boxes in the coordinates of the frame
    you passed in, largest face first. Returns an empty list when there
    is no face — never raises for that, so a video loop can just keep
    going. `max_faces` keeps only the N largest.
    """
    frame_h, frame_w = frame_bgr.shape[:2]

    scale = min(1.0, DETECT_MAX_WIDTH / frame_w)
    if scale < 1.0:
        small = cv2.resize(
            frame_bgr,
            (int(frame_w * scale), int(frame_h * scale)),
            interpolation=cv2.INTER_AREA,
        )
    else:
        small = frame_bgr

    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    # Evens out dim or uneven lighting before searching. Used for
    # detection only — the emotion model gets the untouched crop.
    gray = cv2.equalizeHist(gray)

    min_px = max(20, int(round(min_face_size * scale)))
    found = detector.detectMultiScale(
        gray,
        scaleFactor=SCALE_FACTOR,
        minNeighbors=MIN_NEIGHBORS,
        minSize=(min_px, min_px),
    )

    boxes = [
        (int(x / scale), int(y / scale), int(w / scale), int(h / scale))
        for (x, y, w, h) in found
    ]
    boxes.sort(key=lambda b: b[2] * b[3], reverse=True)
    return boxes[:max_faces] if max_faces else boxes


def crop_face(frame_bgr, box, padding=CROP_PADDING):
    """Cuts a face out of the frame, with a little padding, clamped to
    the frame edges. Returns a BGR array (a view of the frame, so copy
    it if you plan to draw on the frame afterwards), or None if the box
    ends up empty."""
    frame_h, frame_w = frame_bgr.shape[:2]
    x, y, w, h = box
    pad_x, pad_y = int(w * padding), int(h * padding)

    x0, y0 = max(0, x - pad_x), max(0, y - pad_y)
    x1, y1 = min(frame_w, x + w + pad_x), min(frame_h, y + h + pad_y)
    if x1 <= x0 or y1 <= y0:
        return None
    return frame_bgr[y0:y1, x0:x1]
