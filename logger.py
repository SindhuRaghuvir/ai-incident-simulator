"""
Structured log store. Logs are stored in SQLite alongside metrics.
Each log entry has a timestamp, level, message, and optional request_id to group related logs.
"""

import sqlite3
import os
import uuid
from datetime import datetime

import pandas as pd

import config


def _get_connection():
    os.makedirs(os.path.dirname(config.METRICS_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(config.METRICS_DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            level TEXT NOT NULL,
            message TEXT NOT NULL,
            request_id TEXT DEFAULT '',
            component TEXT DEFAULT ''
        )
    """)
    conn.commit()
    return conn


def new_request_id() -> str:
    return uuid.uuid4().hex[:8]


def log(level: str, message: str, request_id: str = "", component: str = ""):
    conn = _get_connection()
    conn.execute(
        "INSERT INTO logs (timestamp, level, message, request_id, component) VALUES (?, ?, ?, ?, ?)",
        (datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"), level, message, request_id, component),
    )
    conn.commit()
    conn.close()


def info(message: str, request_id: str = "", component: str = ""):
    log("INFO", message, request_id, component)


def warn(message: str, request_id: str = "", component: str = ""):
    log("WARN", message, request_id, component)


def error(message: str, request_id: str = "", component: str = ""):
    log("ERROR", message, request_id, component)


def get_logs(limit: int = 200) -> pd.DataFrame:
    conn = _get_connection()
    df = pd.read_sql_query(
        f"SELECT * FROM logs ORDER BY id DESC LIMIT {limit}", conn
    )
    conn.close()
    return df


def clear_logs():
    conn = _get_connection()
    conn.execute("DELETE FROM logs")
    conn.commit()
    conn.close()
