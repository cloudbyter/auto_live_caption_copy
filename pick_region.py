"""
Interactive region picker: draw a rectangle on screen to set the caption capture area.

Run directly: python pick_region.py
Or use tray menu "Set region". The selected rectangle is saved to config;
no need to look up x, y pixel values manually.
"""
import sys
import os

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import tkinter as tk

import config


def run_picker():
    """Show fullscreen overlay; user drags to select region; save to config and exit."""
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0.25)
    root.overrideredirect(True)
    root.config(cursor="cross")

    canvas = tk.Canvas(
        root,
        highlightthickness=0,
        bg="gray20",
    )
    canvas.pack(fill=tk.BOTH, expand=True)

    start = {"x": None, "y": None}
    rect_id = None

    def on_press(e):
        start["x"], start["y"] = e.x, e.y
        nonlocal rect_id
        if rect_id is not None:
            canvas.delete(rect_id)
        rect_id = canvas.create_rectangle(e.x, e.y, e.x, e.y, outline="lime", width=3)

    def on_drag(e):
        if rect_id is not None and start["x"] is not None:
            canvas.coords(rect_id, start["x"], start["y"], e.x, e.y)

    def on_release(e):
        if start["x"] is None:
            return
        x1, y1 = start["x"], start["y"]
        x2, y2 = e.x, e.y
        left = min(x1, x2)
        top = min(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        # Ignore tiny accidental clicks
        if width < 20 or height < 20:
            root.destroy()
            return
        region = {"left": left, "top": top, "width": width, "height": height}
        cfg = config.load_config()
        cfg["region"] = region
        config.save_config(cfg)
        root.destroy()

    def on_escape(e):
        root.destroy()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    root.bind("<Escape>", on_escape)

    # Hint
    canvas.create_text(
        root.winfo_screenwidth() // 2,
        40,
        text="Drag to select the caption area, then release. Press Esc to cancel.",
        fill="white",
        font=("Segoe UI", 14),
    )

    root.mainloop()


if __name__ == "__main__":
    run_picker()
