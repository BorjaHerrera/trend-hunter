import pandas as pd
import logging
import time
from llm.factory import get_llm_client
from storage.database import Database

logger = logging.getLogger(__name__)

RELEVANT_KEYWORDS = [
    "ai", "voice", "dubbing", "localization", "translation",
    "subtitle", "elearning", "media", "cloning", "localización",
    "traducción", "doblaje", "subtítulos", "voces", "idioma",
    "language", "multilingual", "content creation", "automation"
]


class LLMEnricher:

    def __init__(self):
        self.client = get_llm_client()
        self.db = Database()

    def enrich(self, df: pd.DataFrame, industry: str, top_n: int = 15) -> pd.DataFrame:
        """Analiza las top N tendencias con Gemini y guarda los insights."""

        if df.empty:
            return df

        # Filtrar solo tendencias potencialmente relevantes
        filtered_df = df[
            df["trend"].str.lower().str.contains("|".join(RELEVANT_KEYWORDS), na=False)
        ].head(top_n)

        # Si no hay tendencias relevantes usar las top N por score
        if filtered_df.empty:
            logger.warning("No hay tendencias con keywords relevantes, usando top N por score")
            filtered_df = df.head(top_n)

        insights = []
        for _, row in filtered_df.iterrows():
            trend = row["trend"]
            logger.info(f"Analizando: {trend}")

            insight = self.client.analyze_trend(trend, industry)
            time.sleep(13)  # 5 requests/minuto en plan gratuito. Con Gemini Pro reducir a 2 segundos.

            if insight.is_relevant:
                insights.append({
                    "trend": trend,
                    "industry": industry,
                    "content_idea": insight.content_idea,
                    "business_opportunity": insight.business_opportunity,
                    "business_angle": insight.business_angle,
                    "priority_level": insight.priority_level,
                    "llm_relevance_score": insight.llm_relevance_score
                })

        if not insights:
            logger.info("No se encontraron tendencias relevantes")
            return pd.DataFrame()

        result = pd.DataFrame(insights)
        self.db.save_insights(result, industry)

        logger.info(f"LLMEnricher: {len(result)} tendencias relevantes encontradas")

        return result