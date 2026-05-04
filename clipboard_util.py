"""Copy text to clipboard."""
import pyperclip


def copy_to_clipboard(text):
    """Copy text to system clipboard. Raises on failure."""
    if text is None:
        text = ""
    pyperclip.copy(str(text).strip())
