from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # API Keys — SecretStr prevents accidental logging
    OPENAI_API_KEY: SecretStr | None = None
    PINECONE_API_KEY: SecretStr
    COHERE_API_KEY: SecretStr | None = None

    # App settings
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    ALLOWED_ORIGINS: List[str] = ["*"] # Adjust in production

    # Redis config
    REDIS_URL: str = "redis://localhost:6379"

    # RAG settings
    PINECONE_INDEX: str = "medical-chatbot" # Retaining original index name
    RETRIEVAL_K: int = 5        # Fetch more, rerank to 3
    RERANK_TOP_N: int = 3
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 120

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 20
    MAX_MESSAGE_LENGTH: int = 2000

    # Session
    SESSION_TTL_SECONDS: int = 3600
    MAX_HISTORY_TURNS: int = 10

settings = Settings()
