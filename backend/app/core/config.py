"""
Application configuration.

All configuration comes from environment variables (see backend/.env.example).
Never hard-code secrets or URLs here.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # General
    environment: str = "development"  # development | production
    log_level: str = "INFO"

    # Inference
    # "mock"   -> DEVELOPMENT ONLY. Deterministic fake responses. Never allowed in production.
    # "remote" -> Calls an external GPU-hosted inference service over HTTP.
    # "local"  -> Loads the model in-process (only valid when this backend itself runs on a GPU host).
    inference_mode: str = "mock"
    model_api_url: str = ""          # required if inference_mode == "remote"
    model_api_key: str = ""          # required if inference_mode == "remote" and the service needs auth
    model_name: str = "Qwen2.5-VL-7B-Instruct"
    lora_adapter_path: str = ""      # required if inference_mode == "local"

    # CORS
    allowed_origins: str = "http://localhost:5173"

    # Uploads
    max_image_size_mb: int = 10

    # Knowledge base
    knowledge_base_path: str = "../knowledge/crop_diseases.json"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        protected_namespaces=("settings_",),  # avoids false-positive warnings on model_* field names
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    @property
    def max_image_size_bytes(self) -> int:
        return self.max_image_size_mb * 1024 * 1024


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()

    # Hard safety rail: never allow mock inference in a production environment.
    if settings.environment.lower() == "production" and settings.inference_mode == "mock":
        raise RuntimeError(
            "INFERENCE_MODE=mock cannot be used when ENVIRONMENT=production. "
            "Set INFERENCE_MODE to 'remote' or 'local' and configure the real model."
        )

    return settings
