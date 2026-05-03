from app.engine.scorer import score_prompt, _score_clarity, _score_structure
from app.schemas.pipeline import AnalysisReport, DomainResult


def test_score_clarity_high():
    clear_text = "Please write a Python function that receives a list of integers and returns a new sorted list using the quicksort algorithm."
    score = _score_clarity(clear_text)
    assert score >= 60


def test_score_clarity_low():
    vague_text = "sort"
    score = _score_clarity(vague_text)
    assert score < 70


def test_score_structure():
    analysis = AnalysisReport(
        has_role_definition=True,
        has_output_spec=True,
        has_context=False,
        has_constraints=True,
        structure_score=0.75,
        redundancy_markers=[],
        missing_sections=["Background context"],
    )
    text = "[Role]\nYou are a Python developer\n[Output]\nCode"
    score = _score_structure(text, analysis)
    assert score >= 60


def test_score_prompt_integration():
    orig = "write a sorting code"
    opt = "[Role]\nYou are a Python developer\n\n[Goal]\nImplement quicksort for integer lists\n\n[Output]\nComplete Python code"
    analysis = AnalysisReport(
        has_role_definition=False,
        has_output_spec=False,
        has_context=False,
        has_constraints=False,
        structure_score=0.25,
        redundancy_markers=[],
        missing_sections=["Role definition", "Output specification"],
    )
    domain = DomainResult(domain="code_dev", confidence=0.8)
    report = score_prompt(orig, opt, analysis, domain)
    assert report.total > 0
    assert report.clarity.score > 0
    assert report.structure.score > 0
