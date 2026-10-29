import random


# TODO: calculate from the user's chat history instead of returning random values
def get_reputation(user_id: int) -> float:
    """Star rating from 1 to 5, in steps of 0.5."""
    return round(random.uniform(1, 5) * 2) / 2


def get_reputation_change(user_id: int, months: int) -> int:
    """How much the user's reputation score changed over the last `months` months."""
    return random.randint(-50, 50)
