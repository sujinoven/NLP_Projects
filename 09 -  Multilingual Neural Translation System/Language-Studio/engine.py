"""Translation logic, kept separate from the Streamlit interface."""
from dataclasses import dataclass, asdict
from copy import deepcopy
from pathlib import Path
import os
import re
import threading
import time
from protection import detect_items

LANGUAGES = {
    "English": "eng_Latn", "French": "fra_Latn", "Spanish": "spa_Latn",
    "Hindi": "hin_Deva", "Tamil": "tam_Taml",
}
DETECTION_CODES = {"en": "English", "fr": "French", "es": "Spanish", "hi": "Hindi", "ta": "Tamil"}
MODEL_ID = "facebook/nllb-200-distilled-600M"
MARKER_PREFIX = "ZXQTERM"
DETECTION_LOCK = threading.Lock()


class TranslationError(ValueError):
    """A failure that can be explained directly to the user."""


@dataclass
class Result:
    original: str
    translation: str
    source: str
    target: str
    status: str
    detection_score: float | None
    protected_terms: list[str]
    sentence_count: int
    elapsed_seconds: float
    notes: list[str]

    def to_dict(self):
        return asdict(self)


def collect_terms(text, supplied):
    """Detect terms automatically; optional caller overrides remain supported."""
    terms = [t.strip() for t in supplied if t.strip()]
    terms.extend(item["text"] for item in detect_items(text))
    return sorted({t for t in terms if t in text}, key=lambda t: (-len(t), t))


def term_pattern(terms):
    # Escape punctuation, protect whole terms, and prefer longer overlaps.
    return re.compile(r"(?<!\w)(?:" + "|".join(re.escape(t) for t in terms) + r")(?!\w)") if terms else None


def protect(text, terms):
    if MARKER_PREFIX in text:
        raise TranslationError("This message contains a reserved protection marker. Remove ZXQTERM text and retry.")
    pattern = term_pattern(terms)
    if pattern is None:
        return text, {}
    mapping = {}
    def replace(match):
        # Give each occurrence its own marker so repeated terms are checked too.
        marker = f"{MARKER_PREFIX}{len(mapping)}QXZ"
        mapping[marker] = match.group(0)
        return marker
    return pattern.sub(replace, text), mapping


def restore(raw, mapping):
    for marker in mapping:
        if raw.count(marker) != 1:
            raise TranslationError("The model changed or omitted a protected term. No translation was released. Try a shorter message.")
    result = raw
    for marker, term in mapping.items():
        result = result.replace(marker, term)
    if MARKER_PREFIX in result:
        raise TranslationError("An unexpected protection marker remains in the translation.")
    return result


def scripts_in(text):
    patterns = {"Latin": r"[A-Za-z]", "Devanagari": r"[\u0900-\u097F]", "Tamil": r"[\u0B80-\u0BFF]"}
    return [name for name, pattern in patterns.items() if re.search(pattern, text)]


def split_sentences(text):
    # Conservative baseline: abbreviations can still split incorrectly.
    return [part.strip() for part in re.split(r"(?<=[.!?।])\s+|\n+", text) if part.strip()]


def detect_source(text):
    from langdetect import DetectorFactory, detect_langs
    from langdetect.lang_detect_exception import LangDetectException
    with DETECTION_LOCK:
        DetectorFactory.seed = 0
        try:
            best = detect_langs(text)[0]
        except LangDetectException as error:
            raise TranslationError("Could not identify a language. Select the source language manually.") from error
    if best.lang not in DETECTION_CODES or best.prob < 0.90:
        raise TranslationError("Automatic detection is uncertain or suggests an unsupported language. Select the source language manually.")
    return DETECTION_CODES[best.lang], float(best.prob)


