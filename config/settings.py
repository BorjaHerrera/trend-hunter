import os
from dotenv import load_dotenv

load_dotenv()

def get_env_var(name):
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Falta la variable de entorno: {name}")
    return value

LLM_PROVIDER = get_env_var("LLM_PROVIDER")
GEMINI_API_KEY = get_env_var("GEMINI_API_KEY")
SERPAPI_KEY = get_env_var("SERPAPI_KEY")
YOUTUBE_API_KEY = get_env_var("YOUTUBE_API_KEY")
EMAIL_SENDER = get_env_var("EMAIL_SENDER")
EMAIL_PASSWORD = get_env_var("EMAIL_PASSWORD")
EMAIL_RECIPIENT = get_env_var("EMAIL_RECIPIENT")
REDDIT_CLIENT_ID = get_env_var("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = get_env_var("REDDIT_CLIENT_SECRET")
REDDIT_USER_AGENT = get_env_var("REDDIT_USER_AGENT")
