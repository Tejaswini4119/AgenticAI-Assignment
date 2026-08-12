"""Centralised configuration, loaded from environment variables / .env."""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    generation_model: str = os.getenv("GENERATION_MODEL", "gpt-4o")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "")  # blank -> TF-IDF retriever
    top_k_tables: int = int(os.getenv("TOP_K_TABLES", "4"))
    db_path: str = os.getenv("DB_PATH", "data/company.db")
    max_repair_attempts: int = int(os.getenv("MAX_REPAIR_ATTEMPTS", "2"))


settings = Settings()
