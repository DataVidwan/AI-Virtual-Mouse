"""
mouse_controller.py
-------------------
Translates gesture events into actual OS mouse / keyboard actions.
Only essential actions: move, left click, right click, scroll, screenshot.
"""

import pyautogui
import numpy as np
from hand_tracker import HandTracker
from gesture_controller import Gesture


# Disable pyautogui's built-in pause for responsiveness
pyautogui.PAUSE    = 0
pyautogui.FAILSAFE = True   # Move to top-left corner to abort


class MouseConfig:
    FRAME_REDUCTION = 100   # pixels cropped from each webcam edge
    SMOOTHING       = 0.4   # EMA factor (higher = less smooth, more responsive)
    SCROLL_SPEED    = 10


class MouseController:
    """
    Translates gestures into OS mouse actions.
    Call handle(gesture, tracker) each frame.
    """

    def __init__(self, frame_shape: tuple[int, int], config: MouseConfig | None = None):
        self.cfg = config or MouseConfig()
        self.frame_h, self.frame_w = frame_shape
        self.screen_w, self.screen_h = pyautogui.size()

        # Smoothed cursor position (double-EMA)
        self._cur_x    = self.screen_w / 2
        self._cur_y    = self.screen_h / 2
        self._smooth_x = self.screen_w / 2
        self._smooth_y = self.screen_h / 2

    # ------------------------------------------------------------------

    def handle(self, gesture: str, tracker: HandTracker) -> dict:
        """Execute the mouse action for the given gesture."""
        action_info: dict = {"gesture": gesture, "action": "—"}

        if gesture == Gesture.CURSOR_MOVE:
            if tracker.detected:
                self._move_cursor(tracker)

        elif gesture == Gesture.LEFT_CLICK:
            pyautogui.click()
            action_info["action"] = "Left Click"
            print("[Action] Left Click")

        elif gesture == Gesture.RIGHT_CLICK:
            pyautogui.rightClick()
            action_info["action"] = "Right Click"
            print("[Action] Right Click")

        elif gesture == Gesture.SCROLL_UP:
            pyautogui.scroll(self.cfg.SCROLL_SPEED)
            action_info["action"] = "Scroll ↑"

        elif gesture == Gesture.SCROLL_DOWN:
            pyautogui.scroll(-self.cfg.SCROLL_SPEED)
            action_info["action"] = "Scroll ↓"

        elif gesture == Gesture.SCREENSHOT:
            import datetime, os
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.isdir(desktop):
                desktop = os.path.expanduser("~")
            path = os.path.join(desktop, f"screenshot_{ts}.png")
            try:
                pyautogui.screenshot(path)
                action_info["action"] = "Screenshot saved!"
                action_info["screenshot_taken"] = True
                print(f"[Screenshot] Saved → {path}")
            except Exception as e:
                action_info["action"] = "Screenshot failed"
                print(f"[Screenshot] Error: {e}")

        return action_info

    # ------------------------------------------------------------------

    def _move_cursor(self, tracker: HandTracker):
        """
        Map index fingertip to screen coords with velocity-adaptive
        single-EMA smoothing — responsive with minimal lag.
        """
        ix, iy, _ = tracker.landmark(HandTracker.INDEX_TIP)
        red = self.cfg.FRAME_REDUCTION

        # Clamp to active zone
        ix = np.clip(ix, red, self.frame_w - red)
        iy = np.clip(iy, red, self.frame_h - red)

        # Map to screen coordinates
        target_x = np.interp(ix, [red, self.frame_w - red], [0, self.screen_w])
        target_y = np.interp(iy, [red, self.frame_h - red], [0, self.screen_h])

        # Velocity-adaptive alpha:
        #   Slow movement → base alpha (0.5) — smooth, precise
        #   Fast movement → up to 0.85 — responsive, keeps up
        dx = target_x - self._cur_x
        dy = target_y - self._cur_y
        velocity = np.hypot(dx, dy)

        base_alpha = self.cfg.SMOOTHING  # 0.5 default
        speed_ratio = float(np.clip(velocity / 200.0, 0.0, 1.0))
        alpha = base_alpha + (0.85 - base_alpha) * speed_ratio

        # Single EMA — responsive, no double-smoothing lag
        self._cur_x = alpha * target_x + (1 - alpha) * self._cur_x
        self._cur_y = alpha * target_y + (1 - alpha) * self._cur_y

        pyautogui.moveTo(int(self._cur_x), int(self._cur_y))
