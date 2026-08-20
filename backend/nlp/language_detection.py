"""Lightweight language identification for English, Swahili, and Sheng.

Mixed social-media posts are common, so Sheng is checked first; it is a
practical code-switching label rather than a claim that a whole post is Sheng.
"""
import re

SHENG_MARKERS = {
    "mbogi", "buda", "noma", "poa", "fiti", "siwezi", "ameshtuka", "wantam", "msee",
    "vibe", "sasa", "chapaa", "zakayo", "form", "maze", "morio", "manze", "rieng",
    "kejani", "ngori", "otile", "orezo", "luku", "dobi"
}
SWAHILI_MARKERS = {
    "na", "kwa", "watu", "hii", "hiyo", "maandamano", "serikali", "polisi", "karibu",
    "kutoka", "kuelekea", "saa", "hali", "ni", "wananchi", "mwananchi", "haki",
    "bunge", "vijana", "amani", "uhuru", "harambee"
}
ENGLISH_MARKERS = {
    "the", "and", "protest", "police", "people", "today", "with", "from", "this",
    "that", "are", "is", "finance", "bill", "government", "rights", "peaceful"
}


def detect_language(text: str) -> str:
    tokens = set(re.findall(r"[a-zA-Z']+", (text or "").lower()))
    if not tokens:
        return "unknown"
    sheng = len(tokens & SHENG_MARKERS)
    swahili = len(tokens & SWAHILI_MARKERS)
    english = len(tokens & ENGLISH_MARKERS)
    if sheng:
        return "sheng"
    if swahili > english and swahili:
        return "swahili"
    if english:
        return "english"
    return "unknown"
