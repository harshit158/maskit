from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from src.settings import settings
from src.types import LLMProvider

def get_ollama():
    llm_ollama = ChatOllama(
        model=settings.ollama_model_id,
        temperature=0.3,
    )
    return llm_ollama

def get_openai():
    llm_openai = ChatOpenAI(
        model="gpt-5-mini",
        temperature=0.3,
        timeout=None,
        max_retries=2,
        api_key=settings.openai_api_key
    )
    return llm_openai

def get_llm(provider: LLMProvider):
    if provider == LLMProvider.OLLAMA:
        return get_ollama()
    elif provider == LLMProvider.OPENAI:
        return get_openai()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")