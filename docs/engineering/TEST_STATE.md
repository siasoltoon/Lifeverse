# TEST STATE
Earlier final phases 26–32 candidate CI: PASS.
Verified workflow: 35589115359.
Earlier quality gates: Ruff format PASS; Ruff lint PASS; pytest PASS (24 passed); Alembic upgrade head PASS; Docker container build PASS.
Earlier regression: PASS. E2E database-backed health/readiness: PASS. Job idempotency, atomic claim, retry/backoff, lease recovery and dead-letter tests: PASS.

PostgreSQL compatibility task OPS-DB-01:
- Verified workflow: 43017377284 / 43017377266 per PR record.
- Ruff format: PASS.
- Ruff lint: PASS.
- pytest: PASS (28 passed; 46 warnings).
- SQLite Alembic upgrade head: PASS.
- PostgreSQL 16 Alembic upgrade head: PASS.
- PostgreSQL schema and committed write/read/delete smoke: PASS.
- Docker container build: PASS.

Actual Supabase Session Pooler acceptance (2026-11-12):
- Actual hosted project Alembic upgrade head using migration/admin identity: PASS.
- Public table count: 44; Alembic revision: 0004_phases_26_32.
- Runtime role privilege audit: PASS; non-superuser/non-createdb/non-createrole/no-bypassrls; public schema CREATE denied; app-table DML and sequence USAGE allowed; alembic_version SELECT denied.
- Runtime-role persistence across independent Python processes: PASS.
- Test-row cleanup: PASS; remaining test records 0.
- Runtime-role DDL denial: PASS; probe table absent.
- API startup and /health: PASS (status=ready, database=ok).
- API clean shutdown/restart and post-restart /health: PASS.
- Worker --once: process exit code 0; queue empty before and after; no handler invoked.
- Regression after actual Supabase configuration: pytest 28 passed.
- Client connection TLS encryption: PASS; CA/hostname certificate validation deferred.
- Backup/restore/PITR deferred.

OBS-01 observability baseline CI:
- Workflow run: 43118198244.
- Commit: ee5235efd9fa0da9bc650bc22ade31127fdc5354.
- Ruff format: PASS.
- Ruff lint: PASS.
- pytest: PASS — 43 passed in 3.56s.
- SQLite Alembic upgrade head: PASS.
- PostgreSQL 16 Alembic upgrade head: PASS.
- PostgreSQL schema and committed persistence smoke: PASS.
- Docker container build: PASS.
- Warnings: 46 total (one Starlette/httpx TestClient deprecation and 45 datetime.utcnow() deprecations); retained, not suppressed.
- First CI attempt failed only Ruff formatting in a new test assertion; the formatting was corrected and the subsequent complete workflow passed.

Not tested / still pending: centralized metrics export, external alert delivery, controlled real worker-handler execution against Supabase, production load/concurrency and failure/recovery, Supabase service/database restart, backup restore/PITR. Backup/PITR and CA/hostname validation are deferred by decision.


Durable worker heartbeat (OPS-DB-03 follow-up):
- Added migration 0005_worker_heartbeats for persistent worker identity, status, started/last-seen/stopped timestamps and optional current job.
- Added atomic SQLite/PostgreSQL upsert, stale-worker query, periodic reporter using an independent database session, current-job tracking and clean shutdown status.
- Added tests for upsert/stale detection, current-job visibility and reporter shutdown.
- Initial CI attempts 43118898302 and 43119128692 caught two Ruff formatting differences (jobs.py and one test assertion); both were corrected without weakening tests. Final CI run 43119236816 on commit 22d2d8e889ef03f6a111edbe9da86731c4443df7 PASS: Ruff format, Ruff lint, pytest 46 passed (46 existing warnings), SQLite migration, PostgreSQL 16 migration, PostgreSQL schema/persistence smoke and Docker build.
