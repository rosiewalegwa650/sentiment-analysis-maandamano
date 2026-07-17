"""
POST /api/collect — runs the full pipeline once:
  collect -> clean -> detect language -> classify sentiment -> store

This is the "System Architecture Flow" from proposal 3.3, expressed as one
endpoint call. In production you'd trigger this on a schedule (cron / Celery
beat) rather than by hand.
"""
from flask import Blueprint, jsonify, request, current_app

from ..database import db
from ..models import SocialMediaPost, SentimentResult
from ..nlp.preprocessing import clean_text, deduplicate
from ..nlp.language_detection import detect_language
from ..nlp.sentiment_model import classify_sentiment
from ..data_collection.mock_generator import generate_mock_posts

collect_bp = Blueprint("collect", __name__)


@collect_bp.route("/collect", methods=["POST"])
def collect():
    source = request.json.get("source", "mock") if request.is_json else "mock"
    count = int(request.json.get("count", 50)) if request.is_json else 50

    if source == "mock":
        raw_posts = generate_mock_posts(count)
    elif source == "reddit":
        from ..data_collection.reddit_collector import collect_reddit_posts
        raw_posts = collect_reddit_posts(count)
    elif source == "twitter":
        from ..data_collection.twitter_collector import collect_twitter_posts
        raw_posts = collect_twitter_posts(count)
    else:
        return jsonify({"error": f"unknown source '{source}'"}), 400

    # Deduplicate on raw content before hitting the DB/model (proposal 3.5.1)
    # Keep the first occurrence only.  Comparing against a set of unique values
    # would accidentally retain every duplicate.
    unique_contents = set()
    raw_posts = [
        p for p in raw_posts
        if not (p["content"].strip().lower() in unique_contents or unique_contents.add(p["content"].strip().lower()))
    ]

    stored = 0
    for raw in raw_posts:
        external_id = raw.get("external_id")
        existing = SocialMediaPost.query.filter_by(external_id=external_id).first() if external_id else None
        if existing:
            continue  # already collected

        cleaned = clean_text(raw["content"])
        language = detect_language(raw["content"])

        post = SocialMediaPost(
            external_id=external_id,
            content=raw["content"],
            cleaned_content=cleaned,
            language=language,
            timestamp=raw.get("timestamp"),
            platform=raw.get("platform"),
            location=raw.get("location"),
            likes=raw.get("likes", 0),
            shares=raw.get("shares", 0),
            comments=raw.get("comments", 0),
        )
        db.session.add(post)
        db.session.flush()  # get post.post_id before commit

        sentiment = classify_sentiment(cleaned, language)
        result = SentimentResult(
            post_id=post.post_id,
            sentiment_type=sentiment["sentiment_type"],
            confidence_score=sentiment["confidence_score"],
        )
        db.session.add(result)
        stored += 1

    db.session.commit()
    return jsonify({"collected": len(raw_posts), "stored": stored, "source": source})
