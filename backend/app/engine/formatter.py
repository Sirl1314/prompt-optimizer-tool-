from ..schemas.pipeline import ScoreReport, PipelineResult, AnalysisReport
from ..utils.diff import generate_diff_html
from ..utils.token_counter import count_tokens


def format_output(
    original: str,
    optimized: str,
    domain: str,
    domain_confidence: float,
    scores: ScoreReport,
    model_used: str,
    analysis_report: AnalysisReport,
) -> PipelineResult:
    diff_html = generate_diff_html(original, optimized)
    token_raw = count_tokens(original)
    token_opt = count_tokens(optimized)

    return PipelineResult(
        original_text=original,
        optimized_text=optimized,
        domain=domain,
        domain_confidence=domain_confidence,
        scores=scores,
        token_count_raw=token_raw,
        token_count_optimized=token_opt,
        token_saved=token_raw - token_opt,
        diff_html=diff_html,
        model_used=model_used,
        analysis_report=analysis_report,
    )
