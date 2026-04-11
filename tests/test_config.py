import pytest

import config


def test_setup_api_keys_raises_when_groq_key_missing(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    with pytest.raises(ValueError, match="GROQ_API_KEY"):
        config.setup_api_keys()


def test_setup_api_keys_accepts_present_groq_key(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    config.setup_api_keys()


def test_get_telegram_token_returns_env_value(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "telegram-token")

    assert config.get_telegram_token() == "telegram-token"


def test_get_telegram_token_raises_when_missing(monkeypatch):
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)

    with pytest.raises(ValueError, match="TELEGRAM_BOT_TOKEN"):
        config.get_telegram_token()
