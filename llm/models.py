from dataclasses import dataclass
from typing import Optional

@dataclass
class TrendInsight:
    is_relevant: bool
    content_idea: Optional[str] = None
    business_opportunity: Optional[str] = None
    business_angle: Optional[str] = None
    priority_level: Optional[str] = None
    llm_relevance_score: float = 0.0