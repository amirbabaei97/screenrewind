# ScreenRewind Frontend (Web)

The web-based dashboard for ScreenRewind. It connects to the ScreenRewind Backend API to display productivity metrics, manage projects, and "time travel" through past work.

## Features
- **Modern UI:** Built with React 19, TypeScript, and Tailwind CSS.
- **Interactive Charts:** Visualizes time usage with Recharts.
- **Time Travel:** A visual interface to scrub through past screenshots.
- **Management:** Interface to create Projects, Tasks, and Categorization Rules.

## Prerequisites
- **Node.js** (v18+) or **Bun** (recommended)

## Installation & Setup

1. **Install Dependencies**
   ```bash
   cd frontend
   bun install  # or npm install
   ```

2. **Configuration**
   The frontend expects the backend API to be running.
   
   By default, it points to `https://api.screenrewind.amir.rocks`. 
   To change this for local development:
   - Edit `src/services/api.ts`
   - Set `baseURL` to `http://localhost:8000`.

3. **Running Development Server**
   ```bash
   bun dev
   ```
   Open `http://localhost:5173` to view the app.

4. **Building for Production**
   ```bash
   bun run build
   ```
   This generates static files in the `dist/` folder, ready to be served by Nginx or any static file host.

## Project Structure

- `src/components`: Reusable UI components (Charts, Buttons, Layouts).
- `src/layouts`: Page layouts (Main container with Sidebar).
- `src/pages`:
    - **Dashboard:** Main view with today's summary.
    - **Projects:** Management table for Projects/Tasks.
    - **Rules:** Interface for regex rules.
    - **Rewind:** The time-scrubber interface.
    - **Settings:** App configuration and data management.
- `src/services`: API client (`axios`) configuration.
- `src/types`: TypeScript interfaces reflecting backend models.
