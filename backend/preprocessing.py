"""
Text cleaning pipeline — proposal section 3.5 (Data Preprocessing).
Removes URLs, emojis, special characters, excess whitespace.
"""
import re

URL_PATTERN = re.compile(r"https?://\S+|www\.\S+")
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002700-\U000027BF"
    "]+",
    flags=re.UNICODE,
)
MENTION_PATTERN = re.compile(r"@\w+")
HASHTAG_PATTERN = re.compile(r"#(\w+)")
SPECIAL_CHARS_PATTERN = re.compile(r"[^a-zA-Z0-9\s.,!?'\-]")
WHITESPACE_PATTERN = re.compile(r"\s+")


def clean_text(raw_text: str, keep_hashtags: bool = False) -> str:
    """Clean a single social media post. Order matters: URLs/emojis first,
    then special chars, then whitespace collapse."""
    if not raw_text:
        return ""

    text = raw_text.strip()
    text = URL_PATTERN.sub(" ", text)
    text = EMOJI_PATTERN.sub(" ", text)

    text = MENTION_PATTERN.sub(" ", text)
    # Keep a topic word such as #Maandamano while removing the # symbol.
    if not keep_hashtags:
        text = HASHTAG_PATTERN.sub(r" \1 ", text)

    text = SPECIAL_CHARS_PATTERN.sub(" ", text)
    text = WHITESPACE_PATTERN.sub(" ", text).strip()
    return text


def deduplicate(posts: list[str]) -> list[str]:
    """Remove duplicate entries, preserving order (proposal 3.5.1)."""
    seen = set()
    unique = []
    for p in posts:
        key = p.strip().lower()
        if key and key not in seen:
            seen.add(key)
            unique.append(p)
    return unique


def tokenize(text: str) -> list[str]:
    """Simple whitespace/punctuation tokenizer (proposal 3.5.2)."""
    return re.findall(r"[A-Za-z']+", text.lower())


# Minimal stopword sets for English + common Swahili/Sheng function words
# (proposal 3.5.3). Not exhaustive — extend as your dataset grows.
STOPWORDS_EN = {"the", "and", "is", "are", "a", "an", "in", "on", "of", "to", "it", "for"}
STOPWORDS_SW = {"na", "ya", "wa", "kwa", "ni", "za", "la", "kuwa", "hii", "hiyo"}


def remove_stopwords(tokens: list[str]) -> list[str]:
    stop = STOPWORDS_EN | STOPWORDS_SW
    return [t for t in tokens if t not in stop]
