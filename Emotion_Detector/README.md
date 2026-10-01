# Emotion Detector

Standalone emotion-detection component, refactored out of the original
Colab notebook so training and inference are fully separate. **Not yet
wired into NeoMind's FastAPI backend** — that's a later phase.

## Files

| File | Responsibility |
|---|---|
| `model.py` | CNN architecture, shared preprocessing, checkpoint save/load. No training, no dataset access, no webcam. Safe to import from anywhere, including later from NeoMind's backend. |
| `face_detector.py` | OpenCV Haar-cascade face detection and cropping. Only depends on OpenCV — no torch, no model. Safe to import and test on its own. |
| `focus_monitor.py` | Turns a stream of face-detected/not observations into a focus state, score, and distraction count. Only depends on the standard library `time` module — no cv2, no torch, no model. Safe to import and test on its own. |
| `train.py` | Trains the model and saves the best checkpoint to `models/trained_model.pth`. Only runs when executed directly (`python train.py`) — never on import, and never automatically when NeoMind starts. |
| `monitor.py` | Loads the saved checkpoint, detects a face in each webcam frame, classifies **the face crop** (never the whole frame), and feeds the face-detected signal into a `FocusMonitor`. Never trains, never imports `train.py`. Exits with a clear message (no stack trace) if no trained model exists yet. |
| `models/` | Where `trained_model.pth` lands after training. Empty right now — the original checkpoint was never committed and no longer exists, so this needs to be retrained. |

## Setup

```
pip install torch torchvision "opencv-python<5" pillow
```

These aren't in the main `requirements.txt` yet — deliberately, since
this phase isn't integrated with the FastAPI backend.

**Pin OpenCV below version 5.** OpenCV 5.0 moved `CascadeClassifier`
out of the base package and into opencv_contrib — a plain
`pip install opencv-python` grabs 5.0 and `face_detector.py` fails
with `AttributeError: module 'cv2' has no attribute 'CascadeClassifier'`.
If you already hit this: `pip uninstall opencv-python -y` then
reinstall with the pin above.

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

## 4. Focus monitoring

`monitor.py` now feeds the face-detected signal into a `FocusMonitor`
(from `focus_monitor.py`) every frame, and shows its output as a status
panel bottom-left of the window:

```
Focus: FOCUSED  Score: 92.4
Distractions: 1  (4.2s)
Monitored: 38.6s
```

```
python monitor.py --distraction-threshold 5   # more tolerant of brief look-aways
```

**What this is, and what it deliberately is NOT.** This is a
prototype heuristic based on exactly one signal — whether a face is
visible. It does not measure attention or concentration, and nothing
here infers a psychological state from the emotion prediction; emotion
is carried through purely as supplementary information; it never
affects `focus_state`, `focus_score`, or `distraction_count`.

**States:**

- `focused` — a face is visible right now.
- `no_face` — no face right now, but for less than
  `--distraction-threshold` seconds (default 3s). A quick glance away,
  not (yet) counted as a distraction.
- `distracted` — no face for `--distraction-threshold` seconds or
  more. `distraction_count` goes up exactly once per continuous
  absence — not once per frame while it continues — and the time is
  added to `total_distraction_time`.

**`focus_score`** is a plain, transparent formula, not a model:

```
focus_score = 100 * (1 - total_distraction_time / total_monitored_time)
```

A short look-away that never crosses the threshold doesn't touch this
score at all — the "no_face" grace period contributes nothing to
`total_distraction_time`. `total_distraction_time` itself is *live*: it
already includes the current in-progress distraction, and grows from
the exact moment the threshold was crossed (not from whenever the next
frame happens to notice), so it doesn't sit frozen mid-distraction and
jump on recovery.

`focus_monitor.py` has no cv2/torch dependency at all — it's a plain
Python class driven by `update(face_detected, emotion=None, now=...)`,
so it's reusable wherever NeoMind ends up wiring this in (the FastAPI
backend, a different capture loop, tests) without dragging in OpenCV or
torch just to track state.

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
  meaningful signal — see the focus monitor above, which now does
  exactly that.
- No FastAPI integration for the focus monitor either — same as the
  emotion pipeline, this phase is standalone.
- `focus_score` is a simple ratio, not anything scientific. It doesn't
  account for how *recent* distractions were, doesn't weight short vs.
  long absences differently, and treats "no data yet" as a perfect
  100 — all deliberate simplicity, worth knowing before this number
  gets shown to a student as if it meant more than it does.

## Testing status — focus monitoring (this phase)

Unlike face detection, `focus_monitor.py` has zero dependency on cv2,
torch, or a camera — it's a plain Python class driven by timestamps —
so this phase got a real, deterministic automated test suite (a
virtual clock, not `time.sleep`), 45 assertions covering:

- constant presence (stays `focused`, nothing ever counted)
- a brief absence under the threshold (`no_face`, not counted, score
  untouched) and recovery without ever counting
- an absence crossing the threshold (`distracted`, `distraction_count`
  incremented exactly once — confirmed it does **not** re-increment on
  every subsequent frame while still absent)
- recovery after a counted distraction (`total_distraction_time`
  settles and stops growing)
- three separate prolonged absences → count == 3, not more
- ten short blips that never cross the threshold → count stays 0
- the `focus_score` formula checked against its own definition by hand
- the very first call (zero elapsed time) → `focus_score` defaults to
  100 with no division-by-zero
- the exact boundary — `absence_duration == threshold` — counts as
  distracted; one instant under does not
- an invalid (zero/negative) threshold is rejected
- `emotion` is passed through unchanged and confirmed to have zero
  effect on `focus_state`/`focus_score`/`distraction_count`
- `snapshot()` contains exactly the required keys, plus
  `total_monitored_time`
- `reset()` zeroes every counter while keeping the configured threshold

Two real (small) issues turned up while writing these tests and were
fixed, not just documented: total_distraction_time now reflects the
exact moment a distraction started (backdated to when the threshold
was actually crossed, since that moment is knowable exactly) rather
than the frame that happened to detect it — otherwise it would read 0
on the exact frame a distraction is first flagged and only start
growing on the next one.

Also ran the real, non-synthetic pipeline this phase enables: real
`face_detector.detect_faces()` output (not a hand-written boolean) fed
into a real `FocusMonitor` across a focused → absent → distracted →
recovered sequence, confirming the two files work together exactly as
`monitor.py`'s loop uses them — the state transitions landed on the
correct frame given the configured threshold.

**Not run in this environment:** the live webcam version — same
limitation as every phase so far (no camera, no room for
torch/torchvision here). The status panel's layout (bottom-left,
clear of the top-left "no face" notice and the per-face label) was
checked with synthetic frames, but seeing it update live, and reading
the numbers as you deliberately look away for different lengths of
time, is worth doing on your machine:

```
python monitor.py
```

Try a deliberately short glance away (should show `no_face`, count
stays put) and a longer one past your threshold (should flip to
`distracted`, red panel text, count goes up by exactly 1).

## Testing status — face detection (Phase 3)

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
