import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path

import config

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    guild_id          INTEGER NOT NULL,
    user_id           INTEGER NOT NULL,
    rating            REAL NOT NULL CHECK (rating BETWEEN 1 AND 5),
    messages_analyzed INTEGER NOT NULL DEFAULT 0,
    updated_at        TEXT NOT NULL,
    PRIMARY KEY (guild_id, user_id)
);

CREATE TABLE IF NOT EXISTS message_scores (
    id        INTEGER PRIMARY KEY,
    guild_id  INTEGER NOT NULL,
    user_id   INTEGER NOT NULL,
    score     REAL NOT NULL,
    scored_at TEXT NOT NULL,
    FOREIGN KEY (guild_id, user_id) REFERENCES users (guild_id, user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS flagged_messages (
    id         INTEGER PRIMARY KEY,
    guild_id   INTEGER NOT NULL,
    user_id    INTEGER NOT NULL,
    channel_id INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    content    TEXT NOT NULL,
    score      REAL NOT NULL,
    reason     TEXT,
    sent_at    TEXT NOT NULL,
    removed    INTEGER NOT NULL DEFAULT 0,  -- set by moderators to undo a flag without deleting it
    FOREIGN KEY (guild_id, user_id) REFERENCES users (guild_id, user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS message_scores_user ON message_scores (guild_id, user_id, scored_at);
CREATE INDEX IF NOT EXISTS flagged_messages_user ON flagged_messages (guild_id, user_id);
"""

conn: sqlite3.Connection | None = None


@dataclass
class UserStats:
    rating: float
    messages_analyzed: int
    recent_scores: list[float]  # oldest first


def init_db() -> Path:
    """open the db at config.DB_PATH and create missing tables"""
    global conn
    config.DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return config.DB_PATH


def _timestamp(dt: datetime | None = None) -> str:
    """times are stored as UTC ISO 8601 strings"""
    return (dt or datetime.now(UTC)).astimezone(UTC).isoformat(timespec="seconds")


def save_score(guild_id: int, user_id: int, score: float):
    """record a scored message and increment the user's messages_analyzed count"""
    now = _timestamp()
    with conn:
        conn.execute(
            "INSERT INTO users (guild_id, user_id, rating, messages_analyzed, updated_at) VALUES (?, ?, ?, 1, ?) "
            "ON CONFLICT (guild_id, user_id) DO UPDATE SET "
            "messages_analyzed = messages_analyzed + 1, updated_at = excluded.updated_at",
            (guild_id, user_id, config.DEFAULT_RATING, now),
        )
        conn.execute(
            "INSERT INTO message_scores (guild_id, user_id, score, scored_at) VALUES (?, ?, ?, ?)",
            (guild_id, user_id, score, now),
        )


def save_flagged_message(
    guild_id: int,
    user_id: int,
    channel_id: int,
    message_id: int,
    content: str,
    score: float,
    reason: str | None,
    sent_at: datetime,
):
    with conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (guild_id, user_id, rating, updated_at) VALUES (?, ?, ?, ?)",
            (guild_id, user_id, config.DEFAULT_RATING, _timestamp()),
        )
        conn.execute(
            "INSERT INTO flagged_messages (guild_id, user_id, channel_id, message_id, content, score, reason, sent_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (guild_id, user_id, channel_id, message_id, content, score, reason, _timestamp(sent_at)),
        )


def get_user_stats(guild_id: int, user_id: int, months: int = config.REP_CHANGE_MONTHS) -> UserStats:
    """rating, messages analyzed, and scores from the last `months` months for the trend"""
    user = conn.execute(
        "SELECT rating, messages_analyzed FROM users WHERE guild_id = ? AND user_id = ?",
        (guild_id, user_id),
    ).fetchone()
    if user is None:
        return UserStats(config.DEFAULT_RATING, 0, [])

    since = datetime.now(UTC) - timedelta(days=30 * months)
    rows = conn.execute(
        "SELECT score FROM message_scores WHERE guild_id = ? AND user_id = ? AND scored_at >= ? "
        "ORDER BY scored_at, id",
        (guild_id, user_id, _timestamp(since)),
    )
    return UserStats(user["rating"], user["messages_analyzed"], [row["score"] for row in rows])


def update_rating(guild_id: int, user_id: int, rating: float):
    with conn:
        conn.execute(
            "INSERT INTO users (guild_id, user_id, rating, updated_at) VALUES (?, ?, ?, ?) "
            "ON CONFLICT (guild_id, user_id) DO UPDATE SET rating = excluded.rating, updated_at = excluded.updated_at",
            (guild_id, user_id, rating, _timestamp()),
        )


def get_flagged_messages(guild_id: int, user_id: int) -> list[sqlite3.Row]:
    """flags a moderator hasn't removed"""
    return conn.execute(
        "SELECT * FROM flagged_messages WHERE guild_id = ? AND user_id = ? AND removed = 0 ORDER BY sent_at DESC",
        (guild_id, user_id),
    ).fetchall()
