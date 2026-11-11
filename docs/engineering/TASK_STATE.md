# TASK STATE
Current task: OPS-DB-03 — operational readiness validation
Status: IN PROGRESS. OBS-01 and OBS-02 code-level implementation and GitHub CI verification PASS; hosted operational acceptance is not complete.
Branch: feat/postgresql-supabase-support
PR: https://github.com/siasoltoon/Lifeverse/pull/7 (draft/unmerged)

OPS-DB-01 PostgreSQL/Supabase compatibility foundation: implementation and CI verification PASS. Ruff, pytest 28, SQLite/PostgreSQL 16 migrations, PostgreSQL persistence smoke and Docker build passed.

OPS-DB-02 actual Supabase Session Pooler acceptance (2026-11-12):
- Administrative migration identity ran alembic upgrade head; 44 public tables and revision 0004_phases_26_32 verified.
- lifeverse_runtime role is non-superuser, non-createdb, non-createrole, no-bypassrls; public schema CREATE denied; application-table DML and sequence access allowed; alembic_version access denied.
- Runtime-role write/read across independent Python processes PASS; test-row cleanup PASS.
- Runtime-role DDL denial probe PASS.
- API /health PASS before and after clean API process restart.
- Worker --once exited 0 with an empty queue; no real job handler was invoked.
- Client connection TLS encryption verified. CA/hostname certificate verification deferred.
- Backup/restore/PITR deferred by user decision.
- Hosted database remains at last verified revision 0004; do not assume migrations 0005–0006 have been applied there.

OBS-01 observability baseline:
- Thread-safe metrics, API request totals/4xx/5xx/latency, privacy-conscious request logs and liveness/readiness endpoints.
- Worker completed/failed/dead-letter metrics.
- Durable worker heartbeat persistence, independent-session reporter, current-job visibility and graceful stopped status in migration 0005_worker_heartbeats.

OBS-02 centralized metrics/monitoring:
- Migration 0006_metrics_snapshots persists process-level API/worker snapshots.
- Independent-session publishers and authenticated GET /internal/metrics exporter; exporter disabled by default and requires a 32+ character Bearer token.
- Optional Prometheus/Alertmanager Compose profile; localhost-only ports; five alert rules.
- Worker Compose service publishes metrics when enabled, explicitly disables exporter and receives no metrics token.
- Generic Alertmanager webhook configuration is present; real receiver configuration and delivery remain unverified.
- Tests cover snapshot validation/upsert/staleness, reporter lifecycle, exporter auth, monitoring YAML, alert definitions, and Compose publisher/exporter isolation.
- CI run 43121685847 on commit 38e53d1db0eb27e27b4b588ef5062c61c5cfbff0 PASS: Ruff format/lint, pytest 60 passed, SQLite migration, PostgreSQL 16 migration, PostgreSQL persistence smoke, Prometheus config/rules, Alertmanager config, Docker build. 46 existing warnings retained.

Known limitations / pending:
- Apply migrations 0005–0006 to actual Supabase with migration identity; audit runtime-role DML permissions for both new tables.
- No real Alertmanager webhook delivery test.
- No controlled real worker business/economy handler integration against Supabase.
- Production load/concurrency and failure/recovery behavior remain unverified.
- Supabase service/database restart and disaster recovery remain untested.
- Backup/PITR and CA/hostname certificate validation remain deferred.

Exact next task: hosted Supabase migration and least-privilege grant acceptance for 0005–0006, followed by authenticated Prometheus scrape and a real webhook delivery test. Then controlled worker-handler integration and representative load/concurrency/failure-recovery tests. Do not claim production-ready status.
