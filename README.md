# ScreenRewind

ScreenRewind is a locally hosted, cross-platform desktop application that automatically tracks user activity by capturing screen snapshots, performing Optical Character Recognition (OCR), and utilizing local AI to categorize work context.

## Project Structure

- `backend/`: Python backend (FastAPI, SQLite, OCR, Capture)
- `frontend/`: React + Vite + TailwindCSS (Tauri wrapper) - *Coming in Phase 3*

## Phase 1: Core Logic

The current implementation focuses on the core daemon:
1.  Capturing screenshots using `mss`.
2.  Processing images with `RapidOCR`.
3.  Storing metadata and text in `SQLite`.

## Setup

1.  Navigate to `backend/`.
2.  Create a virtual environment: `python3 -m venv venv`
3.  Activate it: `source venv/bin/activate`
4.  Install dependencies: `pip install -r requirements.txt`
5.  Run the daemon: `python src/main.py`
