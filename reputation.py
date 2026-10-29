import random

import db


def get_reputation(guild_id: int, user_id: int) -> float:
    """Star rating from 1 to 5, in steps of 0.5."""
    user = db.get_user(guild_id, user_id)
    rating = user["rating"] if user else db.DEFAULT_RATING
    return round(rating * 2) / 2


# TODO: calculate from db.get_scores_since() instead of returning random values
def get_reputation_change(guild_id: int, user_id: int, months: int) -> int:
    """How much the user's reputation score changed over the last `months` months."""
    return random.randint(-50, 50)
