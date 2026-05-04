"""
Auto-detect Windows 11 Live Caption window position using Win32 API.

Finds the visible top-level window whose title contains "Live Caption"
and returns its screen rectangle so we don't need to configure region manually.
"""
import ctypes
from ctypes import wintypes

if not hasattr(ctypes, "windll") or not hasattr(ctypes.windll, "user32"):
    user32 = None
else:
    user32 = ctypes.windll.user32

# Window title substring to match (case-insensitive). Windows 11 uses "Live Caption".
LIVE_CAPTION_TITLE_SUBSTR = "Live Caption"


def _find_live_caption_hwnd():
    """Return HWND of the first visible top-level window with 'Live Caption' in title, or None."""
    if user32 is None:
        return None

    result = [None]  # mutable so callback can set it

    RECT = wintypes.RECT
    HWND = wintypes.HWND
    LPARAM = wintypes.LPARAM

    def enum_cb(hwnd, lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd) + 1
        if length <= 1:
            return True
        buf = ctypes.create_unicode_buffer(length)
        user32.GetWindowTextW(hwnd, buf, length)
        title = buf.value or ""
        if LIVE_CAPTION_TITLE_SUBSTR.lower() in title.lower():
            result[0] = hwnd
            return False  # stop enumeration
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, HWND, LPARAM)
    cb = WNDENUMPROC(enum_cb)
    user32.EnumWindows(cb, 0)
    return result[0]


def get_live_caption_region():
    """
    Try to find the Live Caption window and return its screen region.

    Returns:
        dict with keys left, top, width, height (pixels), or None if not found
        or not on Windows.
    """
    if user32 is None:
        return None

    hwnd = _find_live_caption_hwnd()
    if not hwnd:
        return None

    rect = wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        return None

    left = rect.left
    top = rect.top
    width = rect.right - rect.left
    height = rect.bottom - rect.top

    if width <= 0 or height <= 0:
        return None

    return {"left": left, "top": top, "width": width, "height": height}
