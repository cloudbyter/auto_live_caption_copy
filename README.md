# Live Caption Copy

Copy text from **Windows 11 Live Caption** to the clipboard using OCR. Uses the built-in Windows OCR engine (no Tesseract or other engines required). Ideal for saving captions from videos, meetings, or any audio that Live Caption is displaying.

## Features

- **One-key copy** — Global hotkey (default **Ctrl+Shift+C**) captures the caption area, runs OCR, and pastes the result to the clipboard.
- **Auto-detect caption position** — When the Live Caption window is open, the app finds it automatically so you don’t need to set coordinates.
- **Manual region** — If auto-detect isn’t used, you can draw the capture area on screen (“Set region”) or edit pixel values.
- **Settings GUI** — Configure region, OCR language, and hotkey in a window instead of editing JSON.
- **Multi-language OCR** — Supports English, Japanese, Chinese, Korean, and other languages that Windows OCR supports (with the matching language pack installed).

## Requirements

- **Windows 10/11** (uses Windows OCR and Win32 APIs).
- **Python 3.8+** with venv.
- **Windows OCR language pack** for your caption language (e.g. **Settings → Time & language → Language & region → Add a language** and ensure the language has “Text-to-speech” / OCR support, or install **Language.OCR** capability for your language).

## Setup

### 1. Clone or download the project

Use the folder as the project root (where `main.py` and `requirements.txt` are).

### 2. Create and activate a virtual environment

From the project root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

If you already have a venv, just activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

This installs: `mss` (screen capture), `Pillow` (image handling), `winocr` (Windows OCR), `pyperclip` (clipboard), `pystray` (tray icon), and `keyboard` (global hotkey).

### 4. Run the app

```powershell
python main.py
```

A **tray icon** appears in the system tray. The app keeps running in the background until you choose **Quit** from the tray menu.

## How to use

### Copying captions

1. Turn on **Windows Live Caption** (e.g. **Win+Ctrl+L** or via **Settings → Accessibility → Captions**) and position the caption bar where you want it.
2. When captions are visible, press the **hotkey** (default **Ctrl+Shift+C**) or right-click the tray icon and choose **Copy captions now**.
3. The app captures the caption area, runs OCR, and copies the text to the clipboard. Paste (**Ctrl+V**) wherever you need it.

### Tray menu

| Item | Description |
|------|-------------|
| **Copy captions now** | Capture the configured region, run OCR, copy to clipboard. Same as the hotkey. |
| **Set region** | Opens a fullscreen overlay; drag a rectangle over the caption area. The rectangle is saved as the capture region. Press **Esc** to cancel. |
| **Settings** | Opens the settings window to change region, auto-detect, OCR language, and hotkey. |
| **Quit** | Exits the app and removes the tray icon. |

### Startup notification

If **auto-detect** is on and the Live Caption window is **not** found at startup, a tray notification suggests using **Set region** to define the capture area manually.

## Setting the caption region

The app needs to know *which part of the screen* contains the Live Caption text.

### Automatic (default)

With **Auto-detect Live Caption window** enabled (default), the app looks for a visible window whose title contains “Live Caption” and uses its position and size. No setup is needed as long as the Live Caption window is open when you trigger copy.

If the window isn’t found (e.g. it’s closed or the title is different), the app falls back to the **region** you configured.

### Manual: draw on screen

1. Open **Set region** from the tray (or run `python pick_region.py`).
2. A dimmed fullscreen overlay appears. **Drag** a rectangle so it fully covers the Live Caption bar.
3. **Release** the mouse; the region is saved. Press **Esc** to cancel without saving.

### Manual: edit numbers

