import sqlite3
from datetime import date

DB_NAME = "tracker.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS activities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        active INTEGER DEFAULT 1
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS daily_time (
        activity_id INTEGER,
        day TEXT,
        seconds INTEGER,
        PRIMARY KEY (activity_id, day)
    )
    """)

    conn.commit()
    conn.close()


# -------- ACTIVIDADES -------- #

def add_activity(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO activities (name, active) VALUES (?, 1)",
        (name,)
    )
    conn.commit()
    conn.close()

def get_activities(active_only=True):
    conn = get_connection()
    cur = conn.cursor()

    if active_only:
        cur.execute(
            "SELECT id, name FROM activities WHERE active = 1"
        )
    else:
        cur.execute(
            "SELECT id, name, active FROM activities"
        )

    data = cur.fetchall()
    conn.close()
    return data

def hide_activity(activity_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE activities SET active = 0 WHERE id = ?",
        (activity_id,)
    )
    conn.commit()
    conn.close()

def show_activity(activity_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE activities SET active = 1 WHERE id = ?",
        (activity_id,)
    )
    conn.commit()
    conn.close()

# -------- TIEMPO -------- #

def add_time(activity_id, seconds):
    today = date.today().isoformat()
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO daily_time (activity_id, day, seconds)
    VALUES (?, ?, ?)
    ON CONFLICT(activity_id, day)
    DO UPDATE SET seconds = seconds + ?
    """, (activity_id, today, seconds, seconds))

    conn.commit()
    conn.close()

def get_today_times():
    today = date.today().isoformat()
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT a.name, d.seconds
    FROM daily_time d
    JOIN activities a ON a.id = d.activity_id
    WHERE d.day = ? AND a.active = 1
    """, (today,))

    data = cur.fetchall()
    conn.close()
    return data
