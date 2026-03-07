import pandas as pd
import logging
import json
import time
from llm.factory import get_llm_client
from llm.prompts import build_pre_filter_prompt
from storage.database import Database

logger = logging.getLogger(__name__)

SOFT_KEYWORDS = [
    "ai", "ia", "voice", "video", "lang", "trad", "dub", "sound",
    "tech", "cloud", "llm", "gpt", "model", "sora", "runway", "openai",
    "elevenlabs", "media", "stream", "content", "subtitle", "caption",
    "translate", "locali", "automation", "neural", "speech", "audio"
]


class LLMEnricher:

    def __init__(self):
        self.client = get_llm_client()
        self.db = Database()

    def enrich(self, df: pd.DataFrame, industry: str, top_n: int = 15) -> pd.DataFrame:
        if df.empty:
            return df

        # PASO 1: Filtro blando
        all_trends = df["trend"].tolist()
        soft_filtered = [t for t in all_trends if any(k in t.lower() for k in SOFT_KEYWORDS)]

        if not soft_filtered:
            logger.info("Filtro blando: ninguna tendencia pasó el filtro")
            return pd.DataFrame()

        logger.info(f"Filtro blando: {len(soft_filtered)} tendencias de {len(all_trends)}")

        # PASO 2: Pre-filtro Gemini en batch (chunks de 50)
        relevant_trends = []
        chunks = [soft_filtered[i:i+50] for i in range(0, len(soft_filtered), 50)]

        for chunk in chunks:
            filtered = self._pre_filter_with_gemini(chunk)
            relevant_trends.extend(filtered)

        if not relevant_trends:
            logger.info("Pre-filtro Gemini: ninguna tendencia relevante encontrada")
            return pd.DataFrame()

        logger.info(f"Pre-filtro Gemini: {len(relevant_trends)} tendencias relevantes")

        # PASO 3: Análisis individual de las relevantes (top_n)
        relevant_df = df[df["trend"].isin(relevant_trends)].head(top_n)

        insights = []
        for _, row in relevant_df.iterrows():
            trend = row["trend"]
            logger.info(f"Analizando en profundidad: {trend}")

            insight = self.client.analyze_trend(trend, industry)
            time.sleep(5)

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

    def _pre_filter_with_gemini(self, trends: list) -> list:
        try:
            prompt = build_pre_filter_prompt(trends)
            response = self.client.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            data = json.loads(response.text)
            return data.get("relevant", [])

        except Exception as e:
            logger.error(f"Error en pre-filtro Gemini: {e}")
            return trends