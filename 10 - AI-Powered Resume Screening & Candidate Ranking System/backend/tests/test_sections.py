from app.services.sections import split_into_sections, split_jd_into_sections

def test_split_into_sections_standard():
    resume_text = """
john doe
john@example.com

technical skills:
- python, fastapi, pytorch, docker

work experience:
- senior software developer at acme corp
- built nlp recommendation models

education:
- bs in computer science
"""
    sections, used_fallback = split_into_sections(resume_text.strip())
    assert used_fallback is False
    assert "skills" in sections
    assert "experience" in sections
    assert "education" in sections

def test_split_into_sections_fallback():
    unstructured_text = "this is a plain text resume without standard section headers."
    sections, used_fallback = split_into_sections(unstructured_text)
    assert used_fallback is True
    assert "full_text" in sections

def test_split_jd_into_sections():
    jd_text = """
role: senior machine learning engineer
required skills:
- 3+ years experience with PyTorch and Transformers
- Python expertise
experience: 3+ years
"""
    sections, used_fallback = split_jd_into_sections(jd_text.strip())
    assert used_fallback is False
    assert "required_skills" in sections
    assert "experience" in sections
    assert "3+ years" in sections["experience"]
