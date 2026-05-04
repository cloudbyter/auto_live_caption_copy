"""
Live Caption Copy — Copy text from Windows 11 Live Caption via OCR.

Run this script (with venv activated). Use the tray icon or the default
hotkey Ctrl+Shift+C to capture the configured screen region and copy
the recognized text to the clipboard.

First run: adjust the capture region in ~/.live_caption_copy/config.json
so it matches where Live Caption appears on your screen (left, top, width, height).
"""
import sys
import os

# Ensure project root is on path when running as script
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from tray_app import run_tray

if __name__ == "__main__":
    run_tray()

