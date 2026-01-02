import mss
import mss.tools
from datetime import datetime
import os
from PIL import Image

SCREENSHOTS_DIR = "data/screenshots"
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def capture_screen() -> str:
    """
    Captures the primary screen, saves it as WebP, and returns the file path.
    """
    with mss.mss() as sct:
        # Capture the first monitor (primary)
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)

        # Generate filename based on timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.webp"
        filepath = os.path.join(SCREENSHOTS_DIR, filename)

        # Convert to PIL Image and save as WebP
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        img.save(filepath, "WEBP", quality=75)

        return filepath
