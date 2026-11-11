# TEST STATE
Earlier final phases 26–32 candidate CI: PASS.
Verified workflow: 35589115359.
Earlier quality gates: Ruff format PASS; Ruff lint PASS; pytest PASS (24 passed); Alembic upgrade head PASS; Docker container build PASS.
Earlier regression: PASS. E2E database-backed health/readiness: PASS. Job idempotency, atomic claim, retry/backoff, lease recovery and dead-letter tests: PASS.

PostgreSQL compatibility task OPS-DB-01:
- Verified workflow: 43017388284 (per latest continuation record).
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
- Runtime role privilege audit: PASS; non-superuser/non-createdb/non-createrole/no-bypassrls; public schema CREATE denied; app-table SELECT/INSERT/UPDATE/DELETE and sequence USAGE allowed; alembic_version SELECT denied.
- Runtime-role persistence across independent Python processes: PASS.
- Test-row cleanup: PASS; remaining test records 0.
- Runtime-role DDL denial: PASS; probe table absent.
- API startup and /health: PASS (status=ready, database=ok).
- API clean shutdown/restart and post-restart /health: PASS.
- Worker --once: process exit code 0.
- Queue inspection before and after worker: NO JOB RECORDS; no queued work and no unintended queue mutation.
- Regression after actual Supabase configuration: pytest 28 passed.
- Warnings observed: one Starlette/httpx deprecation and 45 datetime.datetime.utcnow() deprecations; retained as follow-up work.

Not tested: Supabase service/database restart, backup restore/PITR, deployed TLS enforcement, alert delivery, worker handler execution, and production load/concurrency. Worker handler was intentionally not run because no controlled test job existed and production handlers may mutate game/economic state.
