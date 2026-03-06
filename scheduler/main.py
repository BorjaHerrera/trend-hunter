import logging
from agents.trend_hunter_agent import TrendHunterAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Iniciando Trend Hunter Agent...")
    agent = TrendHunterAgent(industry="localization")
    trends, insights = agent.collect_trends()
    logger.info("Trend Hunter Agent finalizado.")