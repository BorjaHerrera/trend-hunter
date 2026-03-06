import pandas as pd
import logging

logger = logging.getLogger(__name__)

NOISE_KEYWORDS = [
    # Deporte ES
    "fútbol", "futbol", "liga", "champions", "copa del rey", "gol", "partido", "atletico",
    "barcelona", "real madrid", "sevilla", "valencia", "betis", "athletic",
    # Deporte EN
    "nba", "nfl", "nhl", "mlb", "soccer", "football", "basketball", "baseball",
    "tennis", "golf", "formula 1", "f1", "superbowl", "super bowl", "playoffs",
    "standings", "scores", "match", "tournament",
    # Televisión y entretenimiento ES
    "gran hermano", "gh duo", "supervivientes", "masterchef", "got talent",
    "resident evil", "invincible", "poppy playtime", "minecraft", "fortnite",
    "rainbow six", "jujutsu", "dragon ball", "anime",
    # Televisión y entretenimiento EN
    "netflix", "disney", "hbo", "amazon prime", "streaming", "episode",
    "season finale", "trailer", "movie", "film", "serie", "sitcom",
    "prime video", "apple tv", "peacock",
    # Videojuegos
    "gaming", "gameplay", "walkthrough", "speedrun", "twitch", "streamer",
    "playstation", "xbox", "nintendo", "steam", "esports",
    # Política ES
    "trump", "elecciones", "congreso", "senado", "presidente", "pedro sánchez",
    "gobierno", "partido político", "psoe", "pp ", "vox ", "podemos", "guerra",
    # Política EN
    "election", "congress", "senate", "democrat", "republican", "obama",
    "white house", "parliament", "war", "khamenei", "biden",
    # Meteorología
    "tiempo", "lluvia", "nieve", "temperatura", "clima",
    "weather", "storm", "hurricane", "tornado", "forecast",
    # Lotería
    "lotería", "loteria", "euromillones", "bonoloto", "primitiva",
    "lottery", "powerball", "mega millions",
    # Música
    "rosalía", "bad bunny", "taylor swift", "beyonce", "shakira", "peso pluma",
    "melanie martinez", "concierto", "concert", "album", "single",
    "music video", "letra", "lyrics", "official video", "lyric video",
    # Ciudades y lugares sin contexto
    "bucharest", "montreal", "budapest", "philadelphia", "hong kong",
    # Streamers y personajes virales
    "joe rogan", "tfue", "berry bury",
    # Deportes específicos
    "lazio", "atalanta", "kraken", "st louis blues",
]

class TrendCleaner:

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:

        if df.empty:
            return df

        original_count = len(df)

        # 1. Eliminar filas con trend vacía
        df = df[df["trend"].notna()]
        df = df[df["trend"].str.strip() != ""]

        # 2. Normalizar texto
        df["trend"] = df["trend"].str.strip()
        df["trend_lower"] = df["trend"].str.lower()

        # 3. Eliminar tendencias muy cortas (menos de 3 caracteres)
        df = df[df["trend"].str.len() >= 3]

        # 4. Filtrar ruido
        df = df[~df["trend_lower"].apply(self._is_noise)]

        # 5. Eliminar columna auxiliar
        df = df.drop(columns=["trend_lower"])

        # 6. Reset index
        df = df.reset_index(drop=True)

        logger.info(f"TrendCleaner: {original_count} → {len(df)} tendencias tras limpiar")

        return df

    def _is_noise(self, trend_lower: str) -> bool:
        for keyword in NOISE_KEYWORDS:
            if keyword in trend_lower:
                return True
        return False