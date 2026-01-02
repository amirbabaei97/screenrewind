#!/bin/bash

# Ensure we are in the backend directory
cd "$(dirname "$0")"

# Clean previous builds
rm -rf build dist

# Run PyInstaller
# --windowed: Create a .app bundle (macOS)
# --noconsole: Don't show terminal
# --name: App name
# --add-data: Add config folder if needed (we create it at runtime, but good to know)
# We need to ensure hidden imports for sqlalchemy drivers or rapidocr might be needed.

./venv/bin/pyinstaller --noconfirm --clean \
    --windowed \
    --name "ScreenRewind" \
    --add-data "src:src" \
    --hidden-import "sqlalchemy.sql.default_comparator" \
    --hidden-import "rapidocr_onnxruntime" \
    --hidden-import "uvicorn" \
    --hidden-import "fastapi" \
    --hidden-import "mss" \
    --hidden-import "Quartz" \
    --hidden-import "Cocoa" \
    --hidden-import "AppKit" \
    --hidden-import "Foundation" \
    --collect-all "rapidocr_onnxruntime" \
    --collect-all "uvicorn" \
    --collect-all "fastapi" \
    --collect-all "mss" \
    --collect-all "Quartz" \
    --collect-all "Cocoa" \
    --collect-all "AppKit" \
    --collect-all "Foundation" \
    src/gui/tray.py

echo "Build complete. App is in backend/dist/ScreenRewind.app"
