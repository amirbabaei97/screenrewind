import sqlite3
import os
import json
from datetime import datetime

class UploadQueue:
    def __init__(self, db_path):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS queue (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                ocr_text TEXT,
                window_title TEXT,
                app_name TEXT,
                image_path TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def add(self, timestamp, ocr_text, window_title, app_name, image_path):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO queue (timestamp, ocr_text, window_title, app_name, image_path)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp.isoformat(), ocr_text, window_title, app_name, image_path))
        conn.commit()
        conn.close()

    def pop(self, limit=10):
        """Get a batch of items from queue, but don't delete yet."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute('SELECT * FROM queue ORDER BY id ASC LIMIT ?', (limit,))
        rows = c.fetchall()
        
        items = []
        for row in rows:
            items.append(dict(row))
        conn.close()
        return items

    def remove(self, item_ids):
        if not item_ids:
            return
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        placeholders = ','.join('?' * len(item_ids))
        c.execute(f'DELETE FROM queue WHERE id IN ({placeholders})', item_ids)
        conn.commit()
        conn.close()
