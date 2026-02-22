"""
SQLite database setup and helpers.
"""
import sqlite3
import os
from config import DB_PATH


def get_conn() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    """Create tables if they don't exist."""
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS features (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name    TEXT    NOT NULL,
            category        TEXT    NOT NULL,   -- 'ai' or 'non-ai'
            feature_name    TEXT    NOT NULL,
            description     TEXT    NOT NULL,
            release_date    TEXT,               -- ISO-8601 date string
            source_url      TEXT,
            source_type     TEXT,               -- 'blog', 'appstore', 'twitter'
            scraped_at      TEXT    NOT NULL DEFAULT (datetime('now')),
            embedding_id    INTEGER             -- FK into embeddings table
        );

        CREATE TABLE IF NOT EXISTS embeddings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            feature_id  INTEGER UNIQUE REFERENCES features(id) ON DELETE CASCADE,
            vector      BLOB    NOT NULL        -- pickled numpy float32 array
        );

        CREATE TABLE IF NOT EXISTS scrape_log (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            run_at      TEXT    NOT NULL DEFAULT (datetime('now')),
            product     TEXT,
            source_type TEXT,
            status      TEXT,                  -- 'ok' | 'error'
            message     TEXT,
            items_added INTEGER DEFAULT 0
        );

        CREATE INDEX IF NOT EXISTS idx_features_product  ON features(product_name);
        CREATE INDEX IF NOT EXISTS idx_features_category ON features(category);
        CREATE INDEX IF NOT EXISTS idx_features_date     ON features(release_date DESC);
    """)
    conn.commit()
    conn.close()
    print(f"[db] Initialized at {DB_PATH}")


def insert_feature(product_name, category, feature_name, description,
                   release_date, source_url, source_type) -> int | None:
    """
    Insert a feature row; skip duplicates (same product + feature_name + release_date).
    Returns the new row id or None if it was a duplicate.
    """
    conn = get_conn()
    try:
        existing = conn.execute(
            "SELECT id FROM features WHERE product_name=? AND feature_name=? AND release_date=?",
            (product_name, feature_name, release_date)
        ).fetchone()
        if existing:
            return None

        cur = conn.execute(
            """INSERT INTO features
               (product_name, category, feature_name, description,
                release_date, source_url, source_type)
               VALUES (?,?,?,?,?,?,?)""",
            (product_name, category, feature_name, description,
             release_date, source_url, source_type)
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def log_scrape(product, source_type, status, message="", items_added=0):
    conn = get_conn()
    conn.execute(
        """INSERT INTO scrape_log (product, source_type, status, message, items_added)
           VALUES (?,?,?,?,?)""",
        (product, source_type, status, message, items_added)
    )
    conn.commit()
    conn.close()
