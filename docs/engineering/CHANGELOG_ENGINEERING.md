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
- Remaining operational readiness work: verify backup/PITR restore, deployed TLS, alert delivery, controlled worker handler integration and load/concurrency.

2026-11-12
- OPS-DB-03 / OBS-01: added thread-safe process-local request/job metrics with input validation.
- Added API request status/latency middleware and method/status/duration logs without request paths or payloads.
- Added database-independent /health/live and database-backed /health/ready; retained /health readiness compatibility.
- Added completed/failed/dead-letter worker outcome metrics.
- Added metrics validation, thread-safety, API instrumentation and worker outcome regression tests.
- Added docs/operations/OBSERVABILITY.md, explicitly documenting that metrics are process-local and no external alert delivery/exporter is configured.
- CI run 43118198244 on ee5235efd9fa0da9bc650bc22ade31127fdc5354: Ruff format PASS, Ruff lint PASS, pytest 43 passed, SQLite migration PASS, PostgreSQL 16 migration PASS, PostgreSQL persistence smoke PASS, Docker build PASS.
- First CI attempt caught a Ruff formatting issue in a test; corrected without weakening assertions; complete rerun passed.
- Remaining OPS-DB-03 work: central multi-process metrics export, alert delivery, durable worker heartbeat, controlled worker handler integration and load/concurrency validation. Backup/PITR and CA/hostname validation remain deferred.

2026-11-12
- OPS-DB-03: added durable worker heartbeat persistence with migration 0005_worker_heartbeats.
- Added PostgreSQL/SQLite atomic upsert, stale-worker query, independent-session periodic reporter, current-job visibility and graceful stopped status.
- Added heartbeat lifecycle, stale detection and worker current-job regression tests.
- Initial CI run failed only Ruff formatting; corrected in commit 92561ca75cdc1c331c847e02cc0fc16dc215a5f6. Final CI verification pending.
