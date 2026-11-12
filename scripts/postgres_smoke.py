"""Smoke-test the migrated PostgreSQL schema and committed data visibility."""

from uuid import uuid4

from sqlalchemy import inspect, text

from lifeverse.db import engine


def main() -> None:
    if engine.dialect.name != "postgresql":
        raise RuntimeError("PostgreSQL smoke test requires LIFEVERSE_DATABASE_URL")

    required_tables = {"accounts", "wallets", "ledger_transactions", "background_jobs"}
    existing_tables = set(inspect(engine).get_table_names())
    missing_tables = required_tables - existing_tables
    if missing_tables:
        raise RuntimeError(f"Database schema is missing tables: {sorted(missing_tables)}")

    account_id = uuid4()
    username = f"postgres-smoke-{account_id.hex}"
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO accounts (id, username, created_at) "
                    "VALUES (:id, :username, CURRENT_TIMESTAMP)"
                ),
                {"id": account_id, "username": username},
            )

        with engine.connect() as connection:
            persisted_username = connection.scalar(
                text("SELECT username FROM accounts WHERE id = :id"),
                {"id": account_id},
            )
        if persisted_username != username:
            raise RuntimeError("Committed PostgreSQL data was not visible on a new connection")
    finally:
        with engine.begin() as connection:
            connection.execute(
                text("DELETE FROM accounts WHERE id = :id"),
                {"id": account_id},
            )
        engine.dispose()


if __name__ == "__main__":
    main()
