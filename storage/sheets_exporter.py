#Para exportar las tendencias relevantes a Google Sheets

import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

CREDENTIALS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config/credentials.json")
SHEET_NAME = "Trend Hunter"

SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]


class SheetsExporter:

    def __init__(self):
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_PATH, SCOPES)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open(SHEET_NAME)

    def export_daily_insights(self, trends_df: pd.DataFrame, insights_df: pd.DataFrame):
        """Exporta las tendencias relevantes del día a Google Sheets."""
        try:
            worksheet = self._get_or_create_worksheet("Daily Insights")
            rows = self._build_rows(trends_df, insights_df)

            if not rows:
                logger.warning("No hay insights para exportar")
                return

            self._write_headers(worksheet)
            self._append_rows(worksheet, rows)

            logger.info(f"Exportadas {len(rows)} tendencias a Google Sheets")

        except Exception as e:
            logger.error(f"Error exportando a Google Sheets: {e}")

    def _get_or_create_worksheet(self, name: str):
        try:
            return self.sheet.worksheet(name)
        except gspread.exceptions.WorksheetNotFound:
            return self.sheet.add_worksheet(title=name, rows=1000, cols=20)

    def _write_headers(self, worksheet):
        headers = worksheet.row_values(1)
        if not headers:
            worksheet.append_row([
                "Fecha", "Tendencia", "Fuente", "Región", "Score",
                "Rank", "Stage", "Movement", "First Seen",
                "Content Idea", "Business Opportunity", "Business Angle",
                "Priority", "LLM Score"
            ])

    def _build_rows(self, trends_df: pd.DataFrame, insights_df: pd.DataFrame) -> list:
        if insights_df.empty:
            return []

        today = datetime.now().strftime("%d-%m-%Y")
        rows = []

        for _, insight in insights_df.iterrows():
            trend_data = trends_df[trends_df["trend"] == insight["trend"]]

            if trend_data.empty:
                continue

            row = trend_data.iloc[0]

            rows.append([
                today,
                insight["trend"],
                row.get("source", ""),
                row.get("region", ""),
                float(row.get("total_score", 0)),
                int(row.get("trend_rank", 0)),
                row.get("trend_stage", "EMERGING"),
                int(row.get("movement", 0)),
                row.get("first_seen_date", today),
                insight.get("content_idea", ""),
                insight.get("business_opportunity", ""),
                insight.get("business_angle", ""),
                insight.get("priority_level", ""),
                insight.get("llm_relevance_score", 0)
            ])

        return rows

    def _append_rows(self, worksheet, rows: list):
        worksheet.insert_rows(rows, row=2, value_input_option="RAW")