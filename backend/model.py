from datetime import datetime, timezone
from .database import db


def utcnow():
    return datetime.now(timezone.utc)


class User(db.Model):
    """Table 1: Users (proposal 4.5.2)"""
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(30), default="researcher")  # administrator | researcher | decision_maker
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)


class SocialMediaPost(db.Model):
    """Table 2: Social_Media_Posts (proposal 4.5.2)"""
    __tablename__ = "social_media_posts"

    post_id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(120), index=True)  # ID on the source platform
    content = db.Column(db.Text, nullable=False)
    cleaned_content = db.Column(db.Text)
    language = db.Column(db.String(20))  # english | swahili | sheng | unknown
    timestamp = db.Column(db.DateTime, default=utcnow)
    platform = db.Column(db.String(50))  # reddit | twitter | mock | forum
    location = db.Column(db.String(100))
    likes = db.Column(db.Integer, default=0)
    shares = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)

    sentiment_result = db.relationship(
        "SentimentResult", backref="post", uselist=False, cascade="all, delete-orphan"
    )


class SentimentResult(db.Model):
    """Table 3: Sentiment_Results (proposal 4.5.2)"""
    __tablename__ = "sentiment_results"

    sentiment_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("social_media_posts.post_id"), nullable=False)
    sentiment_type = db.Column(db.String(20))  # positive | negative | neutral
    confidence_score = db.Column(db.Float)
    analyzed_at = db.Column(db.DateTime, default=utcnow)


class EscalationAlert(db.Model):
    """Table 4: Escalation_Alerts (proposal 4.5.2)"""
    __tablename__ = "escalation_alerts"

    alert_id = db.Column(db.Integer, primary_key=True)
    alert_level = db.Column(db.String(20))  # Low | Medium | High | Critical
    score = db.Column(db.Float)
    location = db.Column(db.String(100))
    generated_time = db.Column(db.DateTime, default=utcnow)
