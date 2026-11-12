# TASK STATE
Current task: OPS-DB-03 — operational readiness validation
Status: IN PROGRESS. OBS-01/OBS-02 observability and OBS-03 worker-handler retry safety/payroll concurrency are CI verified; hosted operational acceptance is not complete.
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
- Hosted database remains at last verified revision 0004; do not assume migrations 0005–0008 have been applied there.

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

OBS-03 worker-handler and economic retry safety:
- Migration 0007_business_payroll_payments adds a unique idempotent payroll payment ledger.
- Business payroll locks business, employee and wallet rows; new payment, business debit, wallet credit and audit record share one transaction. Legacy AuditLog idempotency keys are lazily imported to protect pre-migration retries.
- business.payroll handler now returns a string amount correctly; event dispatch uses row locks with SKIP LOCKED; travel completion validates state/origin and is idempotent.
- Migration 0008_expand_ledger_account_code widens ledger_accounts.code to 128 for wallet identifiers containing full character and currency UUIDs.
- CI run 43124375294 on commit 153a3282376df988377babb5c070e028c14e599c PASS: 65 tests, 1 Starlette/httpx warning; Ruff format/lint; SQLite/PostgreSQL migrations; PostgreSQL persistence, payroll concurrency and 4-worker/24-job claim concurrency smoke; Prometheus/Alertmanager/Compose config validation; Docker build.

Known limitations / pending:
- Apply migrations 0005–0008 to actual Supabase with migration identity; audit runtime-role DML permissions for worker_heartbeats, operational_metric_snapshots and business_payroll_payments.
- No real Alertmanager webhook delivery test.
- Worker business-payroll/event-dispatch/travel-completion retry integration and PostgreSQL payroll concurrency are CI verified, but not yet run against the actual Supabase project.
- Broader queue throughput/load and multi-worker failure/recovery remain unverified.
- Supabase service/database restart and disaster recovery remain untested.
- Backup/PITR and CA/hostname certificate validation remain deferred.

Exact next task: after local branch sync, hosted Supabase migration and least-privilege grant acceptance for 0005–0008, followed by authenticated Prometheus scrape and a real webhook delivery test. Then broader queue/load and multi-worker failure-recovery tests. Do not claim production-ready status.
