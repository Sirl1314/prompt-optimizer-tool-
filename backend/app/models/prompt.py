import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base
import enum


class PromptStatus(str, enum.Enum):
    draft = "draft"
    optimized = "optimized"
    archived = "archived"


class PromptRecord(Base):
    __tablename__ = "prompt_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(200), default="未命名")
    raw_prompt: Mapped[str] = mapped_column(Text)
    optimized_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    domain: Mapped[str] = mapped_column(String(50), default="general")
    source_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    token_count_raw: Mapped[int] = mapped_column(Integer, default=0)
    token_count_optimized: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[PromptStatus] = mapped_column(SAEnum(PromptStatus), default=PromptStatus.draft)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8))))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8))), onupdate=lambda: datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8))))

    sessions: Mapped[list["OptimizationSession"]] = relationship(
        back_populates="prompt", cascade="all, delete-orphan"
    )


class OptimizationSession(Base):
    __tablename__ = "optimization_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    prompt_id: Mapped[str] = mapped_column(String(36), ForeignKey("prompt_records.id"))
    version: Mapped[int] = mapped_column(Integer, default=1)
    optimized_text: Mapped[str] = mapped_column(Text)
    model_used: Mapped[str] = mapped_column(String(100))
    domain_strategy: Mapped[str] = mapped_column(String(50))
    scores: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    diff_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_delta: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8))))

    prompt: Mapped["PromptRecord"] = relationship(back_populates="sessions")
