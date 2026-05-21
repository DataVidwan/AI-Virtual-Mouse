"""
test_clicks.py
--------------
A simple test window to verify that the AI Virtual Mouse
gestures (left click, right click, scroll) are working correctly.

Run this ALONGSIDE main.py:
    Terminal 1:  python main.py
    Terminal 2:  python test_clicks.py

Then use hand gestures to interact with the buttons and scroll area.
"""

import tkinter as tk
from tkinter import font as tkfont
import time


class ClickTestApp:
    """A dark-themed test window with big buttons and a scroll area."""

    BG_DARK      = "#0f0f1a"
    BG_PANEL     = "#1a1a2e"
    ACCENT_CYAN  = "#00dca0"
    ACCENT_BLUE  = "#3c8cff"
    ACCENT_PINK  = "#ff5096"
    TEXT_WHITE    = "#e8e8f0"
    TEXT_GREY     = "#808090"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🖱️ AI Virtual Mouse — Click & Scroll Test")
        self.root.geometry("520x650")
        self.root.configure(bg=self.BG_DARK)
        self.root.resizable(False, False)

        # Keep window on top so it's visible while using gestures
        self.root.attributes("-topmost", True)

        self._click_count_l = 0
        self._click_count_r = 0

        self._build_ui()

    def _build_ui(self):
        root = self.root

        # ── Title ─────────────────────────────────────────────────────
        title_font = tkfont.Font(family="Segoe UI", size=16, weight="bold")
        sub_font   = tkfont.Font(family="Segoe UI", size=10)
        btn_font   = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        log_font   = tkfont.Font(family="Consolas", size=10)

        tk.Label(
            root, text="🖱️  Gesture Test Panel",
            font=title_font, fg=self.ACCENT_CYAN, bg=self.BG_DARK,
        ).pack(pady=(20, 4))

        tk.Label(
            root, text="Use hand gestures to click these buttons & scroll below",
            font=sub_font, fg=self.TEXT_GREY, bg=self.BG_DARK,
        ).pack(pady=(0, 20))

        # ── Button frame ──────────────────────────────────────────────
        btn_frame = tk.Frame(root, bg=self.BG_DARK)
        btn_frame.pack(pady=10)

        # Left-click button
        self.btn_left = tk.Button(
            btn_frame,
            text="👆  LEFT CLICK\n(Pinch thumb + index)",
            font=btn_font,
            width=20, height=3,
            bg=self.BG_PANEL, fg=self.ACCENT_CYAN,
            activebackground=self.ACCENT_CYAN, activeforeground=self.BG_DARK,
            relief="flat", bd=0, cursor="hand2",
            command=self._on_left_click,
        )
        self.btn_left.pack(side=tk.LEFT, padx=10)

        # Right-click button
        self.btn_right = tk.Button(
            btn_frame,
            text="👆  RIGHT CLICK\n(Pinch thumb + middle)",
            font=btn_font,
            width=20, height=3,
            bg=self.BG_PANEL, fg=self.ACCENT_BLUE,
            activebackground=self.ACCENT_BLUE, activeforeground=self.BG_DARK,
            relief="flat", bd=0, cursor="hand2",
        )
        self.btn_right.pack(side=tk.LEFT, padx=10)
        # Bind right-click event
        self.btn_right.bind("<Button-3>", self._on_right_click)
        # Also make left-click on right button work for testing
        self.btn_right.configure(command=self._on_right_click_via_left)

        # ── Counter labels ────────────────────────────────────────────
        counter_frame = tk.Frame(root, bg=self.BG_DARK)
        counter_frame.pack(pady=(10, 5))

        self.label_left = tk.Label(
            counter_frame, text="Left clicks: 0",
            font=sub_font, fg=self.ACCENT_CYAN, bg=self.BG_DARK,
        )
        self.label_left.pack(side=tk.LEFT, padx=40)

        self.label_right = tk.Label(
            counter_frame, text="Right clicks: 0",
            font=sub_font, fg=self.ACCENT_BLUE, bg=self.BG_DARK,
        )
        self.label_right.pack(side=tk.LEFT, padx=40)

        # ── Separator ────────────────────────────────────────────────
        tk.Frame(root, bg=self.TEXT_GREY, height=1).pack(fill=tk.X, padx=30, pady=15)

        # ── Scroll test area ──────────────────────────────────────────
        tk.Label(
            root, text="⬇  SCROLL TEST AREA  ⬇",
            font=sub_font, fg=self.ACCENT_PINK, bg=self.BG_DARK,
        ).pack(pady=(0, 5))

        scroll_frame = tk.Frame(root, bg=self.BG_PANEL)
        scroll_frame.pack(padx=30, pady=5, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_area = tk.Text(
            scroll_frame,
            font=log_font,
            bg=self.BG_PANEL, fg=self.TEXT_WHITE,
            insertbackground=self.ACCENT_CYAN,
            selectbackground=self.ACCENT_BLUE,
            relief="flat", bd=10,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.text_area.yview)

        # Fill with scrollable content
        lines = []
        for i in range(1, 51):
            lines.append(f"  Line {i:02d}  │  Scroll here with ✌️ two-finger gesture")
        self.text_area.insert(tk.END, "\n".join(lines))
        self.text_area.config(state=tk.DISABLED)

        # ── Status bar ────────────────────────────────────────────────
        self.status = tk.Label(
            root, text="Waiting for gestures…",
            font=sub_font, fg=self.TEXT_GREY, bg=self.BG_DARK,
            anchor="w",
        )
        self.status.pack(fill=tk.X, padx=20, pady=(5, 10))

    # ── Event handlers ────────────────────────────────────────────────

    def _on_left_click(self):
        self._click_count_l += 1
        self.label_left.config(text=f"Left clicks: {self._click_count_l}")
        self._flash_button(self.btn_left, self.ACCENT_CYAN)
        self.status.config(
            text=f"✅ Left click detected!  ({time.strftime('%H:%M:%S')})",
            fg=self.ACCENT_CYAN,
        )

    def _on_right_click(self, event=None):
        self._click_count_r += 1
        self.label_right.config(text=f"Right clicks: {self._click_count_r}")
        self._flash_button(self.btn_right, self.ACCENT_BLUE)
        self.status.config(
            text=f"✅ Right click detected!  ({time.strftime('%H:%M:%S')})",
            fg=self.ACCENT_BLUE,
        )

    def _on_right_click_via_left(self):
        """Also count left-clicks on the right button (for testing)."""
        self._on_right_click()

    def _flash_button(self, btn: tk.Button, color: str):
        """Brief flash animation on button press."""
        original_bg = self.BG_PANEL
        btn.config(bg=color, fg=self.BG_DARK)
        self.root.after(200, lambda: btn.config(bg=original_bg, fg=color))

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    print("╔══════════════════════════════════════════════════╗")
    print("║   🖱️  AI Virtual Mouse — Click & Scroll Tester   ║")
    print("║                                                  ║")
    print("║  1. Run 'python main.py' in another terminal     ║")
    print("║  2. Use gestures to click the buttons            ║")
    print("║  3. Use two-finger scroll on the text area       ║")
    print("╚══════════════════════════════════════════════════╝")
    app = ClickTestApp()
    app.run()
