import time
import logging
import sys
import os
import threading
from datetime import datetime

# Add the backend directory to sys.path to allow imports from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import init_db, SessionLocal
from src.models.snapshot import Snapshot
from src.core.capture import capture_screen
from src.core.ocr import extract_text
from src.core.config import load_settings, APP_DATA_DIR
from src.core.categorization import categorize_activity

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

class ScreenRewindDaemon(threading.Thread):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.interval = self.settings.get("capture_interval", 10)
        self.running = False
        self.paused = False
        self._stop_event = threading.Event()
        # self.categories = load_categories() # Deprecated in FR3

    def update_interval(self, new_interval):
        self.interval = new_interval
        logging.info(f"Capture interval updated to {self.interval} seconds")

    def run(self):
        logging.info(f"Starting ScreenRewind Daemon (Interval: {self.interval}s)...")
        init_db()
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

            # Reload settings periodically or just use current interval
            # For now, interval is updated via update_interval method
            
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
        
        # 3. Categorize (Rules + AI)
        logging.info("Categorizing activity...")
        cat_result = categorize_activity(filepath, text, window_title, app_name)
        
        project = cat_result.get("project", "Uncategorized")
        task = cat_result.get("task", "General")
        explanation = cat_result.get("explanation", "")
        
        logging.info(f"Categorized as: Project='{project}', Task='{task}' with explanation: {explanation}")

        # 4. Save
        session = SessionLocal()
        try:
            snapshot = Snapshot(
                file_path=filepath,
                ocr_text=text,
                timestamp=datetime.now(),
                window_title=window_title,
                app_name=app_name,
                project_name=project,
                task_name=task,
                explanation=explanation,
                category=project # Backward compatibility
            )
            session.add(snapshot)
            session.commit()
            logging.info(f"Snapshot saved (ID: {snapshot.id})")
        except Exception as e:
            logging.error(f"Database error: {e}")
            session.rollback()
        finally:
            session.close()

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
