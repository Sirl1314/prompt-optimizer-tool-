from ..schemas.pipeline import ParsedInput, AnalysisReport, DomainResult
from ..domains import registry


def apply_template(
    parsed: ParsedInput,
    analysis: AnalysisReport,
    domain_result: DomainResult,
) -> str:
    strategy = registry.get(domain_result.domain)
    if not strategy:
        return parsed.raw_text

    template = strategy.template
    sections = []

    for section_name, section_desc in template.items():
        filled = section_desc
        if "{技术栈" in filled:
            filled = filled.replace("{技术栈、框架版本、关键依赖}",
                                     "Python 3.11, FastAPI, SQLAlchemy")
        if "{具体功能" in filled:
            filled = filled.replace("{具体功能描述、输入→输出}",
                                     parsed.raw_text[:200])
        sections.append(f"[{section_name}]\n{filled}")

    template_part = "\n\n".join(sections)

    if analysis.missing_sections:
        suggestions = "\n".join(f"- 建议补充: {s}" for s in analysis.missing_sections)
        template_part += f"\n\n## 结构优化建议\n{suggestions}"

    result = f"{template_part}\n\n## 原始需求\n{parsed.raw_text}"

    return result
