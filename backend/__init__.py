"""Application factory for the protest-sentiment API."""
from flask import Flask
from flask_cors import CORS

from .config import Config
from .database import db


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    CORS(app)

    from . import models  # noqa: F401 - registers SQLAlchemy models
    from .routes import register_routes
    register_routes(app)

    with app.app_context():
        db.create_all()
        # Seed default analyst account if no users exist
        from .models import User
        if not User.query.filter_by(username="analyst").first():
            default_analyst = User(
                username="analyst",
                email="analyst@maandamanopulse.co.ke",
                role="Senior Analyst"
            )
            default_analyst.set_password("password123")
            db.session.add(default_analyst)
            db.session.commit()

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app
