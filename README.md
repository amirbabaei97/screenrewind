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

## Setup

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
