from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "AI Workflow Platform"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: Literal["development", "test", "staging", "production"] = "development"
    DEBUG: bool = True

    API_PREFIX: str = "/api/v1"
    SECRET_KEY: str = Field(
        default="dev-secret-change-me-in-prod-override",
        min_length=16,
    )
    CORS_ORIGINS: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )

    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://aiwf:changeme_in_production@localhost:5432/aiwf_dev",
    )
    REDIS_URL: str = Field(default="redis://:changeme@localhost:6379/0")
    OPA_URL: str = "http://opa:8181"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = "http://localhost:4317"

    LOG_LEVEL: str = "INFO"
    ENABLE_METRICS: bool = True
    ENABLE_TRACING: bool = True
    REQUESTS_PER_MINUTE: int = 120

    MCP_POSTGRES_ENABLED: bool = True
    MCP_GITHUB_ENABLED: bool = False
    MCP_PUPPETEER_ENABLED: bool = False
    MCP_SLACK_ENABLED: bool = False
    GITHUB_TOKEN: str | None = None
    SLACK_BOT_TOKEN: str | None = None
    SLACK_DEFAULT_CHANNEL: str = "#alerts"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @computed_field  # type: ignore[misc]
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    def validate_production_secrets(self) -> list[str]:
        """Validate that no insecure default secrets are used in production.

        Returns a list of validation error messages (empty = all clear).
        """
        errors: list[str] = []
        if not self.is_production:
            return errors

        insecure_defaults = {
            "SECRET_KEY": "dev-secret-change-me-in-prod-override",
            "DATABASE_URL": "changeme_in_production",
            "REDIS_URL": "changeme",
        }
        for field_name, insecure_marker in insecure_defaults.items():
            value = getattr(self, field_name, "")
            if isinstance(value, str) and insecure_marker in value:
                errors.append(
                    f"{field_name} contains an insecure default value. "
                    f"Set {field_name} to a production-safe value."
                )

        if self.SECRET_KEY and len(self.SECRET_KEY) < 32:
            errors.append(
                "SECRET_KEY must be at least 32 characters in production."
            )
        return errors


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
