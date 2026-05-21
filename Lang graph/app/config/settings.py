from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM provider keys
    google_api_key: Optional[str] = None
    github_token: Optional[str] = None
    groq_api_key: Optional[str] = None
    sambanova_api_key: Optional[str] = None
    deepseek_api_key: Optional[str] = None

    # LangSmith tracing
    langchain_api_key: Optional[str] = None
    langchain_project: str = "langgraph-pipeline"
    langchain_tracing_v2: bool = False
    langchain_endpoint: str = "https://api.smith.langchain.com"

    # Pipeline behaviour
    output_dir: str = "."
    max_retries: int = 3
    batch_size: int = 20
    concurrency_limit: int = 3

    # API server
    api_version: str = "1.0.0"
    cors_origins: list[str] = ["*"]


settings = Settings()
