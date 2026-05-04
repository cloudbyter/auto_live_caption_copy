"""System tray app: icon, menu (Copy now, Set region, Quit), and hotkey."""
import os
import subprocess
import sys
import threading
import time
from PIL import Image, ImageDraw

import pystray
import keyboard

import config
import capture_ocr
import clipboard_util


def _app_dir():
    """Root directory of the app (sources when dev, exe dir when frozen)."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _make_icon():
    """Create a simple tray icon (document/copy style)."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Rounded rectangle (document shape)
    margin = 6
    d.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=8,
        fill=(70, 130, 180, 255),
        outline=(255, 255, 255, 200),
        width=2,
    )
    # Simple "A" or lines suggesting text
    cx, cy = size // 2, size // 2
    d.line([(cx - 10, cy - 5), (cx - 10, cy + 10)], fill=(255, 255, 255), width=2)
    d.line([(cx - 10, cy - 5), (cx + 10, cy + 10)], fill=(255, 255, 255), width=2)
    d.line([(cx + 6, cy + 2), (cx + 10, cy + 10)], fill=(255, 255, 255), width=2)
    return img


def do_copy_captions(show_notification=None, paste_after=False):
    """
    Capture region, OCR, copy to clipboard.
    show_notification: optional callable(message: str) to show a toast/tray message.
    paste_after: if True, simulate Ctrl+V after copying so text is pasted into focused app.
    """
    cfg = config.load_config()
    region = config.get_region(cfg)
    ocr_lang = config.get_ocr_lang(cfg)
    ok, text = capture_ocr.get_caption_text(region, ocr_lang)
    if not ok:
        if show_notification:
            show_notification(f"OCR error: {text}")
        return
    if not text:
        if show_notification:
            show_notification("No text recognized in capture region.")
        return
    try:
        clipboard_util.copy_to_clipboard(text)
        if show_notification:
            show_notification("Copied and pasted." if paste_after else "Copied to clipboard.")
        if paste_after:
            time.sleep(0.05)  # let clipboard settle
            keyboard.send("ctrl+v")
    except Exception as e:
        if show_notification:
            show_notification(f"Copy failed: {e}")


def _on_copy(icon, item):
    def show(msg):
        icon.notify(msg, "Live Caption Copy")

    do_copy_captions(show_notification=show)


def _on_quit(icon, item):
    icon.stop()


def _on_set_region(icon, item):
    """Launch the region picker in a subprocess (tkinter needs its own process)."""
    root = _app_dir()
    if getattr(sys, "frozen", False):
        pick_cmd = [os.path.join(root, "pick_region.exe")]
        cwd = root
    else:
        pick_cmd = [sys.executable, os.path.join(root, "pick_region.py")]
        cwd = root
    try:
        subprocess.Popen(pick_cmd, cwd=cwd)
        icon.notify("Draw a rectangle over the caption area, then release.", "Set region")
    except Exception as e:
        icon.notify(f"Could not start region picker: {e}", "Set region")


def _on_settings(icon, item):
    """Open the config GUI in a subprocess."""
    root = _app_dir()
    if getattr(sys, "frozen", False):
        gui_cmd = [os.path.join(root, "config_gui.exe")]
        cwd = root
    else:
        gui_cmd = [sys.executable, os.path.join(root, "config_gui.py")]
        cwd = root
    try:
        subprocess.Popen(gui_cmd, cwd=cwd)
    except Exception as e:
        icon.notify(f"Could not open settings: {e}", "Live Caption Copy")


def _register_hotkey(icon):
    cfg = config.load_config()
    hotkey = (cfg.get("hotkey") or config.DEFAULT_HOTKEY).strip().lower()

    def on_hotkey():
        def show(msg):
            icon.notify(msg, "Live Caption Copy")

        def copy_and_paste():
            do_copy_captions(show_notification=show, paste_after=True)

        # Run in a separate thread so we don't block the keyboard hook thread
        # (avoids Windows asyncio Overlapped errors when calling keyboard.send from the hook)
        threading.Thread(target=copy_and_paste, daemon=True).start()

    try:
        keyboard.add_hotkey(hotkey, on_hotkey, suppress=False)
    except Exception:
        pass  # e.g. invalid hotkey


def _startup_notifications(icon):
    """Show 'app is running' notification, then optionally warn if Live Caption window not found."""
    time.sleep(1.0)
    try:
        icon.notify("Live Caption Copy is running.", "Live Caption Copy")
    except Exception:
        pass
    time.sleep(0.5)
    try:
        cfg = config.load_config()
        if not cfg.get("auto_detect_region", config.DEFAULT_AUTO_DETECT_REGION):
            return
        from live_caption_finder import get_live_caption_region

        if get_live_caption_region() is not None:
            return
        icon.notify(
            "Live Caption window not found. Use \"Set region\" to set the capture area manually.",
            "Live Caption Copy",
        )
    except Exception:
        pass


def run_tray():
    """Run the system tray app (blocking)."""
    icon = pystray.Icon("live_caption_copy", _make_icon(), "Live Caption Copy")
    icon.menu = pystray.Menu(
        pystray.MenuItem("Copy captions now", _on_copy, default=True),
        pystray.MenuItem("Set region", _on_set_region),
        pystray.MenuItem("Settings", _on_settings),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", _on_quit),
    )
    _register_hotkey(icon)
    t = threading.Thread(target=_startup_notifications, args=(icon,), daemon=True)
    t.start()
    icon.run()


if __name__ == "__main__":
    run_tray()
