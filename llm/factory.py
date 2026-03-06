import logging
from llm.base import LLMClientBase
from config.settings import LLM_PROVIDER

logger = logging.getLogger(__name__)


def get_llm_client() -> LLMClientBase:

    if LLM_PROVIDER == "gemini":
        from llm.gemini_api import GeminiClient
        return GeminiClient()

    #if LLM_PROVIDER == "openai":
        #from llm.openai_api import OpenAIClient
        #return OpenAIClient()

    #if LLM_PROVIDER == "anthropic":
        #from llm.anthropic_api import AnthropicClient
        #return AnthropicClient()

    raise ValueError(f"LLM provider no soportado: {LLM_PROVIDER}")
