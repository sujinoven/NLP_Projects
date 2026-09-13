from pathlib import Path
import pytest
from unittest.mock import MagicMock
import torch
from app.qa_service import QAService


def test_qa_service_missing_model_directory(tmp_path):
    missing_dir = tmp_path / "non_existent_model"
    service = QAService(model_dir=missing_dir)
    service.load_model()

    assert service.is_loaded is False
    assert "not found" in service.load_error

    with pytest.raises(RuntimeError) as exc_info:
        service.answer_question(context="Context text", question="Question?")
    assert "Model directory not found" in str(exc_info.value)


def test_qa_service_span_selection_mock():
    """Test span selection logic using mocked model outputs."""
    service = QAService(model_dir=Path("./mock_dir"))
    service.is_loaded = True

    # Setup mock tokenizer
    mock_tokenizer = MagicMock()
    mock_tokenizer.return_value = {
        "input_ids": torch.tensor([[101, 1000, 102, 2000, 2001, 2002, 102]]),
        "offset_mapping": torch.tensor([[[0, 0], [0, 5], [0, 0], [0, 6], [7, 12], [13, 17], [0, 0]]])
    }
    # Mock sequence_ids for window 0: None, 0, None, 1, 1, 1, None
    mock_inputs_dict = mock_tokenizer.return_value
    mock_inputs_obj = MagicMock()
    mock_inputs_obj.__getitem__.side_effect = lambda k: mock_inputs_dict[k]
    mock_inputs_obj.pop.side_effect = lambda k, default=None: mock_inputs_dict.pop(k, default)
    mock_inputs_obj.sequence_ids.return_value = [None, 0, None, 1, 1, 1, None]

    service.tokenizer = lambda *args, **kwargs: mock_inputs_obj

    # Setup mock model outputs with start and end logits
    # Token 4 (index 4: '13 to 17' in offset) has high start/end score
    mock_outputs = MagicMock()
    start_logits = torch.zeros((1, 7))
    start_logits[0, 4] = 5.0  # token 4 start
    end_logits = torch.zeros((1, 7))
    end_logits[0, 5] = 4.0    # token 5 end
    mock_outputs.start_logits = start_logits
    mock_outputs.end_logits = end_logits

    mock_model = MagicMock()
    mock_model.return_value = mock_outputs
    service.model = mock_model

    context_text = "Sample context with target answer text inside."
    question_text = "Where is target?"

    res = service.answer_question(context=context_text, question=question_text)

    assert "answer" in res
    assert "start_char" in res
    assert "end_char" in res
    assert "score" in res
    assert res["score"] == 9.0  # 5.0 + 4.0
