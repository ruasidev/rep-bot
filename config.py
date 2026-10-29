import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
TESTING = bool(os.getenv("TESTING"))
DB_PATH = Path(os.getenv("DB_PATH") or Path(__file__).parent / "rep.db").expanduser()

DEFAULT_RATING = 5.0
MAX_STARS = 5
REP_CHANGE_MONTHS = 3

FLAG_THRESHOLD = -0.5  # messages scoring at or below this get flagged for moderators
RATING_SMOOTHING = 0.05  # how far each message moves the rating toward that message's stars
