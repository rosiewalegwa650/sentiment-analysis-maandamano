"""Reddit collector using Reddit's documented OAuth API via PRAW."""
from datetime import datetime, timezone


def collect_reddit_posts(limit: int = 50) -> list[dict]:
    try:
        import praw
    except ImportError as exc:
        raise RuntimeError("Install dependencies from backend/requirements.txt to use Reddit collection.") from exc

    from flask import current_app
    client_id = current_app.config["REDDIT_CLIENT_ID"]
    client_secret = current_app.config["REDDIT_CLIENT_SECRET"]
    if not client_id or not client_secret:
        raise RuntimeError("Set REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET in .env before collecting from Reddit.")

    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret,
                         user_agent=current_app.config["REDDIT_USER_AGENT"])
    query = " OR ".join(current_app.config["PROTEST_KEYWORDS"])
    posts = []
    for submission in reddit.subreddit("all").search(query, sort="new", time_filter="week", limit=limit):
        posts.append({
            "external_id": f"reddit-{submission.id}",
            "content": f"{submission.title}\n{submission.selftext}".strip(),
            "timestamp": datetime.fromtimestamp(submission.created_utc, tz=timezone.utc),
            "platform": "reddit",
            "location": None,
            "likes": int(submission.score or 0),
            "shares": 0,
            "comments": int(submission.num_comments or 0),
        })
    return posts
