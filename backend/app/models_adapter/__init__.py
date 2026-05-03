from .base import BaseAdapter
from .deepseek import DeepSeekAdapter
from .openai import OpenAIAdapter
from .qwen import QwenAdapter
from .mimo import MiMoAdapter
from .custom import CustomAdapter


_adapters: dict[str, BaseAdapter] = {}
_custom_adapters: dict[str, CustomAdapter] = {}
_custom_loaded: bool = False

BUILTIN_MODELS = {"deepseek-chat", "gpt-3.5-turbo", "qwen-turbo", "mimo-v2.5-pro"}


def _init_adapters():
    if _adapters:
        return
    for cls in [DeepSeekAdapter, OpenAIAdapter, QwenAdapter, MiMoAdapter]:
        try:
            instance = cls()
            _adapters[instance.model_name] = instance
        except Exception:
            pass


async def load_custom_from_db(db):
    """Load all custom model configs from DB and register as adapters."""
    global _custom_loaded
    if _custom_loaded:
        return
    from ..models.model_config import ModelConfig
    from sqlalchemy import select
    result = await db.execute(select(ModelConfig).where(ModelConfig.is_available == True))
    for row in result.scalars().all():
        if row.model_name in BUILTIN_MODELS:
            continue
        adapter = CustomAdapter(
            model_name=row.model_name,
            provider=row.provider,
            api_endpoint=row.api_endpoint,
            api_key=row.api_key_ref,
            max_tokens=row.max_tokens,
            temperature=row.temperature,
            db_id=row.id,
        )
        _custom_adapters[adapter.model_name] = adapter
    _custom_loaded = True


def reset_custom_cache():
    """Allow reloading custom adapters after create/update/delete."""
    global _custom_loaded
    _custom_loaded = False


def register_custom(adapter: CustomAdapter):
    _custom_adapters[adapter.model_name] = adapter
    reset_custom_cache()


def unregister_custom(model_name: str):
    _custom_adapters.pop(model_name, None)
    reset_custom_cache()


def get_adapter(model_name: str | None = None) -> BaseAdapter:
    _init_adapters()
    if model_name and model_name in _custom_adapters:
        return _custom_adapters[model_name]
    if model_name and model_name in _adapters:
        return _adapters[model_name]
    for a in _custom_adapters.values():
        return a
    for a in _adapters.values():
        return a
    raise RuntimeError("没有可用的 LLM 适配器，请至少配置一个 API 密钥")


def list_adapters() -> list[dict]:
    _init_adapters()
    result = []
    for a in _adapters.values():
        result.append({
            "model_name": a.model_name,
            "provider": a.provider,
            "is_custom": False,
        })
    for a in _custom_adapters.values():
        result.append({
            "model_name": a.model_name,
            "provider": a.provider,
            "is_custom": True,
            "db_id": a.db_id,
        })
    return result


__all__ = ["BaseAdapter", "CustomAdapter", "get_adapter", "list_adapters",
           "register_custom", "unregister_custom", "load_custom_from_db", "BUILTIN_MODELS"]
