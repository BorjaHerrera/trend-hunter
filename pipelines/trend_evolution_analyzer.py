import pandas as pd
from datetime import datetime, timedelta
import logging
from storage.database import Database

logger = logging.getLogger(__name__)


class TrendEvolutionAnalyzer:

    def __init__(self):
        self.db = Database()

    def analyze(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analiza la evolución de las tendencias comparando con días anteriores."""

        if df.empty:
            return df

        today = datetime.now().strftime("%d-%m-%Y")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%d-%m-%Y")
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%d-%m-%Y")

        yesterday_df = self.db.get_trends_by_date(yesterday)
        week_ago_df = self.db.get_trends_by_date(week_ago)

        yesterday_ranks = self._build_rank_map(yesterday_df)
        week_ago_ranks = self._build_rank_map(week_ago_df)
        today_first_seen = self._build_first_seen_map(df)

        df = df.copy()
        df["movement"] = df.apply(
            lambda row: self._calculate_movement(row, yesterday_ranks), axis=1
        )
        df["trend_stage"] = df.apply(
            lambda row: self._calculate_stage(row, yesterday_ranks, week_ago_ranks, today_first_seen),
            axis=1
        )

        logger.info(f"TrendEvolutionAnalyzer: evolución calculada para {len(df)} tendencias")

        return df

    def _build_rank_map(self, df: pd.DataFrame) -> dict:
        if df.empty:
            return {}
        return dict(zip(df["trend"], df["trend_rank"]))

    def _build_first_seen_map(self, df: pd.DataFrame) -> dict:
        if "first_seen_date" not in df.columns:
            return {}
        return dict(zip(df["trend"], df["first_seen_date"]))

    def _calculate_movement(self, row, yesterday_ranks: dict) -> int:
        """Calcula el movimiento de posición respecto a ayer."""
        today_rank = row["trend_rank"]
        yesterday_rank = yesterday_ranks.get(row["trend"])

        if yesterday_rank is None:
            return 0  # tendencia nueva, sin movimiento previo

        return yesterday_rank - today_rank  # positivo = subió, negativo = bajó

    def _calculate_stage(self, row, yesterday_ranks: dict, week_ago_ranks: dict, first_seen_map: dict) -> str:
        """Determina el stage de la tendencia."""
        trend = row["trend"]
        today_rank = row["trend_rank"]
        yesterday_rank = yesterday_ranks.get(trend)
        week_ago_rank = week_ago_ranks.get(trend)
        first_seen = first_seen_map.get(trend)
        today = datetime.now().strftime("%d-%m-%Y")

        # Nueva tendencia
        if first_seen == today or yesterday_rank is None:
            return "EMERGING"

        movement = yesterday_rank - today_rank

        # Lleva una semana y sigue arriba
        if week_ago_rank is not None and today_rank <= 50 and movement >= 0:
            return "PEAKING"

        # Subiendo
        if movement > 5:
            return "GROWING"

        # Bajando
        if movement < -5:
            return "DECLINING"

        return "EMERGING"