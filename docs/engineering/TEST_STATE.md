# TEST STATE
Earlier final phases 26–32 candidate CI: PASS.
Verified workflow: 35589115359.
Earlier quality gates: Ruff format PASS; Ruff lint PASS; pytest PASS (24 passed); Alembic upgrade head PASS; Docker container build PASS.
Earlier regression: PASS. E2E database-backed health/readiness: PASS. Job idempotency, atomic claim, retry/backoff, lease recovery and dead-letter tests: PASS.

OPS-DB-01 PostgreSQL compatibility:
- Ruff format/lint PASS.
- pytest 28 passed.
- SQLite Alembic migration PASS.
- PostgreSQL 16 Alembic migration PASS.
- PostgreSQL schema and committed write/read/delete smoke PASS.
- Docker container build PASS.

Actual Supabase Session Pooler acceptance (2026-11-12, last verified at revision 0004_phases_26_32):
- Actual hosted project Alembic upgrade head using migration/admin identity: PASS.
- Public table count: 44; Alembic revision: 0004_phases_26_32.
- Runtime role privilege audit: PASS; non-superuser/non-createdb/non-createrole/no-bypassrls; public schema CREATE denied; app-table DML and sequence USAGE allowed; alembic_version SELECT denied.
- Runtime-role persistence across independent Python processes: PASS; test-row cleanup PASS; remaining test records 0.
- Runtime-role DDL denial: PASS; probe table absent.
- API startup and /health: PASS (status=ready, database=ok); clean API restart and post-restart /health PASS.
- Worker --once exit code 0; queue empty before and after; no handler invoked.
- Client connection TLS encryption PASS; CA/hostname certificate validation deferred.
- Backup/restore/PITR deferred.
- Migrations 0005 and 0006 have NOT yet been applied to hosted Supabase.

OBS-01 / durable worker heartbeat:
- CI run 43119236816 on commit 22d2d8e889ef03f6a111edbe9da86731c4443df7 PASS: Ruff format/lint, pytest 46 passed, SQLite/PostgreSQL migrations, PostgreSQL persistence smoke and Docker build.
- Existing warnings retained; no tests weakened.

OBS-02 centralized metrics and monitoring:
- CI run 43121145977 on commit 43b3b6bc41295efe79703b7b02ebf8754e96bb77.
- Ruff format: PASS.
- Ruff lint: PASS.
- pytest: PASS — 60 passed in 3.94s.
- SQLite Alembic migration: PASS.
- PostgreSQL 16 Alembic migration: PASS.
- PostgreSQL schema and persistence smoke: PASS.
- Prometheus config validation with promtool: PASS.
- Prometheus alert rule validation with promtool: PASS — 5 rules.
- Alertmanager config validation with amtool: PASS.
- Docker build: PASS.
- Warnings: 46 total (one Starlette/httpx TestClient deprecation and 45 datetime.utcnow() deprecations); retained, not suppressed.
- First monitoring-validation attempt failed because the Prometheus/Alertmanager image entrypoints were invoked as arguments. Corrected with explicit --entrypoint promtool/amtool; complete rerun passed.

Still not tested: hosted Supabase migrations 0005–0006 and runtime grants, real alert webhook delivery, controlled worker business/economy handler integration against Supabase, production load/concurrency and failure/recovery, Supabase service/database restart, backup restore/PITR. Backup/PITR and CA/hostname validation remain deferred.
