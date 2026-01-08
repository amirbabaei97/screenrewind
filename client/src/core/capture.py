import mss
import mss.tools
from datetime import datetime
import os
from PIL import Image
import logging
from src.core.utils import get_active_window_info
from src.core.config import APP_DATA_DIR

SCREENSHOTS_DIR = os.path.join(APP_DATA_DIR, "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

def get_monitor_intersection(monitor, window):
    """
    Calculates the intersection area between a monitor and a window.
    """
    m_x1 = monitor['left']
    m_y1 = monitor['top']
    m_x2 = m_x1 + monitor['width']
    m_y2 = m_y1 + monitor['height']

    w_x1 = window['x']
    w_y1 = window['y']
    w_x2 = w_x1 + window['width']
    w_y2 = w_y1 + window['height']

    x_overlap = max(0, min(m_x2, w_x2) - max(m_x1, w_x1))
    y_overlap = max(0, min(m_y2, w_y2) - max(m_y1, w_y1))

    return x_overlap * y_overlap

def capture_screen() -> tuple[str, dict]:
    """
    Captures the screen containing the active window, saves it as WebP, and returns the file path and window info.
    """
    # Get active window info BEFORE initializing mss
    # This avoids any potential conflict or delay
    active_window = get_active_window_info()

    with mss.mss() as sct:
        selected_monitor = sct.monitors[1] # Default to primary
        
        if active_window:
            logging.info(f"Active window found: {active_window.get('app_name', 'Unknown')} - {active_window}")
            max_area = 0
            best_monitor_idx = 1
            
            # Iterate over all monitors (skipping index 0 which is all monitors combined)
            for i, monitor in enumerate(sct.monitors[1:], start=1):
                area = get_monitor_intersection(monitor, active_window)
                logging.info(f"Monitor {i} intersection area: {area}")
                
                if area > max_area:
                    max_area = area
                    selected_monitor = monitor
                    best_monitor_idx = i
            
            logging.info(f"Selected Monitor {best_monitor_idx} with intersection area {max_area}")
        else:
            logging.info("No active window detected, using primary monitor.")

        sct_img = sct.grab(selected_monitor)

        # Generate filename based on timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.webp"
        filepath = os.path.join(SCREENSHOTS_DIR, filename)

        # Convert to PIL Image and save as WebP
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        img.save(filepath, "WEBP", quality=75)

        return filepath, active_window
