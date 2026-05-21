# 🖱️ AI Virtual Mouse — Hand Gesture Controller

> Control your computer with nothing but your hand. No hardware. Just a webcam.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-green?style=flat-square&logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.14-orange?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-purple?style=flat-square)

---

## 📖 Overview

**AI Virtual Mouse** is a real-time hand gesture recognition system that replaces your physical mouse using only a standard webcam. Built with **OpenCV**, **MediaPipe Hands**, and **PyAutoGUI**, it tracks 21 hand landmarks at up to 60 FPS and maps them to precise, smooth cursor movements and OS-level mouse events.

The project is designed to be **portfolio-ready** — modular, commented, production-quality code with a visually impressive dark-themed HUD overlay.

---

## ✨ Feature Overview

| Gesture | Action | How |
|---|---|---|
| ☝️ Index finger up | **Move cursor** | Index fingertip maps to full screen |
| 🤟 Three fingers close | **Left click** | Index + Middle + Ring tips touching |
| ✌️ Two fingers close | **Right click** | Index + Middle tips touching |
| 🤏 Thumb + Index pinch (move up/down) | **Scroll** | Pinch thumb & index, move hand vertically |
| 🖐️ All fingers + thumb spread | **Volume control** | Thumb-index distance = volume level |
| 🤙 Thumb + Pinky pinch | **Screenshot** | Saves PNG to home folder |

---

## 📁 Project Structure

```
virtual_mouse/
│
├── main.py               # Entry point — camera loop, arg parsing, orchestration
├── hand_tracker.py       # MediaPipe wrapper — landmark detection & drawing
├── gesture_controller.py # Gesture state machine — debounce, cooldowns, thresholds
├── mouse_controller.py   # OS mouse actions — EMA smoothing, drag, volume, screenshot
├── utils.py              # HUD overlay — FPS, badges, panels, vignette, log
│
├── requirements.txt      # Python dependencies
└── README.md             # This file
```

---

## 🚀 Installation

### 1. Prerequisites

- Python **3.10+**
- A working webcam (built-in or USB)
- Good lighting (hand clearly visible)

### 2. Clone the repository

```bash
git clone https://github.com/yourname/ai-virtual-mouse.git
cd ai-virtual-mouse/virtual_mouse
```

### 3. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

#### Windows — Volume Control (optional)

```bash
pip install pycaw comtypes
```

Then uncomment those lines in `requirements.txt`.

---

## ▶️ Running the App

```bash
# Basic run (camera 0, default settings)
python main.py

# Use a different camera
python main.py --cam 1

# Run calibration before starting
python main.py --calibrate

# Adjust smoothing (lower = snappier, higher = smoother)
python main.py --smoothing 0.12

# Adjust sensitivity
python main.py --sensitivity 1.5

# Higher resolution
python main.py --width 1920 --height 1080
```

**Press `Q` or `Esc` to quit.**

---

## 🎮 Detailed Gesture Guide

### 1. Move Cursor
- **Gesture:** Raise only your **index finger**
- **How it works:** The index fingertip position is mapped from the webcam's "active zone" (inner frame) to your full screen resolution using `numpy.interp`. Exponential Moving Average (EMA) smoothing removes jitter.
- **Tip:** Keep your other fingers curled down for cleaner tracking.

### 2. Left Click
- **Gesture:** Raise **three fingers** (index + middle + ring) and bring their tips **close together**
- **Threshold:** Index-middle and middle-ring distances both < `0.055`
- **Debounce:** Requires 3 consecutive frames to confirm — prevents accidental clicks
- **Cooldown:** 350ms between clicks

### 3. Right Click
- **Gesture:** Raise **two fingers** (index + middle) and bring their tips **close together**
- **Threshold:** Index-middle distance < `0.055`
- **Cooldown:** 450ms

### 4. Scroll
- **Gesture:** **Pinch thumb and index** together, then move your hand **up or down**
- **How it works:** Pinching enters scroll mode. Vertical movement from the anchor point scrolls up/down.
- **Cooldown:** 60ms (fast scrolling supported)

### 5. Volume Control
- **Gesture:** **Thumb + Index + Middle + Ring** up (pinky down)
- **How it works:** Thumb-index distance is mapped to system volume 0–100%. Wider = louder.

