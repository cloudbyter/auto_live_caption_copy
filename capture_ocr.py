"""Capture a screen region and run Windows OCR to get text."""
import mss
from PIL import Image

try:
    from winocr import recognize_pil_sync
except ImportError:
    recognize_pil_sync = None


def capture_region(region):
    """
    Capture a screen region.
    region: dict with left, top, width, height (in pixels).
    Returns PIL.Image (RGB).
    """
    with mss.mss() as sct:
        # Use monitor 0 (primary) and clip region to that monitor
        mon = sct.monitors[0]
        x = region.get("left", 0)
        y = region.get("top", 0)
        w = region.get("width", 400)
        h = region.get("height", 150)
        # Clamp to monitor bounds
        x = max(mon["left"], min(mon["left"] + mon["width"] - w, x))
        y = max(mon["top"], min(mon["top"] + mon["height"] - h, y))
        bbox = {"left": x, "top": y, "width": w, "height": h}
        shot = sct.grab(bbox)
        # mss returns BGRA; convert to RGB for PIL
        img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
        return img


# WinRT Language() requires a valid BCP-47 tag; empty string causes [WinError -2147024809] languageTag
DEFAULT_OCR_LANG = "en"


def ocr_image(img, lang=""):
    """
    Run Windows OCR on a PIL Image.
    lang: language code (e.g. '' or 'en' for English, 'ja' for Japanese).
          Must be non-empty; Windows OCR rejects empty languageTag.
    Returns recognized text string.
    """
    if recognize_pil_sync is None:
        raise RuntimeError("winocr is not installed. Run: pip install winocr")
    if not (lang and lang.strip()):
        lang = DEFAULT_OCR_LANG
    result = recognize_pil_sync(img, lang)
    if hasattr(result, "text"):
        return result.text or ""
    if isinstance(result, dict):
        return result.get("text", "") or ""
    return str(result).strip()


def get_caption_text(region, ocr_lang="en"):
    """
    Capture the given screen region and return OCR text.
    region: dict with left, top, width, height.
    ocr_lang: optional OCR language code.
    Returns (success: bool, text: str). success is False if OCR failed or no text.
    """
    try:
        img = capture_region(region)
        text = ocr_image(img, ocr_lang)
        text = (text or "").strip()
        return True, text
    except Exception as e:
        return False, str(e)
