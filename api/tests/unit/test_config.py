from __future__ import annotations

from app.core.config import Settings


def test_settings_defaults_to_development() -> None:
    settings = Settings(
        ENVIRONMENT="development",
        SECRET_KEY="test-secret-key-at-least-16-chars",
    )
    assert settings.ENVIRONMENT == "development"
    assert not settings.is_production
    assert settings.DEBUG is True


def test_settings_production_mode() -> None:
    settings = Settings(
        ENVIRONMENT="production",
        SECRET_KEY="a-very-long-secret-key-for-production-use-32chars",
        DEBUG=False,
    )
    assert settings.is_production
    assert settings.APP_NAME == "AI Workflow Platform"


def test_settings_api_prefix_default() -> None:
    settings = Settings(
        SECRET_KEY="test-secret-key-at-least-16-chars",
    )
    assert settings.API_PREFIX == "/api/v1"


def test_settings_cors_origins_parsed() -> None:
    settings = Settings(
        SECRET_KEY="test-secret-key-at-least-16-chars",
        CORS_ORIGINS=["http://example.com", "https://app.example.com"],
    )
    assert len(settings.CORS_ORIGINS) == 2
    assert "http://example.com" in settings.CORS_ORIGINS


def test_settings_mcp_flags_default() -> None:
    settings = Settings(
        SECRET_KEY="test-secret-key-at-least-16-chars",
    )
    assert settings.MCP_POSTGRES_ENABLED is True
    assert settings.MCP_GITHUB_ENABLED is False
    assert settings.MCP_PUPPETEER_ENABLED is False
    assert settings.MCP_SLACK_ENABLED is False


def test_validate_production_secrets_rejects_defaults() -> None:
    """Production mode with default secrets should produce validation errors."""
    settings = Settings(
        ENVIRONMENT="production",
        DEBUG=False,
        SECRET_KEY="dev-secret-change-me-in-prod-override",  # insecure default
        DATABASE_URL="postgresql+asyncpg://user:changeme_in_production@localhost/db",
        REDIS_URL="redis://:changeme@localhost:6379/0",
    )
    errors = settings.validate_production_secrets()
    assert len(errors) >= 1  # At minimum, the SECRET_KEY default is detected


def test_validate_production_secrets_passes_with_good_values() -> None:
    """Production mode with proper secrets should produce no errors."""
    settings = Settings(
        ENVIRONMENT="production",
        DEBUG=False,
        SECRET_KEY="a-very-secure-random-production-key-that-is-long-enough",
        DATABASE_URL="postgresql+asyncpg://prod_user:strong_pass@prod-db:5432/prod_db",
        REDIS_URL="redis://:strong_redis_pass@prod-redis:6379/0",
    )
    errors = settings.validate_production_secrets()
    assert len(errors) == 0


def test_validate_production_secrets_skips_in_development() -> None:
    """Development mode should not validate secrets (allow defaults)."""
    settings = Settings(
        ENVIRONMENT="development",
        SECRET_KEY="dev-secret-change-me-in-prod-override",
    )
    errors = settings.validate_production_secrets()
    assert len(errors) == 0


def test_production_requires_long_secret_key() -> None:
    """Production mode should require SECRET_KEY >= 32 chars."""
    settings = Settings(
        ENVIRONMENT="production",
        DEBUG=False,
        SECRET_KEY="abcdefghijklmnop",  # exactly 16 chars — passes Pydantic min_length, fails production 32-min check
    )
    errors = settings.validate_production_secrets()
    assert any("32" in e for e in errors)
