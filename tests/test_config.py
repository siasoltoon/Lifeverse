from lifeverse.config import Settings


def test_postgresql_url_uses_psycopg_driver():
    settings = Settings(database_url="postgresql://user:password@localhost:5432/lifeverse")

    assert settings.database_url == "postgresql+psycopg://user:password@localhost:5432/lifeverse"


def test_legacy_postgres_url_uses_psycopg_driver():
    settings = Settings(database_url="postgres://user:password@localhost:5432/lifeverse")

    assert settings.database_url == "postgresql+psycopg://user:password@localhost:5432/lifeverse"


def test_explicit_sqlite_url_is_unchanged():
    settings = Settings(database_url="sqlite:///./lifeverse.db")

    assert settings.database_url == "sqlite:///./lifeverse.db"


def test_explicit_postgresql_driver_is_preserved():
    url = "postgresql+psycopg://user:password@localhost:5432/lifeverse"
    settings = Settings(database_url=url)

    assert settings.database_url == url
