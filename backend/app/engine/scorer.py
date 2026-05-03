import re
from ..schemas.pipeline import ScoreDetail, ScoreReport, AnalysisReport, DomainResult
from ..domains import registry


def score_prompt(
    original: str,
    optimized: str,
    analysis: AnalysisReport,
    domain_result: DomainResult,
) -> ScoreReport:
    strategy = registry.get(domain_result.domain)
    weights = strategy.scoring_weights if strategy else {
        "clarity": 0.25, "structure": 0.25, "redundancy": 0.20,
        "role_setting": 0.15, "output_spec": 0.15,
    }

    clarity_score = _score_clarity(optimized)
    structure_score = _score_structure(optimized, analysis)
    redundancy_score = _score_redundancy(original, optimized, analysis)
    role_score = _score_role(optimized, domain_result)
    output_score = _score_output_spec(optimized)

    total = (
        clarity_score * weights.get("clarity", 0.25)
        + structure_score * weights.get("structure", 0.25)
        + redundancy_score * weights.get("redundancy", 0.20)
        + role_score * weights.get("role_setting", 0.15)
        + output_score * weights.get("output_spec", 0.15)
    )

    return ScoreReport(
        clarity=ScoreDetail(score=clarity_score, weight=weights.get("clarity", 0.25),
                            notes=_clarity_notes(clarity_score)),
        structure=ScoreDetail(score=structure_score, weight=weights.get("structure", 0.25),
                              notes=_structure_notes(analysis)),
        redundancy=ScoreDetail(score=redundancy_score, weight=weights.get("redundancy", 0.20),
                               notes=_redundancy_notes(analysis)),
        role_setting=ScoreDetail(score=role_score, weight=weights.get("role_setting", 0.15),
                                 notes=_role_notes(optimized)),
        output_spec=ScoreDetail(score=output_score, weight=weights.get("output_spec", 0.15),
                                notes=_output_notes(optimized)),
        total=round(total, 1),
    )


def _score_clarity(text: str) -> float:
    sentences = re.split(r"[。.！!？?\n]", text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
    if not sentences:
        return 40.0
    avg_len = sum(len(s) for s in sentences) / len(sentences)
    if 20 <= avg_len <= 80:
        base = 90.0
    elif avg_len < 20:
        base = avg_len / 20 * 70
    else:
        base = max(50, 90 - (avg_len - 80) * 0.5)
    return round(min(base, 95), 1)


def _score_structure(text: str, analysis: AnalysisReport) -> float:
    base = analysis.structure_score * 70
    if re.search(r"\[.+\]", text) or re.search(r"#{1,3}\s", text):
        base += 20
    if re.search(r"(\n\s*[-*\d.]\s)", text):
        base += 10
    return round(min(base, 95), 1)


def _score_redundancy(original: str, optimized: str, analysis: AnalysisReport) -> float:
    redundancy_count = len(analysis.redundancy_markers)
    base = 100 - redundancy_count * 15
    if len(optimized) < len(original) * 0.95:
        base += 10
    if len(optimized) < len(original) * 0.7:
        base += 5
    return round(max(min(base, 95), 30), 1)


def _score_role(text: str, _domain_result: DomainResult) -> float:
    roles_found = len(re.findall(
        r"你是[一个位名]?\s*\S*(工程师|专家|助手|老师|分析师|设计师|策划|顾问|写手|诗人|开发|程序员)",
        text
    ))
    if roles_found >= 1:
        return 85.0
    if re.search(r"(act as|扮演|作为|you are)", text, re.IGNORECASE):
        return 70.0
    return 30.0


def _score_output_spec(text: str) -> float:
    score = 30.0
    if re.search(r"(输出|返回|给出|生成|output|return)", text):
        score += 20
    if re.search(r"(json|markdown|表格|列表|代码|图表|字数|行数|格式|format)", text):
        score += 25
    if re.search(r"(```|代码块|示例|example)", text):
        score += 15
    return round(min(score, 95), 1)


def _clarity_notes(score: float) -> str:
    if score >= 85: return "表达清晰，易于理解"
    if score >= 65: return "大部分清晰，部分句子可以进一步优化"
    return "表达略显模糊，建议补充具体描述"


def _structure_notes(analysis: AnalysisReport) -> str:
    missing = analysis.missing_sections
    if not missing: return "结构完整"
    return f"结构不完整，缺少: {', '.join(missing)}"


def _redundancy_notes(analysis: AnalysisReport) -> str:
    count = len(analysis.redundancy_markers)
    if count == 0: return "无明显冗余"
    return f"检测到 {count} 处冗余表达"


def _role_notes(text: str) -> str:
    if re.search(r"你是|you are|act as", text, re.IGNORECASE): return "角色设定清晰"
    return "缺少角色定义，建议补充"


def _output_notes(text: str) -> str:
    if re.search(r"(格式|输出|字数|format|output)", text): return "输出规范适当"
    return "输出格式约束不足"
