import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "database" / "techscan.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_conn()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            nickname TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS job_postings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            title TEXT,
            company TEXT,
            raw_text TEXT,
            crawled_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS tech_mentions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            posting_id INTEGER REFERENCES job_postings(id),
            tech_name TEXT NOT NULL,
            category TEXT
        );

        CREATE TABLE IF NOT EXISTS cert_mentions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            posting_id INTEGER REFERENCES job_postings(id),
            cert_name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS community_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            view_count INTEGER DEFAULT 0,
            like_count INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER REFERENCES community_posts(id),
            user_id INTEGER REFERENCES users(id),
            content TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );
    """)

    conn.commit()
    conn.close()
