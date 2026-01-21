# ScreenRewind Server (Backend)

The central brain of the ScreenRewind architecture. This is a FastAPI application that handles data ingestion from clients, storage, AI categorization, and serves the API for the frontend.

## Features
- **FastAPI:** High-performance async API.
- **Data Ingestion:** Receives snapshots (images + metadata) from Mac Clients.
- **Categorization:** Hybrid logic using Regex Rules (Layer 1) and Google Gemini AI (Layer 2).
- **PostgreSQL:** Robust relational database for users, projects, tasks, and snapshots.
- **Authentication:** (Planned) OAuth2/JWT for multi-user support.

## Prerequisites
- **Python 3.10+**
- **PostgreSQL**
- **Google Gemini API Key** (for AI features)

## Installation & Setup

### 1. Environment Setup

```bash
cd server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Database Configuration

Ensure PostgreSQL is running and you have a database created.

```bash
# Example Postgres user/db creation
# createuser screenuser -P
# createdb screenrewind -O screenuser
```

Set the database connection string and API key in your environment (or create a `.env` file):

```bash
export DATABASE_URL="postgresql://screenuser:password@localhost/screenrewind"
export GEMINI_API_KEY="your_google_api_key"
```

### 3. Running the Server

**Development Mode:**
```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```
The API will be available at `http://localhost:8000`.
Docs are at `http://localhost:8000/docs`.

**Production Mode:**
Use Gunicorn as a process manager with Uvicorn workers.

```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.api.main:app
```

## API Structure

The backend exposes a REST API structured around key resources.

### 1. Snapshots (`/snapshots`)
The core data unit.
- **POST `/snapshots/`**: (Client Only) Upload a new screen capture. 
  - Accepts `multipart/form-data`.
  - Fields: `file` (image), `ocr_text`, `window_title`, `app_name`, `timestamp`, `duration` (optional, seconds).
  - Triggers the categorization pipeline.
- **GET `/snapshots/`**: List snapshots. Supports pagination (`img`, `limit`) and search (`q` for OCR text).
- **GET `/snapshots/latest`**: Fetch the most recent snapshot (for real-time dashboard).
- **GET `/snapshots/{id}`**: Retrieve metadata for a single snapshot.

### 2. Analytics (`/analytics`)
Aggregated data for charts and graphs.
- **GET `/analytics/projects`**: Time distribution per project (Pie Chart support).
- **GET `/analytics/projects/{name}/tasks`**: Breakdown of tasks within a specific project.
- **GET `/analytics/activity`**: Heatmap data (activity density over time).

### 3. Projects (`/projects`)
Management of work categories.
- **GET `/projects/`**: List all projects.
- **POST `/projects/`**: Create a new project.
- **PUT `/projects/{id}`**: Update details.
- **DELETE `/projects/{id}`**: Delete a project.

### 4. Rules (`/rules`)
User-defined overrides for categorization.
- **GET `/rules/`**: List current regex rules.
- **POST `/rules/`**: Add a new rule (e.g., "If Window Title matches `.*YouTube.*`, set Project=`Personal`).
- **DELETE `/rules/{id}`**: Remove a rule.

### 5. System (`/system`)
Maintenance endpoints.
- **DELETE `/system/reset-data`**: Clears all snapshots and history without deleting Project/Rule definitions.

## Folder Structure

- `src/api`: API Routers and endpoints.
- `src/core`: Core logic (AI, Config, Database connections).
- `src/models`: SQLAlchemy ORM models.
- `src/schemas`: Pydantic schemas for validation.
- `uploads/`: Directory where uploaded screenshot images are stored.
