import re

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# naive word-based sentiment for the prototype, doesn't understand context (sarcasm, quotes, slang like "sick")
_analyzer = SentimentIntensityAnalyzer()


def score_message(text: str) -> float:
    """sentiment from -1 (very negative) to 1 (very positive)"""
    return _analyzer.polarity_scores(text)["compound"]


def negative_words(text: str) -> list[str]:
    """words in `text` that VADER's lexicon rates as negative"""
    words = dict.fromkeys(re.findall(r"[\w']+", text.lower()))
    return [word for word in words if _analyzer.lexicon.get(word, 0) < 0]
