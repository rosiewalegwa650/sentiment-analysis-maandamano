"""Sentiment classification with a resilient baseline for local demos.

The transformer is loaded only when a post is classified, keeping health and
dashboard routes available on machines that have not installed ML packages.
"""
POSITIVE = {"good", "great", "peaceful", "poa", "fiti", "sawa", "fresh", "vibe", "hope"}
NEGATIVE = {"tear gas", "injured", "arrest", "violence", "killed", "police", "mbaya", "noma", "wantam", "imeshtuka"}


def _lexicon_classify(text):
    lower = text.lower()
    pos = sum(term in lower for term in POSITIVE)
    neg = sum(term in lower for term in NEGATIVE)
    if neg > pos:
        return {"sentiment_type": "negative", "confidence_score": 0.6}
    if pos > neg:
        return {"sentiment_type": "positive", "confidence_score": 0.6}
    return {"sentiment_type": "neutral", "confidence_score": 0.5}


def classify_sentiment(cleaned_text: str, language: str = "unknown") -> dict:
    if not cleaned_text or not cleaned_text.strip():
        return {"sentiment_type": "neutral", "confidence_score": 0.0}
    try:
        from ..sentiment_model import classify_sentiment as transformer_classify
        return transformer_classify(cleaned_text, language)
    except (ImportError, OSError, RuntimeError):
        # OSError includes an unavailable locally cached Hugging Face model.
        return _lexicon_classify(cleaned_text)
