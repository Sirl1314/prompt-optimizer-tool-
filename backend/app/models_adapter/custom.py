from openai import AsyncOpenAI
from .base import BaseAdapter
from ..utils.exceptions import LLMException


class CustomAdapter(BaseAdapter):
    """A user-defined adapter wrapping any OpenAI-compatible API endpoint."""

    def __init__(self, model_name: str, provider: str, api_endpoint: str,
                 api_key: str, max_tokens: int = 4096, temperature: float = 0.7,
                 db_id: int | None = None):
        self._model_name = model_name
        self._provider = provider
        self._max_tokens = max_tokens
        self._temperature = temperature
        self.db_id = db_id
        self.client = AsyncOpenAI(api_key=api_key, base_url=api_endpoint)

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def provider(self) -> str:
        return self._provider

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self._model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature if temperature is not None else self._temperature,
                max_tokens=max_tokens if max_tokens is not None else self._max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise LLMException(502, f"自定义模型 {self._model_name} 调用失败: {str(e)}")

    async def test_connection(self) -> bool:
        try:
            await self.generate("Hello", "Hi", max_tokens=10)
            return True
        except Exception:
            return False
