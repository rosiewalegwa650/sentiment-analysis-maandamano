import os

try:
    from dotenv import load_dotenv
except ImportError:

    def load_dotenv():
        return False

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///sentiment.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "maandamano-sentiment-bot/0.1")

    TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN", "")

    ESCALATION_LOW_MAX = int(os.getenv("ESCALATION_LOW_MAX", 30))
    ESCALATION_MEDIUM_MAX = int(os.getenv("ESCALATION_MEDIUM_MAX", 60))
    ESCALATION_HIGH_MAX = int(os.getenv("ESCALATION_HIGH_MAX", 80))

    # Keywords used for data collection and escalation risk weighting
    PROTEST_KEYWORDS = [
        "maandamano", "protest", "demonstration", "nairobi", "finance bill",
        "cost of living", "serikali", "ruto", "wantam", "gen z", "zakayo",
        "bunge", "mwananchi", "vijana", "githurai", "kondele", "mombasa"
    ]
    RISK_KEYWORDS = [
        "tear gas", "teargas", "gunshot", "arrest", "curfew", "blocked", "shutdown",
        "violence", "killed", "injured", "police brutality", "risasi", "ngori",
        "imeharibika", "water cannon", "live bullets"
    ]
