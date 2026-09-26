# Emotion Detector

Standalone emotion-detection component, refactored out of the original
Colab notebook so training and inference are fully separate. **Not yet
wired into NeoMind's FastAPI backend** — that's a later phase.

## Files

| File | Responsibility |
|---|---|
| `model.py` | CNN architecture, shared preprocessing, checkpoint save/load. No training, no dataset access, no webcam. Safe to import from anywhere, including later from NeoMind's backend. |
| `train.py` | Trains the model and saves the best checkpoint to `models/trained_model.pth`. Only runs when executed directly (`python train.py`) — never on import, and never automatically when NeoMind starts. |
| `monitor.py` | Loads the saved checkpoint and runs webcam inference. Never trains, never imports `train.py`. Exits with a clear message (no stack trace) if no trained model exists yet. |
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
```

Opens the given webcam, classifies every frame, and overlays the
predicted class and confidence. Press `q` to quit.

Still classifies the whole frame — no face detection yet, same as the
original. That's a known gap flagged for a later phase, not something
this refactor adds or removes.

## What's deliberately out of scope here

- No FastAPI route, no NeoMind integration.
- No face detection / face cropping.
- No architecture changes — same CNN as the notebook (generalized to
  any `img_size`, but the math is identical at `IMG_SIZE=64`).

## Testing status (this phase)

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
