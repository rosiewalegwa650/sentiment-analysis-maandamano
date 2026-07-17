"""
Sentiment classification engine — proposal section 3.6.

Model choice: cardiffnlp/twitter-xlm-roberta-base-sentiment
  - A multilingual XLM-RoBERTa fine-tuned on tweets for sentiment.
  - Covers English natively and transfers reasonably to Swahili thanks to
    XLM-R's cross-lingual pretraining (100+ languages), even without direct
    Swahili fine-tuning.
  - Sheng has NO dedicated sentiment model anywhere (this is a genuine open
    research gap, matching your Ch. 2.6/2.7 literature review). We correct
    for this with a small lexicon-based adjustment layer on top of the
    model's raw output, rather than pretending the transformer alone
    handles it perfectly.

This mirrors the "Feature Extraction -> ML Algorithm" flow in 3.6.1/3.6.2:
the transformer supplies contextual features + a base prediction, and the
lexicon layer is the lightweight rule-based correction your literature
review (2.6) says this domain still needs.
"""
from functools import lru_cache
from transformers import pipeline

MODEL_NAME = "cardiffnlp/twitter-xlm-roberta-base-sentiment"

# Seed Sheng sentiment lexicon — extend as you annotate more data (Ch 1.6.2
# names this as a known limitation; growing this file is the fix).
SHENG_POSITIVE = {"poa", "fiti", "noma poa", "sawa", "freshi"}
SHENG_NEGATIVE = {"noma", "mbaya", "buda ameshtuka", "wantam", "story mbaya", "imeharibika"}


@lru_cache(maxsize=1)
def _get_pipeline():
    # Cached so the model loads once per process, not once per request.
    return pipeline("sentiment-analysis", model=MODEL_NAME, tokenizer=MODEL_NAME)


LABEL_MAP = {
    "positive": "positive",
    "negative": "negative",
    "neutral": "neutral",
    # some model versions return LABEL_0/1/2
    "LABEL_0": "negative",
    "LABEL_1": "neutral",
    "LABEL_2": "positive",
}


def classify_sentiment(cleaned_text: str, language: str = "unknown") -> dict:
    """Returns {'sentiment_type': ..., 'confidence_score': ...}."""
    if not cleaned_text.strip():
        return {"sentiment_type": "neutral", "confidence_score": 0.0}

    clf = _get_pipeline()
    result = clf(cleaned_text[:512])[0]  # truncate to model's max length
    label = LABEL_MAP.get(result["label"], "neutral")
    confidence = float(result["score"])

    if language == "sheng":
        label, confidence = _apply_sheng_adjustment(cleaned_text, label, confidence)

    return {"sentiment_type": label, "confidence_score": round(confidence, 4)}


def _apply_sheng_adjustment(text: str, base_label: str, base_confidence: float):
    lower = text.lower()
    pos_hits = sum(1 for term in SHENG_POSITIVE if term in lower)
    neg_hits = sum(1 for term in SHENG_NEGATIVE if term in lower)

    if pos_hits > neg_hits:
        return "positive", max(base_confidence, 0.6)
    if neg_hits > pos_hits:
        return "negative", max(base_confidence, 0.6)
    return base_label, base_confidence
