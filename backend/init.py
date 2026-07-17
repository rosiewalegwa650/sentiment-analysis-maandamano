from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

from .config import Config
from .database import db

migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)  # allow the React dev server (localhost:5173) to call this API

    from . import models  # noqa: F401  (ensures models are registered before create_all)
    from .routes import register_routes
    register_routes(app)

    @app.route("/api/health")
    def health():
        return {"status": "ok"}

    return app
