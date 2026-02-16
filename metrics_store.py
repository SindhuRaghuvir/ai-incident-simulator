import sqlite3
import os
from datetime import datetime

import pandas as pd

import config


def _get_connection():
    os.makedirs(os.path.dirname(config.METRICS_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(config.METRICS_DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            query TEXT NOT NULL,
            model TEXT NOT NULL,
            temperature REAL,
            top_k INTEGER,
            input_tokens INTEGER DEFAULT 0,
            output_tokens INTEGER DEFAULT 0,
            retrieval_ms INTEGER DEFAULT 0,
            generation_ms INTEGER DEFAULT 0,
            total_ms INTEGER DEFAULT 0,
            success INTEGER DEFAULT 1,
            failure_mode TEXT DEFAULT '',
            error_message TEXT DEFAULT '',
            estimated_cost REAL DEFAULT 0.0
        )
    """)
    conn.commit()
    return conn


def log_request(
    query: str,
    model: str,
    temperature: float = 0.3,
    top_k: int = 3,
    input_tokens: int = 0,
    output_tokens: int = 0,
    retrieval_ms: int = 0,
    generation_ms: int = 0,
    total_ms: int = 0,
    success: bool = True,
    failure_mode: str = "",
    error_message: str = "",
    estimated_cost: float = 0.0,
):
    conn = _get_connection()
    conn.execute(
        """INSERT INTO requests
           (timestamp, query, model, temperature, top_k, input_tokens, output_tokens,
            retrieval_ms, generation_ms, total_ms, success, failure_mode, error_message, estimated_cost)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            datetime.utcnow().isoformat(),
            query,
            model,
            temperature,
            top_k,
            input_tokens,
            output_tokens,
            retrieval_ms,
            generation_ms,
            total_ms,
            1 if success else 0,
            failure_mode,
            error_message,
            estimated_cost,
        ),
    )
    conn.commit()
    conn.close()


def get_metrics() -> pd.DataFrame:
    conn = _get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM requests ORDER BY id DESC", conn
    )
    conn.close()
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["success"] = df["success"].astype(bool)
    return df


def get_summary() -> dict:
    df = get_metrics()
    if df.empty:
        return {
            "total_requests": 0,
            "success_rate": 0.0,
            "avg_latency_ms": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
        }
    return {
        "total_requests": len(df),
        "success_rate": df["success"].mean() * 100,
        "avg_latency_ms": int(df["total_ms"].mean()),
        "total_tokens": int(df["input_tokens"].sum() + df["output_tokens"].sum()),
        "total_cost": float(df["estimated_cost"].sum()),
    }
