import random

import discord

import db
from analysis import score_message


def analyze_message(message: discord.Message):
    """score a message and save the score"""
    guild_id, user_id = message.guild.id, message.author.id
    score = score_message(message.content)
    db.save_score(guild_id, user_id, score)


def get_reputation(guild_id: int, user_id: int) -> float:
    """Star rating from 1 to 5, in steps of 0.5."""
    return round(db.get_user_stats(guild_id, user_id).rating * 2) / 2


# TODO: calculate from the user's message scores instead of returning random values
def get_reputation_change(guild_id: int, user_id: int, months: int) -> int:
    """How much the user's reputation score changed over the last `months` months."""
    return random.randint(-50, 50)
