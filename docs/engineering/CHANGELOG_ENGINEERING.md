# ENGINEERING CHANGELOG
2026-09-21
- Phases 0–15 completed, tested, verified and merged.
- Phases 16–25 completed and merged with persistent events, business, market, law/crime/combat, AI intent boundary, localization, anti-exploit, security and performance foundations.
- Phase 26: persistent background job queue with idempotency, atomic conditional claims, worker leases, recovery, retries/backoff and dead-letter state.
- Phase 27: expanded unit/integration/API/reliability regression coverage.
- Phase 28: database readiness, operational metrics and structured timing logs.
- Phase 29: portable worker entrypoint, Dockerfile and docker-compose deployment topology; no Railway-specific business dependency.
- Phase 30: deployment and operations runbooks plus production audit document.
- Phase 31: database-backed health E2E and application integration verification.
- Phase 32: final candidate audit across persistence, state boundaries, job reliability, security, deployment and regression gates.
- Root causes fixed during verification: Ruff formatting, unused lint assignment, worker lease ownership bug, and stale health contract assertion.
- Verified candidate CI 35589115359: Ruff format PASS, Ruff lint PASS, pytest PASS (24 passed), Alembic upgrade head PASS, Docker container build PASS.
- PR #6 merged as d8f308e062a175f3a9d56da70fbb1e1fd843a2f9.

2026-11-11
- OPS-DB-01: added psycopg 3, centralized PostgreSQL URL normalization and SQLAlchemy connection pre-ping while retaining SQLite local development.
- Added PostgreSQL 16 CI service with Alembic migration and committed persistence smoke checks.
- Added four database URL normalization tests and documented Supabase Session Pooler/Direct selection and credential boundaries.
- Verified workflow 43017388284: Ruff format PASS, Ruff lint PASS, pytest 28 passed, SQLite migration PASS, PostgreSQL 16 migration PASS, PostgreSQL persistence smoke PASS, Docker build PASS.
- PR #7 opened as draft; actual Supabase-hosted acceptance initially pending.

2026-11-12
- OPS-DB-02 actual Supabase Session Pooler acceptance: Alembic upgrade head PASS; 44 public tables and revision 0004_phases_26_32 verified.
- Created and audited restricted lifeverse_runtime role; schema DDL denied, application DML/sequence access allowed, alembic_version access denied.
- Runtime-role write/read across independent processes and cleanup PASS; runtime DDL denial probe PASS.
- API /health PASS before and after clean API process restart.
- Worker --once exited 0 with an empty queue before and after; no production handler was invoked.
- Regression pytest: 28 passed. Recorded one Starlette/httpx and 45 datetime.utcnow deprecation warnings for follow-up; no tests weakened.
- TLS encryption verified; CA/hostname certificate validation deferred. Backup/PITR deferred by user decision.

2026-11-12
- OBS-01: added thread-safe process-local request/job metrics, API request instrumentation, liveness/readiness probes and privacy-conscious request logs.
- Added durable worker heartbeat persistence, independent-session periodic reporter, current-job visibility and graceful stopped status with migration 0005_worker_heartbeats.
- OBS-02: added migration 0006_metrics_snapshots, cross-process metric snapshot publishing, authenticated Prometheus text exporter, optional Prometheus/Alertmanager Compose profile and five operational alert rules.
- Fixed Compose worker monitoring environment: worker publishes snapshots when enabled, keeps exporter disabled and receives no metrics token.
- Added Compose wiring regression assertions and real promtool/amtool validation to CI. First validator attempt exposed incorrect Docker entrypoint invocation; fixed with explicit --entrypoint.
- Verified CI run 43121685847 on commit 38e53d1db0eb27e27b4b588ef5062c61c5cfbff0: Ruff format/lint PASS, pytest 60 passed, SQLite/PostgreSQL migrations PASS, PostgreSQL persistence smoke PASS, Prometheus config/rules PASS, Alertmanager config PASS, Docker Compose config PASS, Docker build PASS.
- 46 existing warnings remain visible; none suppressed and no tests weakened.
- Remaining OPS-DB-03: apply migrations 0005–0006 to actual Supabase and verify runtime grants, configure/test real webhook delivery, controlled worker-handler integration, representative load/concurrency/failure recovery and hosted DB restart/recovery. Backup/PITR and CA/hostname validation remain deferred.

- Deployment hardening: .env.example leaves LIFEVERSE_DATABASE_URL unset by default, preserving the local Python SQLite default while allowing Docker Compose to select its persistent /data/lifeverse.db named-volume fallback. Regression assertions for the example and Compose DB paths are included in the 60-test CI run 43121685847 (Docker Compose config validation also PASS).

2026-11-12
- OBS-03: fixed business payroll worker result handling; added BusinessPayrollPayment with a unique idempotency key and atomic payroll ledger/wallet/business/audit transaction.
- Added lazy legacy payroll AuditLog backfill so pending pre-migration jobs cannot repay already-settled employees.
- Added row-level locks for payroll, SELECT FOR UPDATE SKIP LOCKED for event dispatch, and idempotent state/origin checks for travel completion.
- Added migration 0007_business_payroll_payments and migration 0008_expand_ledger_account_code; widened LedgerAccount.code to 128 because full UUID wallet account codes exceed the old 64-character limit.
- Added worker retry integration tests and a PostgreSQL concurrency smoke test covering distinct payroll keys with insufficient funds and duplicate idempotency keys.
- Replaced datetime.utcnow model defaults with timezone-aware UTC defaults; only the Starlette/httpx TestClient deprecation remains.
- Verified CI run 43124375294 on commit 153a3282376df988377babb5c070e028c14e599c: Ruff format/lint PASS, pytest 65 passed with 1 warning, SQLite/PostgreSQL migrations PASS, PostgreSQL persistence/payroll concurrency smoke PASS, promtool/amtool validation PASS, Docker Compose config PASS and Docker build PASS.
- Hosted Supabase remains at revision 0004; migrations 0005–0008 and runtime grants, authenticated scrape and actual webhook delivery remain pending. Backup/PITR and CA/hostname validation remain deferred.

2026-11-12
- Extended PostgreSQL concurrency smoke coverage to persistent background jobs: four concurrent workers claimed and completed 24 queued jobs without duplicate or lost claims.
- Verified CI run 43125062636 on commit e8abece630c19df10db3d12302e89934a698d5aa: Ruff format/lint PASS, pytest 65 passed with 1 Starlette/httpx warning, SQLite/PostgreSQL migrations PASS, PostgreSQL persistence/payroll/job-claim concurrency smoke PASS, promtool/amtool validation PASS, Docker Compose config PASS and Docker build PASS.
