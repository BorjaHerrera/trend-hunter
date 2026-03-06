import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class TrendAggregator:

    def aggregate(self, dataframes: list) -> pd.DataFrame:

        if not dataframes:
            logger.warning("No hay datos para agregar")
            return pd.DataFrame(columns=["trend", "source", "region", "date", "engagement", "extra_context"])

        normalized = []

        for df in dataframes:
            if df.empty:
                continue
            normalized.append(self._normalize(df))

        if not normalized:
            return pd.DataFrame(columns=["trend", "source", "region", "date", "engagement", "extra_context"])

        result = pd.concat(normalized, ignore_index=True)
        result = result.drop_duplicates(subset=["trend", "source", "region"])

        logger.info(f"Total tendencias agregadas: {len(result)}")

        return result

    def _normalize(self, df: pd.DataFrame) -> pd.DataFrame:

        normalized = pd.DataFrame()

        normalized["trend"] = df["trend"]
        normalized["source"] = df["source"]
        normalized["region"] = df["region"]
        normalized["date"] = df["date"]

        # engagement
        if "views" in df.columns:
            normalized["engagement"] = df["views"]
        else:
            normalized["engagement"] = 0

        # extra_context
        if "keyword" in df.columns:
            normalized["extra_context"] = df["keyword"]
        else:
            normalized["extra_context"] = ""

        return normalized