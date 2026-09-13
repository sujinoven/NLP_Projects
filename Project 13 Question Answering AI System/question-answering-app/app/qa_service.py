import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import torch
from transformers import AutoTokenizer, AutoModelForQuestionAnswering

logger = logging.getLogger(__name__)


class QAService:
    """Service class for managing DistilBERT Question Answering model inference."""

    def __init__(self, model_dir: Path, max_length: int = 384, stride: int = 128, max_answer_length: int = 30):
        self.model_dir = Path(model_dir)
        self.max_length = max_length
        self.stride = stride
        self.max_answer_length = max_answer_length

        self.tokenizer = None
        self.model = None
        self.device = torch.device("cpu")
        self.is_loaded = False
        self.load_error: Optional[str] = None

    def load_model(self) -> None:
        """Load tokenizer and model from local directory using local_files_only=True."""
        if not self.model_dir.exists():
            self.load_error = f"Model directory not found at '{self.model_dir.absolute()}'."
            logger.warning(self.load_error)
            return

        # Check for essential model files
        config_file = self.model_dir / "config.json"
        if not config_file.exists():
            self.load_error = (
                f"Model configuration 'config.json' not found in '{self.model_dir.absolute()}'. "
                "Please extract distilbert_squad_model.zip into the model/ folder."
            )
            logger.warning(self.load_error)
            return

        try:
            logger.info(f"Loading local DistilBERT tokenizer and model from {self.model_dir}...")
            self.tokenizer = AutoTokenizer.from_pretrained(
                str(self.model_dir),
                local_files_only=True
            )
            self.model = AutoModelForQuestionAnswering.from_pretrained(
                str(self.model_dir),
                local_files_only=True
            )
            self.model.to(self.device)
            self.model.eval()
            self.is_loaded = True
            self.load_error = None
            logger.info("DistilBERT Question Answering model loaded successfully.")
        except Exception as e:
            self.is_loaded = False
            self.load_error = f"Failed to load model from '{self.model_dir.absolute()}': {str(e)}"
            logger.error(self.load_error, exc_info=True)

    def answer_question(self, context: str, question: str) -> Dict[str, Any]:
        """
        Predict answer for a given context and question.
        Handles long context using sliding token windows, offset mappings, and combined span scoring.
        """
        if not self.is_loaded or self.model is None or self.tokenizer is None:
            raise RuntimeError(
                self.load_error or "Model is not loaded. Please verify model weights exist in the model/ directory."
            )

        # Tokenize with sliding windows (overflowing tokens)
        # Sequence 0 is question, Sequence 1 is context when passed as (question, context) with truncation="only_second"
        inputs = self.tokenizer(
            question,
            context,
            max_length=self.max_length,
            stride=self.stride,
            return_overflowing_tokens=True,
            return_offsets_mapping=True,
            padding="max_length",
            truncation="only_second",
            return_tensors="pt"
        )

        offset_mappings = inputs.pop("offset_mapping")
        inputs.pop("overflow_to_sample_mapping", None)

        num_windows = inputs["input_ids"].shape[0]

        best_score = float("-inf")
        best_answer = ""
        best_start_char = 0
        best_end_char = 0

        with torch.inference_mode():
            outputs = self.model(**inputs)
            start_logits = outputs.start_logits  # shape: [num_windows, seq_len]
            end_logits = outputs.end_logits      # shape: [num_windows, seq_len]

        for i in range(num_windows):
            window_start_logits = start_logits[i].cpu().numpy()
            window_end_logits = end_logits[i].cpu().numpy()
            offsets = offset_mappings[i].cpu().numpy()
            seq_ids = inputs.sequence_ids(i)

            # Identify token indices belonging exclusively to context (sequence_id == 1)
            context_token_indices = [
                idx for idx, seq_id in enumerate(seq_ids) if seq_id == 1
            ]

            if not context_token_indices:
                continue

            # Search valid (start, end) span candidates within this window
            for start_idx in context_token_indices:
                for end_idx in context_token_indices:
                    if end_idx < start_idx:
                        continue
                    if (end_idx - start_idx + 1) > self.max_answer_length:
                        continue

                    # Extract character bounds from offset mapping
                    start_char = int(offsets[start_idx][0])
                    end_char = int(offsets[end_idx][1])

                    # Basic sanity check on character bounds
                    if start_char < 0 or end_char <= start_char or end_char > len(context):
                        continue

                    span_score = float(window_start_logits[start_idx] + window_end_logits[end_idx])

                    if span_score > best_score:
                        extracted_text = context[start_char:end_char].strip()
                        if extracted_text:
                            best_score = span_score
                            best_answer = extracted_text
                            best_start_char = start_char
                            best_end_char = end_char

        # Fallback if no valid non-empty span was scored
        if best_score == float("-inf") or not best_answer:
            best_answer = "Unable to extract answer span."
            best_start_char = 0
            best_end_char = 0
            best_score = 0.0

        return {
            "answer": best_answer,
            "start_char": best_start_char,
            "end_char": best_end_char,
            "score": round(best_score, 4),
            "context_length": len(context)
        }
