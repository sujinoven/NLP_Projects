import re
import torch
from typing import Dict, List, Any
from app.config import settings

try:
    from transformers import pipeline
except ImportError:
    pipeline = None

class NERModelManager:
    _instance = None
    _pipeline = None

    @classmethod
    def get_pipeline(cls):
        if cls._pipeline is None:
            if pipeline is None:
                raise ImportError("transformers pipeline is not installed.")
            device = 0 if torch.cuda.is_available() else -1
            print(f"Loading NER pipeline '{settings.NER_MODEL}' on device {device}...")
            cls._pipeline = pipeline(
                "ner",
                model=settings.NER_MODEL,
                aggregation_strategy="simple",
                device=device
            )
            print("NER pipeline loaded successfully.")
        return cls._pipeline

    @classmethod
    def is_loaded(cls) -> bool:
        return cls._pipeline is not None

def header_text(text: str, n_lines: int = 40) -> str:
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return "\n".join(lines[:n_lines])[:1500]

def extract_contact(text: str) -> Dict[str, str]:
    """
    Regex-based extraction for email, phone, LinkedIn, and GitHub.
    Preserves original text format for accuracy.
    """
    email = re.findall(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}", text)

    phone = []
    for cand in re.findall(r"(?:\+?\d{1,3}[\s\-]?)?(?:\(?\d{2,5}\)?[\s\-]?)?\d{3,5}[\s\-]?\d{4,6}", text):
        digits = re.sub(r"\D", "", cand)
        if 10 <= len(digits) <= 13:
            phone.append(cand.strip())

    linkedin = re.findall(r"linkedin\.com/in/[A-Za-z0-9\-_%]+", text, flags=re.I)
    github = re.findall(r"github\.com/[A-Za-z0-9\-_]+", text, flags=re.I)

    return {
        "email": email[0] if email else "",
        "phone": phone[0] if phone else "",
        "linkedin": linkedin[0] if linkedin else "",
        "github": github[0] if github else "",
    }

def run_ner(text: str) -> Dict[str, List[str]]:
    """
    Run HuggingFace NER pipeline on top header text of original resume.
    Returns {entity_group: [values]} with confidence >= 0.60.
    """
    head = header_text(text)
    try:
        ner_pipe = NERModelManager.get_pipeline()
        ents = ner_pipe(head)
    except Exception as e:
        print(f"NER execution warning: {e}")
        return {}

    out: Dict[str, List[str]] = {}
    for e in ents:
        if e.get("score", 0) < 0.60:
            continue
        g = e.get("entity_group", "")
        v = e.get("word", "").replace(" ##", "").strip()
        if len(v) < 2:
            continue
        out.setdefault(g, [])
        if v not in out[g]:
            out[g].append(v)

    return out

def pick_name(ner_out: Dict[str, List[str]], original_text: str) -> str:
    """
    Select candidate name from NER entities or header fallback.
    Explicitly ignores company names or organization labels.
    """
    for key, values in ner_out.items():
        key_upper = key.upper()
        if ("NAME" in key_upper or key_upper in ("PER", "PERSON")) and "ORG" not in key_upper and "COMPANY" not in key_upper:
            if values:
                return values[0].title()

    head = header_text(original_text, n_lines=5)
    for line in head.split("\n"):
        line = line.strip()
        if 1 < len(line.split()) <= 4 and "@" not in line and not re.search(r"\d{4}", line) and not re.search(r"resume|curriculum|vitae|profile", line, re.I):
            return line.title()

    return ""
