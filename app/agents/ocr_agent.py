"""OCR Agent
Lightweight wrapper around pytesseract + PIL to provide OCR functionality.
If pytesseract or PIL are not available, the agent returns an empty string and
logs a helpful message.
"""
from pathlib import Path
import logging

try:
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False


class OCRAgent:
    """Runs OCR on image files. Returns extracted text or empty string on failure."""

    def __init__(self):
        self.available = OCR_AVAILABLE
        if not self.available:
            logging.getLogger(__name__).warning("OCRAgent initialized but pytesseract/Pillow not available")

    def run(self, image_path: str) -> str:
        p = Path(image_path)
        if not p.exists():
            return ""
        if not self.available:
            return ""
        try:
            img = Image.open(p)
            text = pytesseract.image_to_string(img)
            return text or ""
        except Exception as e:
            logging.getLogger(__name__).exception("OCR failed: %s", e)
            return ""
