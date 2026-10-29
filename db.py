import sqlite3
from datetime import UTC, datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "rep.db"
DEFAULT_RATING = 5.0

SCHEMA = f"""
CREATE TABLE IF NOT EXISTS users (
    guild_id          INTEGER NOT NULL,
    user_id           INTEGER NOT NULL,
    rating            REAL NOT NULL DEFAULT {DEFAULT_RATING} CHECK (rating BETWEEN 1 AND 5),
    messages_analyzed INTEGER NOT NULL DEFAULT 0,
    updated_at        TEXT NOT NULL,
    PRIMARY KEY (guild_id, user_id)
);

-- one row per scored message, no content; used for the rating and its trend
CREATE TABLE IF NOT EXISTS message_scores (
    id        INTEGER PRIMARY KEY,
    guild_id  INTEGER NOT NULL,
    user_id   INTEGER NOT NULL,
    score     REAL NOT NULL,
    scored_at TEXT NOT NULL,
    FOREIGN KEY (guild_id, user_id) REFERENCES users (guild_id, user_id) ON DELETE CASCADE
);

-- low-scoring messages only
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

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys = ON")


def init_db():
    conn.executescript(SCHEMA)


def _timestamp(dt: datetime | None = None) -> str:
    """Times are stored as UTC ISO 8601 strings so they compare correctly as text."""
    return (dt or datetime.now(UTC)).astimezone(UTC).isoformat(timespec="seconds")


def get_user(guild_id: int, user_id: int) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM users WHERE guild_id = ? AND user_id = ?", (guild_id, user_id)
    ).fetchone()


def set_rating(guild_id: int, user_id: int, rating: float):
    with conn:
        conn.execute(
            "INSERT INTO users (guild_id, user_id, rating, updated_at) VALUES (?, ?, ?, ?) "
            "ON CONFLICT (guild_id, user_id) DO UPDATE SET rating = excluded.rating, updated_at = excluded.updated_at",
            (guild_id, user_id, rating, _timestamp()),
        )


def add_message_score(guild_id: int, user_id: int, score: float, scored_at: datetime | None = None):
    """Record a scored message and bump the user's messages_analyzed count."""
    with conn:
        conn.execute(
            "INSERT INTO users (guild_id, user_id, messages_analyzed, updated_at) VALUES (?, ?, 1, ?) "
            "ON CONFLICT (guild_id, user_id) DO UPDATE SET "
            "messages_analyzed = messages_analyzed + 1, updated_at = excluded.updated_at",
            (guild_id, user_id, _timestamp()),
        )
        conn.execute(
            "INSERT INTO message_scores (guild_id, user_id, score, scored_at) VALUES (?, ?, ?, ?)",
            (guild_id, user_id, score, _timestamp(scored_at)),
        )


def get_scores_since(guild_id: int, user_id: int, since: datetime) -> list[float]:
    rows = conn.execute(
        "SELECT score FROM message_scores WHERE guild_id = ? AND user_id = ? AND scored_at >= ? ORDER BY scored_at",
        (guild_id, user_id, _timestamp(since)),
    )
    return [row["score"] for row in rows]


def add_flagged_message(
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
            "INSERT OR IGNORE INTO users (guild_id, user_id, updated_at) VALUES (?, ?, ?)",
            (guild_id, user_id, _timestamp()),
        )
        conn.execute(
            "INSERT INTO flagged_messages (guild_id, user_id, channel_id, message_id, content, score, reason, sent_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (guild_id, user_id, channel_id, message_id, content, score, reason, _timestamp(sent_at)),
        )


def get_flagged_messages(guild_id: int, user_id: int) -> list[sqlite3.Row]:
    """Flags a moderator hasn't removed, newest first."""
    return conn.execute(
        "SELECT * FROM flagged_messages WHERE guild_id = ? AND user_id = ? AND removed = 0 ORDER BY sent_at DESC",
        (guild_id, user_id),
    ).fetchall()
