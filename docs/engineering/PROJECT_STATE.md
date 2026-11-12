# PROJECT STATE
Repository: siasoltoon/Lifeverse
Current phase: Phase 32 — Final Production Audit (completed and merged)
Current task: OPS-DB-03 — operational readiness validation
Task status: OBS-01/OBS-02 observability and centralized monitoring are CI verified. OBS-03 worker-handler retry safety and PostgreSQL payroll concurrency are CI verified. OPS-DB-03 remains IN PROGRESS; hosted Supabase migration/privilege acceptance for revisions 0005–0008, authenticated hosted scrape, real alert receiver delivery, and broader queue/load/failure-recovery validation remain.
PR: #7 — feat(db): add PostgreSQL and Supabase Session Pooler support
Branch: feat/postgresql-supabase-support
PR #7 remains draft and is not merged.

Completed: Phase 0; Phases 1–15; Phase 16 events; Phase 17 business; Phase 18 market; Phase 19 law/crime/combat; Phase 20 AI intent boundary; Phase 21 Telegram/UI client boundary; Phase 22 localization; Phase 23 anti-exploit; Phase 24 security; Phase 25 performance; Phase 26 background jobs/scheduler; Phase 27 complete test suite; Phase 28 observability; Phase 29 deployment; Phase 30 documentation; Phase 31 E2E; Phase 32 final audit.

PostgreSQL foundation: psycopg 3 dependency, PostgreSQL URL normalization, SQLAlchemy pool pre-ping, SQLite local default retained, PostgreSQL 16 migration and committed persistence smoke tests in CI.

Actual Supabase acceptance (2026-11-12, last verified at revision 0004_phases_26_32):
- Session Pooler (IPv4) connected using local ignored .env; credentials were not committed or shared.
- Alembic upgrade head executed against the actual Supabase project using the administrative migration identity; 44 public tables and revision 0004_phases_26_32 verified.
- Dedicated lifeverse_runtime role verified LOGIN=true, SUPERUSER=false, CREATEDB=false, CREATEROLE=false, BYPASSRLS=false; public schema USAGE granted and CREATE denied; application table DML and sequence usage granted; runtime access to alembic_version denied as intended.
- Runtime-role persistence write/read across independent Python processes passed; test record was deleted and zero test records remained.
- Runtime-role DDL probe was denied as expected; probe table did not exist.
- API startup and /health returned status=ready, database=ok; clean API shutdown/restart followed by another successful /health check passed.
- Worker --once exited with code 0. The background_jobs queue was empty before and after; no business/economy handler execution was attempted.
- TLS encryption on the client connection was verified with psycopg's pgconn.ssl_in_use. CA/hostname certificate validation is deferred by decision.
- Backup/restore/PITR verification is deferred by user decision.
- Important boundary: revisions 0005_worker_heartbeats, 0006_metrics_snapshots, 0007_business_payroll and 0008_expand_ledger_account_code were added after this hosted acceptance. They have passed PostgreSQL 16 CI migrations, but have NOT yet been applied to the actual Supabase database.

OBS-01 observability baseline:
- Thread-safe process-local Metrics counters with input validation.
- API middleware records request count, 4xx/5xx counts, total/max request duration, and privacy-conscious request logs.
- /health/live is DB-independent; /health/ready is database readiness; /health remains a compatibility alias.
- Worker records completed, failed, and dead-letter outcomes.
- Durable worker heartbeat table/reporter, independent DB sessions, current-job visibility and clean shutdown implemented in migration 0005_worker_heartbeats.

