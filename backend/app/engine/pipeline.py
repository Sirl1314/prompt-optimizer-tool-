from .input_parser import parse_input
from .analyzer import analyze_structure
from .classifier import classify_domain
from .refactor import apply_template
from .ai_refiner import ai_refine
from .scorer import score_prompt
from .formatter import format_output
from ..schemas.pipeline import PipelineResult, DomainResult


async def run_pipeline(
    raw_prompt: str,
    force_domain: str | None = None,
    model_name: str = "deepseek-chat",
    output_language: str = "zh",
) -> PipelineResult:
    # Stage 1: Input parsing
    parsed = parse_input(raw_prompt)

    # Stage 2: Structure analysis
    analysis = analyze_structure(parsed)

    # Stage 3: Domain classification
    domain_result = classify_domain(parsed, analysis)
    if force_domain:
        domain_result = DomainResult(domain=force_domain, confidence=1.0)

    # Stage 4a: Template refactoring
    template_text = apply_template(parsed, analysis, domain_result)

    # Stage 4b: AI refinement
    lang = output_language if output_language in ("zh", "en") else parsed.language
    refined_text, actual_model = await ai_refine(template_text, domain_result, model_name, language=lang)

    # Stage 5: Multi-dimensional scoring
    scores = score_prompt(raw_prompt, refined_text, analysis, domain_result)

    # Stage 6: Output formatting
    result = format_output(
        original=raw_prompt,
        optimized=refined_text,
        domain=domain_result.domain,
        domain_confidence=domain_result.confidence,
        scores=scores,
        model_used=actual_model,
        analysis_report=analysis,
    )

    return result
