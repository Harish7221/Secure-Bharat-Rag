import sqlite3
import json

DB_PATH = "threads.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 🧵 Thread storage
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS threads (
        thread_id TEXT,
        user_id TEXT,
        summary TEXT,
        messages TEXT,
        PRIMARY KEY (thread_id, user_id)
    )
    """)

    # 🧠 Structured Long-Term Memory
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_memory (
        user_id TEXT,
        key TEXT,
        value TEXT,
        PRIMARY KEY (user_id, key)
    )
    """)

    conn.commit()
    conn.close()


# =========================
# Thread Functions
# =========================

def load_thread(thread_id, user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT summary, messages FROM threads
    WHERE thread_id = ? AND user_id = ?
    """, (thread_id, user_id))

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "summary": row[0] or "",
            "messages": json.loads(row[1]) if row[1] else []
        }

    return {"summary": "", "messages": []}


def save_thread(thread_id, user_id, summary, messages):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT OR REPLACE INTO threads (thread_id, user_id, summary, messages)
    VALUES (?, ?, ?, ?)
    """, (thread_id, user_id, summary, json.dumps(messages)))

    conn.commit()
    conn.close()


# =========================
# Structured Memory Functions
# =========================

def save_memory(user_id, key, value):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO user_memory (user_id, key, value)
    VALUES (?, ?, ?)
    ON CONFLICT(user_id, key)
    DO UPDATE SET value = excluded.value
    """, (user_id, key, value))

    conn.commit()
    conn.close()


def load_all_memory(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT key, value FROM user_memory
    WHERE user_id = ?
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return {key: value for key, value in rows}
