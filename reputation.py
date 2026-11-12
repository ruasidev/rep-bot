import random

import discord

import config
import db
from analysis import negative_words, score_message


def message_stars(score: float) -> float:
    """1 to 5 stars for a single message. neutral and positive messages count as 5"""
    return config.MAX_STARS + (config.MAX_STARS - 1) * min(score, 0)


def analyze_message(message: discord.Message):
    """score a message, move the author's rating toward it, and flag it if it's very negative"""
    guild_id, user_id = message.guild.id, message.author.id
    score = score_message(message.content)
    db.save_score(guild_id, user_id, score)

    rating = db.get_user_stats(guild_id, user_id).rating
    rating += config.RATING_SMOOTHING * (message_stars(score) - rating)
    db.update_rating(guild_id, user_id, min(max(rating, 1), config.MAX_STARS))

    if score <= config.FLAG_THRESHOLD:
        words = negative_words(message.content)
        db.save_flagged_message(
            guild_id,
            user_id,
            message.channel.id,
            message.id,
            message.content,
            score,
            "negative words: " + ", ".join(words) if words else None,
            message.created_at,
        )


def get_reputation(guild_id: int, user_id: int) -> float:
    """Star rating from 1 to 5, in steps of 0.5."""
    return round(db.get_user_stats(guild_id, user_id).rating * 2) / 2


# TODO: calculate from the user's message scores instead of returning random values
def get_reputation_change(guild_id: int, user_id: int, months: int) -> int:
    """How much the user's reputation score changed over the last `months` months."""
    return random.randint(-50, 50)
