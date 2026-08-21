import pytest
from backend import create_app
from backend.database import db
from backend.models import SocialMediaPost, SentimentResult
from backend.nlp.language_detection import detect_language
from backend.nlp.sentiment_model import classify_sentiment
from backend.nlp.escalation import compute_escalation


@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json == {"status": "ok"}


def test_collect_mock_endpoint(client):
    response = client.post("/api/collect", json={"source": "mock", "count": 20})
    assert response.status_code == 200
    data = response.json
    assert data["source"] == "mock"
    assert data["stored"] > 0


def test_dashboard_endpoints_after_collection(client):
    client.post("/api/collect", json={"source": "mock", "count": 20})

    # Summary
    res_summary = client.get("/api/dashboard/summary")
    assert res_summary.status_code == 200
    assert res_summary.json["total_posts"] > 0

    # Trends
    res_trends = client.get("/api/dashboard/trends")
    assert res_trends.status_code == 200
    assert isinstance(res_trends.json, list)

    # Geographic
    res_geo = client.get("/api/dashboard/geographic")
    assert res_geo.status_code == 200
    assert isinstance(res_geo.json, list)

    # Escalation
    res_esc = client.get("/api/dashboard/escalation")
    assert res_esc.status_code == 200
    assert "score" in res_esc.json
    assert "alert_level" in res_esc.json

    # Keywords
    res_kw = client.get("/api/dashboard/keywords")
    assert res_kw.status_code == 200
    assert isinstance(res_kw.json, list)

    # Posts
    res_posts = client.get("/api/posts")
    assert res_posts.status_code == 200
    assert len(res_posts.json) > 0


def test_language_detection():
    assert detect_language("Story ni ngori kabisa, mbogi imeshtuka!") == "sheng"
    assert detect_language("Wananchi wana haki ya kuandamana kwa amani.") == "swahili"
    assert detect_language("The protesters gathered peacefully near the city hall.") == "english"


def test_sentiment_classification():
    neg_res = classify_sentiment("Police fired teargas and injured several peaceful protesters.", "english")
    assert neg_res["sentiment_type"] == "negative"

    pos_res = classify_sentiment("Vibe ni poa sana ma-youth wameungana fiti kabisa.", "sheng")
    assert pos_res["sentiment_type"] == "positive"


def test_escalation_logic():
    posts = [
        {"content": "Police teargas and live bullets reported near CBD", "sentiment_type": "negative"},
        {"content": "Multiple arrests and violence near town", "sentiment_type": "negative"},
    ]
    res = compute_escalation(posts, [10, 30])
    assert res["score"] > 0
    assert res["alert_level"] in ["Low", "Medium", "High", "Critical"]
