"""Pattern matching only: this is not an entailment or legal accuracy model."""
import re

PATTERNS = [
    r"(?:\$|USD\s*|INR\s*|EUR\s*|£|Rs\.?\s*)\s?\d[\d,]*(?:\.\d+)?",
    r"\b\d+(?:\.\d+)?%",
    r"\b\d+\s+(?:hours?|days?|months?|years?)\b",
    r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
    r"\b(?:\d{1,2}\s+)?(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)(?:\s+\d{1,2},?)?\s+\d{4}\b",
    r"\b[A-Z][A-Za-z]*(?:\s+[A-Z][A-Za-z]*)+\b",
]


def extract_facts(text):
    return sorted({m.group().strip() for pattern in PATTERNS
                   for m in re.finditer(pattern, text)})


def normalize(text):
    return re.sub(r"\s+", " ", text).strip().casefold()


def present(fact, text):
    # Boundaries prevent $50 from matching $500 or Party A from matching Party AB.
    return re.search(r"(?<!\w)" + re.escape(normalize(fact)) + r"(?!\w|[,.]\d)", normalize(text)) is not None


def fact_report(source, summary):
    facts = extract_facts(summary)
    matched = [fact for fact in facts if present(fact, source)]
    unsupported = [fact for fact in facts if not present(fact, source)]
    missing = [fact for fact in extract_facts(source) if not present(fact, summary)]
    return {
        "match_precision": len(matched) / len(facts) if facts else None,
        "matched": matched,
        "not_found_in_source": unsupported,
        "source_items_not_in_summary": missing,
        "note": "Text matches only. Missing items may be intentional; role reversals, negation and paraphrases require review.",
    }
