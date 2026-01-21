# ScreenRewind

ScreenRewind is a privacy-focused, multi-device activity tracking system. It consists of a lightweight **Client** (Mac Tray App) that captures your work context, a centralized **Server** that processes and stores data, and a **Web Dashboard** for analytics and "Time Travel".

## Architecture

ScreenRewind is built on a 3-tier architecture:

1.  **Client (Mac):** 
    - Runs silently in the system tray.
    - Captures screenshots and Active Window metadata.
    - Performs **Offline OCR** (Optical Character Recognition) on the device.
    - Queues data locally if offline, syncing when the connection is restored.
    - Tech: Python, MSS, RapidOCR, SQLite (Queue), Requests.

2.  **Server (API):**
    - REST API powered by **FastAPI**.
    - Handles data ingestion, storage, and retrieval.
    - Stores images in file storage and metadata in **PostgreSQL**.
    - Manages User Authentication and Logic Rules.
    - Tech: FastAPI, SQLAlchemy, PostgreSQL, Google Gemini (AI).

3.  **Frontend (Web):**
    - Modern Dashboard to view productivity insights.
    - "Rewind" feature to traverse your history visually.
    - Tech: React 19, Vite, Tailwind CSS, Recharts.

---

## 🚀 Deployment & Installation

### 1. Server Setup (Ubuntu/Linux)

The server acts as the central brain.

**Prerequisites:** Python 3.10+, PostgreSQL, Nginx.

```bash
# 1. Clone & Navigate
git clone https://github.com/yourusername/screenrewind.git
cd screenrewind/server

# 2. Setup Database (PostgreSQL)
# Ensure you have a DB created named 'screenrewind'

# 3. Environment Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Configuration
export DATABASE_URL="postgresql://user:password@localhost/screenrewind"

# 5. Run (Dev)
uvicorn src.api.main:app --reload

# 5. Run (Prod)
# Use gunicorn/systemd as described in deployment docs.
```

### 2. Client Setup (macOS)

The client runs on your machine to capture data.

**Prerequisites:** Python 3.10+ (recommend creating a virtual env).

```bash
cd screenrewind/client

# 1. Environment Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Run Locally
python src/main.py

# 3. Build Standalone App (.app)
pyinstaller --name ScreenRewind --windowed --icon=assets/app_icon.icns src/gui/tray.py
```

*Note: The client is configured to send data to `https://api.screenrewind.amir.rocks`. Edit `API_URL` in `src/main.py` for local dev. Time tracking interval is controlled by `~/.screenrewind/settings.json`.*

### 3. Frontend Setup (Web)

The interface to view your data.

**Prerequisites:** Node.js / Bun.

```bash
cd screenrewind/frontend

# 1. Install
bun install # or npm install

# 2. Run Dev Server
bun dev

# 3. Build for Production
bun run build
# The 'dist' folder is ready for deployment to Nginx/Vercel/Netlify.
```

## Features

- **Offline-First:** The client queues data when internet is lost and syncs automatically.
- **Privacy-Centric:** OCR happens on-device. Images are stored securely on your self-hosted server.
- **Smart Categorization:**
    - **Layer 1:** Regex Rules (defined by you).
    - **Layer 2:** AI Classification (Google Gemini) for "fuzzy" understanding.
- **Smart Time Tracking:**
    - Precise duration measurement (handles lag/latency).
    - Intelligent pause/resume handling.
    - System sleep detection (prevents "ghost" hours).
- **Time Travel:** Visually scrub back through your day to find what you were working on.

## Project Structure

```
.
├── client/           # Mac Tray Application
│   ├── src/
│   │   ├── gui/      # Tray menu logic
│   │   ├── core/     # Capture, OCR, Queue logic
│   │   └── main.py   # Entry point
│
├── server/           # Backend API
│   ├── src/
│   │   ├── api/      # FastAPI Routers
│   │   ├── models/   # SQLAlchemy Models
│   │   └── core/     # Config & Database
│   └── uploads/      # Stored screenshots
│
└── frontend/         # React Dashboard
    ├── src/
    │   ├── pages/    # Dashboard, Projects, Rules
    │   └── services/ # API Client
```