In **Settings**, use the **Capture region** fields (Left, Top, Width, Height in pixels), or edit the config file (see [Config file](#config-file) below).

## Configuration

### Settings window (recommended)

Right-click the tray icon → **Settings**. You can:

- **Auto-detect Live Caption window** — Check to find the caption window automatically; uncheck to always use the fixed region below.
- **Capture region** — Left, Top, Width, Height (pixels). Use **Set region (draw on screen)** to set them by drawing.
- **OCR language** — Dropdown: Default (English), English, Japanese, Chinese Simplified/Traditional, Korean, French, German, Spanish. Must match a Windows OCR language you have installed.
- **Hotkey** — e.g. `ctrl+shift+c`. **Restart the app** after changing for the new hotkey to take effect.

Click **Save** to write settings to disk, or **Cancel** to close without saving.

### Config file

Settings are stored in:

```text
%USERPROFILE%\.live_caption_copy\config.json
```

Example:

```json
{
  "region": {
    "left": 100,
    "top": 700,
    "width": 1000,
    "height": 180
  },
  "auto_detect_region": true,
  "ocr_lang": "",
  "hotkey": "ctrl+shift+c"
}
```

| Key | Description |
|-----|-------------|
| **region** | `left`, `top`, `width`, `height` in pixels. Used when auto-detect is off or when the Live Caption window isn’t found. |
| **auto_detect_region** | `true` (default) = try to find the Live Caption window when capturing; `false` = always use `region`. |
| **ocr_lang** | BCP-47 language tag: `""` or `"en"` for English, `"ja"` for Japanese, `"zh-Hans"` for Chinese Simplified, etc. Requires the matching Windows OCR language. |
| **hotkey** | Global hotkey string, e.g. `ctrl+shift+c`. Modifiers: `ctrl`, `alt`, `shift`, `win`. |

Editing the file is optional; the **Settings** GUI writes the same file.

## Building a standalone .exe (Windows, no Python required)

You can build a folder with `.exe` files that run on Windows 11 without installing Python.

1. Install dependencies and PyInstaller:
   ```powershell
   pip install -r requirements.txt
   pip install pyinstaller
   ```
2. From the project root, run:
   ```powershell
   .\build_exe.bat
   ```
3. The result is in **`dist\LiveCaptionCopy\`**:
   - **LiveCaptionCopy.exe** — main app (double‑click to run; tray icon appears).
   - **pick_region.exe** and **config_gui.exe** — used by the main app for “Set region” and “Settings”.

Copy the whole **LiveCaptionCopy** folder to another PC if needed. Config is still stored in `%USERPROFILE%\.live_caption_copy\config.json` on each machine.

## Running tools separately

From the project root with the venv activated:

- **Settings window only** (no tray):
  ```powershell
  python config_gui.py
  ```
- **Region picker only** (draw rectangle, save to config, then exit):
  ```powershell
  python pick_region.py
  ```

## Troubleshooting

| Problem | What to try |
|--------|----------------------|
| **“Live Caption window not found”** at startup | Open the Live Caption bar before using the app, or turn off auto-detect and use **Set region** to define the area. |
| **No text copied** | Ensure the capture region fully contains the caption text. Use **Set region** and draw a slightly larger rectangle, or increase `width`/`height` in Settings or config. |
| **OCR error (e.g. “languageTag”)** | The OCR language must be a valid BCP-47 tag and installed in Windows. Use **Settings** and pick a language from the list, or set `ocr_lang` to `""` or `"en"` in config. |
| **Hotkey doesn’t work** | Restart the app after changing the hotkey. Ensure no other app is using the same shortcut. Use lowercase in config, e.g. `ctrl+shift+c`. |
| **Wrong area captured** | If auto-detect picks the wrong window or fails, set **auto_detect_region** to `false` and use **Set region** to choose the exact area. |

## Project structure (main files)

| File | Purpose |
|------|---------|
| `main.py` | Entry point; starts the tray app. |
| `tray_app.py` | Tray icon, menu (Copy, Set region, Settings, Quit), hotkey, and copy logic. |
| `config.py` | Load/save `config.json`, default values, and region resolution (auto-detect vs manual). |
| `config_gui.py` | Settings window (region, auto-detect, OCR language, hotkey). |
| `capture_ocr.py` | Screen capture (mss) and Windows OCR (winocr) for the selected region. |
| `pick_region.py` | Fullscreen overlay to draw and save the capture region. |
| `live_caption_finder.py` | Finds the Live Caption window by title (Win32) and returns its rectangle. |
| `clipboard_util.py` | Copy text to the clipboard (pyperclip). |
| `LiveCaptionCopy.spec`, `pick_region.spec`, `config_gui.spec` | PyInstaller specs for building the standalone .exe. |
| `build_exe.bat` | Build script: creates `dist\LiveCaptionCopy\` with the exes. |

## License

Use and modify as you like. No warranty.
