"""
Sentiment classification engine with multilingual transformer + Sheng/Swahili lexicon fine-tuning.
"""
from functools import lru_cache

MODEL_NAME = "cardiffnlp/twitter-xlm-roberta-base-sentiment"

# Sheng & Swahili sentiment lexicons
POSITIVE_LEXICON = {
    "good", "great", "peaceful", "poa", "fiti", "sawa", "fresh", "freshi", "vibe", "hope",
    "hongera", "amani", "uhuru", "haki", "mwananchi", "baraka", "shukrani", "pamoja"
}
NEGATIVE_LEXICON = {
    "tear gas", "teargas", "injured", "arrest", "arrests", "violence", "killed", "police",
    "mbaya", "noma", "wantam", "imeshtuka", "ngori", "brutality", "zakayo", "shut down",
    "curfew", "imeharibika", "rip", "risasi"
}

LABEL_MAP = {
    "positive": "positive",
    "negative": "negative",
    "neutral": "neutral",
    "LABEL_0": "negative",
    "LABEL_1": "neutral",
    "LABEL_2": "positive",
}


@lru_cache(maxsize=1)
def _get_pipeline():
    from transformers import pipeline
    return pipeline("sentiment-analysis", model=MODEL_NAME, tokenizer=MODEL_NAME)


def _lexicon_classify(text: str) -> dict:
    lower = text.lower()
    pos = sum(1 for term in POSITIVE_LEXICON if term in lower)
    neg = sum(1 for term in NEGATIVE_LEXICON if term in lower)
    if neg > pos:
        return {"sentiment_type": "negative", "confidence_score": 0.75}
    if pos > neg:
        return {"sentiment_type": "positive", "confidence_score": 0.75}
    return {"sentiment_type": "neutral", "confidence_score": 0.5}


def classify_sentiment(cleaned_text: str, language: str = "unknown") -> dict:
    """Returns {'sentiment_type': ..., 'confidence_score': ...}."""
    if not cleaned_text or not cleaned_text.strip():
        return {"sentiment_type": "neutral", "confidence_score": 0.0}

    # First attempt transformer classification
    try:
        clf = _get_pipeline()
        result = clf(cleaned_text[:512])[0]
        label = LABEL_MAP.get(result["label"], "neutral")
        confidence = float(result["score"])

        # Post-process for Sheng / Swahili nuance
        if language in {"sheng", "swahili"}:
            label, confidence = _apply_lexicon_adjustment(cleaned_text, label, confidence)

        return {"sentiment_type": label, "confidence_score": round(confidence, 4)}
    except Exception:
        # Fallback to rules-based lexicon classifier if offline or transformer fails
        return _lexicon_classify(cleaned_text)


def _apply_lexicon_adjustment(text: str, base_label: str, base_confidence: float):
    lower = text.lower()
    pos_hits = sum(1 for term in POSITIVE_LEXICON if term in lower)
    neg_hits = sum(1 for term in NEGATIVE_LEXICON if term in lower)

    if pos_hits > neg_hits:
        return "positive", max(base_confidence, 0.7)
    if neg_hits > pos_hits:
        return "negative", max(base_confidence, 0.7)
    return base_label, base_confidence
