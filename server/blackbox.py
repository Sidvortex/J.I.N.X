"""
BLACKBOX.PY — DATABASE LOGGING
All events, alerts, and system logs stored in SQLite.
"""

import sqlite3
import json
import base64
import cv2
import os
from datetime import datetime
from pathlib import Path

import dna


class Blackbox:
    def __init__(self):
        db_path = "data/jinx_database.db"
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()
        print("  [BLACKBOX] Database ready")

    def _create_tables(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                type      TEXT,
                data      TEXT,
                screenshot_path TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS faces (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name      TEXT UNIQUE,
                label     TEXT,
                added_at  TEXT
            )
        """)
        self.conn.commit()

    def log_event(self, event_type: str, data: dict, frame=None):
        screenshot_path = None
        if frame is not None:
            alerts_dir = Path("data/alerts")
            alerts_dir.mkdir(exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = str(alerts_dir / f"{event_type}_{ts}.jpg")
            cv2.imwrite(screenshot_path, frame)

        c = self.conn.cursor()
        c.execute(
            "INSERT INTO events (timestamp, type, data, screenshot_path) VALUES (?,?,?,?)",
            (datetime.now().isoformat(), event_type, json.dumps(data), screenshot_path)
        )
        self.conn.commit()

    def get_recent_events(self, limit: int = 50) -> list:
        c = self.conn.cursor()
        c.execute("SELECT timestamp, type, data FROM events ORDER BY id DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        return [{"timestamp": r[0], "type": r[1], "data": json.loads(r[2])} for r in rows]

    def get_stats(self) -> dict:
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM events")
        total = c.fetchone()[0]
        c.execute("SELECT type, COUNT(*) FROM events GROUP BY type")
        by_type = dict(c.fetchall())
        return {"total_events": total, "by_type": by_type}
