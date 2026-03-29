import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = Field(default="development")
    storage_dir: str = Field(default="backend_storage")

    openai_api_key: str = Field(default="")
    openai_model: str = Field(default="gpt-4o-mini")
    openai_embedding_model: str = Field(default="text-embedding-3-small")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def ensure_storage_dir() -> str:
    settings = get_settings()
    base = settings.storage_dir
    os.makedirs(base, exist_ok=True)
    return base
