from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app
app = Flask(__name__)

# Configure database (adjust URI to your setup)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sentiment.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Import and register blueprints
from routes.dashboard import dashboard_bp
app.register_blueprint(dashboard_bp)

@app.route("/")
def home():
    return {"message": "Backend is running!"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)
