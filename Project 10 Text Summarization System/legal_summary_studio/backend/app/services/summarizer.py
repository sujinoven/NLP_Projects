"""Lazy local BART inference, serialized to avoid GPU/CPU memory contention."""
import threading
import time

from .facts import fact_report
from .metrics import rouge_report
from .text_processing import preprocess, token_windows


class ServiceError(Exception):
    def __init__(self, message, status=503):
        super().__init__(message)
        self.status = status


class Summarizer:
    def __init__(self, config):
        self.config = config
        self.model = None
        self.tokenizer = None
        self.device = None
        self.state = "not_loaded"
        self.lock = threading.Lock()

    def health(self):
        return {"status": "ok", "model": self.config["MODEL_NAME"],
                "model_state": self.state, "device": self.device,
                "busy": self.lock.locked()}

    def load(self):
        if self.model is not None:
            return
        self.state = "loading"
        try:
            import torch
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
            requested = self.config["DEVICE"]
            if requested not in ("auto", "cpu", "cuda"):
                raise ValueError("DEVICE must be auto, cpu or cuda")
            self.device = ("cuda" if torch.cuda.is_available() else "cpu") if requested == "auto" else requested
            kwargs = {"local_files_only": self.config["LOCAL_FILES_ONLY"]}
            tokenizer = AutoTokenizer.from_pretrained(self.config["MODEL_NAME"], **kwargs)
            model = AutoModelForSeq2SeqLM.from_pretrained(
                self.config["MODEL_NAME"], use_safetensors=True, **kwargs
            ).to(self.device)
            if model.config.model_type != "bart":
                raise ValueError("This service supports BART checkpoints only")
            model.eval()
            self.tokenizer, self.model = tokenizer, model
            self.state = "ready"
        except Exception as exc:
            self.model = None
            self.state = "error"
            raise ServiceError("BART could not load. Run python download_model.py in backend and check the terminal, network, disk space and DEVICE setting.") from exc

    def encode(self, text):
        return self.tokenizer.encode(text, add_special_tokens=False)

    def generate(self, ids, ratio, max_tokens):
        import torch
        # No fixed 40-token minimum; tiny inputs never receive a forced expansion.
        budget = min(max_tokens, max(2, int(len(ids) * ratio)), max(2, len(ids) - 1))
        # BART single inputs use <s> content </s>. Assemble directly: this
        # preserves exact window IDs and works across tokenizer backends in v4/v5.
        input_ids = torch.tensor(
            [[self.tokenizer.bos_token_id, *ids, self.tokenizer.eos_token_id]],
            dtype=torch.long, device=self.device,
        )
        inputs = {"input_ids": input_ids, "attention_mask": torch.ones_like(input_ids)}
        if inputs["input_ids"].shape[-1] > self.model.config.max_position_embeddings:
            raise ServiceError("Internal chunk length exceeds model capacity.", 500)
        with torch.inference_mode():
            outputs = self.model.generate(
                **inputs, num_beams=4, do_sample=False,
                min_length=0, min_new_tokens=0, max_new_tokens=budget,
                no_repeat_ngram_size=3, length_penalty=1.0, early_stopping=True,
            )
        summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        if not summary:
            raise ServiceError("The model returned an empty summary. Try a longer document.", 422)
        return summary

    def summarize(self, text, ratio=0.3, max_tokens=220, reference=None):
        if not self.lock.acquire(blocking=False):
            raise ServiceError("Another document is being processed. Please try again when it finishes.", 429)
        started = time.perf_counter()
        try:
            cleaned = preprocess(text)
            if not cleaned:
                raise ServiceError("No document text remains after cleanup.", 400)
            self.load()
            ids = self.encode(cleaned)
            original_count = len(ids)
            if original_count > self.config["MAX_DOCUMENT_TOKENS"]:
                raise ServiceError("Document exceeds the configured token limit. Submit a smaller document.", 413)
            warnings = ["BART is a news-trained summarizer. Review legal facts and obligations against the source."]
            if original_count < 24:
                summary = cleaned
                chunks_count, passes = 1, 0
                warnings.append("Very short input returned unchanged to avoid forced expansion; no compression performed.")
            else:
                capacity = min(1024, self.model.config.max_position_embeddings) - self.tokenizer.num_special_tokens_to_add(pair=False)
                chunks = token_windows(ids, capacity, min(64, capacity // 8))
                chunks_count, passes = len(chunks), 0
                while True:
                    passes += 1
                    partials = [self.generate(chunk, ratio, max_tokens) for chunk in chunks]
                    if len(partials) == 1:
                        summary = partials[0]
                        break
                    combined = "\n".join(partials)
                    next_ids = self.encode(combined)
                    if passes >= 6 or len(next_ids) >= len(ids):
                        raise ServiceError("The model could not reduce this document within safe processing limits. Try a smaller section.", 422)
                    ids = next_ids
                    chunks = token_windows(ids, capacity, min(64, capacity // 8))
                if chunks_count > 1:
                    warnings.append("Multiple summarization passes can omit details and cross-references.")
            out_count = len(self.encode(summary))
            actual_ratio = out_count / max(original_count, 1)
            if actual_ratio >= 1:
                warnings.append("The output is not shorter than the source.")
            return {"summary": summary, "model": self.config["MODEL_NAME"],
                    "input_tokens": original_count, "summary_tokens": out_count,
                    "compression_ratio": actual_ratio, "target_ratio": ratio,
                    "chunks": chunks_count, "passes": passes,
                    "elapsed_seconds": round(time.perf_counter() - started, 2),
                    "facts": fact_report(cleaned, summary),
                    "rouge": rouge_report(reference, summary) if reference else None,
                    "warnings": warnings}
        finally:
            self.lock.release()