class NllbBackend:
    """Load on first translation. A lock protects the shared mutable tokenizer."""
    def __init__(self, model_source=None):
        self.model_source = model_source or os.environ.get("TRANSLATION_MODEL", MODEL_ID)
        self.lock = threading.RLock()
        self.model = None
        self.tokenizer = None
        self.device = "Not loaded"

    def _load(self):
        if self.model is not None:
            return
        import torch
        from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        device = "cuda" if torch.cuda.is_available() else "cpu"
        cache_dir = os.environ.get(
            "TRANSLATION_CACHE",
            str(Path(__file__).resolve().parent / ".cache" / "huggingface" / "hub"),
        )
        tokenizer = AutoTokenizer.from_pretrained(self.model_source, src_lang="eng_Latn", cache_dir=cache_dir)
        for code in LANGUAGES.values():
            if tokenizer.convert_tokens_to_ids(code) == tokenizer.unk_token_id:
                raise TranslationError("The selected model does not provide the required NLLB language tokens.")
        model = AutoModelForSeq2SeqLM.from_pretrained(
            self.model_source,
            dtype=torch.float16 if device == "cuda" else torch.float32,
            cache_dir=cache_dir,
        ).to(device)
        model.eval()
        self.tokenizer, self.model, self.device = tokenizer, model, device

    def translate_many(self, sentences, source, target):
        import torch
        with self.lock:
            self._load()
            self.tokenizer.src_lang = LANGUAGES[source]
            encoded_items = []
            for sentence in sentences:
                encoded = self.tokenizer(sentence, return_tensors="pt", truncation=False)
                if encoded["input_ids"].shape[1] > 512:
                    raise TranslationError("A sentence exceeds 512 model tokens. Shorten it; the app will not silently truncate it.")
                encoded_items.append(encoded.to(self.device))
            config = deepcopy(self.model.generation_config)
            # One explicit length control; do not hide all library warnings.
            config.max_length = None
            config.max_new_tokens = 256
            config.forced_eos_token_id = None
            config.forced_bos_token_id = self.tokenizer.convert_tokens_to_ids(LANGUAGES[target])
            config.num_beams = 1
            config.do_sample = False
            translations = []
            with torch.inference_mode():
                for encoded in encoded_items:
                    output = self.model.generate(**encoded, generation_config=config)[0].tolist()
                    if self.tokenizer.unk_token_id in output:
                        raise TranslationError("The model generated an unknown token. Try a clearer or shorter sentence.")
                    if output[-1] != self.tokenizer.eos_token_id:
                        raise TranslationError("The translation reached its length limit. Shorten the message and retry.")
                    translations.append(self.tokenizer.decode(output, skip_special_tokens=True))
            return translations


def translate_message(text, source, target, supplied_terms, sentence_mode, backend):
    started = time.monotonic()
    if not isinstance(text, str) or not text.strip():
        raise TranslationError("Enter a message to translate.")
    if len(text) > 4000:
        raise TranslationError("Keep messages under 4,000 characters.")
    if source not in ["Auto-detect", *LANGUAGES] or target not in LANGUAGES:
        raise TranslationError("Choose a supported language.")
    terms = collect_terms(text, supplied_terms)
    masked, mapping = protect(text, terms)
    # Remove only real protected spans when checking scripts and language.
    linguistic_text = masked
    for marker in mapping:
        linguistic_text = linguistic_text.replace(marker, " ")
    result_args = dict(original=text, target=target, detection_score=None,
                       protected_terms=list(dict.fromkeys(mapping.values())))
    if mapping and not any(c.isalnum() for c in linguistic_text):
        return Result(**result_args, translation=text, source="Not needed", status="Preserved",
                      sentence_count=0, elapsed_seconds=time.monotonic()-started,
                      notes=["This message contains only protected terms and punctuation."])
    if len(scripts_in(linguistic_text)) > 1:
        raise TranslationError("This message mixes scripts beyond the automatically recognised terms. Mixed-language translation is not supported reliably yet. Use a single language.")
    notes = []
    if source == "Auto-detect":
        if sum(c.isalpha() for c in linguistic_text) < 15:
            raise TranslationError("This message is too short for reliable automatic detection. Select its source language manually.")
        source, score = detect_source(linguistic_text)
        result_args["detection_score"] = score
        notes.append("Language-detection scores are not a guarantee of correctness.")
    if source == target:
        return Result(**result_args, translation=text, source=source, status="Unchanged",
                      sentence_count=0, elapsed_seconds=time.monotonic()-started,
                      notes=notes+["Source and target match. Text was returned unchanged, not translated; check the source selection."])
    sentences = split_sentences(masked) if sentence_mode else [masked]
    raw_parts = backend.translate_many(sentences, source, target)
    if len(raw_parts) != len(sentences):
        raise TranslationError("The translation returned an unexpected number of sentences.")
    restored = []
    for sentence, raw in zip(sentences, raw_parts):
        local_mapping = {m: t for m, t in mapping.items() if m in sentence}
        restored.append(restore(raw, local_mapping))
    if sentence_mode:
        notes.append("Sentences were translated separately. Review context and politeness.")
    notes.append("Review meaning and tone. Exact-term checks do not measure translation quality.")
    return Result(**result_args, translation=" ".join(restored), source=source, status="Translated",
                  sentence_count=len(sentences), elapsed_seconds=time.monotonic()-started, notes=notes)
