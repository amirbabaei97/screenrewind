import rumps
import threading
import sys
import os
import json

from src.main import ScreenRewindDaemon
from src.core.config import load_categories, save_categories, CATEGORIES_FILE, load_settings, save_settings
import subprocess

import webbrowser

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        # In dev, we are in src/gui, so we need to go up to backend root to find assets if we used that structure
        # But here we expect the icon to be in src/gui in the bundle.
        # Let's handle the dev case: if we are in src/gui, look in ../../assets
        
    # Check if we are in dev mode (no _MEIPASS)
    if not hasattr(sys, '_MEIPASS'):
        # Dev mode: assets are in backend/assets
        # Current file is backend/src/gui/tray.py
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base_path, "assets", relative_path)
    
    # Bundle mode: we put the icon in src/gui
    return os.path.join(base_path, "src", "gui", relative_path)

class ScreenRewindApp(rumps.App):
    def __init__(self):
        # Use icon if available, otherwise fallback to text
        # In build_app.sh we added: --add-data "assets/menubar_icon.png:src/gui"
        # So in the bundle it is at src/gui/menubar_icon.png
        # In dev, we want to look at assets/menubar_icon.png
        
        icon_name = "menubar_icon.png"
        icon_path = resource_path(icon_name)
        
        # Debug logging (temporary, writes to a file on Desktop if it fails)
        if not os.path.exists(icon_path):
             # Fallback logic or logging
             pass

        if os.path.exists(icon_path):
            super(ScreenRewindApp, self).__init__("SR", icon=icon_path)
        else:
            super(ScreenRewindApp, self).__init__("SR", icon=None)
        
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
            rumps.MenuItem("Dashboard", callback=self.open_dashboard)
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

    def open_dashboard(self, _):
        # Open the dashboard URL in default browser
        url = "https://app.screenrewind.amir.rocks"
        webbrowser.open(url)

    def open_settings_file_deprecated(self, _):
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
