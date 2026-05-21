"""
main.py
-------
AI Virtual Mouse — entry point.
Run:   python main.py
       python main.py --cam 1
"""

import cv2
import sys
import argparse
import time
import numpy as np

from hand_tracker      import HandTracker
from gesture_controller import GestureController, Gesture, GestureConfig
from mouse_controller  import MouseController, MouseConfig
from utils             import FPSCounter, HUDOverlay, draw_calibration_overlay


# ─────────────────────────────────────────────────────────────────────────────
# CLI arguments
# ─────────────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="AI Virtual Mouse Using Hand Gestures")
    p.add_argument("--cam",         type=int,   default=0,    help="Camera index (default 0)")
    p.add_argument("--width",       type=int,   default=1280, help="Capture width")
    p.add_argument("--height",      type=int,   default=720,  help="Capture height")
    p.add_argument("--calibrate",   action="store_true",      help="Run calibration on startup")
    p.add_argument("--smoothing",   type=float, default=0.5,  help="Cursor smoothing (0.2–0.8)")
    return p.parse_args()


# ─────────────────────────────────────────────────────────────────────────────
# Calibration routine
# ─────────────────────────────────────────────────────────────────────────────

def run_calibration(cap: cv2.VideoCapture, tracker: HandTracker, duration: float = 3.0):
    """Show a countdown overlay, collect hand detections."""
    print("[Calibration] Hold your hand clearly in frame for 3 seconds…")
    start      = time.time()
    detections = 0
    frames     = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        tracker.process(frame)
        elapsed  = time.time() - start
        progress = min(elapsed / duration, 1.0)

        if tracker.detected:
            detections += 1
            tracker.draw(frame)
        frames += 1

        draw_calibration_overlay(frame, progress, "Show your hand — calibrating…")
        cv2.imshow("AI Virtual Mouse — Calibration", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break
        if elapsed >= duration:
            break

    cv2.destroyWindow("AI Virtual Mouse — Calibration")
    success_rate = detections / max(frames, 1)
    print(f"[Calibration] Detection rate: {success_rate:.0%}")
    if success_rate < 0.5:
        print("[Calibration] ⚠  Low detection rate — check lighting & camera position.")
        return False
    print("[Calibration] ✓  Calibration complete.")
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Main loop
# ─────────────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    # ── Open camera ───────────────────────────────────────────────────
    print(f"[Init] Opening camera {args.cam}…")
    cap = cv2.VideoCapture(args.cam)
    if not cap.isOpened():
        sys.exit(f"[Error] Cannot open camera {args.cam}. "
                 "Check it's connected and not in use by another app.")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    cap.set(cv2.CAP_PROP_FPS, 60)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"[Init] Camera resolution: {actual_w}×{actual_h}")

    # ── Subsystems ────────────────────────────────────────────────────
    tracker      = HandTracker(max_hands=1, model_complexity=1,
                               detection_confidence=0.65, tracking_confidence=0.5)
    gesture_ctrl = GestureController(GestureConfig())

    m_cfg = MouseConfig()
    m_cfg.SMOOTHING = args.smoothing
    mouse_ctrl = MouseController(frame_shape=(actual_h, actual_w), config=m_cfg)

    fps_counter = FPSCounter(window=30)
    hud         = HUDOverlay(actual_w, actual_h, frame_reduction=m_cfg.FRAME_REDUCTION)

    # ── Optional calibration ──────────────────────────────────────────
    if args.calibrate:
        ok = run_calibration(cap, tracker)
        if not ok:
            print("[Warn] Continuing without successful calibration.")

    # ── Print gesture guide ───────────────────────────────────────────
    print()
    print("╔════════════════════════════════════════════════════╗")
    print("║           GESTURE CONTROLS                        ║")
    print("╠════════════════════════════════════════════════════╣")
    print("║  1 finger  (index)         → Move Cursor          ║")
    print("║  2 fingers (index+middle)  → Left Click           ║")
    print("║  3 fingers (index+mid+ring)→ Right Click          ║")
    print("║  5 fingers (open palm)     → Scroll Up/Down       ║")
    print("║  0 fingers (fist, hold)    → Screenshot           ║")
    print("╠════════════════════════════════════════════════════╣")
    print("║  Press Q or Esc to quit                           ║")
    print("╚════════════════════════════════════════════════════╝")
    print()

    # ── State ─────────────────────────────────────────────────────────
    window_name      = "AI Virtual Mouse  •  Press Q to quit"
    screenshot_flash = 0

    # ── Make window small, always-on-top (PiP style) ──────────────────
    # The virtual mouse works on your ENTIRE screen via pyautogui.
    # You can minimize this window and it keeps working.
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.resizeWindow(window_name, 480, 270)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

    # ── Frame loop ────────────────────────────────────────────────────
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[Error] Failed to grab frame — camera disconnected?")
            break

        # Mirror the frame (natural UX)
        frame = cv2.flip(frame, 1)

        # Lightweight brightness boost
        frame = cv2.convertScaleAbs(frame, alpha=1.05, beta=5)

        # ── Hand detection ────────────────────────────────────────────
        tracking = tracker.process(frame)

        # ── Gesture recognition ───────────────────────────────────────
        gesture = gesture_ctrl.update(tracker)

        # ── Mouse action ──────────────────────────────────────────────
        action_info = mouse_ctrl.handle(gesture, tracker)

        # ── Screenshot flash effect ───────────────────────────────────
        if action_info.get("screenshot_taken"):
            screenshot_flash = 6

        if screenshot_flash > 0:
            flash_alpha = screenshot_flash / 6.0
            white = np.full_like(frame, 255)
            cv2.addWeighted(white, flash_alpha * 0.5, frame, 1.0, 0, frame)
            screenshot_flash -= 1

        # ── Draw hand landmarks ───────────────────────────────────────
        if tracking:
            tracker.draw(frame)

            # Show finger count on frame
            count = tracker.fingers_up_count()
            cv2.putText(frame, f"Fingers: {count}", (actual_w - 200, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 200), 2, cv2.LINE_AA)

        # ── HUD overlay ───────────────────────────────────────────────
        fps = fps_counter.tick()
        hud.draw(
            frame,
            fps         = fps,
            gesture     = gesture,
            tracking    = tracking,
            volume      = 0.5,
            action_info = action_info,
        )

        # ── Show ──────────────────────────────────────────────────────
        cv2.imshow(window_name, frame)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), ord("Q"), 27):
            print("[Exit] Quit requested.")
            break

    # ── Cleanup ───────────────────────────────────────────────────────
    tracker.release()
    cap.release()
    cv2.destroyAllWindows()
    print("[Done] Virtual mouse stopped.")


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
