from app.services.preprocessing import preprocess

def test_preprocess_cleaning():
    raw = "John Doe\tSoftware Developer\n• Bullet item 1\n‣ Bullet item 2\nVisit https://example.com for details.\n\n\nSkills: Python & C++"
    cleaned = preprocess(raw)
    
    assert "john doe" in cleaned
    assert "\t" not in cleaned
    assert "•" not in cleaned
    assert "-" in cleaned
    assert "https://" not in cleaned
    assert "c++" in cleaned
    assert "\n\n\n" not in cleaned
