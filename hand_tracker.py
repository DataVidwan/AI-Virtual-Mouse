"""
hand_tracker.py
---------------
Handles all MediaPipe hand detection and landmark extraction.
Simple, reliable — no smoothing or hysteresis that can break detection.
"""

import cv2
import mediapipe as mp
import numpy as np


class HandTracker:
    """
    Detects and tracks hand landmarks using MediaPipe Hands.
    Provides normalized and pixel-space landmark coordinates.
    """

    # Landmark indices (MediaPipe standard)
    WRIST          = 0
    THUMB_CMC      = 1
    THUMB_MCP      = 2
    THUMB_IP       = 3
    THUMB_TIP      = 4
    INDEX_MCP      = 5
    INDEX_PIP      = 6
    INDEX_DIP      = 7
    INDEX_TIP      = 8
    MIDDLE_MCP     = 9
    MIDDLE_PIP     = 10
    MIDDLE_DIP     = 11
    MIDDLE_TIP     = 12
    RING_MCP       = 13
    RING_PIP       = 14
    RING_DIP       = 15
    RING_TIP       = 16
    PINKY_MCP      = 17
    PINKY_PIP      = 18
    PINKY_DIP      = 19
    PINKY_TIP      = 20

    # Finger groups
    FINGER_TIPS    = [THUMB_TIP, INDEX_TIP, MIDDLE_TIP, RING_TIP, PINKY_TIP]
    FINGER_PIPS    = [THUMB_IP,  INDEX_PIP, MIDDLE_PIP, RING_PIP, PINKY_PIP]

    # Visual style
    LANDMARK_COLOR      = (0, 255, 200)
    CONNECTION_COLOR    = (100, 200, 255)
    FINGERTIP_COLOR     = (255, 80, 150)
    LANDMARK_RADIUS     = 5
    FINGERTIP_RADIUS    = 8
    CONNECTION_THICKNESS = 2

    def __init__(
        self,
        max_hands: int = 1,
        model_complexity: int = 1,
        detection_confidence: float = 0.65,
        tracking_confidence: float = 0.5,
    ):
        self.mp_hands   = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_styles  = mp.solutions.drawing_styles

        self.hands = self.mp_hands.Hands(
            max_num_hands=max_hands,
            model_complexity=model_complexity,
            min_detection_confidence=detection_confidence,
            min_tracking_confidence=tracking_confidence,
        )

        self._landmarks_normalized = None
        self._landmarks_px         = None
        self._handedness           = None
        self._frame_shape          = (480, 640)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process(self, bgr_frame: np.ndarray) -> bool:
        """Run hand detection. Returns True if a hand is detected."""
        h, w = bgr_frame.shape[:2]
        self._frame_shape = (h, w)

        rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self.hands.process(rgb)
        rgb.flags.writeable = True

        if results.multi_hand_landmarks:
            self._landmarks_normalized = results.multi_hand_landmarks[0]
            self._landmarks_px = self._to_pixel_coords(
                self._landmarks_normalized, w, h
            )
            if results.multi_handedness:
                self._handedness = results.multi_handedness[0].classification[0].label
            return True

        self._landmarks_normalized = None
        self._landmarks_px         = None
        self._handedness           = None
        return False

    @property
    def detected(self) -> bool:
        return self._landmarks_px is not None

    @property
    def handedness(self) -> str | None:
        return self._handedness

    def landmark(self, idx: int) -> tuple[int, int, float]:
        """Return (x_px, y_px, z_norm) for landmark idx."""
        if not self.detected:
            return (0, 0, 0.0)
        return self._landmarks_px[idx]

    def landmark_norm(self, idx: int) -> tuple[float, float, float]:
        """Return normalized (x, y, z) in [0,1]."""
        if not self.detected:
            return (0.0, 0.0, 0.0)
        lm = self._landmarks_normalized.landmark[idx]
        return (lm.x, lm.y, lm.z)

    def all_landmarks_px(self) -> list[tuple[int, int, float]]:
        return self._landmarks_px or []

    def distance(self, idx_a: int, idx_b: int) -> float:
        """Euclidean distance in pixels."""
        ax, ay, _ = self.landmark(idx_a)
        bx, by, _ = self.landmark(idx_b)
        return float(np.hypot(ax - bx, ay - by))

    def distance_norm(self, idx_a: int, idx_b: int) -> float:
        """Euclidean distance in normalized coords."""
        ax, ay, _ = self.landmark_norm(idx_a)
        bx, by, _ = self.landmark_norm(idx_b)
        return float(np.hypot(ax - bx, ay - by))

    def midpoint(self, idx_a: int, idx_b: int) -> tuple[int, int]:
        ax, ay, _ = self.landmark(idx_a)
        bx, by, _ = self.landmark(idx_b)
        return (int((ax + bx) / 2), int((ay + by) / 2))

    def fingers_up_count(self) -> int:
        """Return the number of fingers currently extended."""
        return sum(self.fingers_up_mask())

    def fingers_up_mask(self) -> list[bool]:
        """
        Returns [thumb, index, middle, ring, pinky] booleans.
        True = finger extended.  Simple tip-vs-pip Y comparison.
        """
        if not self.detected:
            return [False] * 5

        # Thumb: compare X position (lateral movement)
        thumb_tip_x = self.landmark(self.THUMB_TIP)[0]
        thumb_mcp_x = self.landmark(self.THUMB_MCP)[0]
        handedness  = self._handedness or "Right"
        thumb_up = (
            thumb_tip_x > thumb_mcp_x
            if handedness == "Right"
            else thumb_tip_x < thumb_mcp_x
        )

        # Other 4 fingers: tip.y < pip.y means finger is up
        mask = [thumb_up]
        for tip, pip in zip(self.FINGER_TIPS[1:], self.FINGER_PIPS[1:]):
            tip_y = self.landmark(tip)[1]
            pip_y = self.landmark(pip)[1]
            mask.append(tip_y < pip_y)

        return mask

    # ------------------------------------------------------------------
    # Visualization
    # ------------------------------------------------------------------

    def draw(self, frame: np.ndarray) -> np.ndarray:
        """Draw landmarks and connections on the frame."""
        if not self.detected:
            return frame

        lms = self._landmarks_px

        for start_idx, end_idx in self.mp_hands.HAND_CONNECTIONS:
            sx, sy, _ = lms[start_idx]
            ex, ey, _ = lms[end_idx]
            cv2.line(frame, (sx, sy), (ex, ey),
                     self.CONNECTION_COLOR, self.CONNECTION_THICKNESS, cv2.LINE_AA)

        for i, (x, y, _) in enumerate(lms):
            if i in self.FINGER_TIPS:
                cv2.circle(frame, (x, y), self.FINGERTIP_RADIUS,
                           self.FINGERTIP_COLOR, -1, cv2.LINE_AA)
                cv2.circle(frame, (x, y), self.FINGERTIP_RADIUS + 2,
                           (255, 255, 255), 1, cv2.LINE_AA)
            else:
                cv2.circle(frame, (x, y), self.LANDMARK_RADIUS,
                           self.LANDMARK_COLOR, -1, cv2.LINE_AA)

        return frame

    # ------------------------------------------------------------------

    def _to_pixel_coords(self, hand_landmarks, w: int, h: int):
        result = []
        for lm in hand_landmarks.landmark:
            result.append((int(lm.x * w), int(lm.y * h), lm.z))
        return result

    def release(self):
        self.hands.close()
