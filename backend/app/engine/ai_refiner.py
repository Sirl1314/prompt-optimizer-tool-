from ..schemas.pipeline import DomainResult
from ..domains import registry
from ..models_adapter import get_adapter

_LANG_PROMPTS = {
    "zh": {
        "system": (
            "你的任务是将以下原始需求优化为结构清晰、表达精准的高质量 Prompt。"
            "请按照提供的结构模板，补充缺失的关键信息，精简冗余表达，"
            "确保每个部分都有具体、可操作的内容。"
        ),
        "user": (
            "请将以下内容优化为结构化的 Prompt。保留模板框架，"
            "纠正模糊表述，补全缺失的关键要素。\n\n"
            "```\n{template_text}\n```\n\n"
            "只输出最终优化后的 Prompt 文本，不要任何额外解释。"
        ),
    },
    "en": {
        "system": (
            "Your task is to optimize the following raw requirements into a well-structured, "
            "clear, and precise high-quality Prompt. Follow the provided structural template, "
            "fill in missing key information, reduce redundant expressions, and ensure each "
            "section has specific, actionable content."
        ),
        "user": (
            "Please optimize the following into a structured Prompt. Preserve the template "
            "framework, correct vague phrasing, and complete missing key elements.\n\n"
            "```\n{template_text}\n```\n\n"
            "Output only the final optimized Prompt text, without any additional explanation."
        ),
    },
}


async def ai_refine(
    template_text: str,
    domain_result: DomainResult,
    model_name: str = "deepseek-chat",
    language: str = "zh",
) -> tuple[str, str]:
    strategy = registry.get(domain_result.domain)
    role_instruction = strategy.role_instruction if strategy else "你是一位 Prompt 优化专家。"

    lang = "zh" if language not in ("zh", "en") else language
    prompts = _LANG_PROMPTS[lang]

    system_prompt = f"{role_instruction}\n\n{prompts['system']}"
    user_prompt = prompts["user"].format(template_text=template_text)

    adapter = get_adapter(model_name)
    result = await adapter.generate(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.3,
    )

    return result, adapter.model_name
