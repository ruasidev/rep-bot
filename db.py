import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
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


def get_user_stats(guild_id: int, user_id: int) -> UserStats:
    """rating and number of messages analyzed"""
    user = conn.execute(
        "SELECT rating, messages_analyzed FROM users WHERE guild_id = ? AND user_id = ?",
        (guild_id, user_id),
    ).fetchone()
    if user is None:
        return UserStats(config.DEFAULT_RATING, 0)
    return UserStats(user["rating"], user["messages_analyzed"])
