# ScreenRewind

ScreenRewind is a locally hosted, cross-platform desktop application that automatically tracks user activity by capturing screen snapshots, performing Optical Character Recognition (OCR), and utilizing local AI to categorize work context.

## Project Structure

- `backend/`: Python backend (FastAPI, SQLite, OCR, Capture)
- `frontend/`: React + Vite + TailwindCSS (Tauri wrapper) - *Coming in Phase 3*

## Features

### Phase 1: Core Logic (Completed)
- Captures screenshots every 10 seconds using `mss`.
- Intelligent active monitor detection (macOS supported).
- Extracts text using `RapidOCR`.
- Stores metadata and text in `SQLite`.

### Phase 2: API Layer (Completed)
- FastAPI backend for querying data.
- Endpoints to retrieve snapshots and search OCR text.

## Installation (macOS App)

**Compatibility:** This build is optimized for **Apple Silicon (M1/M2/M3/M4)** Macs running macOS.

1.  **Download** the latest release from the GitHub Releases page.
2.  **Unzip** the file to extract `ScreenRewind.app`.

### First-Time Launch
Because this app is not signed with an Apple Developer certificate yet, macOS will block it if you just double-click.

1.  **Right-click (or Control-click)** on `ScreenRewind.app`.
2.  Select **Open** from the menu.
3.  Click **Open** in the warning dialog.
    *   *You only need to do this once.*

### Permissions
To allow the app to capture your activity:
1.  When prompted, grant **Screen Recording** permission in System Settings.
2.  If you don't see a prompt, go to **System Settings > Privacy & Security > Screen Recording** and enable **ScreenRewind**.

### How to Use
*   The app runs in the **Menu Bar** (look for the "SR" icon).
*   **Start/Pause:** Click the icon to pause or resume recording.
*   **Interval:** Change how often snapshots are taken (10s - 5m).
*   **Settings:** Open the configuration file to customize categories.

## Setup (For Developers)

1.  Navigate to `backend/`.
2.  Create a virtual environment: `python3 -m venv venv`
3.  Activate it: `source venv/bin/activate`
4.  Install dependencies: `pip install -r requirements.txt`

## Usage

### Running the Capture Daemon
To start recording your screen activity:
```bash
python src/main.py
```

### Running the API Server
To start the API server for querying data:
```bash
uvicorn src.api.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.
Interactive documentation is available at `http://127.0.0.1:8000/docs`.

### API Endpoints
- `GET /snapshots/`: List all snapshots (supports pagination and search via `q` parameter).
- `GET /snapshots/latest`: Get the most recent snapshot.
- `GET /snapshots/{id}`: Get details of a specific snapshot.
