from app.services.preprocessing import clean_text, tokenize_text


def test_clean_text():
    text = "Hello!!! Visit https://example.com NOW."
    assert clean_text(text) == "hello visit now"


def test_negation_is_preserved():
    tokens = tokenize_text("payment is not working")
    assert "not" in tokens
    assert "is" not in tokens
