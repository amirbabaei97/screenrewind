# ScreenRewind

ScreenRewind is an intelligent, locally-hosted time tracking tool that automatically captures your screen, extracts text via OCR, and uses AI (Google Gemini) to categorize your work into Projects and Tasks.

It features a background daemon with a system tray interface and a modern React-based dashboard for analytics and management.

## Features

### 🧠 Intelligent Tracking
- **Automated Capture:** Takes screenshots at configurable intervals (10s, 30s, 60s, 5m).
- **OCR Engine:** Extracts text from every screenshot using Tesseract.
- **AI Categorization:** Uses Google Gemini (Generative AI) to analyze screen content and automatically assign it to a **Project** and **Task**.
- **Rules Engine:** Define regex-based rules to override AI categorization for specific window titles or app names.

### 📊 Dashboard & Analytics
- **Activity Overview:** Visualize time spent on projects via Pie Charts and Bar Charts.
- **Drill-Down:** Click on a project to see the breakdown of specific Tasks.
- **Time Filtering:** View data for Today, Yesterday, Last 7 Days, or a Custom Range.
- **Detailed Tooltips:** Precise duration tracking.

### 🛠 Management
- **Projects & Tasks:** Create, Edit, and Delete projects and tasks explicitly.
- **Rules:** Manage manual overrides (e.g., "If window title contains 'YouTube', categorize as 'Personal'").
- **Settings:** "Danger Zone" to reset all captured data while preserving project structures.

### 🖥 MacOS Tray App
- **Status Icon:** Visible in the menu bar ("SR").
- **Quick Controls:** Pause/Resume recording, Change Interval.
- **One-Click Dashboard:** Opens the web interface directly.

## Tech Stack

*   **Backend:** Python 3.10+, FastAPI, SQLAlchemy (SQLite), google-generativeai, pytesseract, mss.
*   **Frontend:** React 19, TypeScript, Vite, Tailwind CSS v4, Recharts, Lucide Icons.
*   **System:** MacOS specific optimizations (Quartz window management).

## Installation & Setup (Developer)

### Prerequisites
1.  **Python 3.10+**
2.  **Bun** (or Node.js)
3.  **Tesseract OCR** (`brew install tesseract`)
4.  **Google Gemini API Key** (Set as `GEMINI_API_KEY` env var)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GEMINI_API_KEY=your_key_here" > .env

# Run the Tray App (Background Daemon + API)
python src/gui/tray.py
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
bun install

# Run Development Server
bun dev
```

### 3. Usage

1.  Start the Backend (Tray App will appear in menu bar).
2.  Start the Frontend (visting `http://localhost:5173`).
3.  **Tray Icon:** Right-click the "SR" icon in your mac menu bar -> Click **Dashboard** to open the UI.
4.  **Dashboard:**
    *   **Projects:** Define your main projects (e.g., "ScreenRewind", "Freelance", "Learning").
    *   **Rules:** (Optional) Add specific rules if AI gets it wrong.
    *   **Work:** Just work! The app will capture, OCR, and AI-classify your time.
5.  **View Data:** Refresh the dashboard to see your time distribution.

## "Danger Zone"

In the **Settings** tab, you can reset the capture database.
*   **Reset Database:** Deletes ALL screenshots, OCR text, and time logs.
*   **Note:** Your Project definitions, Tasks, and Rules are *preserved*.

## Project Structure

- `backend/src/daemon`: Capture & AI logic.
- `backend/src/api`: FastAPI endpoints.
- `backend/src/gui`: macOS Tray application.
- `frontend/src/pages`: React UI (Dashboard, Projects, Rules, Settings).

### API Endpoints

#### Snapshots (`/snapshots`)
- `GET /snapshots/`: List all snapshots (supports pagination and text search via `q`).
- `GET /snapshots/latest`: Get the most recent snapshot.
- `GET /snapshots/{id}`: Get details of a specific snapshot.

#### Projects & Tasks (`/projects`)
- `GET /projects/`: List all projects.
- `POST /projects/`: Create a new project.
- `PUT /projects/{id}`: Update a project's name or description.
- `DELETE /projects/{id}`: Delete a project.
- `POST /projects/{id}/tasks`: Create a task for a project.
- `DELETE /projects/tasks/{task_id}`: Delete a task.

#### Analytics (`/analytics`)
- `GET /analytics/projects`: Get time distribution by project (filtering by start/end date).
- `GET /analytics/projects/{name}/tasks`: Get time distribution by task for a specific project.

#### Rules (`/rules`)
- `GET /rules/`: List all categorization rules.
- `POST /rules/`: Create a new regex-based rule.
- `DELETE /rules/{id}`: Delete a rule.

#### System (`/system`)
- `DELETE /system/reset-data`: Clear all captured data (Screenshots, OCR, AI logs) but keep Projects/Tasks.
