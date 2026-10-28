import sqlite3
from datetime import datetime

DB_FILE = "guardrail.db"

def init_db():
    """Creates the analytics logging table if it doesn't already exist."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            original_length INTEGER NOT NULL,
            clean_length INTEGER NOT NULL,
            leaks_blocked_count INTEGER NOT NULL,
            leak_types TEXT
        )
    """)
    conn.commit()
    conn.close()

def log_transaction(original_text: str, clean_text: str, vault: dict):
    """Saves safety statistics about the prompt into the database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    leak_types = "None"
    if vault:
        leak_types = "PII Detected"

    cursor.execute("""
        INSERT INTO audit_logs (timestamp, original_length, clean_length, leaks_blocked_count, leak_types)
        VALUES (?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        len(original_text),
        len(clean_text),
        len(vault.keys()),
        leak_types
    ))
    conn.commit()
    conn.close()

def get_dashboard_metrics():
    """Retrieves aggregated metrics to feed into our frontend charts."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Calculate totals securely
    cursor.execute("SELECT COUNT(*), SUM(leaks_blocked_count) FROM audit_logs")
    total_requests, total_leaks_blocked = cursor.fetchone()
    
    # Get last 10 entries for history timeline charting
    cursor.execute("SELECT timestamp, leaks_blocked_count FROM audit_logs ORDER BY id DESC LIMIT 10")
    raw_history = cursor.fetchall()
    conn.close()
    
    # Clean Formatting: Output straight structural fields to match JS assumptions
    history = []
    for row in raw_history:
        history.append({
            "timestamp": row[0],
            "leaks": row[1] if row[1] is not None else 0
        })
    
    return {
        "total_requests": total_requests or 0,
        "total_leaks_blocked": total_leaks_blocked or 0,
        "history": list(reversed(history))
    }