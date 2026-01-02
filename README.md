# ScreenRewind

ScreenRewind is a locally hosted, cross-platform desktop application that automatically tracks user activity by capturing screen snapshots, performing Optical Character Recognition (OCR), and utilizing local AI to categorize work context.

## Project Structure

- `backend/`: Python backend (FastAPI, SQLite, OCR, Capture)
- `frontend/`: React + Vite + TailwindCSS (Tauri wrapper) - *Coming in Phase 3*

## Phase 1: Core Logic (Completed)

The current implementation focuses on the core daemon:
1.  **Smart Capture**: Captures the screen containing the currently active window using `mss` and macOS native APIs (`Quartz`, `Cocoa`).
2.  **OCR Processing**: Extracts text from images using `RapidOCR`.
3.  **Data Storage**: Stores metadata (timestamp, file path, OCR text, app name) in `SQLite`.

## Setup

1.  Navigate to `backend/`:
    ```bash
    cd backend
    ```
2.  Create a virtual environment:
    ```bash
    python3 -m venv venv
    ```
3.  Activate it:
    ```bash
    source venv/bin/activate
    ```
4.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5.  Run the daemon:
    ```bash
    python src/main.py
    ```

## Notes
- The daemon runs every 60 seconds.
- Screenshots are saved in `backend/data/screenshots/`.
- Database is located at `backend/data/screenrewind.db`.
- **macOS Support**: The app currently supports macOS for active window detection.
