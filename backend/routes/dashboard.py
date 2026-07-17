"""
Dashboard endpoints — backs proposal section 4.6 (Dashboard Design).
Each function maps to one dashboard component from that section.
"""
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify
from sqlalchemy import func

from ..database import db
from ..models import SocialMediaPost, SentimentResult, EscalationAlert
from ..nlp.escalation import compute_escalation

dashboard_bp = Blueprint("dashboard", __name__)


def _joined_query():
    return db.session.query(SocialMediaPost, SentimentResult).join(
        SentimentResult, SocialMediaPost.post_id == SentimentResult.post_id
    )


@dashboard_bp.route("/dashboard/summary", methods=["GET"])
def summary():
    """4.6.1 Sentiment Summary Panel."""
    rows = _joined_query().all()
    total = len(rows)
    if total == 0:
        return jsonify({"total_posts": 0, "positive_pct": 0, "negative_pct": 0, "neutral_pct": 0})

    counts = defaultdict(int)
    for _, sr in rows:
        counts[sr.sentiment_type] += 1

    return jsonify({
        "total_posts": total,
        "positive_pct": round(counts["positive"] / total * 100, 1),
        "negative_pct": round(counts["negative"] / total * 100, 1),
        "neutral_pct": round(counts["neutral"] / total * 100, 1),
    })


@dashboard_bp.route("/dashboard/trends", methods=["GET"])
def trends():
    """4.6.2 Sentiment Trend Graph — daily % breakdown."""
    rows = _joined_query().all()
    by_day = defaultdict(lambda: defaultdict(int))

    for post, sr in rows:
        day = post.timestamp.strftime("%Y-%m-%d") if post.timestamp else "unknown"
        by_day[day][sr.sentiment_type] += 1

    trend_data = []
    for day in sorted(by_day.keys()):
        counts = by_day[day]
        total = sum(counts.values())
        trend_data.append({
            "date": day,
            "positive": round(counts["positive"] / total * 100, 1) if total else 0,
            "neutral": round(counts["neutral"] / total * 100, 1) if total else 0,
            "negative": round(counts["negative"] / total * 100, 1) if total else 0,
        })
    return jsonify(trend_data)


@dashboard_bp.route("/dashboard/geographic", methods=["GET"])
def geographic():
    """4.6.3 Geographic Sentiment Map."""
    rows = _joined_query().all()
    by_location = defaultdict(lambda: defaultdict(int))

    for post, sr in rows:
        loc = post.location or "Unknown"
        by_location[loc][sr.sentiment_type] += 1

    result = []
    for loc, counts in by_location.items():
        total = sum(counts.values())
        result.append({
            "location": loc,
            "total_posts": total,
            "negative_pct": round(counts["negative"] / total * 100, 1) if total else 0,
        })
    return jsonify(sorted(result, key=lambda x: -x["negative_pct"]))


@dashboard_bp.route("/dashboard/escalation", methods=["GET"])
def escalation():
    """4.6.4 Escalation Alert Panel using two comparable 24-hour windows."""
    rows = _joined_query().all()
    posts_data = [{"content": p.content, "sentiment_type": sr.sentiment_type} for p, sr in rows]

    now = datetime.now(timezone.utc)
    def as_utc(value):
        return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)

    recent_cutoff = now - timedelta(hours=24)
    prior_cutoff = now - timedelta(hours=48)
    window_recent = [p for p, _ in rows if p.timestamp and as_utc(p.timestamp) >= recent_cutoff]
    window_prior = [p for p, _ in rows if p.timestamp and prior_cutoff <= as_utc(p.timestamp) < recent_cutoff]
    recent_ids = {p.post_id for p in window_recent}
    recent_data = [
        {"content": p.content, "sentiment_type": sr.sentiment_type}
        for p, sr in rows if p.post_id in recent_ids
    ]
    result = compute_escalation(recent_data, [len(window_prior), len(window_recent)])
    result.update({"recent_posts": len(window_recent), "prior_posts": len(window_prior)})

    # Persist meaningful alerts; dashboard refreshes should not fill the table.
    if result["alert_level"] in {"High", "Critical"}:
        last = EscalationAlert.query.order_by(EscalationAlert.generated_time.desc()).first()
        if not last or last.alert_level != result["alert_level"] or abs(last.score - result["score"]) >= 5:
            db.session.add(EscalationAlert(alert_level=result["alert_level"], score=result["score"], location="All locations"))
            db.session.commit()

    return jsonify(result)


@dashboard_bp.route("/dashboard/keywords", methods=["GET"])
def keywords():
    """4.6.5 Keyword Analysis Section — simple frequency count."""
    from ..nlp.preprocessing import tokenize, remove_stopwords

    rows = SocialMediaPost.query.all()
    freq = defaultdict(int)
    for post in rows:
        for tok in remove_stopwords(tokenize(post.cleaned_content or post.content)):
            if len(tok) > 3:  # skip short/noise tokens
                freq[tok] += 1

    top = sorted(freq.items(), key=lambda x: -x[1])[:15]
    return jsonify([{"keyword": k, "count": v} for k, v in top])


@dashboard_bp.route("/posts", methods=["GET"])
def list_posts():
    """Raw post + sentiment feed, for a posts table view."""
    rows = _joined_query().order_by(SocialMediaPost.timestamp.desc()).limit(100).all()
    return jsonify([
        {
            "post_id": p.post_id,
            "content": p.content,
            "language": p.language,
            "platform": p.platform,
            "location": p.location,
            "timestamp": p.timestamp.isoformat() if p.timestamp else None,
            "sentiment_type": sr.sentiment_type,
            "confidence_score": sr.confidence_score,
        }
        for p, sr in rows
    ])


@dashboard_bp.route("/posts", methods=["DELETE"])
def clear_posts():
    """Clear locally collected records so a fresh demo or collection can be run."""
    SentimentResult.query.delete()
    SocialMediaPost.query.delete()
    EscalationAlert.query.delete()
    db.session.commit()
    return jsonify({"message": "Dashboard data cleared."})
