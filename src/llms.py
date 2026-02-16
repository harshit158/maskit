from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from src.settings import settings
from src.types import LLMProvider

llm_ollama = ChatOllama(
    model="llama3.1:8b",
    temperature=0.3,
)

llm_openai = ChatOpenAI(
    model="gpt-5-mini",
    temperature=0.3,
    timeout=None,
    max_retries=2,
    api_key=settings.openai_api_key
)

def get_llm(provider: LLMProvider):
    if provider == LLMProvider.OLLAMA:
        return llm_ollama
    elif provider == LLMProvider.OPENAI:
        return llm_openai
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")