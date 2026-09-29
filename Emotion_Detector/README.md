# Emotion Detector

Standalone emotion-detection component, refactored out of the original
Colab notebook so training and inference are fully separate. **Not yet
wired into NeoMind's FastAPI backend** — that's a later phase.

## Files

| File | Responsibility |
|---|---|
| `model.py` | CNN architecture, shared preprocessing, checkpoint save/load. No training, no dataset access, no webcam. Safe to import from anywhere, including later from NeoMind's backend. |
| `face_detector.py` | OpenCV Haar-cascade face detection and cropping. Only depends on OpenCV — no torch, no model. Safe to import and test on its own. |
| `train.py` | Trains the model and saves the best checkpoint to `models/trained_model.pth`. Only runs when executed directly (`python train.py`) — never on import, and never automatically when NeoMind starts. |
| `monitor.py` | Loads the saved checkpoint, detects a face in each webcam frame, and classifies **the face crop** (never the whole frame). Never trains, never imports `train.py`. Exits with a clear message (no stack trace) if no trained model exists yet. |
| `models/` | Where `trained_model.pth` lands after training. Empty right now — the original checkpoint was never committed and no longer exists, so this needs to be retrained. |

## Setup

```
pip install torch torchvision opencv-python pillow
```

These aren't in the main `requirements.txt` yet — deliberately, since
this phase isn't integrated with the FastAPI backend.

## 1. Get the dataset in place

Point `--data-dir` at a folder that directly contains one sub-folder
per emotion:

```
data/
    Angry/
    Fear/
    Happy/
    Neutral/
    Sad/
    Suprise/
```

This matches the `Testing` folder already used (6 classes, ~7k images,
~49% validation accuracy last time it was trained — real room to
improve). `train.py` reads whatever class folders it finds rather than
hard-coding names, so pointing `--data-dir` at `archive (3)`'s `train/`
folder (8 classes) instead works the same way.

## 2. Train

```
cd Emotion_Detector
python train.py --data-dir /path/to/data
```

Prints train/val loss and accuracy every epoch and saves the best
checkpoint (by validation accuracy) to `models/trained_model.pth`. On
CPU, expect roughly what the original run took: ~30s/epoch on the
6-class Testing set. Useful flags:

- `--epochs`, `--batch-size`, `--lr`, `--val-split` — same meaning as
  the original notebook, with the same defaults (30 / 32 / 0.001 / 0.2).
- `--num-workers` — defaults to 2 instead of the original 12, which
  was tuned for a Colab GPU runtime and oversubscribes a normal machine.
- `--patience N` — stop early after N epochs with no validation
  improvement (default 0 = train the full `--epochs`). Worth using:
  the last run's validation accuracy peaked after epoch 1 and never
  improved again while training accuracy kept climbing, i.e. it was
  overfitting for the remaining 29 epochs.
- `--seed` — makes the train/validation split repeatable (default 42).

Two correctness fixes from the original notebook are folded in here:

- **Validation transform bug.** The original ran `random_split()` on
  one `ImageFolder`, then reassigned `val.dataset.transform` — but
  `random_split()` returns views over the *same* underlying dataset
  object, so that reassignment silently changed the transform for the
  training split too (both ended up augmented). `train.py` builds two
  independent `ImageFolder` instances, one per transform, and slices
  both with the same random indices — same split, genuinely separate
  transforms.
- **Grayscale handling.** `get_train_transform` / `get_eval_transform`
  now include `Grayscale(num_output_channels=3)`. This is a no-op for
  images that are already grayscale (the likely case for this dataset)
  and, either way, guarantees a webcam's 3-channel color frame is
  preprocessed the same way as a grayscale training image at inference
  time — that mismatch was invisible in training but would have
  silently hurt live accuracy.

## 3. Run inference

```
python monitor.py
python monitor.py --model ./models/trained_model.pth --camera 0
python monitor.py --min-face 25   # pick up faces farther from the camera
```

Opens the given webcam. Each frame now goes through OpenCV's frontal-face
Haar cascade (bundled with `opencv-python` — nothing extra to install)
before the model ever sees it:

```
frame -> detect largest face -> draw its box -> crop it
       -> same preprocessing as training -> model -> label + confidence
       -> label drawn just above the box
```

If no face is found, the frame is shown with an amber "No face detected"
notice instead — the loop keeps running either way, it just skips
classification for that frame. Press `q` to quit.

Only the single largest face is boxed and classified, on purpose —
this phase's pipeline is one face in, one prediction out. `face_detector.py`
can return every face it finds (`detect_faces(..., max_faces=None)`) for
whenever multi-face support is wanted later; `monitor.py` just doesn't
ask for that yet.

