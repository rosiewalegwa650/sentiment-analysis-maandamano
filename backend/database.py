from flask_sqlalchemy import SQLAlchemy

# Single shared SQLAlchemy instance, imported by models.py and __init__.py
# (kept in its own file to avoid circular imports)
db = SQLAlchemy()
