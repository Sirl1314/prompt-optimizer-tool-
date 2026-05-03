from openai import AsyncOpenAI
from ..config import QWEN_API_KEY, QWEN_BASE_URL
from ..utils.exceptions import LLMException
from .base import BaseAdapter


class QwenAdapter(BaseAdapter):
    model_name = "qwen-turbo"
    provider = "qwen"

    def __init__(self):
        if not QWEN_API_KEY:
            raise ValueError("QWEN_API_KEY not configured")
        self.client = AsyncOpenAI(
            api_key=QWEN_API_KEY,
            base_url=QWEN_BASE_URL,
        )

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise LLMException(502, f"Qwen call failed: {str(e)}")

    async def test_connection(self) -> bool:
        try:
            await self.generate("Hello", "Hi", max_tokens=10)
            return True
        except Exception:
            return False
