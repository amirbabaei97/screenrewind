import rumps
import threading
import sys
import os
import json
import uvicorn

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.main import ScreenRewindDaemon
from src.core.config import load_categories, save_categories, CATEGORIES_FILE, load_settings, save_settings
from src.api.main import app as api_app
import subprocess

def run_api():
    # Run uvicorn in a separate thread
    uvicorn.run(api_app, host="127.0.0.1", port=8000, log_level="error")

class ScreenRewindApp(rumps.App):
    def __init__(self):
        super(ScreenRewindApp, self).__init__("SR", icon=None)
        
        # Start API Server
        self.api_thread = threading.Thread(target=run_api, daemon=True)
        self.api_thread.start()
        
        # Start Capture Daemon
        self.daemon = ScreenRewindDaemon()
        self.daemon.daemon = True  # Ensure thread dies when app quits
        self.daemon.start()
        
        # Interval Menu
        self.interval_menu = rumps.MenuItem("Recording Interval")
        self.intervals = [10, 30, 60, 300]
        current_interval = self.daemon.interval
        
        for i in self.intervals:
            item = rumps.MenuItem(f"{i} seconds", callback=self.set_interval)
            item.state = 1 if i == current_interval else 0
            self.interval_menu.add(item)

        self.menu = [
            rumps.MenuItem("Pause Recording", callback=self.toggle_recording),
            rumps.separator,
            self.interval_menu,
            rumps.MenuItem("Settings", callback=self.open_settings)
        ]
        self.is_paused = False

    def set_interval(self, sender):
        # Parse interval from title "10 seconds" -> 10
        new_interval = int(sender.title.split()[0])
        
        # Update Daemon
        self.daemon.update_interval(new_interval)
        
        # Update Config
        settings = load_settings()
        settings["capture_interval"] = new_interval
        save_settings(settings)
        
        # Update UI Checkmarks
        for item in self.interval_menu.values():
            item.state = 0
        sender.state = 1

    def toggle_recording(self, sender):
        if self.is_paused:
            self.daemon.resume()
            sender.title = "Pause Recording"
            self.is_paused = False
        else:
            self.daemon.pause()
            sender.title = "Resume Recording"
            self.is_paused = True

    def open_settings(self, _):
        # Ensure config file exists
        if not os.path.exists(CATEGORIES_FILE):
            save_categories(load_categories())
            
        # Open the JSON file with the default system editor (TextEdit, VS Code, etc.)
        try:
            subprocess.run(["open", CATEGORIES_FILE], check=True)
        except Exception as e:
            rumps.alert("Error", f"Could not open settings file: {e}")

if __name__ == "__main__":
    ScreenRewindApp().run()
