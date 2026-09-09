"""Automatic exact-term detection. No customer/product-name list is embedded.

Rules recognise technical formats and likely names from spelling or context.
They are intentionally transparent; ambiguous names can still be missed.
"""
import re

PATTERNS = [
    # Longer structured spans win over tokens inside them.
    ("link", r"https?://[^\s<>\"']+|www\.[^\s<>\"']+"),
    ("email", r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"),
    ("identifier", r"\b[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}\b"),
    ("version", r"\bv?\d+(?:\.\d+){1,3}(?:[-+][A-Za-z0-9.]+)?\b"),
    ("error / identifier", r"\b(?=[A-Za-z0-9_-]*[A-Za-z])(?=[A-Za-z0-9_-]*\d)[A-Za-z][A-Za-z0-9]*(?:[-_][A-Za-z0-9]+)*\b"),
    ("technical identifier", r"\b[A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+\b"),
    ("reference number", r"(?<!\w)\#\d+\b"),
    ("likely product name", r"\b[a-zA-Z][a-zA-Z0-9]*[a-z][A-Z][a-zA-Z0-9]*\b"),
    ("technical acronym", r"\b[A-Z]{2,8}\b"),
]

# Common prose must not be frozen just because someone types it in capitals.
PROSE = set("I A AN THE MY YOUR OUR THEIR THIS THAT IT IS ARE WAS WERE NOT NO YES PLEASE HELP URGENT NOW ASAP LOGIN LOG IN OUT ERROR FAILED ACCOUNT PASSWORD RESET CANNOT CANT WHY HOW WHAT WHEN WHERE THANKS THANK YOU AND OR BUT FOR TO OF ON AT WITH FROM APP APPLICATION PRODUCT PLATFORM SERVICE VERSION CODE ID MON MA MES LE LA LES UN UNE SVP MI MIS EL LOS LAS POR FAVOR AYUDA".split())
TITLE_WORD = r"[A-ZÀ-ÖØ-Þ][a-zà-öø-ÿA-Z0-9]*(?:[-][A-ZÀ-ÖØ-Þa-zà-öø-ÿ0-9]+)*"
NAME = rf"{TITLE_WORD}(?:[ \t]+{TITLE_WORD}){{0,2}}"
CUES = r"account|app|application|platform|product|software|service|compte|application|logiciel|cuenta|aplicación|plataforma|ऐप|खाता|செயலி|கணக்கு"


def detect_items(text):
    candidates = []
    for category, pattern in PATTERNS:
        for match in re.finditer(pattern, text):
            value = match.group(0)
            if category == "link":
                value = value.rstrip(".,!?;:)]}")
            if value.upper() in PROSE or value.startswith("ZXQTERM"):
                continue
            candidates.append((match.start(), match.start() + len(value), category))

    # For example: "Acme account", "Microsoft Teams app", "compte Acme".
    # Case-insensitive cues but case-sensitive name matching avoid freezing prose.
    for pattern in [rf"(?P<name>{NAME})\s+(?i:{CUES})\b",
                    rf"(?i:\b(?:{CUES}))\s+(?P<name>{NAME})\b",
                    rf"(?i:\b(?:using|with|via|sur|avec|con))\s+(?P<name>{NAME})\b",
                    rf"(?P<name>{NAME})\s+(?i:is down|is not working|keeps crashing|won't open|does not work|ne fonctionne pas|no funciona)\b"]:
        for match in re.finditer(pattern, text):
            name = match.group("name")
            # Trim leading pronouns caught by title-case matching: "My Acme".
            parts = name.split()
            while parts and parts[0].upper() in PROSE:
                parts.pop(0)
            while parts and parts[-1].upper() in PROSE:
                parts.pop()
            if parts:
                value = " ".join(parts)
                offset = name.find(value)
                if offset >= 0:
                    start = match.start("name") + offset
                    candidates.append((start, start + len(value), "likely product name"))

    # Explicit product-label contexts also support lowercase and non-Latin names.
    for match in re.finditer(
        rf"(?i:\b(?:{CUES}))\s*[:=]?\s*[\"“‘'](?P<name>[^\"”’'\n]{{1,60}})[\"”’']", text
    ):
        candidates.append((*match.span("name"), "labelled product name"))

    # Numeric codes immediately following a technical label, e.g. "error 403".
    for match in re.finditer(
        r"(?i:\b(?:error|code|ticket|order|invoice|erreur|código|pedido|facture))\s*(?:id\s*)?[:#-]?\s*(?P<id>\d{2,20})\b", text
    ):
        candidates.append((*match.span("id"), "reference number"))

    # Select longest non-overlapping spans; preserve source order in the UI.
    accepted = []
    for start, end, category in sorted(candidates, key=lambda item: (-(item[1]-item[0]), item[0])):
        if not any(start < e and end > s for s, e, _ in accepted):
            accepted.append((start, end, category))
    seen = set()
    items = []
    for start, end, category in sorted(accepted):
        term = text[start:end]
        if term not in seen:
            items.append({"text": term, "category": category})
            seen.add(term)
    return items
