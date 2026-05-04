"""
Settings GUI for Live Caption Copy.
Edit region, auto-detect, OCR language, and hotkey without editing JSON.
Run directly: python config_gui.py
Or use tray menu "Settings".
"""
import sys
import os
import subprocess

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import tkinter as tk
from tkinter import ttk, messagebox

import config

# Main keys for hotkey combobox (keyboard.add_hotkey format: lowercase)
HOTKEY_MAIN_KEYS = (
    [chr(ord("a") + i) for i in range(26)]  # a-z
    + [str(i) for i in range(10)]  # 0-9
    + [f"f{i}" for i in range(1, 13)]  # f1-f12
    + [
        "space", "enter", "tab", "escape", "backspace", "insert", "delete",
        "home", "end", "page up", "page down", "left", "right", "up", "down",
    ]
)

# Common OCR language tags for the dropdown (label, value)
OCR_LANG_OPTIONS = [
    ("Default (English)", ""),
    ("English", "en"),
    ("Japanese", "ja"),
    ("Chinese Simplified", "zh-Hans"),
    ("Chinese Traditional", "zh-Hant"),
    ("Korean", "ko"),
    ("French", "fr"),
    ("German", "de"),
    ("Spanish", "es"),
]


def _parse_hotkey(s):
    """Parse hotkey string like 'ctrl+shift+c' into (ctrl, shift, win, main_key)."""
    s = (s or "").strip().lower()
    if not s:
        return False, False, False, "c"
    parts = [p.strip() for p in s.split("+") if p.strip()]
    ctrl = "ctrl" in parts
    shift = "shift" in parts
    win = "win" in parts
    modifiers = {"ctrl", "shift", "shift left", "shift right", "alt", "win", "windows"}
    main = "c"
    for p in parts:
        if p not in modifiers and p not in ("left", "right"):
            main = p.replace(" ", "+")  # e.g. "page up" -> "page+up" for keyboard lib
            break
    # Normalize main key for our combobox (keyboard uses "page up" with space)
    if main == "page+up":
        main = "page up"
    elif main == "page+down":
        main = "page down"
    return ctrl, shift, win, main


def _build_hotkey(ctrl, shift, win, main_key):
    """Build hotkey string from modifier checkboxes and main key."""
    parts = []
    if ctrl:
        parts.append("ctrl")
    if shift:
        parts.append("shift")
    if win:
        parts.append("win")
    parts.append(main_key)
    return "+".join(parts)


def _run_region_picker_and_reload(region_vars, update_region_from_config):
    """Launch region picker in subprocess; when it exits, reload config and update region vars."""
    try:
        pick_script = os.path.join(_ROOT, "pick_region.py")
        subprocess.run([sys.executable, pick_script], cwd=_ROOT, check=False)
    except Exception:
        pass
    update_region_from_config()


