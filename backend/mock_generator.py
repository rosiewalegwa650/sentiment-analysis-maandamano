"""
Mock data generator — lets the whole pipeline run end-to-end with zero API
keys, so you can demo the system and test the ML/dashboard layers today.
Swap this out for real collectors (reddit_collector, twitter_collector) once
you have credentials.
"""
import random
from datetime import datetime, timedelta, timezone

NAIROBI_LOCATIONS = ["CBD", "Kibra", "Mathare", "Eastleigh", "Westlands", "Kasarani"]

SAMPLE_POSTS = [
    ("english", "positive", "Good to see young people organizing peacefully today in {loc}, this is how change happens."),
    ("english", "negative", "Police fired tear gas near {loc}, several people injured. This is getting out of hand."),
    ("english", "neutral", "Maandamano scheduled to pass through {loc} this afternoon according to organizers."),
    ("swahili", "negative", "Hali ni mbaya karibu na {loc}, watu wanakimbia kutoka kwa polisi."),
    ("swahili", "neutral", "Maandamano yataanza saa nne asubuhi kutoka {loc} kuelekea mjini."),
    ("sheng", "negative", "Story mbaya kabisa huko {loc}, mbogi imeshtuka na hali ni noma."),
    ("sheng", "positive", "Vibe ni poa leo {loc}, watu wameungana fiti hakuna noma."),
    ("english", "negative", "Cost of living protests turning violent near {loc}, arrests reported."),
    ("english", "positive", "Great turnout at {loc} today, organizers say the demo was peaceful and orderly."),
]

PLATFORMS = ["reddit", "mock_forum", "mock_twitter"]


def generate_mock_posts(count: int = 50) -> list[dict]:
    """Generates realistic sample posts across languages, locations, and time."""
    posts = []
    now = datetime.now(timezone.utc)

    for i in range(count):
        lang, sentiment_hint, template = random.choice(SAMPLE_POSTS)
        location = random.choice(NAIROBI_LOCATIONS)
        content = template.format(loc=location)
        posts.append({
            "external_id": f"mock-{i}-{random.randint(1000,9999)}",
            "content": content,
            "language_hint": lang,          # for validating the language detector
            "sentiment_hint": sentiment_hint,  # for validating the classifier
            "timestamp": now - timedelta(hours=random.randint(0, 72)),
            "platform": random.choice(PLATFORMS),
            "location": location,
            "likes": random.randint(0, 500),
            "shares": random.randint(0, 200),
            "comments": random.randint(0, 150),
        })
    return posts
