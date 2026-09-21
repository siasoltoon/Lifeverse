# Deployment

LifeVerse is deployment-independent. The application uses the SQLAlchemy database URL and environment settings rather than provider-specific APIs.

## Processes

- API: uvicorn lifeverse.api:app --host 0.0.0.0 --port 8000
- Worker: python -m lifeverse.worker
- Database: any SQLAlchemy-supported production database validated by the selected deployment environment.
- Scheduler: the persistent database-backed job queue is driven by the worker process.

## Local

1. Create a virtual environment and install pip install -e ".[dev]".
2. Set LIFEVERSE_DATABASE_URL.
3. Run alembic upgrade head.
4. Start the API and worker as separate processes.
5. Verify /health reports status=ready and database=ok.

## VPS

Run API and worker as independently restartable services. Use a managed or locally backed database with backups. The worker must have access to the same database as the API.

## Railway

Railway may host the API and worker as separate services, but no domain/application code depends on Railway. Configure the same environment variables and database URL used elsewhere.

## Recovery

Jobs have persistent state, idempotency keys, attempts, leases and retry/dead-letter states. Restarting a worker does not erase queued work. Expired worker leases are recovered before new claims.

## Production requirements

Use TLS at the edge, secret management, database backups, restricted database credentials, log retention, monitoring and an external process supervisor. Do not put secrets in source control.
