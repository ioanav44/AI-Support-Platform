"""
Sentiment Service — Lightweight lexicon-based sentiment scoring using VADER.

Provides a score from -1.0 (very negative) to +1.0 (very positive).
"""
import logging
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logger = logging.getLogger(__name__)

_analyzer = SentimentIntensityAnalyzer()


def compute_sentiment(text: str) -> float:
    """
    Compute compound sentiment score for a text.
    Returns float in range [-1.0, 1.0].
    """
    scores = _analyzer.polarity_scores(text)
    return round(scores["compound"], 4)


def classify_sentiment(score: float) -> str:
    """Classify a sentiment score into a human-readable label."""
    if score >= 0.3:
        return "positive"
    elif score <= -0.3:
        return "negative"
    else:
        return "neutral"
