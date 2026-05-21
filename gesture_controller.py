"""
gesture_controller.py
---------------------
Simple finger-count based gesture recognition.
No complex pinch distances — just count how many fingers are up.

Gestures:
  1 finger  (index)              → Move Cursor
  2 fingers (index + middle)     → Left Click
  3 fingers (index + middle + ring) → Right Click
  5 fingers (open palm)          → Scroll (move hand up/down)
  0 fingers (fist, hold 0.5s)    → Screenshot
"""

import time
from hand_tracker import HandTracker


# ── Gesture labels ────────────────────────────────────────────────────────────
class Gesture:
    NONE         = "None"
    CURSOR_MOVE  = "Move Cursor"
    LEFT_CLICK   = "Left Click"
    RIGHT_CLICK  = "Right Click"
    SCROLL_UP    = "Scroll Up"
    SCROLL_DOWN  = "Scroll Down"
    SCREENSHOT   = "Screenshot"


# ── Config ────────────────────────────────────────────────────────────────────
class GestureConfig:
    # Cooldowns (seconds)
    COOLDOWN_LEFT_CLICK    = 0.40
    COOLDOWN_RIGHT_CLICK   = 0.50
    COOLDOWN_SCREENSHOT    = 2.00
    COOLDOWN_SCROLL        = 0.05

    # Scroll: vertical movement threshold (normalized)
    SCROLL_THRESHOLD       = 0.012

    # Consecutive frames to confirm a click gesture (debounce)
    CONFIRM_FRAMES         = 3

    # Fist hold: how many confirmed frames of fist to trigger screenshot
    SCREENSHOT_HOLD_FRAMES = 15   # ~0.5s at 30fps


class GestureController:
    """
    Finger-count gesture recognizer.
    Call update(tracker) each frame → returns Gesture string.
    """

    def __init__(self, config: GestureConfig | None = None):
        self.cfg     = config or GestureConfig()
        self.gesture = Gesture.NONE
        self.data: dict = {}

        # Cooldown timestamps
        self._last: dict[str, float] = {}

        # Debounce counters
        self._left_count  = 0
        self._right_count = 0

        # Edge-trigger latch — prevents re-firing while held
        self._left_fired  = False
        self._right_fired = False
        self._ss_fired    = False

        # Scroll tracking
        self._scroll_anchor_y: float | None = None

        # Screenshot fist hold counter
        self._fist_frames = 0

        # Volume (kept for HUD compatibility but unused)
        self.volume_level: float = 0.5

    # ------------------------------------------------------------------
    # Main update — called every frame
    # ------------------------------------------------------------------

    def update(self, tracker: HandTracker) -> str:
        self.gesture = Gesture.NONE
        self.data    = {}

        if not tracker.detected:
            self._reset_all()
            return self.gesture

        mask  = tracker.fingers_up_mask()
        count = sum(mask)
        thumb, index, middle, ring, pinky = mask

        # ── 0 fingers (FIST) → Screenshot after holding ───────────
        if count == 0:
            self._fist_frames += 1
            if (self._fist_frames >= self.cfg.SCREENSHOT_HOLD_FRAMES
                    and not self._ss_fired):
                if self._cooled(Gesture.SCREENSHOT, self.cfg.COOLDOWN_SCREENSHOT):
                    self.gesture = Gesture.SCREENSHOT
                    self._bump(Gesture.SCREENSHOT)
                    self._ss_fired = True
            # Reset non-fist state
            self._left_count  = 0
            self._right_count = 0
            self._scroll_anchor_y = None
            return self.gesture
        else:
            self._fist_frames = 0
            self._ss_fired    = False

        # ── 1 finger (INDEX only) → Move Cursor ──────────────────
        if count == 1 and index:
            self.gesture = Gesture.CURSOR_MOVE
            self._left_count  = 0
            self._right_count = 0
            self._left_fired  = False
            self._right_fired = False
            self._scroll_anchor_y = None
            return self.gesture

        # ── 2 fingers (INDEX + MIDDLE) → Left Click ──────────────
        if count == 2 and index and middle:
            self._right_count = 0
            self._right_fired = False
            self._scroll_anchor_y = None

            self._left_count += 1
            if self._left_count >= self.cfg.CONFIRM_FRAMES:
                if not self._left_fired:
                    if self._cooled(Gesture.LEFT_CLICK, self.cfg.COOLDOWN_LEFT_CLICK):
                        self.gesture = Gesture.LEFT_CLICK
                        self._bump(Gesture.LEFT_CLICK)
                        self._left_fired = True
            return self.gesture
        else:
            self._left_count = 0
            self._left_fired = False

        # ── 3 fingers (INDEX + MIDDLE + RING) → Right Click ──────
        if count == 3 and index and middle and ring:
            self._scroll_anchor_y = None

            self._right_count += 1
            if self._right_count >= self.cfg.CONFIRM_FRAMES:
                if not self._right_fired:
                    if self._cooled(Gesture.RIGHT_CLICK, self.cfg.COOLDOWN_RIGHT_CLICK):
                        self.gesture = Gesture.RIGHT_CLICK
                        self._bump(Gesture.RIGHT_CLICK)
                        self._right_fired = True
            return self.gesture
        else:
            self._right_count = 0
            self._right_fired = False

        # ── 4-5 fingers (OPEN PALM) → Scroll ─────────────────────
        if count >= 4:
            _, wy, _ = tracker.landmark_norm(HandTracker.WRIST)

            if self._scroll_anchor_y is None:
                self._scroll_anchor_y = wy
            else:
                delta = self._scroll_anchor_y - wy  # positive = moved up
                if abs(delta) > self.cfg.SCROLL_THRESHOLD:
                    if self._cooled("SCROLL", self.cfg.COOLDOWN_SCROLL):
                        self.gesture = (Gesture.SCROLL_UP
                                        if delta > 0 else Gesture.SCROLL_DOWN)
                        self.data["delta"] = delta
                        self._bump("SCROLL")
                        self._scroll_anchor_y = wy
            return self.gesture

        return self.gesture

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _cooled(self, key: str, cd: float) -> bool:
        return time.time() - self._last.get(key, 0.0) >= cd

    def _bump(self, key: str):
        self._last[key] = time.time()

    def _reset_all(self):
        self._left_count  = 0
        self._right_count = 0
        self._left_fired  = False
        self._right_fired = False
        self._ss_fired    = False
        self._fist_frames = 0
        self._scroll_anchor_y = None
