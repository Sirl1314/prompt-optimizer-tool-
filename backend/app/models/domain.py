from sqlalchemy import String, Text, Integer, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base


class DomainStrategy(Base):
    __tablename__ = "domain_strategies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    domain_name: Mapped[str] = mapped_column(String(50), unique=True)
    display_name: Mapped[str] = mapped_column(String(50), default="")
    template: Mapped[dict] = mapped_column(JSON)
    role_instruction: Mapped[str] = mapped_column(Text)
    rules: Mapped[list] = mapped_column(JSON)
    scoring_weights: Mapped[dict] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
