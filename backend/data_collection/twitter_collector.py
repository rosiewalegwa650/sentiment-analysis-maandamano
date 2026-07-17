"""X recent-search API v2 collector."""
from datetime import datetime
import requests

SEARCH_URL = "https://api.x.com/2/tweets/search/recent"


def collect_twitter_posts(limit: int = 50) -> list[dict]:
    from flask import current_app
    token = current_app.config["TWITTER_BEARER_TOKEN"]
    if not token:
        raise RuntimeError("Set TWITTER_BEARER_TOKEN in .env before collecting from X.")
    keywords = current_app.config["PROTEST_KEYWORDS"]
    query = f"({' OR '.join(keywords)}) (lang:en OR lang:sw) -is:retweet"
    response = requests.get(SEARCH_URL, headers={"Authorization": f"Bearer {token}"}, params={
        "query": query, "max_results": min(max(limit, 10), 100),
        "tweet.fields": "created_at,public_metrics,geo",
    }, timeout=20)
    response.raise_for_status()
    posts = []
    for tweet in response.json().get("data", []):
        metrics = tweet.get("public_metrics", {})
        posts.append({
            "external_id": f"x-{tweet['id']}", "content": tweet["text"],
            "timestamp": datetime.fromisoformat(tweet["created_at"].replace("Z", "+00:00")),
            "platform": "x", "location": None, "likes": metrics.get("like_count", 0),
            "shares": metrics.get("retweet_count", 0), "comments": metrics.get("reply_count", 0),
        })
    return posts
