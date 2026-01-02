# Software Requirements Specification (SRS)
## 1. Project Overview

**ScreenRewind** is a locally hosted, cross-platform desktop application that automatically tracks user activity by capturing screen snapshots, performing Optical Character Recognition (OCR), and utilizing local AI to categorize work context.

- **Core Philosophy:** "Uninterrupted workflow" meaning user doesn't need to provide manual input. "Uncompromising Privacy." No data ever leaves the user's machine.
- **Target Audience:** Developers, Researchers, and Knowledge Workers who need granular time tracking without manual input.
- **Distribution Goal:** Free, open-source, single-click install for macOS, Windows, and Linux.

## 2. Technical Stack (Cross-Platform)

### Core Backend (The Logic)
- **Language:** **Python 3.10+**
    - _Why:_ Unmatched ecosystem for OCR and AI integration.
- **Server Framework:** **FastAPI** (running on `localhost`).
    - _Why:_ Provides a robust REST API for the frontend to consume and also I love it.
- **Database:** **SQLite** (with **SQLAlchemy** ORM).
    - _Why:_ Zero-config, single-file storage, perfect for local embedded use.

### The "Eyes" (Capture & Processing)
- **Screenshots:** **MSS** (Multiple Screen Shot).
    - _Why:_ Extremely fast, cross-platform (Mac/Win/Linux), lightweight.     
- **OCR Engine:** **RapidOCR** (Python wrapper for PaddleOCR ONNX).
    - _Why:_ Faster and more accurate than Tesseract; supports ONNX runtime which is portable across OSs without heavy external dependencies.
- **AI/LLM Integration:** User's own API key, for now we use Gemini, later openAI.  

### Frontend (The UI)
- **Framework:** **React** + **Vite** + **TailwindCSS**.
- **Wrapper:** **Tauri v2** (or Electron).
    - _Recommendation:_ **Tauri**. It allows you to bundle the Python backend as a "sidecar." It creates significantly smaller installers (<50MB) compared to Electron (~150MB) and is more performant.

## 3. Functional Requirements

### FR1: Silent Data Collection (The Daemon)

The system must run silently in the background (System Tray application).
- **1.1 Snapshot Interval:** Configurable timer (default: every 60 seconds).
- **1.2 Idle Detection:** Calculate a perceptual hash (pHash) of the current screenshot. If `pHash(current) == pHash(prev)`, discard the image to save storage (User is idle).
- **1.3 App Context:** Capture the active window title and process name using cross-platform calls (`pygetwindow` or custom platform-specific scripts).
- **1.4 Exclusion Rules:** Users can blacklist specific apps (e.g., Password Managers, Banking) or window titles from ever being captured.
- **1.5 Easy pause/resume** users should be able to schedule the recording time as well as easily pause/resume by clicking the app icon in the MacOS menu. 
- **1.6 Active on Startup** the daemon should be active on startup and start capturing automatically. 

### FR2: Local Data Processing

- **2.1 Optical Character Recognition (OCR):** Every valid snapshot is processed to extract raw text strings.
- **2.2 Image Compression:** Raw screenshots must be converted to **WebP** format (Quality 75%) immediately.
    - _Target Size:_ ~100KB per image.
    - _Storage impact:_ ~50MB per 8-hour workday.

### FR3: Intelligent Categorization (The "Brain")

- **3.1 Hierarchy:** The user can define a category tree (max 3 levels depth)(e.g., `PhD -> Research`, `PhD -> Writing`, `Side Hustle -> Coding`-> ScreenRewind app).
- **3.2 Hybrid Classification:**
    - _Layer 1 (Heuristic):_ Regex rules (e.g., If App == "VS Code", Category = "Coding"). These rules are user defined, so this has the highest priority. uses only window title. 
    - _Layer 2 (LLM):_ If first layer rules fail, send the OCR text + Window Title to the local LLM with the prompt: _"Given this text from a screen, classify the activity into one of these categories: [List]. Return JSON."_ (Prompt obviously should be improved)

 ### FR4: User Interface (The Dashboard)
- **4.1 The "Rewind":** A graphical timeline spanning 00:00 to current time. Users can drag a handle to "rewind" their day.
- **4.2 The Viewer:** The center stage displays the screenshot associated with the timestamp.
- **4.3 Activity Heatmap:** A color-coded bar under the scrubber showing category density (e.g., Blue blocks for Work, Red blocks for YouTube). It also shows the icon of the app that was used at that time
- **4.4 Search Bar:** Full-text search across all historical OCR data.
    - _Query:_ "Gradient Descent" -> _Result:_ Shows all timestamps where that text appeared on screen and highlighting the text found in the screenshots.

### FR5: Data Lifecycle Management

- **5.1 Retention Policy:** Configurable "Time to Live" (TTL).
    - _Example:_ "Delete screenshots after 30 days, but keep text logs forever."
- **5.2 Export:** Ability to export a CSV report of time spent per category/project for the desired time. 
- **5.3 "Nuke" Button:** A panic button to delete all data immediately.

## 4. Deployment & Distribution Strategy

To achieve "Everyone can install it":
1. **Packaging:** Use **PyInstaller** to compile the Python backend into a standalone executable (one for `.exe`, one for Mach-O, one for ELF).
2. **Tauri Bundle:** Configure Tauri to bundle the compiled Python executable as a "sidecar."
    - When the user double-clicks the App Icon, Tauri starts -> Tauri spawns the Python process in the background.
3. **Dependencies:**
    - **Included:** SQLite, RapidOCR (via pip), MSS.
    - **Excluded (User Action Required):** LLM API Key. the app should  show a friendly modal: _"To enable AI features, please provide API Key. Until then, we will use basic keyword matching."

## 5. Development Roadmap (MVP)

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