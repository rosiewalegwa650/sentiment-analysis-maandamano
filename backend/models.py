"""Database entities for raw posts, predictions, and escalation alerts."""
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from .database import db


def utcnow():
    return datetime.now(timezone.utc)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50), default="analyst")
    token = db.Column(db.String(100), unique=True, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class SocialMediaPost(db.Model):
    __tablename__ = "social_media_posts"
    post_id = db.Column(db.Integer, primary_key=True)
    external_id = db.Column(db.String(120), index=True, unique=True)
    content = db.Column(db.Text, nullable=False)
    cleaned_content = db.Column(db.Text)
    language = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime(timezone=True), default=utcnow, index=True)
    platform = db.Column(db.String(50), index=True)
    location = db.Column(db.String(100), index=True)
    likes = db.Column(db.Integer, default=0)
    shares = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    sentiment_result = db.relationship("SentimentResult", backref="post", uselist=False,
                                       cascade="all, delete-orphan")


class SentimentResult(db.Model):
    __tablename__ = "sentiment_results"
    sentiment_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("social_media_posts.post_id"), nullable=False, unique=True)
    sentiment_type = db.Column(db.String(20), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    model_version = db.Column(db.String(100), default="xlm-roberta-baseline")
    analyzed_at = db.Column(db.DateTime(timezone=True), default=utcnow)


class EscalationAlert(db.Model):
    __tablename__ = "escalation_alerts"
    alert_id = db.Column(db.Integer, primary_key=True)
    alert_level = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(100), default="All locations")
    generated_time = db.Column(db.DateTime(timezone=True), default=utcnow)