`--min-face` controls the smallest face (in pixels) the detector will
even look for. The default (40px) is a reasonable starting point, but
Haar cascades get less reliable the smaller a face gets — if faces at
your actual "different distances" test aren't being picked up, lower
this rather than assuming something's broken.

## What's deliberately out of scope here

- No FastAPI route, no NeoMind integration.
- No architecture changes — same CNN as the notebook (generalized to
  any `img_size`, but the math is identical at `IMG_SIZE=64`).
- No face detector beyond OpenCV's built-in Haar cascade — no extra
  CV framework, no DNN-based detector. Haar is CPU-friendly and ships
  with `opencv-python` already, which is what was asked for.
- Only the frontal face is detected — a face turned well to the side,
  tilted a lot, or looking down won't register. That's an inherent
  limit of this cascade, not a bug; worth knowing given NeoMind's
  eventual use case (a student not facing the screen is itself a
  meaningful signal, once this is wired into focus tracking).

## Testing status — face detection (this phase)

Verified in this environment, with real synthetic-image tests (not
just a read-through) against `face_detector.py` directly:

- **One face**: detected correctly on a standard test photo, and on a
  synthetic frame with a face placed off-centre, at the left edge, and
  in a corner.
- **No face**: a plain background, pure random noise, and a black frame
  all correctly return zero faces — no false positives, no crash.
- **Different distances**, simulated as face width on a 640×480 frame:
  reliable from ~100px down to the ~40px cutoff; **detection got
  unreliable in between (missed at ~50–70px in these synthetic tests)**.
  Real camera footage at a given distance may behave differently than a
  resized photo does — treat this as "expect the middle distance range
  to need `--min-face` tuning on your setup," not as an exact number to
  trust blindly.
- **Lighting**: tested at four brightness levels (normal, dim, very dim,
  washed out via gamma correction) — the face was still detected at
  every level in these tests. `equalizeHist()` is applied before
  detection either way, cheap insurance for real uneven lighting even
  though this particular synthetic test didn't show a with/without
  difference.
- **Multiple faces**: two real faces in one frame both get detected;
  `max_faces=1` correctly keeps only the larger one.
- **1280×720 frame**: the downscale-then-rescale-coordinates path was
  checked — the returned box lands in the *original* frame's
  coordinates, not the shrunk detection copy's.
- **`crop_face()` edge cases**: a box flush against the frame edge, one
  hanging fully off the frame, and a degenerate negative box all
  handled without crashing (the last two correctly return `None`).
- The updated `monitor.py`'s drawing logic (box, label, label-clamp
  when a face is right at the top edge, the no-face notice) was
  exercised directly with synthetic frames and boxes — no crashes.

**Not run in this environment:** the actual live webcam pipeline —
this sandbox has no camera and still can't fit `torch`/`torchvision`
(confirmed again this phase). This is the real test, on your machine:

```
python monitor.py
```

covering what was actually asked for — one face, no face, a few
different distances from the camera, and normal indoor lighting. If a
distance doesn't get picked up, try `--min-face` before assuming
something's wrong; the synthetic tests above already suggest the
40–100px range is where that's most likely to matter.

## Testing status — training/inference wiring (Phase 2)

Verified in this environment:
- All three files parse and import cleanly against each other — every
  name `train.py` and `monitor.py` import from `model.py` is checked
  to actually exist there.
- Traced the checkpoint contract end-to-end by hand: `save_checkpoint()`
  writes exactly the three keys `load_model()` reads
  (`model_state`, `class_names`, `img_size`), and `CNN.__init__` takes
  `img_size` so a model built from a loaded checkpoint always matches
  the checkpoint's own architecture, whatever `img_size` it was trained
  with.
- `monitor.py` calling `load_model()` on a path with no file present
  hits the `FileNotFoundError` branch and prints the "run train.py
  first" message rather than raising an unhandled traceback.

**Not run in this environment:** an actual training pass, an actual
checkpoint load, or webcam capture. This sandbox has no camera, and
couldn't fit `torch`/`torchvision` in the disk space available
(they're several GB with CUDA support bundled). Your machine already
has a CUDA-capable Colab runtime, so training and the webcam test
should run there — this is the smoke test worth doing next:

```
cd Emotion_Detector
pip install torch torchvision opencv-python pillow
python train.py --data-dir /path/to/data --epochs 2   # fast sanity run
python monitor.py                                       # loads it, opens webcam
```

If the 2-epoch run trains, saves to `models/trained_model.pth`, and
`monitor.py` loads that file and shows a live label on your webcam
feed, the three files are wired correctly end-to-end — then rerun
`train.py` without `--epochs 2` (or with `--patience`) for a real
training pass.
