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

load_dotenv()

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
        
        # 3. Upload or Queue
        logging.info("Attempting upload...")
        success = self._upload_snapshot(filepath, text, window_title, app_name, timestamp)
        
        if not success:
            logging.warning("Upload failed/Offline. Queuing...")
            self.queue.add(timestamp, text, window_title, app_name, filepath)
        else:
            logging.info("Upload successful.")
            self._process_queue()

    def _upload_snapshot(self, filepath, ocr_text, window_title, app_name, timestamp):
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
                    "app_name": app_name
                }
                headers = {
                    "X-API-Key": os.getenv("SCREENREWIND_API_KEY", "")
                }
                logging.info(f"Uploading to {API_URL}")
                response = requests.post(API_URL, files=files, data=data, headers=headers, timeout=30)
                if response.status_code == 200:
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
                item['timestamp']
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
