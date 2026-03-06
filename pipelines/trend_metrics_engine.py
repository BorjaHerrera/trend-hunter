import pandas as pd
import logging

logger = logging.getLogger(__name__)


class TrendMetricsEngine:

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:

        if df.empty:
            return df

        df = df.copy()

        # 1. Score base por fuente
        df["source_score"] = df["source"].map({
            "google_trends": 3,
            "youtube_trends": 2,
            "google_news": 1
        }).fillna(0)

        # 2. Score por engagement (YouTube views normalizado)
        max_engagement = df["engagement"].max()
        if max_engagement > 0:
            df["engagement_score"] = (df["engagement"] / max_engagement * 10).round(2)
        else:
            df["engagement_score"] = 0

        # 3. Score por apariciones en múltiples fuentes
        trend_counts = df.groupby("trend")["source"].nunique()
        df["multi_source_score"] = df["trend"].map(trend_counts) * 2

        # 4. Score total
        df["total_score"] = (
            df["source_score"] +
            df["engagement_score"] +
            df["multi_source_score"]
        ).round(2)

        # 5. Ordenar por score descendente
        df = df.sort_values("total_score", ascending=False)
        df = df.reset_index(drop=True)

        # 6. Rank
        df["trend_rank"] = range(1, len(df) + 1)

        logger.info(f"TrendMetricsEngine: scores calculados para {len(df)} tendencias")

        return df