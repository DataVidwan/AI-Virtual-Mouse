"""
utils.py
--------
UI drawing utilities, FPS counter, and overlay panel for the virtual mouse app.
"""

import cv2
import numpy as np
import time
from collections import deque


# ── Color palette (BGR) ──────────────────────────────────────────────────────
class Color:
    BG_PANEL       = (18,  18,  28)        # near-black for panels
    ACCENT         = (0,  220, 160)        # cyan-green
    ACCENT_ALT     = (60, 140, 255)        # blue
    WARNING        = (0,  140, 255)        # orange
    DANGER         = (50,  50, 220)        # red
    SUCCESS        = (40, 200,  80)        # green
    WHITE          = (245, 245, 255)
    GREY           = (130, 130, 145)
    DARK_GREY      = (45,  45,  58)
    OVERLAY_BG     = (12,  12,  20)        # very dark panel

    # Gesture label colors
    GESTURE_COLORS = {
        "None":         (100, 100, 110),
        "Move Cursor":  (0,   220, 160),
        "Left Click":   (60,  140, 255),
        "Right Click":  (100, 100, 255),
        "Scroll Up":    (0,   200, 255),
        "Scroll Down":  (0,   200, 255),
        "Volume +":     (0,   220, 140),
        "Volume -":     (0,   180, 120),
        "Screenshot":   (255, 200,  60),
        "Drag":         (255, 150,  60),
    }

    @classmethod
    def for_gesture(cls, gesture: str) -> tuple[int, int, int]:
        return cls.GESTURE_COLORS.get(gesture, cls.ACCENT)


# ── FPS Counter ───────────────────────────────────────────────────────────────

class FPSCounter:
    def __init__(self, window: int = 30):
        self._times: deque[float] = deque(maxlen=window)
        self._last  = time.time()

    def tick(self) -> float:
        now = time.time()
        self._times.append(now - self._last)
        self._last = now
        if len(self._times) < 2:
            return 0.0
        return 1.0 / (sum(self._times) / len(self._times))

    @property
    def fps(self) -> float:
        if len(self._times) < 2:
            return 0.0
        return 1.0 / (sum(self._times) / len(self._times))


# ── Drawing helpers ───────────────────────────────────────────────────────────

