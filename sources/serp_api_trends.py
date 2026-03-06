from serpapi import GoogleSearch
import pandas as pd
from datetime import datetime
import logging
from config.settings import SERPAPI_KEY

logger = logging.getLogger(__name__)


class GoogleTrendSource:

    REGION_MAP = {
        "ES": "ES",
        "US": "US"
    }

    def __init__(self):
        self.api_key = SERPAPI_KEY

    def get_trending_searches(self, regions=None):

        if regions is None:
            regions = ["ES"]

        try:
            all_trends = []

            for region in regions:

                geo = self.REGION_MAP.get(region)

                if not geo:
                    logger.warning(f"Región no soportada: {region}")
                    continue

                search = GoogleSearch({
                    "engine": "google_trends_trending_now",
                    "geo": geo,
                    "api_key": self.api_key
                })

                results = search.get_dict()
                trending = results.get("trending_searches", [])

                for item in trending:
                    all_trends.append({
                        "trend": item.get("query", ""),
                        "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                        "source": "google_trends",
                        "region": region
                    })

            if all_trends:
                return pd.DataFrame(all_trends)

            return pd.DataFrame(columns=["trend", "date", "source", "region"])

        except Exception as e:
            logger.error(f"Error al obtener tendencias de Google Trends: {e}")
            return pd.DataFrame(columns=["trend", "date", "source", "region"])