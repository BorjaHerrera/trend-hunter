from googleapiclient.discovery import build
import pandas as pd
from datetime import datetime
import logging
from config.settings import YOUTUBE_API_KEY

logger = logging.getLogger(__name__)

class YoutubeTrendSource:

    def __init__(self):
        self.youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    def get_trending_videos(self, regions=None, max_results=20):  # 1. Argumento mutable
        if regions is None:
            regions = ["ES", "US"]

        try:
            all_videos = []

            for region in regions:

                request = self.youtube.videos().list(
                    part="snippet,statistics",
                    chart="mostPopular",
                    regionCode=region,
                    maxResults=max_results
                )

                response = request.execute()

                for item in response.get("items", []):

                    all_videos.append({
                        "trend": item["snippet"]["title"],
                        "views": int(item["statistics"].get("viewCount", 0)),  # 2. Convertir a int
                        "region": region,
                        "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                        "source": "youtube_trends"
                    })

            return pd.DataFrame(all_videos)

        except Exception as e:
            logger.error(f"Error obteniendo tendencias de YouTube: {e}")  # 3. Logging

            return pd.DataFrame(columns=["trend","views","region","date","source"])