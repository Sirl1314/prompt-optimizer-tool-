from .base import DomainStrategyBase, DomainRegistry, CustomDomainStrategy, registry
from .code_dev import CodeDevStrategy
from .copywriting import CopywritingStrategy
from .data_analysis import DataAnalysisStrategy
from .marketing import MarketingStrategy
from .healthcare import HealthcareStrategy
from .legal import LegalStrategy
from .education import EducationStrategy
from .ai_visual import AIVisualStrategy


def register_all():
    registry.register(CodeDevStrategy())
    registry.register(CopywritingStrategy())
    registry.register(DataAnalysisStrategy())
    registry.register(MarketingStrategy())
    registry.register(HealthcareStrategy())
    registry.register(LegalStrategy())
    registry.register(EducationStrategy())
    registry.register(AIVisualStrategy())


register_all()
