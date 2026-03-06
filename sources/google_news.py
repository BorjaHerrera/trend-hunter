from serpapi import GoogleSearch
import pandas as pd
from datetime import datetime
import logging
from config.settings import SERPAPI_KEY

logger = logging.getLogger(__name__)


class GoogleNewsSource:

    def __init__(self):
        self.api_key = SERPAPI_KEY

    def get_news(self, keywords=None, regions=None):

        if keywords is None:
            keywords = ["localization AI", "voice AI", "video dubbing"]

        if regions is None:
            regions = ["ES", "US"]

        try:
            all_news = []

            for keyword in keywords:
                for region in regions:

                    search = GoogleSearch({
                        "engine": "google_news",
                        "q": keyword,
                        "gl": region,
                        "api_key": self.api_key
                    })

                    results = search.get_dict()
                    news = results.get("news_results", [])

                    for item in news:
                        all_news.append({
                            "trend": item.get("title", ""),
                            "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                            "source": "google_news",
                            "region": region,
                            "keyword": keyword
                        })

            if all_news:
                return pd.DataFrame(all_news)

            return pd.DataFrame(columns=["trend", "date", "source", "region", "keyword"])

        except Exception as e:
            logger.error(f"Error al obtener noticias de Google News: {e}")
            return pd.DataFrame(columns=["trend", "date", "source", "region", "keyword"])