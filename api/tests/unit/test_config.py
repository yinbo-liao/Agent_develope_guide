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
