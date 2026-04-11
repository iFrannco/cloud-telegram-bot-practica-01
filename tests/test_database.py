from unittest.mock import MagicMock

from database.postgres_db import PostgreSQLDatabase


def test_postgres_database_builds_engine_and_sql_database(monkeypatch):
    create_engine_calls = []
    sql_database_calls = []
    fake_engine = MagicMock()
    fake_connection = MagicMock()
    fake_connection.__enter__.return_value = object()
    fake_connection.__exit__.return_value = None
    fake_engine.connect.return_value = fake_connection
    fake_sql_database = object()
    fake_secret = "dummy-credential"

    def fake_create_engine(conn_string, **kwargs):
        create_engine_calls.append((conn_string, kwargs))
        return fake_engine

    def fake_sql_database_factory(engine):
        sql_database_calls.append(engine)
        return fake_sql_database

    monkeypatch.setenv("DB_HOST", "db-host")
    monkeypatch.setenv("DB_PORT", "6543")
    monkeypatch.setenv("POSTGRES_DB", "sakila")
    monkeypatch.setenv("POSTGRES_USER", "bot-user")
    monkeypatch.setenv("POSTGRES_PASSWORD", fake_secret)
    monkeypatch.setattr("database.postgres_db.create_engine", fake_create_engine)
    monkeypatch.setattr("database.postgres_db.SQLDatabase", fake_sql_database_factory)

    database = PostgreSQLDatabase()

    assert database.db_config["host"] == "db-host"
    assert database.db_config["port"] == "6543"
    assert database.db_config["database"] == "sakila"
    assert database.db_config["user"] == "bot-user"
    assert database.db_config["password"] == fake_secret  # NOSONAR - test fixture for db config contract
    assert create_engine_calls[0][0] == (
        f"postgresql+psycopg2://bot-user:{fake_secret}@db-host:6543/sakila"
    )
    assert create_engine_calls[0][1]["pool_size"] == 5
    assert sql_database_calls == [fake_engine]
    assert database.get_db() is fake_sql_database


def test_postgres_database_accepts_explicit_parameters(monkeypatch):
    fake_engine = MagicMock()
    fake_connection = MagicMock()
    fake_connection.__enter__.return_value = object()
    fake_connection.__exit__.return_value = None
    fake_engine.connect.return_value = fake_connection

    monkeypatch.setattr("database.postgres_db.create_engine", lambda *_args, **_kwargs: fake_engine)
    monkeypatch.setattr("database.postgres_db.SQLDatabase", lambda engine: {"engine": engine})

    explicit_config = {
        "host": "localhost",
        "port": "5432",
        "database": "customdb",
        "username": "customuser",
        "password": "dummy-credential",  # NOSONAR - explicit constructor argument being tested
    }
    database = PostgreSQLDatabase(**explicit_config)

    assert database.db_config["host"] == explicit_config["host"]
    assert database.db_config["port"] == explicit_config["port"]
    assert database.db_config["database"] == explicit_config["database"]
    assert database.db_config["user"] == explicit_config["username"]
    assert database.db_config["password"] == explicit_config["password"]  # NOSONAR - test fixture for db config contract
