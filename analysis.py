from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# naive word-based sentiment for the prototype, doesn't understand context (sarcasm, quotes, slang like "sick")
_analyzer = SentimentIntensityAnalyzer()


def score_message(text: str) -> float:
    """sentiment from -1 (very negative) to 1 (very positive)"""
    return _analyzer.polarity_scores(text)["compound"]
