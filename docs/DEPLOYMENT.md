# Deployment

LifeVerse is deployment-independent. The application uses the SQLAlchemy database URL and environment settings rather than provider-specific APIs.

## Processes

- API: uvicorn lifeverse.api:app --host 0.0.0.0 --port 8000
- Worker: python -m lifeverse.worker
- Database: PostgreSQL for production; SQLite remains supported for local development and isolated tests.
- Scheduler: the persistent database-backed job queue is driven by the worker process.

## Database configuration

Set `LIFEVERSE_DATABASE_URL` through the environment or a secret manager. Never commit credentials or paste them into issue reports or logs.

For PostgreSQL, install the project dependencies; the application uses psycopg 3 and accepts standard `postgresql://` URLs, normalizing them to the psycopg SQLAlchemy dialect. Supabase Session Pooler can be used from IPv4-only hosts. Use Direct connections when the runtime has IPv6 connectivity. Do not enable the Supabase Data API for the server-side SQLAlchemy connection path.

Use a dedicated, least-privilege runtime database role rather than the Supabase project owner for application traffic. Keep schema migrations under a separately controlled migration identity where practical. Keep database passwords URL-encoded when special characters are present.

Run `alembic upgrade head` before starting API and worker processes. API and worker must use the same database. Do not point production at the local SQLite default.

For Docker Compose, `LIFEVERSE_DATABASE_URL` is used by API and worker. Set `LIFEVERSE_MIGRATION_DATABASE_URL` separately when migrations require a privileged database identity; the migration service falls back to the runtime URL only when no migration URL is supplied. Keep the migration identity out of API/worker environments.

## Monitoring

See [Observability and Health Checks](operations/OBSERVABILITY.md) for liveness/readiness, metrics publishing, the authenticated Prometheus exporter, optional monitoring Compose profile and alert delivery requirements. Enable metrics publishing on each API/worker process, but enable the exporter only on one designated API instance. Real alerts are not active until a webhook receiver is configured and delivery is tested.

## Local

1. Create a virtual environment and install `pip install -e ".[dev]"`.
2. Leave `LIFEVERSE_DATABASE_URL` unset to use local SQLite, or set it to a PostgreSQL URL for integration testing.
3. Run `alembic upgrade head`.
4. Start the API and worker as separate processes.
5. Verify `/health` reports `status=ready` and `database=ok`.

## VPS

Run API and worker as independently restartable services. Use a managed or locally backed PostgreSQL database with tested backups. The worker must have access to the same database as the API.

## Railway

Railway may host the API and worker as separate services, but no domain/application code depends on Railway. Configure the same environment variables and database URL used elsewhere.

## Recovery

Jobs have persistent state, idempotency keys, attempts, leases and retry/dead-letter states. Restarting a worker does not erase queued work. Expired worker leases are recovered before new claims.

## Production requirements

Use TLS at the edge, secret management, database backups, restricted database credentials, log retention, monitoring and an external process supervisor. Do not put secrets in source control.
