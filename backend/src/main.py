import time
import logging
import sys
import os
from datetime import datetime

# Add the backend directory to sys.path to allow imports from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.database import init_db, SessionLocal
from src.models.snapshot import Snapshot
from src.core.capture import capture_screen
from src.core.ocr import extract_text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

CAPTURE_INTERVAL = 10  # seconds

def main():
    logging.info("Starting GhostTrace Daemon...")
    
    # Initialize Database
    init_db()
    logging.info("Database initialized.")

    try:
        while True:
            start_time = time.time()
            
            try:
                # 1. Capture Screen
                logging.info("Capturing screen...")
                filepath = capture_screen()
                logging.info(f"Screen captured: {filepath}")

                # 2. Perform OCR
                logging.info("Performing OCR...")
                text = extract_text(filepath)
                logging.info(f"OCR complete. Extracted {len(text)} characters.")
                logging.info(f"OCR Text: {text}")

                # 3. Save to Database
                session = SessionLocal()
                try:
                    snapshot = Snapshot(
                        file_path=filepath,
                        ocr_text=text,
                        timestamp=datetime.now()
                        # window_title and app_name to be implemented later
                    )
                    session.add(snapshot)
                    session.commit()
                    logging.info(f"Snapshot saved to database with ID: {snapshot.id}")
                except Exception as e:
                    logging.error(f"Database error: {e}")
                    session.rollback()
                finally:
                    session.close()

            except Exception as e:
                logging.error(f"Error in main loop: {e}")

            # Sleep for the remainder of the interval
            elapsed_time = time.time() - start_time
            sleep_time = max(0, CAPTURE_INTERVAL - elapsed_time)
            logging.info(f"Sleeping for {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        logging.info("GhostTrace Daemon stopped by user.")

if __name__ == "__main__":
    main()
