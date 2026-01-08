# Software Requirements Specification (SRS)
## 1. Project Overview

**ScreenRewind** is a client-server application that automatically tracks user activity across multiple devices. It consists of a lightweight local client (Mac Tray App) for data capture and a centralized server for processing, storage, and analysis.

- **Core Philosophy:** "Seamless multi-device tracking." Users can switch between computers and have a unified view of their productivity.
- **Target Audience:** Developers, Researchers, and Knowledge Workers who work across multiple machines.
- **Distribution:** 
    - **Client:** Mac Tray App (DMG).
    - **Web:** Hosted Web Dashboard.

## 2. Technical Stack

### Component 1: Mac Core (Client / Tray App)
- **Role:** The "Eyes". Runs locally on the user's Mac.
- **Language:** **Python 3.10+**.
- **Responsibilities:** 
    - Capture screenshots using **MSS**.
    - Perform **OCR** locally using **RapidOCR**.
    - Capture window context (Active Window Title).
    - Handle **Offline Queuing**: If internet is unavailable, queue data locally and sync when online.
    - **Authentication:** Authenticate with the backend API to link data to the user account.
    - **Data Transmission:** Send JSON payload (OCR text, metadata) and Screenshot file to the Backend API.

### Component 2: Backend API (Server)
- **Role:** The "Brain" and "Memory". Hosted on Ubuntu VPS.
- **Framework:** **FastAPI**.
- **Database:** **PostgreSQL** (for robust multi-user transactional data).
- **Storage:** Local filesystem or Object Storage (S3-compatible) for storing screenshots.
- **Responsibilities:**
    - **API Endpoints:** Receive data from Clents.
    - **Processing Pipeline:**
        1.  Receive payload.
        2.  **Layer 1 Classification:** Apply user-defined Regex rules.
        3.  **Layer 2 Classification:** If Layer 1 fails, query AI/LLM for categorization.
        4.  Save metadata to DB and screenshot to storage.
    - **User Management:** Authentication (OAuth2/JWT) and multi-tenancy.

### Component 3: Frontend (Web Dashboard)
- **Role:** The "Interface". Hosted on `https://app.amir.rocks` (example).
- **Framework:** **React** + **Vite** + **TailwindCSS**.
- **Responsibilities:**
    - User Authentication (Login/Signup).
    - Dashboard visualization (Charts, Graphs).
    - "Rewind" Time Machine interface.
    - Project & Rule management.

## 3. Functional Requirements

### FR1: Mac Client Behavior
- **1.1 Silent Capture:** Runs in background/tray.
- **1.2 Snapshot Cycle:**
    1.  Take Screenshot.
    2.  Check for Idleness (pHash comparison). Discard if idle.
    3.  Capture Window Title.
    4.  **Perform OCR locally.**
    5.  Prepare payload.
- **1.3 Connectivity Handling:**
    - **Online:** Send payload immediately to `POST /api/v1/snapshots`.
    - **Offline:** Serialize payload and store in a local queue (SQLite/File-based). Retry upload periodically or when connection restores.
- **1.4 Auth:** Login flow via the Tray Menu (opens browser or simple credential input).

### FR2: Server Processing & Intelligence
- **2.1 Ingestion:** Secure endpoints to receive snapshots.
- **2.2 Hybrid Classification (Server-Side):**
    - _Layer 1 (Heuristic):_ Regex rules stored in DB per user. High priority.
    - _Layer 2 (LLM):_ Integration with OpenAI/Gemini APIs from the server.
- **2.3 Data Storage:** Efficient storage of millions of text records and images.

### FR3: Web User Interface
- **3.1 Analytics Dashboard:** Visualization of time tracking data.
    - _Time Periods:_ Selectable ranges: Today, Yesterday, Custom Date Range.
    - _Project Distribution (Pie Chart):_ Shows percentage of time spent on each Project for the selected period.
- **3.2 Time Machine (The Rewind):**
    - Fetches images from server via API.
    - Playback speed controls.
    - Search functionality via server endpoints.

## 4. Deployment Strategy

### Server (Ubuntu VPS)
- **Infrastructure:**
    - **Reverse Proxy:** Nginx (handles SSL and routing).
    - **Process Manager:** Systemd (or Docker Compose) for FastAPI.
    - **Database:** PostgreSQL.
- **Domain:** `amir.rocks`. Web App on subdomain (e.g., `app.amir.rocks`, `api.amir.rocks`).

### Client (macOS)
- **Packaging:** PyInstaller to create standalone `.app`/`.dmg`.
- **Updates:** Sparkle or manual update check implementation.

## 5. Development Roadmap (Refined)

1. **Phase 1 (Core):** Python script that uses `mss` to take screenshots, `RapidOCR` to read them, and saves to SQLite. (No UI yet). **(Completed)**
2. **Phase 2 (API):** Wrap the script in FastAPI so you can query `GET /snapshots/latest`. **(Completed)**
3. **Phase 3 (Menu Bar App - Standalone):** 
    - Develop a lightweight macOS Menu Bar application (using `rumps` or similar).
    - **Features:**
        - Status Icon (Recording/Paused).
        - "Pause/Resume" toggle.
        - "Settings" modal to manage Categories and Keywords.
        - "Quit" option.
    - **Logic:** Implement basic keyword-based categorization (if keyword in OCR text -> assign category).
    - **Packaging:** Create a standalone `.app` executable for macOS.
4. **Phase 4 (Full UI - The "Brain"):** Build the React Timeline component to visualize the data from the API.
5. **Phase 5 (Packaging - Full App):** Set up Tauri to bundle the Python script and React frontend into a `.dmg` / `.exe`.