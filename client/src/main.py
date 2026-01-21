import time
import logging
import sys
import os
import threading
import requests
from datetime import datetime

# Add the backend directory to sys.path to allow imports from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.capture import capture_screen
from src.core.ocr import extract_text
from src.core.config import load_settings, APP_DATA_DIR
from src.core.queue import UploadQueue
from dotenv import load_dotenv

# Configure logging
log_file = os.path.join(APP_DATA_DIR, "screenrewind.log")
handlers = [logging.FileHandler(log_file)]
if sys.stdout:
    handlers.append(logging.StreamHandler(sys.stdout))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=handlers
)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    return os.path.join(base_path, relative_path)

# Load environment variables
# Check if .env is in the bundle resource path (bundled) or current directory (dev)
env_path = resource_path(".env")
if os.path.exists(env_path):
    logging.info(f"Loading .env from {env_path}")
    load_dotenv(env_path)
else:
    # Fallback to default behavior (cwd or parents)
    logging.info("Loading .env from default locations")
    load_dotenv()

API_URL = "https://api.screenrewind.amir.rocks/snapshots/"
QUEUE_DB_PATH = os.path.join(APP_DATA_DIR, "upload_queue.db")

class ScreenRewindDaemon(threading.Thread):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.interval = self.settings.get("capture_interval", 10)
        self.running = False
        self.paused = False
        self._stop_event = threading.Event()
        self.queue = UploadQueue(QUEUE_DB_PATH)
        self.last_capture_time = None

    def update_interval(self, new_interval):
        self.interval = new_interval
        logging.info(f"Capture interval updated to {self.interval} seconds")

    def run(self):
        logging.info(f"Starting ScreenRewind Daemon (Interval: {self.interval}s)...")
        # No local DB init anymore
        self.running = True
        
        while not self._stop_event.is_set():
            if self.paused:
                time.sleep(1)
                continue

            start_time = time.time()
            try:
                self._capture_cycle()
            except Exception as e:
                logging.error(f"Error in capture cycle: {e}")

            elapsed = time.time() - start_time
            sleep_time = max(0, self.interval - elapsed)
            time.sleep(sleep_time)
        
        logging.info("ScreenRewind Daemon stopped.")

    def _capture_cycle(self):
        # 1. Capture
        logging.info("Capturing screen...")
        filepath, window_info = capture_screen()
        
        window_title = ""
        app_name = ""
        if window_info:
            window_title = window_info.get("title", "")
            app_name = window_info.get("app_name", "")
        
        # 2. OCR
        logging.info("Performing OCR...")
        text = extract_text(filepath)
        
        timestamp = datetime.now()
        current_time = time.time()
        
        # Calculate duration
        if self.last_capture_time is None:
            # First run, assume configured interval
            duration = self.interval
        else:
            duration = current_time - self.last_capture_time
            # Cap huge durations (e.g. system sleep) to avoid skewing analytics
            # If duration is more than 10x the interval or > 10 minutes, treat as a break
            if duration > max(self.interval * 10, 600):
                 logging.warning(f"Excessive duration detected ({duration}s). Assuming system sleep/break. Resetting to default.")
                 duration = self.interval
            
        self.last_capture_time = current_time
        
        # 3. Upload or Queue
        logging.info("Attempting upload...")
        success = self._upload_snapshot(filepath, text, window_title, app_name, timestamp, int(duration))
        
        if not success:
            logging.warning("Upload failed/Offline. Queuing...")
            # Note: Queue schema update required to full support duration persistence offline.
            # passing defaults for now compatible with old schema if strict, or we can assume queue handles flexible args?
            # Looking at main.py, queue.add(timestamp, text, window_title, app_name, filepath)
            # We haven't updated queue.py. 
            self.queue.add(timestamp, text, window_title, app_name, filepath)
        else:
            logging.info("Upload successful.")
            self._process_queue()

    def _upload_snapshot(self, filepath, ocr_text, window_title, app_name, timestamp, duration):
        try:
            if not os.path.exists(filepath):
                logging.error(f"File not found: {filepath}")
                return False

            with open(filepath, 'rb') as f:
                files = {'file': f}
                data = {
                    "timestamp": timestamp.isoformat() if isinstance(timestamp, datetime) else timestamp,
                    "ocr_text": ocr_text,
                    "window_title": window_title,
                    "app_name": app_name,
                    "duration": duration
                }
                headers = {
                    "X-API-Key": os.getenv("SCREENREWIND_API_KEY", "")
                }
                logging.info(f"Uploading to {API_URL}")
                response = requests.post(API_URL, files=files, data=data, headers=headers, timeout=30)
                if response.status_code == 200:
                    try:
                        os.remove(filepath)
                        logging.info(f"Deleted local file: {filepath}")
                    except OSError as e:
                        logging.error(f"Error deleting file {filepath}: {e}")
                    return True
                else:
                    logging.error(f"API Error: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            logging.error(f"Connection Error: {e}")
            return False

    def _process_queue(self):
        items = self.queue.pop(limit=5)
        if not items:
            return

        logging.info(f"Processing {len(items)} queued items...")
        processed_ids = []
        for item in items:
            # item is a dict from sqlite Row
            success = self._upload_snapshot(
                item['image_path'], 
                item['ocr_text'], 
                item['window_title'], 
                item['app_name'], 
                item['timestamp'],
                10 # Default for queued items until schema update
            )
            if success:
                processed_ids.append(item['id'])
            else:
                # If one fails, stop processing queue to preserve order/bandwidth
                break
        
        if processed_ids:
            self.queue.remove(processed_ids)
            logging.info(f"Synced {len(processed_ids)} items from queue.")

    def stop(self):

        self._stop_event.set()
        self.running = False

    def pause(self):
        self.paused = True
        self.last_capture_time = None # Reset timer to prevent huge duration on resume
        logging.info("Daemon paused.")

    def resume(self):
        self.paused = False
        logging.info("Daemon resumed.")

def main():
    daemon = ScreenRewindDaemon()
    daemon.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        daemon.stop()
        daemon.join()

if __name__ == "__main__":
    main()
