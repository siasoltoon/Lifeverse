# ARCHITECTURE MAP
Authoritative persistent state:
- src/lifeverse/models.py — simulation state
- src/lifeverse/jobs.py — persistent background jobs, atomic claims, leases/retries, process-local outcome metrics, durable worker heartbeat records and heartbeat reporter
- src/lifeverse/services.py — core/application services for phases 1–15
- src/lifeverse/services_16_25.py — phases 16–25 application/domain services
- src/lifeverse/observability.py — thread-safe process-local metrics, persistent per-process metric snapshots/reporters, database readiness and timed operational logging
- src/lifeverse/production.py — deployment profile contract
- src/lifeverse/worker.py — portable worker process, registered domain handlers, heartbeat and metrics snapshot reporters
- src/lifeverse/api.py — HTTP transport, request metrics middleware, liveness/readiness endpoints, authenticated Prometheus exporter and database-backed readiness
- src/lifeverse/api_16_25.py — versioned /v1 client API
- src/lifeverse/telegram_adapter.py — client-only Telegram update parser
- src/lifeverse/config.py — environment-driven settings and SQLAlchemy PostgreSQL driver URL normalization
- src/lifeverse/db.py — SQLAlchemy engine/session factory; SQLite local default, psycopg 3 PostgreSQL support, connection pre-ping
- migrations/versions/0005_worker_heartbeats.py — durable worker status/current-job schema
- migrations/versions/0006_operational_metric_snapshots.py — per-process operational metrics snapshot schema
- migrations/versions/0007_business_payroll_payments.py — immutable idempotent payroll payment ledger
- migrations/versions/0008_expand_ledger_account_code.py — ledger account code capacity for full UUID wallet references
- tests/ — unit, integration, API, monitoring, reliability and production-audit regression coverage
- scripts/postgres_smoke.py — PostgreSQL schema and committed persistence smoke check
- scripts/postgres_worker_concurrency_smoke.py — PostgreSQL row-lock and payroll idempotency concurrency smoke check
- Dockerfile / docker-compose.yml — portable API, worker, migration and optional monitoring topology
- monitoring/prometheus.yml, monitoring/alert_rules.yml, monitoring/alertmanager.yml — authenticated scrape, operational alert rules and generic webhook delivery
- docs/operations/OBSERVABILITY.md — health probes, metric semantics, monitoring setup and alerting limits

Dependency direction: Core/Domain → Application → Infrastructure/API/Clients.
Database deployment: local SQLite for development and isolated tests; PostgreSQL for production. Supabase is accessed only by backend SQLAlchemy connections, not client-side Supabase SDK/Data API. Runtime credentials must use a restricted DB role.
Background flow: enqueue → persistent queued state → atomic conditional claim → leased running state → domain handler → completed OR retry/dead-letter → audit/logging and process-local outcome metrics.
API health: /health/live checks process liveness without database access; /health/ready checks database readiness; /health remains a compatibility alias for readiness.
Metrics flow: API/worker process-local counters → independent-session periodic snapshot → operational_metric_snapshots → one authenticated API exporter → Prometheus → alert rules → optional Alertmanager generic webhook. Snapshots are operational telemetry, not authoritative simulation state or a historical time-series store.
Monitoring is opt-in. The worker publishes snapshots but does not expose the exporter or receive the bearer token. Prometheus/Alertmanager ports bind to localhost in the Compose profile. Real alert delivery is unverified until a receiver is configured and delivery is tested.
AI flow: Intent → Validation → Game Engine/authorized executor → State Change → Persistence. AIIntentService never mutates game state during proposal.
Economy and market settlement use idempotency keys and atomic transaction boundaries. Business payroll uses BusinessPayrollPayment as a unique durable payment ledger; worker handler retries cannot pay twice, and PostgreSQL row locks serialize distinct payroll operations.
Security includes salted scrypt password hashing, revocable persistent sessions, API rate limiting and audit logging.
Performance uses bounded pagination and database indexes; background work is persistent rather than in-memory-only.
No Railway-specific dependency exists in core/application design; Railway is one deployment profile among local/VPS/CI.

Hosted Supabase was last verified at migration revision 0004. Migrations 0005–0008 are CI verified but still require hosted migration and runtime privilege acceptance.
