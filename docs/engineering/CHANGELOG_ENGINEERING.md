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
