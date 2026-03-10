import smtplib
import logging
import pandas as pd
from email.message import EmailMessage
from datetime import datetime
from config.settings import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT

logger = logging.getLogger(__name__)


class EmailReporter:

    def __init__(self):
        self.sender = EMAIL_SENDER.strip()
        self.password = EMAIL_PASSWORD.strip()
        self.recipient = EMAIL_RECIPIENT.strip()

    def _clean_text(self, text: str) -> str:
        if not text:
            return ""
        return str(text).replace("\xa0", " ").replace("\u2019", "'").replace("\u2014", "-")

    def send_daily_report(self, insights_df: pd.DataFrame, trends_df: pd.DataFrame, top_n: int = 10):
        try:
            if insights_df.empty:
                logger.warning("No hay insights para enviar")
                return

            top_insights = insights_df.head(top_n)
            subject = f"Trend Hunter Report {datetime.now().strftime('%d-%m-%Y')}"
            body = self._build_html(top_insights, trends_df)

            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = self.sender
            msg["To"] = self.recipient
            msg.set_content("Trend Hunter Report")
            msg.add_alternative(body, subtype="html")

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.sender, self.password)
                server.send_message(msg)

            logger.info(f"Email enviado a {self.recipient}")

        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            logger.error(f"Error type: {type(e)}")

    def _build_html(self, insights_df: pd.DataFrame, trends_df: pd.DataFrame) -> str:
        today = datetime.now().strftime("%d-%m-%Y")
        rows_html = ""

        for _, insight in insights_df.iterrows():
            trend_data = trends_df[trends_df["trend"] == insight["trend"]]
            rank = trend_data.iloc[0].get("trend_rank", "-") if not trend_data.empty else "-"
            stage = trend_data.iloc[0].get("trend_stage", "-") if not trend_data.empty else "-"
            movement = trend_data.iloc[0].get("movement", 0) if not trend_data.empty else 0
            movement_str = f"up +{movement}" if movement > 0 else f"down {movement}" if movement < 0 else "= 0"
            priority = insight.get("priority_level", "BAJA")
            priority_color = "#e74c3c" if priority == "ALTA" else "#f39c12" if priority == "MEDIA" else "#95a5a6"

            rows_html += f"""
            <tr>
                <td style="padding:12px;border-bottom:1px solid #eee;">
                    <strong>{self._clean_text(insight['trend'])}</strong><br>
                    <small style="color:#888;">Rank #{rank} | {stage} | {movement_str}</small>
                </td>
                <td style="padding:12px;border-bottom:1px solid #eee;">{self._clean_text(insight.get('content_idea', ''))}</td>
                <td style="padding:12px;border-bottom:1px solid #eee;">{self._clean_text(insight.get('business_opportunity', ''))}</td>
                <td style="padding:12px;border-bottom:1px solid #eee;">{self._clean_text(insight.get('business_angle', ''))}</td>
                <td style="padding:12px;border-bottom:1px solid #eee;text-align:center;">
                    <span style="background:{priority_color};color:white;padding:4px 8px;border-radius:4px;font-size:12px;">
                        {priority}
                    </span>
                </td>
            </tr>
            """

        rows_html = rows_html.encode('ascii', 'xmlcharrefreplace').decode('ascii')

        html = f"""
        <html>
        <body style="font-family:Arial,sans-serif;max-width:900px;margin:0 auto;padding:20px;">
            <h1 style="color:#2c3e50;">Trend Hunter Report</h1>
            <p style="color:#888;">{today} - Tendencias relevantes para localizacion e IA</p>
            <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;margin-top:20px;">
                <thead>
                    <tr style="background:#2c3e50;color:white;">
                        <th style="padding:12px;text-align:left;">Tendencia</th>
                        <th style="padding:12px;text-align:left;">Idea de contenido</th>
                        <th style="padding:12px;text-align:left;">Oportunidad</th>
                        <th style="padding:12px;text-align:left;">Angulo de negocio</th>
                        <th style="padding:12px;text-align:center;">Prioridad</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
            <p style="color:#bbb;font-size:12px;margin-top:30px;">
                Generado automaticamente por Trend Hunter Agent
            </p>
        </body>
        </html>
        """

        return html.encode('ascii', 'xmlcharrefreplace').decode('ascii')