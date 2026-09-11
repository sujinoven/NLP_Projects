import os
import pytest
from app.services.extraction import extract_text, extract_text_from_txt

def test_extract_text_txt(tmp_path):
    txt_file = tmp_path / "sample_resume.txt"
    txt_file.write_text("John Doe\nSoftware Engineer\nPython, FastAPI, PyTorch", encoding="utf-8")
    
    text, ocr_warning = extract_text(str(txt_file), filename="sample_resume.txt")
    assert "John Doe" in text
    assert "Software Engineer" in text
    assert ocr_warning is False

def test_unsupported_format(tmp_path):
    invalid_file = tmp_path / "resume.xyz"
    invalid_file.write_text("invalid content", encoding="utf-8")
    
    with pytest.raises(ValueError, match="Unsupported file format"):
        extract_text(str(invalid_file), filename="resume.xyz")
