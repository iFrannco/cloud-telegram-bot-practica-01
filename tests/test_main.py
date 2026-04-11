import importlib
import sys
import types

import pytest


def _load_main_with_fakes(monkeypatch, *, token="telegram-token", setup_error=None, run_error=None):
    calls = []
    logger = types.SimpleNamespace(
        info=lambda message: calls.append(("info", message)),
        error=lambda message: calls.append(("error", message)),
    )

    config_module = types.ModuleType("config")

    def fake_setup_api_keys():
        calls.append(("setup_api_keys", None))
        if setup_error:
            raise setup_error

    def fake_get_telegram_token():
        calls.append(("get_telegram_token", None))
        return token

    config_module.setup_api_keys = fake_setup_api_keys
    config_module.get_telegram_token = fake_get_telegram_token
    config_module.logger = logger

    database_package = types.ModuleType("database")
    database_module = types.ModuleType("database.postgres_db")

    class FakePostgreSQLDatabase:
        def __init__(self):
            calls.append(("database_init", None))

        def get_db(self):
            calls.append(("get_db", None))
            return "db-object"

    database_module.PostgreSQLDatabase = FakePostgreSQLDatabase
    database_package.postgres_db = database_module

    llm_package = types.ModuleType("llm")
    llm_module = types.ModuleType("llm.agent")

    class FakeLLMAgent:
        def __init__(self, db):
            calls.append(("llm_init", db))
            self.db = db

    llm_module.LLMAgent = FakeLLMAgent
    llm_package.agent = llm_module

    bot_package = types.ModuleType("bot")
    bot_module = types.ModuleType("bot.telegram_bot")

    class FakeTelegramBot:
        def __init__(self, received_token, llm_agent):
            calls.append(("bot_init", received_token, llm_agent.db))

        def run(self):
            calls.append(("bot_run", None))
            if run_error:
                raise run_error

    bot_module.TelegramBot = FakeTelegramBot
    bot_package.telegram_bot = bot_module

    monkeypatch.setitem(sys.modules, "config", config_module)
    monkeypatch.setitem(sys.modules, "database", database_package)
    monkeypatch.setitem(sys.modules, "database.postgres_db", database_module)
    monkeypatch.setitem(sys.modules, "llm", llm_package)
    monkeypatch.setitem(sys.modules, "llm.agent", llm_module)
    monkeypatch.setitem(sys.modules, "bot", bot_package)
    monkeypatch.setitem(sys.modules, "bot.telegram_bot", bot_module)
    monkeypatch.delitem(sys.modules, "main", raising=False)

    imported_main = importlib.import_module("main")
    return imported_main, calls


def test_main_initializes_components_and_runs(monkeypatch):
    main_module, calls = _load_main_with_fakes(monkeypatch)

    main_module.main()

    assert calls == [
        ("setup_api_keys", None),
        ("get_telegram_token", None),
        ("database_init", None),
        ("get_db", None),
        ("llm_init", "db-object"),
        ("bot_init", "telegram-token", "db-object"),
        ("info", "Starting Telegram bot..."),
        ("bot_run", None),
    ]


def test_main_logs_and_reraises_startup_errors(monkeypatch):
    main_module, calls = _load_main_with_fakes(
        monkeypatch,
        setup_error=RuntimeError("startup failed"),
    )

    with pytest.raises(RuntimeError, match="startup failed"):
        main_module.main()

    assert ("error", "Error starting application: startup failed") in calls
