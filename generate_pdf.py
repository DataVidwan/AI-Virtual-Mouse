"""
generate_pdf.py
---------------
Generates the AI Virtual Mouse DIY documentation PDF.
Uses fpdf2 for clean, professional output matching the ImagineX Studio reference style.

Run:  pip install fpdf2   (if not installed)
      python generate_pdf.py
"""

from fpdf import FPDF
import os


class DocPDF(FPDF):
    """Custom PDF with header/footer styling."""

    PAGE_MARGIN = 25
    BODY_FONT = "Helvetica"
    LINE_H = 7  # line height for body text

    def __init__(self):
        super().__init__("P", "mm", "A4")
        self.set_auto_page_break(auto=True, margin=25)
        self.set_left_margin(self.PAGE_MARGIN)
        self.set_right_margin(self.PAGE_MARGIN)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-15)
        self.set_font(self.BODY_FONT, "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"AI Virtual Mouse - Data Vidwan DIY Project", align="L")
        self.cell(0, 10, f"Page {self.page_no()}", align="R")

    # ── Helpers ──────────────────────────────────────────────────────

    def add_title_page(self, title: str, subtitle: str):
        """Full-page title with gradient-style header block."""
        self.add_page()
        # Large colored header block
        self.set_fill_color(15, 23, 42)  # dark navy
        self.rect(0, 0, 210, 120, "F")
        # Accent bar
        self.set_fill_color(0, 200, 150)  # cyan-green accent
        self.rect(0, 120, 210, 3, "F")

        # Title text
        self.set_y(38)
        self.set_font(self.BODY_FONT, "B", 36)
        self.set_text_color(255, 255, 255)
        self.cell(0, 16, "AI Virtual Mouse", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

        # Subtitle
        self.set_font(self.BODY_FONT, "", 14)
        self.set_text_color(180, 220, 210)
        self.cell(0, 8, "Hand Gesture Computer Control", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)
        self.set_font(self.BODY_FONT, "I", 11)
        self.set_text_color(140, 180, 170)
        self.cell(0, 8, "Control your computer with nothing but your hand. No hardware. Just a webcam.",
                  align="C", new_x="LMARGIN", new_y="NEXT")

        # Info box below header
        self.set_y(145)
        self.set_font(self.BODY_FONT, "", 11)
        self.set_text_color(80, 80, 100)

        info_items = [
            ("Project", "AI Virtual Mouse - DIY #2"),
            ("Organization", "Data Vidwan"),
            ("Stack", "Python · OpenCV · MediaPipe · PyAutoGUI"),
            ("Category", "Computer Vision · Gesture Recognition · HCI"),
            ("License", "MIT - use it, modify it, ship it"),
        ]
        for label, value in info_items:
            self.set_font(self.BODY_FONT, "B", 11)
            self.set_text_color(60, 60, 80)
            self.cell(40, 8, f"{label}:")
            self.set_font(self.BODY_FONT, "", 11)
            self.set_text_color(90, 90, 110)
            self.cell(0, 8, value, new_x="LMARGIN", new_y="NEXT")

    def section_heading(self, number: str, title: str):
        """Major section heading like '1. Introduction'."""
        self.ln(6)
        self.set_font(self.BODY_FONT, "B", 20)
        self.set_text_color(15, 23, 42)
        self.cell(0, 12, f"{number}. {title}", new_x="LMARGIN", new_y="NEXT")
        # Accent underline
        x = self.get_x()
        y = self.get_y()
        self.set_draw_color(0, 200, 150)
        self.set_line_width(0.8)
        self.line(x, y, x + 50, y)
        self.ln(6)

    def sub_heading(self, title: str):
        """Sub-section heading like 'Core AI Capabilities'."""
        self.ln(4)
        self.set_font(self.BODY_FONT, "B", 13)
        self.set_text_color(30, 60, 90)
        self.cell(0, 9, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def body(self, text: str):
        """Normal body paragraph."""
        self.set_font(self.BODY_FONT, "", 10.5)
        self.set_text_color(50, 50, 65)
        self.multi_cell(0, self.LINE_H, text)
        self.ln(2)

    def feature_item(self, name: str, description: str):
        """Bold feature name followed by description on the same line."""
        self.set_font(self.BODY_FONT, "B", 10.5)
        self.set_text_color(30, 50, 80)
        name_w = self.get_string_width(name + "  ") + 2
        self.cell(name_w, self.LINE_H, name + " ")

        self.set_font(self.BODY_FONT, "", 10.5)
        self.set_text_color(50, 50, 65)
        remaining_w = self.w - self.get_x() - self.r_margin
        self.multi_cell(remaining_w, self.LINE_H, description)
        self.ln(1)

    def bullet(self, text: str, indent: int = 8):
        """Bullet point item."""
        self.set_font(self.BODY_FONT, "", 10.5)
        self.set_text_color(50, 50, 65)
        x = self.get_x()
        self.cell(indent, self.LINE_H, "")
        self.set_font(self.BODY_FONT, "", 10.5)
        self.cell(5, self.LINE_H, chr(183) + " ")  # bullet char
        remaining_w = self.w - self.get_x() - self.r_margin
        self.multi_cell(remaining_w, self.LINE_H, text)
        self.ln(0.5)

    def step_block(self, step_num: str, title: str, user_text: str, ai_text: str):
        """Step block for 'How the Experience Works' section."""
        self.ln(2)
        # Step header
        self.set_font(self.BODY_FONT, "B", 12)
        self.set_text_color(0, 160, 120)
        self.cell(0, 9, f"{step_num} {title}", new_x="LMARGIN", new_y="NEXT")
        self.ln(1)
        # User line
        self.set_font(self.BODY_FONT, "B", 10.5)
        self.set_text_color(60, 100, 180)
        self.cell(8, self.LINE_H, "")
        user_label_w = self.get_string_width("User: ") + 2
        self.cell(user_label_w, self.LINE_H, "User: ")
        self.set_font(self.BODY_FONT, "", 10.5)
        self.set_text_color(50, 50, 65)
        remaining = self.w - self.get_x() - self.r_margin
        self.multi_cell(remaining, self.LINE_H, user_text)
        self.ln(1)
        # AI line
        self.set_font(self.BODY_FONT, "B", 10.5)
        self.set_text_color(0, 160, 120)
        self.cell(8, self.LINE_H, "")
        ai_label_w = self.get_string_width("AI: ") + 2
        self.cell(ai_label_w, self.LINE_H, "AI: ")
        self.set_font(self.BODY_FONT, "I", 10.5)
        self.set_text_color(60, 60, 80)
        remaining = self.w - self.get_x() - self.r_margin
        self.multi_cell(remaining, self.LINE_H, ai_text)
        self.ln(1)

    def code_line(self, text: str, indent: int = 8):
        """Monospaced code/command line."""
        self.set_font("Courier", "", 9.5)
        self.set_text_color(40, 40, 55)
        # Light grey background
        x = self.get_x() + indent
        y = self.get_y()
        tw = self.get_string_width(text) + 6
        self.set_fill_color(240, 240, 245)
        self.rect(x, y, min(tw, self.w - x - self.r_margin), 6.5, "F")
        self.cell(indent, self.LINE_H, "")
        self.cell(0, self.LINE_H, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def table_row(self, col1: str, col2: str, bold_col1: bool = True):
        """Two-column table row for project structure."""
        x_start = self.get_x()
        col1_w = 45
        col2_w = self.w - self.l_margin - self.r_margin - col1_w

        if bold_col1:
            self.set_font("Courier", "B", 9.5)
        else:
            self.set_font("Courier", "", 9.5)
        self.set_text_color(30, 50, 80)

        y_before = self.get_y()
        self.cell(col1_w, self.LINE_H, col1)

        self.set_font(self.BODY_FONT, "", 10)
        self.set_text_color(50, 50, 65)
        self.multi_cell(col2_w, self.LINE_H, col2)
        self.ln(2)

    def add_follow_page(self):
        """Final 'Follow us' page matching the reference style."""
        self.add_page()
        # Big colored block
        self.set_fill_color(15, 23, 42)
        self.rect(0, 0, 210, 297, "F")

        # Accent bar at top
        self.set_fill_color(0, 200, 150)
        self.rect(0, 0, 210, 4, "F")

        self.set_y(80)
        self.set_font(self.BODY_FONT, "B", 22)
        self.set_text_color(255, 255, 255)
        self.cell(0, 14, "Follow us for more", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_font(self.BODY_FONT, "B", 22)
        self.set_text_color(0, 200, 150)
        self.cell(0, 14, "interesting projects &", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 14, "innovations every week.", align="C", new_x="LMARGIN", new_y="NEXT")

        self.ln(6)
        self.set_font(self.BODY_FONT, "", 14)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "Stay connected.", align="C", new_x="LMARGIN", new_y="NEXT")

        self.ln(12)
        self.set_font(self.BODY_FONT, "", 11)
        self.set_text_color(180, 200, 195)
        self.multi_cell(0, 8,
            "Join the community to explore innovative DIY projects, learn emerging\n"
            "technologies, and stay updated with hands-on development trends.",
            align="C")


def build_pdf():
    pdf = DocPDF()

    # ══════════════════════════════════════════════════════════════════════
    # TITLE PAGE
    # ══════════════════════════════════════════════════════════════════════
    pdf.add_title_page(
        "AI Virtual Mouse",
        "Hand Gesture Computer Control"
    )

    # ══════════════════════════════════════════════════════════════════════
    # 1. INTRODUCTION
    # ══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_heading("1", "Introduction")

    pdf.body(
        "What if you could control your entire computer - move the cursor, click, scroll, "
        "adjust volume, and take screenshots - using nothing but your hand in front of a webcam?"
    )
    pdf.body(
        "That's AI Virtual Mouse. It's an open-source, real-time hand gesture recognition system "
        "that replaces your physical mouse entirely. Built at Data Vidwan, it uses computer vision "
        "and AI to track 21 hand landmarks at up to 60 FPS and maps them to precise, smooth cursor "
        "movements and OS-level mouse events - no special hardware required."
    )
    pdf.body(
        "Under the hood, MediaPipe's hand tracking model detects your hand in every frame, a custom "
        "gesture state machine interprets finger positions into actions, and PyAutoGUI executes those "
        "actions as real mouse clicks, scrolls, and system commands. The result? A touchless computing "
        "experience that feels natural and responsive."
    )
    pdf.body(
        "This isn't just a working app - it's a learning reference. Every design choice, from the EMA "
        "smoothing algorithm to the debounce-based gesture recognition engine, is built to be read, "
        "understood, and improved. If you're a developer, student, or AI enthusiast, this is the kind "
        "of project that makes you think: \"I could build something even better with this.\""
    )

    # ══════════════════════════════════════════════════════════════════════
    # 2. FEATURES
    # ══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_heading("2", "Features")

    pdf.body(
        "AI Virtual Mouse packs a comprehensive feature set across the computer vision pipeline, "
        "gesture recognition engine, and system control layers. Here's what's inside:"
    )

    # -- Core AI --
    pdf.sub_heading("Core AI Capabilities")
    pdf.feature_item("Real-Time Hand Tracking",
        "MediaPipe Hands detects and tracks 21 hand landmarks per frame with sub-millisecond "
        "latency, providing both normalized and pixel-space coordinates.")
    pdf.feature_item("Finger State Detection",
        "A handedness-aware algorithm determines which fingers are extended using tip-vs-PIP "
        "comparisons (y-axis for fingers, x-axis for thumb).")
    pdf.feature_item("Normalized Distance Metrics",
        "Euclidean distances between any two landmarks are computed in normalized space (0-1), "
        "making gesture detection resolution-independent.")
    pdf.feature_item("Landmark Visualization",
        "Custom-styled hand skeleton drawing with cyan-green connections, hot-pink fingertip "
        "highlights, and white-bordered tips for visual clarity.")

    # -- Gesture Engine --
    pdf.sub_heading("Gesture Recognition Engine")
    pdf.feature_item("6 Gesture Types",
        "Move Cursor, Left Click, Right Click, Scroll (Up/Down), Volume Control (Up/Down), "
        "and Screenshot - each with distinct finger patterns and distance thresholds.")
    pdf.feature_item("Debounce System",
        "Every discrete gesture requires N consecutive frames of confirmation before firing, "
        "eliminating accidental triggers from transient hand movements.")
    pdf.feature_item("Cooldown Timers",
        "Per-gesture cooldown windows (300ms for left click, 400ms for right click, 1000ms "
        "for screenshot) prevent rapid-fire duplicate actions.")
    pdf.feature_item("Priority-Based Resolution",
        "When multiple gestures could match, a strict priority order (Screenshot > Left Click "
        "> Right Click > Scroll > Volume > Cursor Move) ensures the most specific gesture wins.")
    pdf.feature_item("Scroll Anchor System",
        "Scroll mode uses a wrist-position anchor; vertical displacement from the anchor "
        "determines scroll direction and magnitude for intuitive control.")

    # -- System Control --
    pdf.add_page()
    pdf.sub_heading("System Control & Mouse Actions")
    pdf.feature_item("EMA-Smoothed Cursor",
        "Exponential Moving Average smoothing (configurable alpha = 0.05-0.5) eliminates hand "
        "jitter while preserving responsiveness for precise cursor placement.")
    pdf.feature_item("Active Zone Mapping",
        "The webcam frame is cropped by a configurable margin (default 100px per edge), and the "
        "remaining active zone is mapped to full screen resolution using numpy.interp.")
    pdf.feature_item("Cross-Platform Volume",
        "Windows volume via pycaw/comtypes with logarithmic dB mapping; macOS via osascript; "
        "graceful degradation on unsupported platforms.")
    pdf.feature_item("Instant Screenshots",
        "Captures the full screen as a timestamped PNG (screenshot_YYYYMMDD_HHMMSS.png) saved "
        "to the user's home directory.")
    pdf.feature_item("PyAutoGUI Integration",
        "All mouse events (moveTo, click, rightClick, scroll) are executed through PyAutoGUI "
        "with PAUSE disabled for maximum responsiveness and FAILSAFE enabled for safety.")

    # -- UI/UX --
    pdf.sub_heading("User Interface & Experience")
    pdf.feature_item("Dark-Themed HUD Overlay",
        "A professional heads-up display rendered directly on the webcam feed with semi-transparent "
        "panels, rounded rectangles, and anti-aliased text.")
    pdf.feature_item("Real-Time FPS Counter",
        "A sliding-window (30-frame) FPS counter with color-coded display: green (>20), orange "
        "(10-20), red (<10).")
    pdf.feature_item("Gesture Badge",
        "A pill-shaped badge at bottom center shows the currently detected gesture with "
        "gesture-specific color coding.")
    pdf.feature_item("Volume Bar",
        "A vertical volume indicator appears on the right edge during volume gestures, showing "
        "current system volume as a filled bar with percentage label.")
    pdf.feature_item("Gesture History Log",
        "The last 5 gesture events displayed in the bottom-right corner with time-based fade "
        "animation (3-second decay from full color to grey).")
    pdf.feature_item("Vignette Effect",
        "A pre-computed radial darkening mask applied per-frame at near-zero cost, giving the "
        "webcam feed a cinematic, focused appearance.")
    pdf.feature_item("Calibration Mode",
        "Optional startup calibration with countdown overlay, progress bar, and detection rate "
        "reporting to verify camera and lighting conditions.")
    pdf.feature_item("Click Test Panel",
        "A standalone tkinter test window with dark theme, large buttons, scroll area, and "
        "real-time feedback for verifying gesture accuracy.")

    # ══════════════════════════════════════════════════════════════════════
    # 3. TECHNOLOGY STACK
    # ══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_heading("3", "Technology Stack")

    pdf.body("AI Virtual Mouse is built with a focused, efficient stack. Here's what powers it:")
    pdf.ln(2)

    pdf.feature_item("Python 3.10+",
        "Core language for all application logic, gesture recognition, and system control.")
    pdf.feature_item("OpenCV >= 4.8",
        "Video capture, frame manipulation, brightness enhancement, and all HUD overlay "
        "rendering (rectangles, circles, text, vignette).")
    pdf.feature_item("MediaPipe 0.10.14",
        "Google's hand landmark detection model - 21 3D landmarks per hand, runs on CPU at "
        "real-time speeds with model_complexity=0 for maximum performance.")
    pdf.feature_item("PyAutoGUI >= 0.9.54",
        "Cross-platform mouse and keyboard automation - cursor movement, clicks, scrolls, "
        "and screenshot capture.")
    pdf.feature_item("NumPy >= 1.24",
        "Array-based math for distance calculations, coordinate interpolation (interp), EMA "
        "smoothing, volume mapping (clip), and vignette mask generation.")
    pdf.feature_item("pycaw >= 20230410",
        "Windows Audio Session API wrapper for direct system volume control via "
        "IAudioEndpointVolume with logarithmic dB conversion.")
    pdf.feature_item("comtypes >= 1.2",
        "COM interface binding required by pycaw for Windows audio endpoint access.")
    pdf.feature_item("Pillow >= 10.0",
        "Screen capture backend used internally by PyAutoGUI for screenshot functionality.")
    pdf.feature_item("argparse (stdlib)",
        "CLI argument parsing for camera index, resolution, sensitivity, smoothing, and "
        "calibration mode.")
    pdf.feature_item("tkinter (stdlib)",
        "Built-in GUI toolkit for the click test verification window.")

    # ══════════════════════════════════════════════════════════════════════
    # 4. HOW THE EXPERIENCE WORKS
    # ══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_heading("4", "How the Experience Works")

    pdf.body(
        "This is where the magic happens. Six steps, running 60 times per second - here's what "
        "you and the AI experience at each one:"
    )

    pdf.step_block("1 -", "Launch & Configure",
        "Run python main.py with optional flags (--cam, --calibrate, --smoothing, --sensitivity).",
        "Opens the webcam, initializes MediaPipe Hands with optimized settings "
        "(model_complexity=0, detection_confidence=0.7), creates the gesture controller, "
        "mouse controller, FPS counter, and HUD overlay subsystems."
    )
    pdf.step_block("2 -", "Hand Detection",
        "Hold your hand in front of the webcam. That's it.",
        "Every frame is flipped (mirror mode), brightness-boosted, converted to RGB, and fed "
        "to MediaPipe. The model returns 21 3D landmarks - wrist, each finger's CMC/MCP/PIP/"
        "DIP/TIP joints - in both normalized (0-1) and pixel coordinates."
    )
    pdf.step_block("3 -", "Gesture Recognition",
        "Form a gesture with your fingers - point, pinch, spread, or curl.",
        "The gesture controller reads the finger-up mask [thumb, index, middle, ring, pinky], "
        "computes inter-landmark distances, and runs a priority-ordered pattern matcher. "
        "Debounce counters and cooldown timers filter out noise. A single, confirmed gesture "
        "string is produced."
    )

    pdf.add_page()
    pdf.step_block("4 -", "System Action",
        "Watch the cursor move, see the click register, or hear the volume change.",
        "The mouse controller maps index fingertip position to screen coordinates via numpy.interp, "
        "applies EMA smoothing, and calls pyautogui.moveTo(). For clicks, scrolls, and volume "
        "changes, the corresponding OS-level action fires immediately. Cursor movement is frozen "
        "during click gestures to prevent drift away from the target."
    )
    pdf.step_block("5 -", "Visual Feedback",
        "See everything happening in real-time on the webcam feed.",
        "The HUD overlay renders the info panel (FPS + tracking status), gesture badge, volume "
        "bar, gesture history log, active zone rectangle, pinch proximity indicator, and vignette "
        "effect - all composited onto the frame before display."
    )
    pdf.step_block("6 -", "Repeat at 60 FPS",
        "Keep using gestures naturally. Press Q or Esc when done.",
        "The frame loop continues until exit. On quit, MediaPipe hands are released, the camera "
        "is freed, and all OpenCV windows are destroyed cleanly."
    )

    pdf.ln(6)
    pdf.sub_heading("The complete pipeline at a glance:")
    pdf.ln(2)
    # Pipeline diagram as text
    pdf.set_font("Courier", "B", 9)
    pdf.set_text_color(0, 140, 105)
    pipeline = (
        "Webcam Frame  -->  MediaPipe Hand Detection  -->  Gesture State Machine\n"
        "     -->  OS Mouse/System Actions  -->  HUD Overlay Feedback  -->  Display"
    )
    pdf.multi_cell(0, 6, pipeline, align="C")

    # ══════════════════════════════════════════════════════════════════════
    # 5. LIVE INTERFACE
    # ══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_heading("5", "Live Interface")

    pdf.body(
        "The AI Virtual Mouse interface is rendered directly onto the webcam feed using OpenCV - "
        "no separate GUI framework needed for the main experience. Every visual element is drawn "
        "in real-time at full frame rate."
    )

    pdf.sub_heading("Camera Feed & Hand Skeleton")
    pdf.body(
        "The webcam feed fills the entire window in mirror mode, so hand movements feel natural "
        "and intuitive. When a hand is detected, the full 21-point skeleton is drawn with "
        "light-blue connections and cyan-green landmark dots. Fingertips get special treatment: "
        "hot-pink filled circles with white borders make them instantly distinguishable."
    )

    pdf.sub_heading("Active Zone Indicator")
    pdf.body(
        "A subtle dark-grey rectangle marks the \"active zone\" - the region of the frame that "
        "maps to your full screen. This visual boundary helps users keep their hand in the "
        "responsive area without guessing."
    )

    pdf.sub_heading("Info Panel (Top-Left)")
    pdf.body(
        "A semi-transparent rounded panel in the top-left corner shows two critical metrics: "
        "FPS (color-coded green/orange/red with one-decimal precision) and Tracking Status "
        "(a colored dot - green = TRACKING, red = NO HAND - with label)."
    )

    pdf.sub_heading("Gesture Badge (Bottom-Center)")
    pdf.body(
        "A pill-shaped badge displays the currently active gesture name. The badge color changes "
        "per gesture type: cyan for Move Cursor, blue for Left Click, red for Right Click, orange "
        "for Scroll, green for Volume, and gold for Screenshot. The dark background and colored "
        "border create a floating, modern appearance."
    )

    pdf.sub_heading("Volume Bar (Right Edge)")
    pdf.body(
        "When volume gestures are active, a vertical bar appears along the right edge of the frame. "
        "The bar fills from bottom to top proportionally to the current system volume, with a "
        "percentage label above. The bar disappears automatically when volume gestures end."
    )

    pdf.sub_heading("Gesture History (Bottom-Right)")
    pdf.body(
        "The last 5 unique gesture events appear as a scrolling log in the bottom-right corner. "
        "Each entry fades from its gesture color to grey over 3 seconds, creating an elegant "
        "timeline of recent actions."
    )

    pdf.sub_heading("Pinch Proximity Indicator")
    pdf.body(
        "A dynamic circle drawn between the thumb and index fingertips changes size and color "
        "based on proximity. As fingers approach: the circle shrinks and transitions from grey to "
        "cyan, giving instant visual feedback on how close you are to triggering a pinch gesture."
    )

    pdf.sub_heading("Calibration Overlay")
    pdf.body(
        "When launched with --calibrate, a full-screen overlay dims the feed and shows a progress "
        "bar with countdown text. The calibration routine measures hand detection consistency over "
        "3 seconds and reports the detection rate. If below 50%, a warning suggests checking "
        "lighting and camera position."
    )

    pdf.sub_heading("Click Test Window")
    pdf.body(
        "A separate test utility (test_clicks.py) opens a dark-themed tkinter window with two "
        "large buttons (LEFT CLICK and RIGHT CLICK) with click counters, a scrollable text area "
        "with 50 lines for testing scroll gestures, flash animations on button press for visual "
        "confirmation, and a status bar showing the last detected action with timestamp. The "
        "window stays on top so it's always visible while using hand gestures."
    )

    # ══════════════════════════════════════════════════════════════════════
    # 6. PROJECT STRUCTURE
    # ══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_heading("6", "Project Structure")

    pdf.body(
        "AI Virtual Mouse uses a clean, modular architecture - each file owns a single "
        "responsibility, making the codebase easy to navigate, test, and extend."
    )
    pdf.ln(2)

    # Table header
    pdf.set_fill_color(240, 242, 248)
    pdf.set_font(pdf.BODY_FONT, "B", 10.5)
    pdf.set_text_color(30, 40, 60)
    pdf.cell(45, 8, "File / Directory", fill=True)
    pdf.cell(0, 8, "Description", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.table_row("main.py",
        "Entry point - CLI argument parsing, camera initialization, calibration "
        "routine, frame loop orchestration, and subsystem coordination.")
    pdf.table_row("hand_tracker.py",
        "MediaPipe Hands wrapper - processes BGR frames, extracts 21 landmarks in "
        "normalized and pixel space, computes distances and midpoints, determines "
        "finger-up states, and draws the hand skeleton.")
    pdf.table_row("gesture_controller.py",
        "Gesture state machine - pattern-matches finger masks and pinch distances "
        "into 6 gesture types. Implements debounce, cooldowns, scroll anchor, and "
        "volume mapping.")
    pdf.table_row("mouse_controller.py",
        "OS action executor - maps gestures to real mouse events via PyAutoGUI. "
        "Handles EMA cursor smoothing, click/scroll dispatch, cross-platform volume "
        "control, and timestamped screenshots.")
    pdf.table_row("utils.py",
        "UI toolkit - FPS counter, color palette, drawing primitives (rounded rects, "
        "pills, text), and the full HUD overlay class (info panel, gesture badge, "
        "volume bar, gesture log, vignette, calibration overlay).")
    pdf.table_row("test_clicks.py",
        "Verification tool - standalone dark-themed tkinter window with click buttons, "
        "scroll area, counters, and flash animations for testing gesture accuracy.")
    pdf.table_row("requirements.txt",
        "Python dependency list: opencv-python, mediapipe, pyautogui, numpy, pycaw, "
        "comtypes, Pillow.")
    pdf.table_row(".venv/",
        "Python virtual environment directory. Install dependencies here; excluded "
        "from Git.")

    # ══════════════════════════════════════════════════════════════════════
    # 7. INSTALLATION & SETUP
    # ══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_heading("7", "Installation & Setup")

    pdf.body("Getting AI Virtual Mouse running locally takes about 5 minutes. Here's how:")

    pdf.sub_heading("Clone the Repository")
    pdf.body("[ https://github.com/DataVidwan/DIY-2-AI-Virtual-Mouse ]")
    pdf.code_line("git clone <repository_url>  &&  cd ai-virtual-mouse")

    pdf.sub_heading("Environment Setup")
    pdf.body(
        "Python 3.10+ is required (developed on 3.11). Use a virtual environment to keep "
        "dependencies clean:"
    )
    pdf.body(
        "Windows (PowerShell): python -m venv .venv  ->  .\\.venv\\Scripts\\Activate.ps1  ->  "
        "pip install -r requirements.txt"
    )
    pdf.body(
        "macOS / Linux: python -m venv .venv  ->  source .venv/bin/activate  ->  "
        "pip install -r requirements.txt"
    )

    pdf.sub_heading("Hardware Requirements")
    pdf.bullet("A working webcam (built-in or USB) - this is the only hardware you need")
    pdf.bullet("No GPU required - MediaPipe runs entirely on CPU")
    pdf.bullet("Good lighting - diffuse, front-facing light produces the best hand detection")

    pdf.sub_heading("Run the App")
    pdf.code_line("python main.py")
    pdf.body(
        "The webcam opens immediately and gesture control is active. Press Q or Esc to quit."
    )

    pdf.sub_heading("Command-Line Options")
    pdf.code_line("python main.py --cam 1              # Different camera")
    pdf.code_line("python main.py --calibrate          # Run calibration")
    pdf.code_line("python main.py --smoothing 0.12     # Cursor smoothing")
    pdf.code_line("python main.py --sensitivity 1.5    # Sensitivity")
    pdf.code_line("python main.py --width 1920 --height 1080  # Resolution")

    pdf.sub_heading("Testing Your Gestures")
    pdf.body("Open a second terminal and run:")
    pdf.code_line("python test_clicks.py")
    pdf.body(
        "A test window with click buttons and a scroll area appears. Use hand gestures to "
        "interact with it and verify that clicks, right-clicks, and scrolling work correctly."
    )

    pdf.sub_heading("Tips for Best Results")
    pdf.bullet("Use clear, front-facing hand position with fingers clearly visible against the background.")
    pdf.bullet("Good lighting and a plain, contrasting background produce the most consistent tracking.")
    pdf.bullet("Keep your hand 30-60 cm from the webcam for optimal landmark detection.")
    pdf.bullet("Move your hand slowly and deliberately - the EMA smoothing rewards steady input.")
    pdf.bullet("For clicking: curl all non-clicking fingers down clearly. Clean gestures = reliable detection.")
    pdf.bullet("1280x720 is the sweet spot for resolution - higher gives better accuracy but lower FPS.")
    pdf.bullet("If clicks trigger too easily, decrease PINCH_THRESHOLD_CLICK in gesture_controller.py.")

    # ══════════════════════════════════════════════════════════════════════
    # 8. COMMUNITY CHALLENGE
    # ══════════════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.section_heading("8", "Community Challenge")

    pdf.body(
        "AI Virtual Mouse is more than a working app. It's an open invitation."
    )
    pdf.body(
        "Every threshold value, every gesture pattern, every smoothing algorithm in this codebase "
        "was made to be questioned, improved, and replaced with something better. This project "
        "represents one approach to gesture-based computer control - there are dozens of others "
        "waiting to be discovered."
    )

    pdf.sub_heading("What You Can Build Next")
    pdf.body(
        "These aren't minor tweaks. They're starting points for substantially more powerful systems:"
    )
    pdf.ln(2)

    challenges = [
        "Add dual-hand support - left hand for shortcuts and hotkeys, right hand for cursor control.",
        "Implement custom gesture mapping - let users define their own gestures via a JSON/YAML config file and train a lightweight ML classifier.",
        "Build a virtual on-screen keyboard controlled entirely by pointing and pinch-to-type.",
        "Add multi-monitor support - gesture to switch between screens or span cursor across displays.",
        "Integrate MediaPipe's face mesh for head-tracking mouse control as an accessibility tool.",
        "Implement drag-and-drop - pinch to grab, move hand to drag, release to drop.",
        "Build a REST API / WebSocket server that streams gesture events for remote control applications.",
        "Add Linux volume control via pactl/amixer integration for full cross-platform coverage.",
        "Create a GUI settings panel (PyQt/tkinter) for real-time threshold tuning without code edits.",
        "Deploy as a system tray application that runs in the background and activates on hotkey.",
        "Extend to full body pose estimation (MediaPipe Pose) for presentation control and gaming.",
        "Build a gesture recorder that captures and replays macro sequences for automation workflows.",
    ]
    for c in challenges:
        pdf.bullet(c)

    pdf.ln(6)
    pdf.set_font(pdf.BODY_FONT, "B", 12)
    pdf.set_text_color(0, 160, 120)
    pdf.cell(0, 10, "This is only the starting point. Now build something even more powerful.",
             align="C", new_x="LMARGIN", new_y="NEXT")

    # ══════════════════════════════════════════════════════════════════════
    # FOLLOW US PAGE
    # ══════════════════════════════════════════════════════════════════════
    pdf.add_follow_page()

    # ── Save ──────────────────────────────────────────────────────────────
    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "AI_Virtual_Mouse_Documentation.pdf"
    )
    pdf.output(output_path)
    print(f"[Done] PDF saved to: {output_path}")
    print(f"       Size: {os.path.getsize(output_path) / 1024:.1f} KB")
    print(f"       Pages: {pdf.page_no()}")


if __name__ == "__main__":
    build_pdf()
