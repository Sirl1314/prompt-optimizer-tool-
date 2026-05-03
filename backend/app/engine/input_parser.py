import re
from ..schemas.pipeline import ParsedInput
from ..utils.token_counter import count_tokens


def parse_input(raw_text: str) -> ParsedInput:
    char_count = len(raw_text)
    word_count = len(raw_text.split()) if " " in raw_text else len(raw_text)
    has_code_blocks = bool(re.search(r"```", raw_text))
    has_markdown = bool(re.search(r"[#*\-\[\]()]", raw_text))
    tokens = count_tokens(raw_text)

    ascii_chars = sum(1 for c in raw_text if ord(c) < 128)
    language = "en" if ascii_chars / max(char_count, 1) > 0.7 else "zh"

    return ParsedInput(
        raw_text=raw_text,
        char_count=char_count,
        word_count=word_count,
        language=language,
        token_count=tokens,
        has_code_blocks=has_code_blocks,
        has_markdown=has_markdown,
    )
