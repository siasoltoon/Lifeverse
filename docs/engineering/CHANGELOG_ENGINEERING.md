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
- OBS-02: added migration 0006_metric_snapshots, cross-process metric snapshot publishing, authenticated Prometheus text exporter, optional Prometheus/Alertmanager Compose profile and five operational alert rules.
- Fixed Compose worker monitoring environment: worker publishes snapshots when enabled, keeps exporter disabled and receives no metrics token.
- Added Compose wiring regression assertions and real promtool/amtool validation to CI. First validator attempt exposed incorrect Docker entrypoint invocation; fixed with explicit --entrypoint.
- Verified CI run 43120857558 on commit 131fd754c12a6cbf137ce029f5fe99b7bc1939fa: Ruff format/lint PASS, pytest 60 passed, SQLite/PostgreSQL migrations PASS, PostgreSQL persistence smoke PASS, Prometheus config/rules PASS, Alertmanager config PASS, Docker build PASS.
- 46 existing warnings remain visible; none suppressed and no tests weakened.
- Remaining OPS-DB-03: apply migrations 0005–0006 to actual Supabase and verify runtime grants, configure/test real webhook delivery, controlled worker-handler integration, representative load/concurrency/failure recovery and hosted DB restart/recovery. Backup/PITR and CA/hostname validation remain deferred.