OBS-02 centralized metrics and monitoring implementation:
- Migration 0006_metrics_snapshots adds operational_metric_snapshots for per-process snapshots.
- API and worker processes can publish snapshots using independent database sessions; one designated API exporter exposes fresh API/worker metrics at authenticated GET /internal/metrics.
- Export requires a Bearer token of at least 32 characters and is disabled by default.
- Added optional Docker Compose monitoring profile for Prometheus and Alertmanager; both management ports bind to localhost.
- Added five Prometheus alert rules: exporter unavailable, elevated HTTP 5xx ratio, high average latency, stale worker heartbeat and dead-letter jobs.
- Compose worker now publishes snapshots when enabled, explicitly keeps exporter disabled and does not receive the metrics bearer token.
- .env.example leaves LIFEVERSE_DATABASE_URL unset by default: local Python retains its relative SQLite default, while Docker Compose selects the persistent /data/lifeverse.db named-volume fallback. Regression coverage for this behavior passed in CI run 43121685847.
- Alert delivery uses a generic Alertmanager-compatible webhook. Rules/configuration exist, but alerts are NOT active until a real receiver is configured and a delivery test succeeds.
- docs/operations/OBSERVABILITY.md documents setup and operational limits.
- CI run 43124375294 on commit 153a3282376df988377babb5c070e028c14e599c: Ruff format/lint PASS; pytest 65 passed in 2.80s with one Starlette/httpx TestClient deprecation warning; SQLite and PostgreSQL 16 migrations PASS; PostgreSQL persistence smoke PASS; PostgreSQL payroll concurrency smoke PASS; Prometheus config/rules PASS (5 rules); Alertmanager config PASS; Docker Compose config PASS; Docker build PASS. datetime.utcnow() model-default warnings were fixed; no warnings were suppressed and no tests were weakened.

OBS-03 worker-handler retry safety and economic idempotency:
- Migration 0007_business_payroll_payments adds a durable payroll payment ledger with a unique idempotency key and restrictive audit-preserving foreign keys.
- Business payroll locks the business/employee/wallet rows, inserts a unique ledger row with dialect-native ON CONFLICT DO NOTHING, and commits business balance, employee wallet, payment ledger and audit record atomically.
- Legacy payroll AuditLog entries are lazily imported into the new ledger so a pre-deployment job retry cannot pay the same employee again.
- business.payroll worker handler now returns the payroll amount rather than incorrectly accessing .id on a Decimal.
- Event dispatch uses SELECT FOR UPDATE SKIP LOCKED; travel completion is state-checked and idempotent after handler commit/job completion failure.
- Migration 0008_expand_ledger_account_code widens ledger_accounts.code from 64 to 128 because wallet account identifiers contain two full UUIDs.
- PostgreSQL concurrency smoke tests verify different payroll keys cannot overdraw a business, duplicate keys credit the employee exactly once, and four concurrent workers claim/complete 24 queued jobs without duplicate or lost claims.

Limits / pending:
- Actual Supabase remains last verified at revision 0004; apply migrations 0005–0008 with the migration identity, then verify runtime-role access to worker_heartbeats, operational_metric_snapshots and business_payroll_payments before enabling heartbeat/metrics publishing there.
- Real Alertmanager webhook delivery has not been tested; no external receiver is configured.
- Worker business-payroll/event-dispatch/travel-completion retry integration, PostgreSQL payroll concurrency and atomic job-claim concurrency are CI verified; these have not yet been exercised against the actual Supabase project.
- Broader queue throughput/load, multi-worker recovery and hosted database restart/failure recovery remain unverified.
- Supabase service/database restart and disaster recovery were not tested.
- Backup/PITR and CA/hostname certificate validation remain deferred.
Production readiness is NOT ESTABLISHED. Do not declare production-ready.

Exact next action: after syncing the GitHub branch to the local laptop, apply and verify migrations 0005–0008 on actual Supabase with the admin migration identity; audit least-privilege runtime grants for worker_heartbeats, operational_metric_snapshots and business_payroll_payments; then verify authenticated Prometheus scrape and a real alert webhook delivery. After that, run broader queue/load and multi-worker failure/recovery tests. Keep backup/PITR and CA/hostname validation deferred unless the user reopens those decisions.
