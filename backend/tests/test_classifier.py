from app.engine.classifier import classify_domain
from app.engine.input_parser import parse_input


def test_classify_code_dev():
    text = "Please write a FastAPI endpoint for user registration and login using Python"
    parsed = parse_input(text)
    result = classify_domain(parsed)
    assert result.domain == "code_dev"


def test_classify_copywriting():
    text = "Please write a 500-word essay about spring, with poetic language"
    parsed = parse_input(text)
    result = classify_domain(parsed)
    assert result.domain == "copywriting"


def test_classify_healthcare():
    text = "A 45-year-old male patient has had persistent headaches for a week. What could be the possible causes and what should be noted?"
    parsed = parse_input(text)
    result = classify_domain(parsed)
    assert result.domain == "healthcare"


def test_classify_ai_visual():
    text = "Generate a cyberpunk-style city night scene, neon lights, rainy, 8K resolution"
    parsed = parse_input(text)
    result = classify_domain(parsed)
    assert result.domain == "ai_visual"
