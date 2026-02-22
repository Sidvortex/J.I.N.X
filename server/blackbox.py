# blackbox.py
# handles all the sqlite stuff for logging alerts, faces, etc
# first time using sqlite in a project ngl, its actually pretty easy

import sqlite3
import os
from datetime import datetime


class JinxDB:
    def __init__(self, db_path="data/jinx_database.db"):
        # make sure the data folder exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.setup_tables()
        print("[DB] database ready")

    def setup_tables(self):
        c = self.conn.cursor()

        # main alerts table
        c.execute('''CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            type TEXT,
            details TEXT,
            confidence REAL,
            screenshot TEXT,
            resolved INTEGER DEFAULT 0
        )''')

        # who jinx has seen
        c.execute('''CREATE TABLE IF NOT EXISTS face_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            name TEXT,
            label TEXT,
            confidence REAL,
            action TEXT
        )''')

        # sound events
        c.execute('''CREATE TABLE IF NOT EXISTS audio_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            classification TEXT,
            confidence REAL,
            is_threat INTEGER DEFAULT 0
        )''')

        # general system log for debugging mostly
        c.execute('''CREATE TABLE IF NOT EXISTS sys_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            module TEXT,
            msg TEXT,
            level TEXT DEFAULT 'INFO'
        )''')

        # network stuff
        c.execute('''CREATE TABLE IF NOT EXISTS network (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            mac TEXT,
            ip TEXT,
            event TEXT,
            details TEXT
        )''')

        self.conn.commit()

    # --- logging functions ---

    def add_alert(self, alert_type, details, conf=0.0, screenshot=None):
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO alerts (timestamp, type, details, confidence, screenshot) VALUES (?,?,?,?,?)",
            (datetime.now().isoformat(), alert_type, details, conf, screenshot)
        )
        self.conn.commit()
        return c.lastrowid

    def add_face(self, name, label, conf=0.0, action="detected"):
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO face_log (timestamp, name, label, confidence, action) VALUES (?,?,?,?,?)",
            (datetime.now().isoformat(), name, label, conf, action)
        )
        self.conn.commit()

    def add_audio(self, classification, conf, threat=False):
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO audio_events (timestamp, classification, confidence, is_threat) VALUES (?,?,?,?)",
            (datetime.now().isoformat(), classification, conf, int(threat))
        )
        self.conn.commit()

    def add_syslog(self, module, msg, level="INFO"):
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO sys_log (timestamp, module, msg, level) VALUES (?,?,?,?)",
            (datetime.now().isoformat(), module, msg, level)
        )
        self.conn.commit()

    def add_network_event(self, mac, ip, event, details=""):
        c = self.conn.cursor()
        c.execute(
            "INSERT INTO network (timestamp, mac, ip, event, details) VALUES (?,?,?,?,?)",
            (datetime.now().isoformat(), mac, ip, event, details)
        )
        self.conn.commit()

    # --- getters ---

    def get_alerts(self, n=20):
        c = self.conn.cursor()
        c.execute("SELECT timestamp, type, details, confidence FROM alerts ORDER BY id DESC LIMIT ?", (n,))
        return c.fetchall()

    def get_faces(self, n=20):
        c = self.conn.cursor()
        c.execute("SELECT timestamp, name, label, confidence FROM face_log ORDER BY id DESC LIMIT ?", (n,))
        return c.fetchall()

    def get_stats(self):
        c = self.conn.cursor()
        stats = {}
        c.execute("SELECT COUNT(*) FROM alerts")
        stats["alerts"] = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM face_log")
        stats["faces_seen"] = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM alerts WHERE type='THREAT'")
        stats["threats"] = c.fetchone()[0]
        c.execute("SELECT COUNT(DISTINCT name) FROM face_log")
        stats["unique_people"] = c.fetchone()[0]
        return stats

    def close(self):
        self.conn.close()


# quick test
if __name__ == "__main__":
    db = JinxDB()
    db.add_syslog("CORE", "test entry")
    db.add_alert("TEST", "testing 123", 0.99)
    db.add_face("admin", "safe", 0.95)
    db.add_audio("dog_bark", 0.87, False)

    print("alerts:", db.get_alerts(5))
    print("stats:", db.get_stats())
    print("[DB] all good")
    db.close()