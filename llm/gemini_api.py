import json
import logging
from google import genai
from llm.base import LLMClientBase
from llm.models import TrendInsight
from llm.prompts import build_trend_analysis_prompt
from config.settings import GEMINI_API_KEY

logger = logging.getLogger(__name__)


class GeminiClient(LLMClientBase):

    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def analyze_trend(self, trend: str, industry: str) -> TrendInsight:
        try:
            prompt = build_trend_analysis_prompt(trend, industry)
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )

            if not response.text:
                return TrendInsight(is_relevant=False)

            return self._parse_response(response.text)

        except Exception as e:
            logger.error(f"Error analizando tendencia '{trend}': {e}")
            return TrendInsight(is_relevant=False)

    def _parse_response(self, response_text: str) -> TrendInsight:
        try:
            clean = response_text.strip().replace("```json", "").replace("```", "")
            data = json.loads(clean)

            return TrendInsight(
                is_relevant=data.get("is_relevant", False),
                content_idea=data.get("content_idea"),
                business_opportunity=data.get("business_opportunity"),
                business_angle=data.get("business_angle"),
                priority_level=data.get("priority_level"),
                llm_relevance_score=float(data.get("llm_relevance_score", 0.0))
            )

        except Exception as e:
            logger.error(f"Error parseando respuesta de Gemini: {e}")
            return TrendInsight(is_relevant=False)