def draw_rounded_rect(
    frame: np.ndarray,
    x1: int, y1: int, x2: int, y2: int,
    radius: int = 12,
    color: tuple = Color.BG_PANEL,
    alpha: float = 0.75,
) -> np.ndarray:
    """Draw a semi-transparent rounded rectangle."""
    overlay = frame.copy()
    # Corners
    cv2.rectangle(overlay, (x1 + radius, y1), (x2 - radius, y2), color, -1)
    cv2.rectangle(overlay, (x1, y1 + radius), (x2, y2 - radius), color, -1)
    for cx, cy in [
        (x1 + radius, y1 + radius),
        (x2 - radius, y1 + radius),
        (x1 + radius, y2 - radius),
        (x2 - radius, y2 - radius),
    ]:
        cv2.circle(overlay, (cx, cy), radius, color, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
    return frame


def draw_text(
    frame: np.ndarray,
    text: str,
    pos: tuple[int, int],
    scale: float = 0.55,
    color: tuple = Color.WHITE,
    thickness: int = 1,
    font=cv2.FONT_HERSHEY_SIMPLEX,
) -> np.ndarray:
    cv2.putText(frame, text, pos, font, scale, color, thickness, cv2.LINE_AA)
    return frame


def draw_pill(
    frame: np.ndarray,
    text: str,
    center: tuple[int, int],
    color: tuple = Color.ACCENT,
    bg: tuple = Color.BG_PANEL,
    scale: float = 0.50,
    pad: int = 10,
    alpha: float = 0.82,
):
    """Draw a pill-shaped badge around text."""
    font  = cv2.FONT_HERSHEY_SIMPLEX
    (tw, th), baseline = cv2.getTextSize(text, font, scale, 1)
    cx, cy = center
    x1 = cx - tw // 2 - pad
    y1 = cy - th // 2 - pad // 2
    x2 = cx + tw // 2 + pad
    y2 = cy + th // 2 + pad // 2 + baseline
    r  = (y2 - y1) // 2

    overlay = frame.copy()
    cv2.rectangle(overlay, (x1 + r, y1), (x2 - r, y2), bg, -1)
    cv2.circle(overlay, (x1 + r, (y1 + y2) // 2), r, bg, -1)
    cv2.circle(overlay, (x2 - r, (y1 + y2) // 2), r, bg, -1)
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    # Colored border
    cv2.rectangle(frame, (x1 + r, y1), (x2 - r, y2), color, 1)
    cv2.circle(frame, (x1 + r, (y1 + y2) // 2), r, color, 1)
    cv2.circle(frame, (x2 - r, (y1 + y2) // 2), r, color, 1)

    cv2.putText(
        frame, text,
        (cx - tw // 2, cy + th // 2),
        font, scale, color, 1, cv2.LINE_AA,
    )


# ── HUD overlay ───────────────────────────────────────────────────────────────

class HUDOverlay:
    """
    Draws the full heads-up display on the frame:
    - Top-left info panel (FPS, tracking, mode)
    - Gesture label badge
    - Volume bar
    - Gesture feedback log
    - Active zone indicator
    - Pinch distance indicator
    """

    def __init__(self, frame_w: int, frame_h: int, frame_reduction: int = 100):
        self.fw   = frame_w
        self.fh   = frame_h
        self.red  = frame_reduction

        self._gesture_log: deque[tuple[str, float]] = deque(maxlen=5)
        self._last_gesture = ""

        # Pre-compute vignette mask ONCE (huge performance gain)
        self._vignette_mask = self._build_vignette_mask(frame_w, frame_h)

    @staticmethod
    def _build_vignette_mask(w: int, h: int) -> np.ndarray:
        """Create a radial vignette darkening mask (pre-computed once)."""
        X = np.linspace(-1, 1, w, dtype=np.float32)
        Y = np.linspace(-1, 1, h, dtype=np.float32)
        Xg, Yg = np.meshgrid(X, Y)
        dist = np.sqrt(Xg ** 2 + Yg ** 2)
        # Subtle darkening at edges: center=1.0, corners≈0.65
        mask = np.clip(1.0 - dist * 0.35, 0.55, 1.0)
        return np.dstack([mask, mask, mask])  # 3-channel for fast multiply

    def push_gesture(self, gesture: str):
        """Record a new gesture event for the feedback log."""
        if gesture and gesture != self._last_gesture and gesture != "None":
            self._gesture_log.appendleft((gesture, time.time()))
            self._last_gesture = gesture

    def draw(
        self,
        frame: np.ndarray,
        fps: float,
        gesture: str,
        tracking: bool,
        volume: float = 0.5,
        action_info: dict | None = None,
    ) -> np.ndarray:

        # ── Dark vignette border (pre-computed mask) ──────────────────
        self._draw_vignette(frame)

        # ── Active zone rectangle ─────────────────────────────────────
        r = self.red
        cv2.rectangle(
            frame,
            (r, r), (self.fw - r, self.fh - r),
            Color.DARK_GREY, 1, cv2.LINE_AA,
        )

        # ── Top-left info panel ───────────────────────────────────────
        self._draw_info_panel(frame, fps, tracking)

        # ── Gesture label ─────────────────────────────────────────────
        g_color = Color.for_gesture(gesture)
        draw_pill(
            frame, gesture,
            center=(self.fw // 2, self.fh - 40),
            color=g_color, bg=Color.OVERLAY_BG,
            scale=0.65, pad=14, alpha=0.88,
        )

        # ── Volume bar (right side) ───────────────────────────────────
        if gesture in ("Volume +", "Volume -"):
            self._draw_volume_bar(frame, volume)

        # ── Gesture feedback log (bottom-right) ───────────────────────
        self.push_gesture(gesture)
        self._draw_gesture_log(frame)

        return frame

    # ── Private helpers ───────────────────────────────────────────────

    def _draw_vignette(self, frame: np.ndarray):
        """Apply pre-computed vignette mask (near-zero cost per frame)."""
        np.multiply(frame, self._vignette_mask, out=frame, casting='unsafe')

    def _draw_info_panel(
        self, frame, fps: float, tracking: bool
    ):
        panel_x, panel_y = 14, 14
        pw, ph = 210, 78

        draw_rounded_rect(
            frame,
            panel_x, panel_y,
            panel_x + pw, panel_y + ph,
            radius=10, color=Color.OVERLAY_BG, alpha=0.82,
        )

        # FPS
        fps_color = Color.SUCCESS if fps > 20 else Color.WARNING if fps > 10 else Color.DANGER
        draw_text(frame, f"FPS  {fps:5.1f}", (panel_x + 12, panel_y + 24),
                  scale=0.55, color=fps_color, thickness=1)

        # Tracking dot
        t_color = Color.SUCCESS if tracking else Color.DANGER
        t_label = "TRACKING" if tracking else "NO HAND"
        cv2.circle(frame, (panel_x + 18, panel_y + 55), 6, t_color, -1, cv2.LINE_AA)
        draw_text(frame, t_label, (panel_x + 32, panel_y + 60),
                  scale=0.48, color=t_color, thickness=1)

    def _draw_volume_bar(self, frame: np.ndarray, volume: float):
        bx    = self.fw - 28
        by1   = int(self.fh * 0.2)
        by2   = int(self.fh * 0.8)
        bar_h = by2 - by1
        fill  = int(bar_h * volume)

        # Track
        cv2.rectangle(frame, (bx - 6, by1), (bx + 6, by2), Color.DARK_GREY, -1)
        # Fill
        cv2.rectangle(frame, (bx - 6, by2 - fill), (bx + 6, by2), Color.ACCENT, -1)
        # Label
        draw_text(frame, f"{int(volume*100)}%", (bx - 18, by1 - 8),
                  scale=0.4, color=Color.ACCENT)

    def _draw_gesture_log(self, frame: np.ndarray):
        now   = time.time()
        bx    = self.fw - 14
        by    = self.fh - 70
        width = 180

        for i, (g, ts) in enumerate(self._gesture_log):
            age   = now - ts
            if age > 3.0:
                continue
            alpha_t = max(0.0, 1.0 - age / 3.0)
            color_base = Color.for_gesture(g)
            # Fade color towards grey
            color = tuple(
                int(c * alpha_t + 60 * (1 - alpha_t)) for c in color_base
            )
            y = by - i * 22
            draw_text(
                frame, f"▸ {g}",
                (bx - width, y),
                scale=0.42, color=color, thickness=1,
            )



# ── Calibration helper ────────────────────────────────────────────────────────

def draw_calibration_overlay(
    frame: np.ndarray,
    progress: float,        # 0.0 – 1.0
    message: str = "Calibrating…",
) -> np.ndarray:
    h, w = frame.shape[:2]
    # Dim frame
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

    # Progress bar
    bw = int(w * 0.6)
    bx = (w - bw) // 2
    by = h // 2 + 20
    cv2.rectangle(frame, (bx, by), (bx + bw, by + 18), Color.DARK_GREY, -1)
    cv2.rectangle(frame, (bx, by), (bx + int(bw * progress), by + 18), Color.ACCENT, -1)

    draw_text(frame, message, (bx, by - 14), scale=0.6, color=Color.WHITE)
    draw_text(
        frame, f"{int(progress*100)}%",
        (bx + bw // 2 - 18, by + 14),
        scale=0.5, color=Color.BG_PANEL, thickness=1,
    )
    return frame
