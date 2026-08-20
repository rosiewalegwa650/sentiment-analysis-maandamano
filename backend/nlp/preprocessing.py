"""
Text preprocessing utilities for social media content.
"""
import re

STOPWORDS = {
    # English
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could",
    "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from", "further", "had", "has", "have",
    "having", "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is",
    "it", "its", "itself", "just", "me", "more", "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on",
    "once", "only", "or", "other", "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should", "so",
    "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then", "there", "these", "they",
    "this", "those", "through", "to", "too", "under", "until", "up", "very", "was", "we", "were", "what", "when",
    "where", "which", "while", "who", "whom", "why", "with", "you", "your", "yours", "yourself", "yourselves",
    # Swahili common stopwords
    "na", "ya", "wa", "kwa", "katika", "ni", "za", "la", "kua", "hata", "pia", "au", "kama", "cha", "kufanya", "yoyote"
}

def clean_text(text: str) -> str:
    """Cleans raw social media post text by stripping URLs, user handles, and extra spaces."""
    if not text:
        return ""
    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", "", text)
    # Remove user mentions
    text = re.sub(r"@\w+", "", text)
    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text

def tokenize(text: str) -> list[str]:
    """Tokenizes text into word tokens."""
    if not text:
        return []
    return re.findall(r"\b\w+\b", text.lower())

def remove_stopwords(tokens: list[str]) -> list[str]:
    """Removes standard stopwords from tokens list."""
    return [t for t in tokens if t.lower() not in STOPWORDS]

def deduplicate(posts: list[dict]) -> list[dict]:
    """Deduplicates a list of post dictionaries based on post content."""
    seen = set()
    unique_posts = []
    for post in posts:
        content = post.get("content", "").strip().lower()
        if content and content not in seen:
            seen.add(content)
            unique_posts.append(post)
    return unique_posts
