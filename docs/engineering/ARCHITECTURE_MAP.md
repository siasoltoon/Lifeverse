# ARCHITECTURE MAP
Authoritative persistent state:
- src/lifeverse/models.py — simulation state
- src/lifeverse/jobs.py — persistent background jobs, atomic claims, leases/retries, process-local outcome metrics, durable worker heartbeat records and heartbeat reporter
- src/lifeverse/services.py — core/application services for phases 1–15
- src/lifeverse/services_16_25.py — phases 16–25 application/domain services
- src/lifeverse/observability.py — database readiness, thread-safe process-local metrics and timed operational logging
- src/lifeverse/production.py — deployment profile contract
- src/lifeverse/worker.py — portable worker process, registered domain handlers and graceful heartbeat shutdown
- src/lifeverse/api.py — HTTP transport, request metrics middleware, liveness/readiness endpoints and database-backed readiness
- src/lifeverse/api_16_25.py — versioned /v1 client API
- src/lifeverse/telegram_adapter.py — client-only Telegram update parser
- src/lifeverse/config.py — environment-driven settings and SQLAlchemy PostgreSQL driver URL normalization
- src/lifeverse/db.py — SQLAlchemy engine/session factory; SQLite local default, psycopg 3 PostgreSQL support, connection pre-ping
- migrations/ — versioned persistence schema through 0004
- tests/ — unit, integration, API, reliability and production-audit regression coverage
- scripts/postgres_smoke.py — PostgreSQL schema and committed persistence smoke check
- Dockerfile / docker-compose.yml — portable deployment topology
- docs/operations/OBSERVABILITY.md — health probes, process-local metric semantics, monitoring limits and alerting status

Dependency direction: Core/Domain → Application → Infrastructure/API/Clients.
Database deployment: local SQLite for development and isolated tests; PostgreSQL for production. Supabase is accessed only by backend SQLAlchemy connections, not client-side Supabase SDK/Data API. Runtime credentials must use a restricted DB role.
Background flow: enqueue → persistent queued state → atomic conditional claim → leased running state → domain handler → completed OR retry/dead-letter → audit/logging and process-local outcome metrics.
API health: /health/live checks process liveness without database access; /health/ready checks database readiness; /health remains a compatibility alias for readiness.
Metrics limitation: request and worker counters are thread-safe but process-local and reset on restart. They are not shared across API/worker processes or exported. Durable worker heartbeat records are stored in PostgreSQL/SQLite and stale workers can be queried, but no external alert delivery is configured.
AI flow: Intent → Validation → Game Engine/authorized executor → State Change → Persistence. AIIntentService never mutates game state during proposal.
Economy and market settlement use idempotency keys and atomic transaction boundaries.
Security includes salted scrypt password hashing, revocable persistent sessions, API rate limiting and audit logging.
Performance uses bounded pagination and database indexes; background work is persistent rather than in-memory-only.
No Railway-specific dependency exists in core/application design; Railway is one deployment profile among local/VPS/CI.
