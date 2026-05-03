from abc import ABC, abstractmethod


class BaseAdapter(ABC):
    @property
    @abstractmethod
    def model_name(self) -> str:
        ...

    @property
    @abstractmethod
    def provider(self) -> str:
        ...

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> str:
        ...

    @abstractmethod
    async def test_connection(self) -> bool:
        ...
