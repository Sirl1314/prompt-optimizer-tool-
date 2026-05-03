import tiktoken


_encoder_cache = {}


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    encoding_name = "cl100k_base"
    if encoding_name not in _encoder_cache:
        _encoder_cache[encoding_name] = tiktoken.get_encoding(encoding_name)
    encoder = _encoder_cache[encoding_name]
    return len(encoder.encode(text))


def estimate_tokens(text: str) -> dict:
    token_count = count_tokens(text)
    return {
        "token_count": token_count,
        "char_count": len(text),
        "rough_cost_estimate": f"~{token_count} tokens",
    }