### 6. Screenshot
- **Gesture:** **Thumb + Pinky** pinch (ring, middle, index curled)
- **Output:** Saved as `screenshot_YYYYMMDD_HHMMSS.png` in your home directory
- **Cooldown:** 1 second


---

## ⚙️ Configuration & Tuning

Edit `GestureConfig` in `gesture_controller.py`:

```python
PINCH_THRESHOLD_CLICK   = 0.045   # ↓ = harder to click, ↑ = easier
PINCH_THRESHOLD_RIGHT   = 0.055
SCROLL_THRESHOLD        = 0.04    # ↓ = scroll triggers more easily
COOLDOWN_CLICK          = 0.40    # seconds between clicks
CONFIRM_FRAMES          = 2       # frames before gesture fires
```

Edit `MouseConfig` in `mouse_controller.py`:

```python
FRAME_REDUCTION = 100    # px cropped from each edge of active zone
SMOOTHING       = 0.18   # EMA factor (0.05 = very smooth, 0.5 = raw)
SCROLL_SPEED    = 8      # scroll lines per event
```

---

## 💡 Tips for Best Performance

1. **Lighting:** Use diffuse front lighting. Avoid harsh backlighting (don't sit in front of a window).
2. **Background:** Plain, contrasting backgrounds improve detection.
3. **Camera angle:** Position the camera so your hand is clearly visible from the front/side.
4. **Distance:** Keep your hand 30–60 cm from the webcam.
5. **Speed:** Move your hand slowly and deliberately — the EMA smoothing rewards steady input.
6. **Resolution:** Higher resolution → better landmark accuracy but lower FPS. `1280×720` is the sweet spot.
7. **Gesture purity:** When clicking, curl all other fingers down. Clean gestures = reliable detection.
8. **Thresholds:** If clicks trigger too easily, decrease `PINCH_THRESHOLD_CLICK`. If they're hard to trigger, increase it.

---

## 🖥️ Screenshots

> _Add your own screenshots here after running the app!_

| HUD Active | Volume Control |
|---|---|
| _(your screenshot)_ | _(your screenshot)_ |

---

## 🔬 Technical Architecture

```
Webcam Frame
    │
    ▼
[hand_tracker.py]
  MediaPipe Hands → 21 landmarks (normalized + pixel)
  Finger state → is_finger_up(), fingers_up_mask()
  Distance → distance_norm(), distance()
    │
    ▼
[gesture_controller.py]
  Pattern matching on finger mask + pinch distances
  Debounce (N consecutive frames required)
  Cooldown timers per gesture
  State machine (drag, scroll anchor, volume)
    │
    ▼
[mouse_controller.py]
  Map index tip → screen coordinates (numpy.interp)
  EMA smoothing → smooth cursor movement
  pyautogui calls → OS mouse events
  Volume → pycaw (Win) / osascript (Mac)
    │
    ▼
[utils.py]
  HUD overlay → FPS, gesture badge, log, volume bar
  draw_rounded_rect, draw_pill, draw_text
  Vignette, calibration overlay
```

---

## 🛠️ Known Limitations

- MediaPipe Hands may struggle under poor lighting or complex backgrounds.
- Thumb gesture detection is handedness-dependent (designed for right hand).
- Volume control requires `pycaw` on Windows; macOS uses `osascript`.
- Linux volume requires `pactl` / `amixer` (not implemented — PRs welcome!).
- Two hands simultaneously not supported (uses first detected hand only).

---

## 🚀 Future Improvements

- [ ] **Dual hand support** — left hand for shortcuts, right for cursor
- [ ] **Custom gesture mapping** — configure gestures via JSON/YAML config
- [ ] **Linux volume** — `pactl` integration
- [ ] **Gesture training** — allow user to record custom gestures with ML classifier
- [ ] **Virtual keyboard** — on-screen keyboard controlled by pointing
- [ ] **Multi-monitor support** — gesture to switch between monitors
- [ ] **REST API** — stream gesture events over WebSocket for remote control
- [ ] **GUI settings panel** — tkinter/PyQt configuration panel

---

## 📄 License

MIT License — use it, modify it, ship it.

---

## 🙏 Acknowledgements

- [Google MediaPipe](https://mediapipe.dev/) — hand landmark detection
- [OpenCV](https://opencv.org/) — video capture & image processing
- [PyAutoGUI](https://pyautogui.readthedocs.io/) — cross-platform mouse control

---

_Built for portfolio showcase. Star ⭐ if you found it useful!_
