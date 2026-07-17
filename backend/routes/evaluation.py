"""Evaluation endpoint for a manually labelled held-out test set."""
from collections import defaultdict
from flask import Blueprint, jsonify, request
from ..nlp.language_detection import detect_language
from ..nlp.preprocessing import clean_text
from ..nlp.sentiment_model import classify_sentiment

evaluation_bp = Blueprint("evaluation", __name__)
LABELS = ("positive", "negative", "neutral")


@evaluation_bp.post("/evaluate")
def evaluate():
    """Evaluate labelled examples: [{"text": "...", "label": "negative"}]."""
    examples = request.get_json(silent=True) or []
    if not isinstance(examples, list) or not examples:
        return jsonify({"error": "Send a non-empty JSON list of {text, label} examples."}), 400
    if any(item.get("label") not in LABELS or not item.get("text") for item in examples):
        return jsonify({"error": "Each example needs text and a label: positive, negative, or neutral."}), 400

    matrix = {actual: {predicted: 0 for predicted in LABELS} for actual in LABELS}
    language_results = defaultdict(lambda: [0, 0])
    for item in examples:
        language = detect_language(item["text"])
        predicted = classify_sentiment(clean_text(item["text"]), language)["sentiment_type"]
        matrix[item["label"]][predicted] += 1
        language_results[language][0] += predicted == item["label"]
        language_results[language][1] += 1

    per_label = {}
    for label in LABELS:
        tp = matrix[label][label]
        fp = sum(matrix[actual][label] for actual in LABELS if actual != label)
        fn = sum(matrix[label][predicted] for predicted in LABELS if predicted != label)
        precision = tp / (tp + fp) if tp + fp else 0
        recall = tp / (tp + fn) if tp + fn else 0
        per_label[label] = {"precision": round(precision, 3), "recall": round(recall, 3), "f1": round(2 * precision * recall / (precision + recall), 3) if precision + recall else 0}
    accuracy = sum(matrix[label][label] for label in LABELS) / len(examples)
    return jsonify({
        "samples": len(examples), "accuracy": round(accuracy, 3), "per_class": per_label,
        "macro_f1": round(sum(item["f1"] for item in per_label.values()) / len(LABELS), 3),
        "confusion_matrix": matrix,
        "accuracy_by_language": {key: round(value[0] / value[1], 3) for key, value in language_results.items()},
    })
