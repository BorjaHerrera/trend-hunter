from config.industry_config import industry_config
from sources.youtube_trends import YoutubeTrendSource
from sources.google_news import GoogleNewsSource
from sources.serp_api_trends import GoogleTrendSource
from pipelines.trend_aggregator import TrendAggregator
from pipelines.trend_cleaner import TrendCleaner
from pipelines.trend_metrics_engine import TrendMetricsEngine
from storage.database import Database
from pipelines.trend_evolution_analyzer import TrendEvolutionAnalyzer
from pipelines.llm_enricher import LLMEnricher
from storage.sheets_exporter import SheetsExporter
from notifications.email_reporter import EmailReporter
import logging

logger = logging.getLogger(__name__)

class TrendHunterAgent:

    def __init__(self, industry):
        self.industry = industry
        self.youtube = YoutubeTrendSource()
        self.google = GoogleTrendSource()
        self.news = GoogleNewsSource()
        self.aggregator = TrendAggregator()
        self.cleaner = TrendCleaner()
        self.metrics = TrendMetricsEngine()
        self.db = Database()
        self.evolution = TrendEvolutionAnalyzer()
        self.enricher = LLMEnricher()
        self.sheets = SheetsExporter()
        self.email = EmailReporter()

    def collect_trends(self):
        config = industry_config[self.industry]

        logger.info(f"Recopilando tendencias para: {self.industry}")

        # Google Trends
        google_data = self.google.get_trending_searches(
            config["sources"]["google_trends"]["regions"]
        )

        # YouTube
        youtube_data = self.youtube.get_trending_videos(
            config["sources"]["youtube"]["regions"]
        )

        # Google News
        news_data = self.news.get_news(
            config["sources"]["google_news"]["keywords"],
            config["sources"]["google_news"]["regions"]
        )

        unified = self.aggregator.aggregate([google_data, youtube_data, news_data])
        cleaned = self.cleaner.clean(unified)
        scored = self.metrics.calculate(cleaned)
        evolved = self.evolution.analyze(scored)

        logger.info(f"Total tendencias tras limpieza: {len(evolved)}")
        self.db.save_trends(evolved, self.industry)
        insights = self.enricher.enrich(evolved, self.industry, top_n=15)
        
        try:
            self.sheets.export_daily_insights(evolved, insights)
        except Exception as e:
            logger.error(f"Error exportando a Sheets: {e}")

        self.email.send_daily_report(insights, evolved, top_n=10)
        return evolved, insights


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    agent = TrendHunterAgent(industry="localization")
    trends, insights = agent.collect_trends()
    print(trends)
    print(insights)