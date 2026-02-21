from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openai_api_key: str = ""
    ollama_model_id: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()