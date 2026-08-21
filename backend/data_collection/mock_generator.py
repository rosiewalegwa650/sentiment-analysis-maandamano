"""
Mock data generator — generates realistic Kenyan social media posts across English, Swahili, and Sheng.
"""
import random
from datetime import datetime, timedelta, timezone

KENYAN_LOCATIONS = [
    "Nairobi CBD", "Kibra", "Mathare", "Eastleigh", "Westlands", "Kasarani",
    "Githurai", "Kondele (Kisumu)", "Mombasa Island", "Eldoret Town", "Nakuru CBD", "Kitengela"
]

SAMPLE_POSTS = [
    ("english", "positive", "Good to see young people organizing peacefully today in {loc}, this is how democracy works."),
    ("english", "negative", "Police fired tear gas near {loc}, several peaceful youth injured. Unacceptable police violence."),
    ("english", "neutral", "Maandamano scheduled to pass through {loc} this afternoon according to civic group notices."),
    ("swahili", "negative", "Hali ni mbaya sana karibu na {loc}, wananchi wanakimbia teargas ya polisi na Zakayo hasikii."),
    ("swahili", "neutral", "Maandamano ya amani yataanza saa nne asubuhi kutoka {loc} kuelekea majengo ya bunge."),
    ("swahili", "positive", "Hongera kwa vijana wa {loc} kwa kuandamana kwa amani na kutetea haki za Wakenya."),
    ("sheng", "negative", "Story ni ngori kabisa huko {loc}, mbogi imeshtuka juu ya teargas na hali ni noma wantam!"),
    ("sheng", "positive", "Vibe ni poa sana leo {loc}, ma-youth wameungana fiti bila noma yoyote freshi kabisa."),
    ("sheng", "neutral", "Form ya leo ni gani hapa {loc}? Tuko kwa ground ku-check kama ma-gen z wako active."),
    ("english", "negative", "High cost of living protests turning tense near {loc}, multiple arrests and tear gas reported."),
    ("english", "positive", "Great turnout at {loc} today! Organizers made sure the demonstration was peaceful and clean."),
]

PLATFORMS = ["X / Twitter", "Reddit", "Facebook", "TikTok"]


def generate_mock_posts(count: int = 50) -> list[dict]:
    """Generates realistic sample posts across languages, locations, and time."""
    posts = []
    now = datetime.now(timezone.utc)

    for i in range(count):
        lang, sentiment_hint, template = random.choice(SAMPLE_POSTS)
        location = random.choice(KENYAN_LOCATIONS)
        content = template.format(loc=location)
        posts.append({
            "external_id": f"mock-{i}-{random.randint(1000,9999)}",
            "content": content,
            "language_hint": lang,
            "sentiment_hint": sentiment_hint,
            "timestamp": now - timedelta(hours=random.randint(0, 72)),
            "platform": random.choice(PLATFORMS),
            "location": location,
            "likes": random.randint(5, 1200),
            "shares": random.randint(2, 450),
            "comments": random.randint(1, 320),
        })
    return posts
