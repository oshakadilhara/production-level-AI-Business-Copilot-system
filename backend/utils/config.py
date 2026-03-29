import os
from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    environment: str = Field(default="development")
    storage_dir: str = Field(default="backend_storage")

    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1-mini")
    openai_embedding_model: str = Field(default="text-embedding-3-small")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def ensure_storage_dir() -> str:
    settings = get_settings()
    base = settings.storage_dir
    os.makedirs(base, exist_ok=True)
    return base

