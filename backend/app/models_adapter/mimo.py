import os
from openai import AsyncOpenAI
from typing import Optional
from .base import BaseAdapter
from ..config import MIMO_API_KEY, MIMO_BASE_URL
from ..utils.exceptions import LLMException

class MiMoAdapter(BaseAdapter):
    """
    小米 MiMo 大模型适配器
    完全兼容 OpenAI 接口规范
    """
    model_name = "mimo-v2.5-pro"
    provider = "xiaomi_mimo"

    def __init__(self):
        self.api_key = MIMO_API_KEY
        self.base_url = MIMO_BASE_URL

        if not self.api_key:
            raise ValueError("MiMo API 密钥未配置，请检查环境变量 MIMO_API_KEY")

        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """调用小米 MiMo 生成内容"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0
            )
            return response.choices[0].message.content or ""

        except Exception as e:
            raise LLMException(502, f"MiMo 模型调用失败: {str(e)}")

    async def test_connection(self) -> bool:
        """测试连接是否正常"""
        try:
            await self.generate(
                system_prompt="You are MiMo",
                user_prompt="hello",
                max_tokens=10
            )
            return True
        except Exception:
            return False