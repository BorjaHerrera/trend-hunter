import sqlite3
import pandas as pd
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "trend_hunter.db")


class Database:

    def __init__(self):
        self.db_path = DB_PATH
        self._create_tables()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS trends (
                    id               INTEGER PRIMARY KEY AUTOINCREMENT,
                    trend            TEXT NOT NULL,
                    source           TEXT NOT NULL,
                    region           TEXT NOT NULL,
                    industry         TEXT NOT NULL,
                    snapshot_date    TEXT NOT NULL,
                    first_seen_date  TEXT NOT NULL,
                    engagement       REAL DEFAULT 0,
                    source_score     REAL DEFAULT 0,
                    engagement_score REAL DEFAULT 0,
                    multi_source_score REAL DEFAULT 0,
                    total_score      REAL DEFAULT 0,
                    trend_rank       INTEGER DEFAULT 0,
                    trend_stage      TEXT DEFAULT 'EMERGING',
                    created_at       TEXT NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS trend_insights (
                    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
                    trend                TEXT NOT NULL,
                    industry             TEXT NOT NULL,
                    snapshot_date        TEXT NOT NULL,
                    content_idea         TEXT,
                    business_opportunity TEXT,
                    business_angle       TEXT,
                    priority_level       TEXT,
                    llm_relevance_score  REAL DEFAULT 0,
                    created_at           TEXT NOT NULL
                )
            """)

            logger.info("Tablas creadas o verificadas correctamente")

    def _get_first_seen_dates(self, trends: list, industry: str) -> dict:
        """Devuelve first_seen_date para cada tendencia. Si es nueva, usa hoy."""
        today = datetime.now().strftime("%d-%m-%Y")

        with self._get_connection() as conn:
            placeholders = ",".join(["?"] * len(trends))
            rows = conn.execute(
                f"""
                SELECT trend, MIN(first_seen_date) as first_seen_date
                FROM trends
                WHERE trend IN ({placeholders}) AND industry = ?
                GROUP BY trend
                """,
                trends + [industry]
            ).fetchall()

        existing = {row[0]: row[1] for row in rows}

        return {trend: existing.get(trend, today) for trend in trends}

    def save_trends(self, df: pd.DataFrame, industry: str):
        try:
            if df.empty:
                logger.warning("No hay tendencias para guardar")
                return

            snapshot_date = datetime.now().strftime("%d-%m-%Y")
            now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            df = df.copy()
            df["industry"] = industry
            df["snapshot_date"] = snapshot_date
            df["created_at"] = now
            df["trend_stage"] = df.get("trend_stage", "EMERGING")

            # first_seen_date
            first_seen_map = self._get_first_seen_dates(df["trend"].tolist(), industry)
            df["first_seen_date"] = df["trend"].map(first_seen_map)

            columns = [
                "trend", "source", "region", "industry", "snapshot_date",
                "first_seen_date", "engagement", "source_score", "engagement_score",
                "multi_source_score", "total_score", "trend_rank", "trend_stage", "created_at"
            ]

            df[columns].to_sql(
                name="trends",
                con=self._get_connection(),
                if_exists="append",
                index=False
            )

            logger.info(f"Guardadas {len(df)} tendencias en la base de datos")

        except Exception as e:
            logger.error(f"Error guardando en base de datos: {e}")

    def get_trends_by_date(self, snapshot_date: str) -> pd.DataFrame:
        with self._get_connection() as conn:
            return pd.read_sql(
                "SELECT * FROM trends WHERE snapshot_date = ?",
                conn,
                params=(snapshot_date,)
            )

    def get_trends_by_rank(self, top_n: int = 20, snapshot_date: str = None) -> pd.DataFrame:
        if snapshot_date is None:
            snapshot_date = datetime.now().strftime("%d-%m-%Y")

        with self._get_connection() as conn:
            return pd.read_sql(
                """
                SELECT * FROM trends
                WHERE snapshot_date = ?
                ORDER BY trend_rank ASC
                LIMIT ?
                """,
                conn,
                params=(snapshot_date, top_n)
            )

    def get_trend_history(self, trend: str, days: int = 7) -> pd.DataFrame:
        with self._get_connection() as conn:
            return pd.read_sql(
                """
                SELECT * FROM trends
                WHERE trend = ?
                ORDER BY snapshot_date DESC
                LIMIT ?
                """,
                conn,
                params=(trend, days)
            )
        
    def save_insights(self, df: pd.DataFrame, industry: str):
        try:
            if df.empty:
                logger.warning("No hay insights para guardar")
                return

            snapshot_date = datetime.now().strftime("%d-%m-%Y")
            now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            df = df.copy()
            df["snapshot_date"] = snapshot_date
            df["created_at"] = now

            columns = [
                "trend", "industry", "snapshot_date", "content_idea",
                "business_opportunity", "business_angle",
                "priority_level", "llm_relevance_score", "created_at"
            ]

            df[columns].to_sql(
                name="trend_insights",
                con=self._get_connection(),
                if_exists="append",
                index=False
            )

            logger.info(f"Guardados {len(df)} insights en la base de datos")

        except Exception as e:
            logger.error(f"Error guardando insights: {e}")