def run_config_gui():
    """Show the settings window (blocking until closed)."""
    cfg = config.load_config()
    region = cfg.get("region", config.get_default_config()["region"])

    root = tk.Tk()
    root.title("Live Caption Copy — Settings")
    root.resizable(True, False)
    root.minsize(360, 1)

    main = ttk.Frame(root, padding=12)
    main.pack(fill=tk.BOTH, expand=True)

    # --- Auto-detect ---
    auto_detect_var = tk.BooleanVar(value=cfg.get("auto_detect_region", config.DEFAULT_AUTO_DETECT_REGION))
    ttk.Checkbutton(
        main,
        text="Auto-detect Live Caption window (find position when capturing)",
        variable=auto_detect_var,
    ).pack(anchor=tk.W, pady=(0, 8))

    # --- Region ---
    region_frame = ttk.LabelFrame(main, text="Capture region (when auto-detect is off or fails)", padding=8)
    region_frame.pack(fill=tk.X, pady=(0, 8))

    region_vars = {
        "left": tk.StringVar(value=str(region.get("left", 0))),
        "top": tk.StringVar(value=str(region.get("top", 0))),
        "width": tk.StringVar(value=str(region.get("width", 400))),
        "height": tk.StringVar(value=str(region.get("height", 150))),
    }

    def update_region_from_config():
        c = config.load_config()
        r = c.get("region", {})
        for k, v in region_vars.items():
            v.set(str(r.get(k, 0)))

    row1 = ttk.Frame(region_frame)
    row1.pack(fill=tk.X)
    ttk.Label(row1, text="Left:").pack(side=tk.LEFT)
    ttk.Spinbox(row1, textvariable=region_vars["left"], width=8, from_=0, to=99999).pack(side=tk.LEFT, padx=(4, 12))
    ttk.Label(row1, text="Top:").pack(side=tk.LEFT)
    ttk.Spinbox(row1, textvariable=region_vars["top"], width=8, from_=0, to=99999).pack(side=tk.LEFT, padx=(4, 12))
    ttk.Label(row1, text="Width:").pack(side=tk.LEFT)
    ttk.Spinbox(row1, textvariable=region_vars["width"], width=8, from_=1, to=99999).pack(side=tk.LEFT, padx=(4, 12))
    ttk.Label(row1, text="Height:").pack(side=tk.LEFT)
    ttk.Spinbox(row1, textvariable=region_vars["height"], width=8, from_=1, to=99999).pack(side=tk.LEFT, padx=(4, 0))

    ttk.Button(
        region_frame,
        text="Set region (draw on screen)",
        command=lambda: _run_region_picker_and_reload(region_vars, update_region_from_config),
    ).pack(pady=(8, 0))

    # --- OCR language ---
    lang_frame = ttk.Frame(main)
    lang_frame.pack(fill=tk.X, pady=(0, 8))
    ttk.Label(lang_frame, text="OCR language:").pack(anchor=tk.W)
    current_lang = (cfg.get("ocr_lang") or "").strip()
    lang_labels = [opt[0] for opt in OCR_LANG_OPTIONS]
    lang_combo = ttk.Combobox(
        lang_frame,
        values=lang_labels,
        width=28,
        state="readonly",
    )
    lang_combo.pack(anchor=tk.W, pady=(2, 0))
    for label, val in OCR_LANG_OPTIONS:
        if (val or "") == current_lang:
            lang_combo.set(label)
            break
    else:
        lang_combo.set(OCR_LANG_OPTIONS[0][0])  # Default (English)

    # --- Hotkey ---
    hotkey_frame = ttk.LabelFrame(main, text="Hotkey", padding=8)
    hotkey_frame.pack(fill=tk.X, pady=(0, 12))
    current_hotkey = (cfg.get("hotkey") or config.DEFAULT_HOTKEY).strip().lower()
    h_ctrl, h_shift, h_win, h_main = _parse_hotkey(current_hotkey)
    hotkey_ctrl_var = tk.BooleanVar(value=h_ctrl)
    hotkey_shift_var = tk.BooleanVar(value=h_shift)
    hotkey_win_var = tk.BooleanVar(value=h_win)
    hotkey_row = ttk.Frame(hotkey_frame)
    hotkey_row.pack(fill=tk.X)
    ttk.Checkbutton(hotkey_row, text="Ctrl", variable=hotkey_ctrl_var).pack(side=tk.LEFT, padx=(0, 12))
    ttk.Checkbutton(hotkey_row, text="Shift", variable=hotkey_shift_var).pack(side=tk.LEFT, padx=(0, 12))
    ttk.Checkbutton(hotkey_row, text="Win", variable=hotkey_win_var).pack(side=tk.LEFT, padx=(0, 12))
    ttk.Label(hotkey_row, text="Key:").pack(side=tk.LEFT, padx=(8, 4))
    hotkey_main_var = tk.StringVar(value=h_main if h_main in HOTKEY_MAIN_KEYS else "c")
    hotkey_combo = ttk.Combobox(
        hotkey_row,
        textvariable=hotkey_main_var,
        values=HOTKEY_MAIN_KEYS,
        width=10,
        state="readonly",
    )
    hotkey_combo.pack(side=tk.LEFT)
    if h_main not in HOTKEY_MAIN_KEYS:
        hotkey_main_var.set("c")
        hotkey_combo.set("c")
    else:
        hotkey_combo.set(h_main)

    # --- Buttons ---
    btn_frame = ttk.Frame(main)
    btn_frame.pack(fill=tk.X, pady=(8, 0))

    def save_and_close():
        hotkey = _build_hotkey(
            hotkey_ctrl_var.get(),
            hotkey_shift_var.get(),
            hotkey_win_var.get(),
            (hotkey_main_var.get() or "c").strip().lower(),
        )
        if not hotkey or hotkey == "+":
            hotkey = config.DEFAULT_HOTKEY
        lang_label = lang_combo.get().strip()
        ocr_lang = ""
        for label, val in OCR_LANG_OPTIONS:
            if label == lang_label:
                ocr_lang = val or ""
                break

        try:
            left = int(region_vars["left"].get() or 0)
            top = int(region_vars["top"].get() or 0)
            width = max(1, int(region_vars["width"].get() or 400))
            height = max(1, int(region_vars["height"].get() or 150))
        except ValueError:
            messagebox.showerror("Invalid region", "Region values must be numbers.")
            return

        new_cfg = {
            "region": {"left": left, "top": top, "width": width, "height": height},
            "auto_detect_region": auto_detect_var.get(),
            "ocr_lang": ocr_lang,
            "hotkey": hotkey,
        }
        config.save_config(new_cfg)
        messagebox.showinfo("Settings", "Settings saved. Restart the app for the new hotkey to take effect.")
        root.destroy()

    def on_cancel():
        root.destroy()

    ttk.Button(btn_frame, text="Save", command=save_and_close).pack(side=tk.LEFT, padx=(0, 8))
    ttk.Button(btn_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT)

    root.mainloop()


if __name__ == "__main__":
    run_config_gui()
