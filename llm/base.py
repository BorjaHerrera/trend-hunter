from abc import ABC, abstractmethod
from llm.models import TrendInsight


class LLMClientBase(ABC):

    @abstractmethod
    def analyze_trend(self, trend: str, industry: str) -> TrendInsight:
        raise NotImplementedError