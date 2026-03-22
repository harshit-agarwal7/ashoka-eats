"""Application settings loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for the ashoka-eats pipeline.

    Attributes:
        openrouter_api_key: API key for OpenRouter LLM access.
        openrouter_base_url: Base URL for the OpenRouter API.
        openrouter_model: Model identifier to use for extraction.
        llm_concurrency: Max concurrent LLM requests.
        confidence_threshold: Minimum confidence to keep an extraction.
        chunk_size: Number of messages per chunk.
        chunk_stride: Step size between chunk windows.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    openrouter_api_key: str
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openrouter_model: str = "google/gemini-flash-1.5"
    llm_concurrency: int = 5
    confidence_threshold: float = 0.5
    chunk_size: int = 30
    chunk_stride: int = 15


settings = Settings()  # type: ignore[call-arg]
