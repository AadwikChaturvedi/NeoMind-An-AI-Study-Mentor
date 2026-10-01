"""
focus_monitor.py
-----------------
A simple, heuristic study-focus tracker built on top of face detection.

IMPORTANT — what this is, and what it deliberately is NOT:

    This is a prototype heuristic based on exactly one observable
    signal: whether a face is visible to the camera. It is NOT a
    scientific measurement of attention or concentration. A student
    can be facing the camera and not be doing anything productive;
    someone glancing at a textbook beside the screen can be perfectly
    focused and briefly register as "no face." Treat focus_score and
    focus_state as a rough, transparent proxy — not ground truth.

    The (optional) emotion prediction is passed through purely as
    supplementary information. Nothing here ever reads it, and no
    psychological state is inferred from it — emotion never affects
    focus_state, focus_score, or distraction_count.

Pipeline this sits in front of:

    face_detector.detect_faces() -> face_detected (bool)
                                  -> FocusMonitor.update(face_detected)
                                  -> {focus_state, focus_score, ...}

Only depends on the standard library `time` module — no cv2, no torch,
no webcam — so it can be reasoned about, tested, and reused (e.g. later
from the FastAPI backend) completely on its own.
"""

import time

DEFAULT_DISTRACTION_THRESHOLD = 3.0  # seconds of continuous face absence before it counts as a distraction, not just a glance away

VALID_STATES = ("focused", "distracted", "no_face")


class FocusMonitor:
    """Tracks focus over one monitoring session from a stream of
    face_detected observations.

    Call update(face_detected) once per observation — once per webcam
    frame, or throttled to a few times a second, doesn't matter. This
    class only cares about wall-clock time between calls, not how often
    they happen.

    States
    ------
    "focused"    — a face is visible right now.
    "no_face"    — no face right now, but for less than
                   distraction_threshold seconds. A quick look away,
                   not (yet) counted as a distraction.
    "distracted" — no face for distraction_threshold seconds or more.
                   Counted: distraction_count goes up exactly once per
                   continuous absence (not once per update() call while
                   it continues), and the absence's duration adds to
                   total_distraction_time.
    """

    def __init__(self, distraction_threshold: float = DEFAULT_DISTRACTION_THRESHOLD, now: float = None):
        if distraction_threshold <= 0:
            raise ValueError("distraction_threshold must be > 0")
        self.distraction_threshold = distraction_threshold

        now = time.monotonic() if now is None else now
        self._start_time = now

        # Public snapshot fields — always in sync after update().
        self.face_detected = False
        self.emotion = None
        self.focus_state = "no_face"  # nothing observed yet
        self.distraction_count = 0
        self.total_monitored_time = 0.0
        self.total_distraction_time = 0.0
        self.focus_score = 100.0  # optimistic starting point — see _compute_focus_score()

        # Internal bookkeeping.
        self._absence_start = None  # wall-clock time the current absence streak began (None = face present)
        self._counted_this_absence = False  # whether this absence streak already incremented distraction_count
        self._distracted_since = None  # wall-clock time focus_state most recently became "distracted" (None otherwise)
        self._committed_distraction_time = 0.0  # settled total, from absences that have already ended

    def update(self, face_detected: bool, emotion=None, now: float = None) -> dict:
        """Feed one observation in.

        `emotion` is optional and purely cosmetic — stored and passed
        through in the snapshot, never used in any of the focus
        calculations below. Returns the same dict snapshot() would;
        the instance's attributes stay in sync too, so callers can use
        either.
        """
        now = time.monotonic() if now is None else now
        self.face_detected = bool(face_detected)
        self.emotion = emotion
        self.total_monitored_time = round(now - self._start_time, 2)

        if self.face_detected:
            if self.focus_state == "distracted" and self._distracted_since is not None:
                self._committed_distraction_time += now - self._distracted_since
            self._distracted_since = None
            self._absence_start = None
            self._counted_this_absence = False
            self.focus_state = "focused"
        else:
            # absence_start is pegged to the call that FIRST reports no
            # face, not to the last successful sighting -- on a live
            # video loop calling update() every frame these are at most
            # one frame apart, so it doesn't matter in practice.
            if self._absence_start is None:
                self._absence_start = now
            absence_duration = now - self._absence_start

            if absence_duration < self.distraction_threshold:
                self.focus_state = "no_face"
            elif self.focus_state != "distracted":
                self.focus_state = "distracted"
                # The threshold was actually crossed distraction_threshold
                # seconds after the absence began, not "right now" -- we
                # know that moment exactly, so backdate to it rather than
                # to the detecting call. Otherwise total_distraction_time
                # would always read 0 on the exact frame a distraction is
                # first detected, then jump on the next one.
                self._distracted_since = self._absence_start + self.distraction_threshold
                if not self._counted_this_absence:
                    self.distraction_count += 1
                    self._counted_this_absence = True
            # else: already "distracted" from an earlier update() call
            # this same absence streak — nothing state-wise to change,
            # total_distraction_time below still keeps growing.

        # total_distraction_time is "live": it includes whatever's
        # happening right now, not just absences that have already
        # ended. Otherwise it would sit frozen for the whole time
        # you're mid-distraction and only jump once you look back.
        ongoing = (
            now - self._distracted_since
            if self.focus_state == "distracted" and self._distracted_since is not None
            else 0.0
        )
        self.total_distraction_time = round(self._committed_distraction_time + ongoing, 2)

        self.focus_score = self._compute_focus_score()
        return self.snapshot()

    def _compute_focus_score(self) -> float:
        """A simple, transparent heuristic — NOT a scientific attention
        measurement. It's just: what fraction of the monitored time so
        far wasn't spent in a counted distraction, scaled to 0-100.

            focus_score = 100 * (1 - total_distraction_time / total_monitored_time)

        A short look-away — still within the "no_face" grace period,
        not yet "distracted" — doesn't touch this score at all. That's
        the "a short absence should not immediately count" requirement,
        expressed directly in the formula rather than as a separate rule.
        """
        if self.total_monitored_time <= 0:
            return 100.0
        score = 100.0 * (1.0 - self.total_distraction_time / self.total_monitored_time)
        return round(max(0.0, min(100.0, score)), 1)

    def snapshot(self) -> dict:
        """The monitoring output. `total_monitored_time` is included in
        addition to the fields asked for, since it's one of the signals
        this class tracks and is generally useful alongside the rest."""
        return {
            "face_detected": self.face_detected,
            "emotion": self.emotion,
            "focus_state": self.focus_state,
            "focus_score": self.focus_score,
            "distraction_count": self.distraction_count,
            "total_distraction_time": self.total_distraction_time,
            "total_monitored_time": self.total_monitored_time,
        }

    def reset(self, now: float = None) -> None:
        """Starts a fresh monitoring session (e.g. a new study-timer
        run) — all counters back to zero. distraction_threshold carries
        over unchanged."""
        self.__init__(distraction_threshold=self.distraction_threshold, now=now)
