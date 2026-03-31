"""
core/config.py — Centralized configuration management.
Loads all settings from environment variables / .env file via Pydantic BaseSettings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────
    PROJECT_NAME: str = "AI Internship Discovery Backend"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # ── Server ───────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: List[str] = ["*"]

    # ── Security ─────────────────────────────────────────────
    # WARNING: Change SECRET_KEY in production!
    SECRET_KEY: str = "intelai_default_secret_key_8h2j8k9l0m1p2q3r"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours


    # ── Database ─────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/internai"
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""

    # ── OpenAI / LLM ─────────────────────────────────────────
    OPENAI_API_KEY: str = "your-openai-api-key"
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"

    # ── Apify (Real Internship Scraping) ──────────────────────
    APIFY_API_KEY: str = "your-apify-api-key"

    # ── Embedding Model ───────────────────────────────────────
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # SentenceTransformer model

    # ── FAISS ─────────────────────────────────────────────────
    FAISS_INDEX_PATH: str = "data/faiss_index"
    FAISS_DIMENSION: int = 384  # Matches all-MiniLM-L6-v2 output dim

    # ── File Uploads ──────────────────────────────────────────
    UPLOAD_DIR: str = "data/uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = ["pdf"]

    # ── spaCy ─────────────────────────────────────────────────
    SPACY_MODEL: str = "en_core_web_sm"

    # ── RAG ───────────────────────────────────────────────────
    CHUNK_SIZE: int = 512
    CHUNK_OVERLAP: int = 64
    RAG_TOP_K: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
