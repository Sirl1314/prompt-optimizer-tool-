from abc import ABC, abstractmethod
from typing import Any


class DomainStrategyBase(ABC):
    domain: str = "general"
    display_name: str = "通用"

    @property
    @abstractmethod
    def template(self) -> dict[str, str]:
        ...

    @property
    @abstractmethod
    def role_instruction(self) -> str:
        ...

    @property
    @abstractmethod
    def rules(self) -> list[dict[str, Any]]:
        ...

    @property
    @abstractmethod
    def scoring_weights(self) -> dict[str, float]:
        ...

    def get_template_as_string(self) -> str:
        lines = []
        for key, desc in self.template.items():
            lines.append(f"[{key}]\n{desc}\n")
        return "\n".join(lines)

    def check_rules(self, parsed_text: str) -> list[dict]:
        violations = []
        for rule in self.rules:
            match = self._apply_rule(rule, parsed_text)
            if match:
                violations.append({**rule, "detail": match})
        return violations

    def _apply_rule(self, rule: dict, text: str) -> str | None:
        import re
        pattern = rule.get("pattern", "")
        if pattern:
            if re.search(pattern, text, re.IGNORECASE):
                return None
        check_type = rule.get("check_type", "")
        if check_type == "missing_keyword":
            keywords = rule.get("keywords", [])
            for kw in keywords:
                if kw.lower() in text.lower():
                    return None
            return f"缺少关键词: {keywords}"
        if check_type == "missing_template_section":
            required = rule.get("required_sections", [])
            missing = [s for s in required if f"[{s}]" not in text]
            if missing:
                return f"缺少模板章节: {missing}"
        return None


class CustomDomainStrategy(DomainStrategyBase):
    """A dynamic domain strategy created from user-provided data at runtime."""

    def __init__(self, domain_name: str, display_name: str, template: dict[str, str],
                 role_instruction: str, rules: list[dict[str, Any]],
                 scoring_weights: dict[str, float], db_id: int | None = None):
        self.domain = domain_name
        self.display_name = display_name
        self._template = template
        self._role_instruction = role_instruction
        self._rules = rules
        self._scoring_weights = scoring_weights
        self.db_id = db_id

    @property
    def template(self) -> dict[str, str]:
        return self._template

    @property
    def role_instruction(self) -> str:
        return self._role_instruction

    @property
    def rules(self) -> list[dict[str, Any]]:
        return self._rules

    @property
    def scoring_weights(self) -> dict[str, float]:
        return self._scoring_weights


class DomainRegistry:
    _instance = None
    _strategies: dict[str, DomainStrategyBase] = {}
    _custom_counter: int = 0

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(self, strategy: DomainStrategyBase):
        self._strategies[strategy.domain] = strategy

    def unregister(self, domain: str):
        self._strategies.pop(domain, None)

    def get(self, domain: str) -> DomainStrategyBase | None:
        return self._strategies.get(domain)

    def list_all(self) -> list[DomainStrategyBase]:
        return list(self._strategies.values())

    def list_custom(self) -> list[CustomDomainStrategy]:
        return [s for s in self._strategies.values() if isinstance(s, CustomDomainStrategy)]

    def get_domain_names(self) -> list[str]:
        return list(self._strategies.keys())


registry = DomainRegistry()
