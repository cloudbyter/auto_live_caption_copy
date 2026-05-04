"""Configuration for Live Caption capture region and app settings."""
import json
import os

# Default: bottom-center area where Windows 11 Live Caption usually appears
# (relative to primary monitor; updated with real size at runtime if needed)
DEFAULT_REGION = {
    "left": 100,
    "top": 700,
    "width": 1000,
    "height": 180,
}

# When True, try to find the Live Caption window automatically each time we capture
DEFAULT_AUTO_DETECT_REGION = True

# OCR language: '' for default (en-US), or e.g. 'ja' for Japanese
DEFAULT_OCR_LANG = ""

# Global hotkey to copy captions (modifiers + key)
DEFAULT_HOTKEY = "ctrl+shift+c"

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".live_caption_copy")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")


def _ensure_config_dir():
    os.makedirs(CONFIG_DIR, exist_ok=True)


def load_config():
    """Load config from disk. Returns dict with region, ocr_lang, hotkey."""
    if not os.path.isfile(CONFIG_PATH):
        cfg = get_default_config()
        save_config(cfg)  # create config file so user can edit region
        return cfg
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Merge with defaults so new keys are present
        default = get_default_config()
        for k, v in default.items():
            if k not in data:
                data[k] = v
        return data
    except (json.JSONDecodeError, IOError):
        return get_default_config()


def get_default_config():
    """Return default config dict."""
    return {
        "region": dict(DEFAULT_REGION),
        "auto_detect_region": DEFAULT_AUTO_DETECT_REGION,
        "ocr_lang": DEFAULT_OCR_LANG,
        "hotkey": DEFAULT_HOTKEY,
    }


def save_config(config):
    """Save config to disk."""
    _ensure_config_dir()
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def get_region(config=None):
    """
    Return capture region dict (left, top, width, height).

    If auto_detect_region is True (default), tries to find the Live Caption
    window on screen and use its position; falls back to configured region
    if not found or auto-detect is disabled.
    """
    if config is None:
        config = load_config()
    if config.get("auto_detect_region", DEFAULT_AUTO_DETECT_REGION):
        try:
            from live_caption_finder import get_live_caption_region

            detected = get_live_caption_region()
            if detected:
                return detected
        except Exception:
            pass
    return config.get("region", dict(DEFAULT_REGION))


def get_ocr_lang(config=None):
    """Return OCR language code (e.g. '' or 'ja')."""
    if config is None:
        config = load_config()
    return config.get("ocr_lang", DEFAULT_OCR_LANG) or ""
