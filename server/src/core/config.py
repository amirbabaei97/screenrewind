import json
import os
import sys
from typing import Dict, List, Any
from pathlib import Path

# Determine App Data Directory (Cross-platform)
if sys.platform == "darwin":
    APP_DATA_DIR = os.path.expanduser("~/Library/Application Support/ScreenRewind")
elif sys.platform == "win32":
    APP_DATA_DIR = os.path.join(os.environ["APPDATA"], "ScreenRewind")
else:
    APP_DATA_DIR = os.path.expanduser("~/.screenrewind")

# Ensure directory exists
if not os.path.exists(APP_DATA_DIR):
    os.makedirs(APP_DATA_DIR)

CONFIG_DIR = APP_DATA_DIR
CATEGORIES_FILE = os.path.join(CONFIG_DIR, "categories.json")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")

DEFAULT_CATEGORIES = {
    "Work": ["jira", "slack", "zoom", "meet", "docs", "sheet"],
    "Coding": ["vscode", "pycharm", "terminal", "github", "stackoverflow", "python", "def ", "class ", "code", "debug"],
    "Social": ["twitter", "facebook", "instagram", "reddit", "youtube"],
    "Communication": ["whatsapp", "telegram", "discord", "signal"]
}

DEFAULT_SETTINGS = {
    "capture_interval": 10
}

def ensure_config_dir():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)

def load_settings() -> Dict[str, Any]:
    ensure_config_dir()
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS
    
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return DEFAULT_SETTINGS

def save_settings(settings: Dict[str, Any]):
    ensure_config_dir()
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

def load_categories() -> Dict[str, List[str]]:
    ensure_config_dir()
    if not os.path.exists(CATEGORIES_FILE):
        save_categories(DEFAULT_CATEGORIES)
        return DEFAULT_CATEGORIES
    
    try:
        with open(CATEGORIES_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return DEFAULT_CATEGORIES

def save_categories(categories: Dict[str, List[str]]):
    ensure_config_dir()
    with open(CATEGORIES_FILE, 'w') as f:
        json.dump(categories, f, indent=4)

def categorize_text(text: str, categories: Dict[str, List[str]]) -> str:
    """
    Simple keyword matching. Returns the first matching category or 'Uncategorized'.
    Case-insensitive.
    """
    text_lower = text.lower()
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return category
    return "Uncategorized"
