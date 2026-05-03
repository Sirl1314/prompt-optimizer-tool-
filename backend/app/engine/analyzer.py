import re
from ..schemas.pipeline import AnalysisReport, RedundancyMarker, ParsedInput


_REDUNDANCY_PATTERNS = [
    (r"(.*?)\1{2,}", "重复的短语"),
    (r"(总而言之|综上所述|简单来说|换句话说|也就是说)", "冗余的过渡词"),
    (r"(\b\w+\b)(\s+\1\b){2,}", "重复的单词(英文)"),
    (r"(请|帮我|麻烦你|能不能|可以不可以)\s*(请|帮我)", "重复的请求词"),
]

_STRUCTURE_INDICATORS = {
    "has_role_definition": [
        r"你是[一个位名]?\s*\S*(工程师|专家|助手|老师|分析师|设计师|策划|顾问|写手|诗人)",
        r"(act as|you are|扮演|作为[一个位名]?)",
    ],
    "has_output_spec": [
        r"(输出|返回|给出|生成|请用|格式|字数|行数|段落)",
        r"(json|markdown|表格|列表|代码|图表)",
    ],
    "has_context": [
        r"(背景|当前|项目|场景|数据|文件)",
    ],
    "has_constraints": [
        r"(不要|禁止|避免|不能|必须|一定|只|仅|不超过|至少)",
    ],
}


def analyze_structure(parsed: ParsedInput) -> AnalysisReport:
    text = parsed.raw_text.lower() if parsed.language != "en" else parsed.raw_text

    has_role = any(re.search(p, text, re.IGNORECASE) for p in _STRUCTURE_INDICATORS["has_role_definition"])
    has_output = any(re.search(p, text, re.IGNORECASE) for p in _STRUCTURE_INDICATORS["has_output_spec"])
    has_context = any(re.search(p, text, re.IGNORECASE) for p in _STRUCTURE_INDICATORS["has_context"])
    has_constraints = any(re.search(p, text, re.IGNORECASE) for p in _STRUCTURE_INDICATORS["has_constraints"])

    present = sum([has_role, has_output, has_context, has_constraints])
    structure_score = min(present / 4.0, 1.0)

    redundancy_markers = []
    for pattern, reason in _REDUNDANCY_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches[:3]:
            redundancy_markers.append(RedundancyMarker(
                text_segment=str(match)[:100],
                reason=reason,
                suggestion="建议删除或精简此冗余部分",
            ))

    missing = []
    if not has_role:
        missing.append("角色定义")
    if not has_output:
        missing.append("输出规范")
    if not has_context:
        missing.append("背景上下文")
    if not has_constraints:
        missing.append("约束条件")

    return AnalysisReport(
        has_role_definition=has_role,
        has_output_spec=has_output,
        has_context=has_context,
        has_constraints=has_constraints,
        structure_score=structure_score,
        redundancy_markers=redundancy_markers,
        missing_sections=missing,
    )
