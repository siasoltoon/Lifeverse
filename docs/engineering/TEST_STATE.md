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
- Migrations 0005–0008 have NOT yet been applied to hosted Supabase.

OBS-01 / durable worker heartbeat:
- CI run 43119236816 on commit 22d2d8e889ef03f6a111edbe9da86731c4443df7 PASS: Ruff format/lint, pytest 46 passed, SQLite/PostgreSQL migrations, PostgreSQL persistence smoke and Docker build.
- Existing warnings retained; no tests weakened.

OBS-02 centralized metrics and monitoring:
- CI run 43125062636 on commit e8abece630c19df10db3d12302e89934a698d5aa.
- Ruff format/lint: PASS.
- pytest: PASS — 65 passed in 4.36s, one Starlette/httpx TestClient deprecation warning.
- SQLite and PostgreSQL 16 Alembic migrations: PASS.
- PostgreSQL schema and persistence smoke: PASS.
- PostgreSQL payroll concurrency smoke: PASS.
- PostgreSQL job-claim concurrency smoke: PASS — four concurrent workers claimed and completed 24 queued jobs exactly once.
- Prometheus config and five alert rules validated with promtool: PASS.
- Alertmanager config validated with amtool: PASS.
- Docker Compose config and Docker build: PASS.
- .env.example leaves LIFEVERSE_DATABASE_URL unset; regression assertions confirm local SQLite field default and Compose persistent /data database fallback.
- datetime.utcnow() model-default warnings were fixed; no warnings suppressed.

OBS-03 worker-handler and payroll concurrency:
- CI verified migrations 0007_business_payroll and 0008_expand_ledger_account_code.
- Worker integration tests cover payroll, event dispatch and travel completion when handler state commits but job completion fails, then the job retries.
- PostgreSQL concurrency smoke proves distinct payroll jobs cannot overdraw a business, duplicate idempotency keys cannot credit a wallet twice, and four concurrent workers claim/complete 24 jobs without duplicate or lost claims.
- Payroll ledger uses unique BusinessPayrollPayment idempotency keys, row locks, dialect-native ON CONFLICT DO NOTHING and atomic business/wallet/ledger/audit updates. Legacy AuditLog keys are lazily backfilled.
- business.payroll handler now returns the Decimal amount correctly; event dispatch uses FOR UPDATE SKIP LOCKED; travel completion is state-checked and idempotent.
- LedgerAccount.code widened to 128 to fit wallet:{character_uuid}:{currency_uuid}.

Still not tested: hosted Supabase migrations 0005–0008 and runtime grants, authenticated hosted Prometheus scrape, real alert webhook delivery, broader queue throughput/load and multi-worker failure/recovery, Supabase service/database restart, backup restore/PITR. Backup/PITR and CA/hostname validation remain deferred.
