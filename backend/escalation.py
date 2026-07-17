"""
Escalation Detection Model — proposal section 3.7.

Escalation Score = (Negative Sentiment Weight) + (Keyword Risk Weight)
                  + (Activity Growth Weight)

Each weight is scaled to contribute up to ~33 points, so the total score
lands in the 0-100 range described in the proposal's alert level table.
"""
from .config import Config


def negative_sentiment_weight(posts: list[dict]) -> float:
    """% of posts classified negative, scaled to 0-40."""
    if not posts:
        return 0.0
    negative = sum(1 for p in posts if p["sentiment_type"] == "negative")
    pct = negative / len(posts)
    return round(pct * 40, 2)


def keyword_risk_weight(posts: list[dict]) -> float:
    """Frequency of risk keywords across posts, scaled to 0-30."""
    if not posts:
        return 0.0
    hits = 0
    for p in posts:
        text = p["content"].lower()
        hits += sum(1 for kw in Config.RISK_KEYWORDS if kw in text)
    # Normalize: assume >= 1 risk keyword per 3 posts is already "high risk"
    density = hits / max(len(posts) / 3, 1)
    return round(min(density, 1.0) * 30, 2)


def activity_growth_weight(counts_by_period: list[int]) -> float:
    """Rate of increase in posting volume, scaled to 0-30.
    counts_by_period: post counts for consecutive time windows, oldest first.
    """
    if len(counts_by_period) < 2 or counts_by_period[-2] == 0:
        return 0.0
    growth = (counts_by_period[-1] - counts_by_period[-2]) / counts_by_period[-2]
    return round(min(max(growth, 0), 1.0) * 30, 2)


def escalation_level(score: float) -> str:
    if score <= Config.ESCALATION_LOW_MAX:
        return "Low"
    if score <= Config.ESCALATION_MEDIUM_MAX:
        return "Medium"
    if score <= Config.ESCALATION_HIGH_MAX:
        return "High"
    return "Critical"


def compute_escalation(posts: list[dict], counts_by_period: list[int]) -> dict:
    score = (
        negative_sentiment_weight(posts)
        + keyword_risk_weight(posts)
        + activity_growth_weight(counts_by_period)
    )
    score = round(min(score, 100), 2)
    return {"score": score, "alert_level": escalation_level(score)}
