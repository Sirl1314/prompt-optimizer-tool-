from sqlalchemy import String, Text, Integer, Float, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class ModelConfig(Base):
    __tablename__ = "model_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model_name: Mapped[str] = mapped_column(String(100))
    provider: Mapped[str] = mapped_column(String(50))
    api_endpoint: Mapped[str] = mapped_column(String(300))
    api_key_ref: Mapped[str] = mapped_column(Text)
    max_tokens: Mapped[int] = mapped_column(Integer, default=4096)
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=0)
