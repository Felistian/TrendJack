# database/db.py
import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))), "trendjack.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    """Create tables if they don't exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword         TEXT NOT NULL,
            trend_title     TEXT,
            trend_url       TEXT,
            total_attempts  INTEGER,
            final_passed    BOOLEAN,
            human_decision  TEXT,
            human_notes     TEXT,
            created_at      TEXT,
            decided_at      TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attempts (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            campaign_id     INTEGER,
            attempt_number  INTEGER,
            instagram_copy  TEXT,
            tiktok_copy     TEXT,
            linkedin_copy   TEXT,
            tone_score      REAL,
            brand_fit_score REAL,
            accuracy_score  REAL,
            trend_relevance REAL,
            overall_score   REAL,
            passed          BOOLEAN,
            feedback        TEXT,
            FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialized ✓")


def save_campaign(pipeline_result: dict) -> int:
    """
    Save pipeline result to DB.
    Returns the campaign_id.
    """
    conn = get_connection()
    cursor = conn.cursor()

    trend = pipeline_result.get("trend", {})

    cursor.execute("""
        INSERT INTO campaigns 
        (keyword, trend_title, trend_url, total_attempts, 
         final_passed, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        pipeline_result.get("keyword"),
        trend.get("title"),
        trend.get("url"),
        pipeline_result.get("total_attempts"),
        pipeline_result.get("final_passed"),
        datetime.now().isoformat()
    ))

    campaign_id = cursor.lastrowid

    for attempt in pipeline_result.get("attempts", []):
        ad   = attempt.get("ad_copy", {})
        val  = attempt.get("validation", {})

        cursor.execute("""
            INSERT INTO attempts
            (campaign_id, attempt_number, instagram_copy, tiktok_copy,
             linkedin_copy, tone_score, brand_fit_score, accuracy_score,
             trend_relevance, overall_score, passed, feedback)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            campaign_id,
            attempt.get("attempt_number"),
            ad.get("instagram"),
            ad.get("tiktok"),
            ad.get("linkedin"),
            val.get("tone_score"),
            val.get("brand_fit_score"),
            val.get("accuracy_score"),
            val.get("trend_relevance"),
            val.get("overall_score"),
            val.get("passed"),
            val.get("feedback")
        ))

    conn.commit()
    conn.close()
    return campaign_id


def update_human_decision(campaign_id: int, decision: str, notes: str = ""):
    """Save human Approve/Reject decision."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE campaigns
        SET human_decision = ?,
            human_notes    = ?,
            decided_at     = ?
        WHERE id = ?
    """, (decision, notes, datetime.now().isoformat(), campaign_id))

    conn.commit()
    conn.close()


def get_all_campaigns() -> list:
    """Fetch all campaigns for history view."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM campaigns ORDER BY created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    init_db()
    print("DB path:", DB_PATH)