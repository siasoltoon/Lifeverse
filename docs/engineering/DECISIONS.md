# DECISIONS
D-0001 Greenfield repository verified.
D-0002 Deployment-agnostic architecture; Railway is not a core dependency.
D-0003 Core/Game Engine owns authoritative state transitions.
D-0004 Account identity is independent from Telegram/Web/Mobile identities.
D-0005 AI is isolated and intent-only until validated by the Game Engine.
D-0006 Law/crime/combat remains approval-gated.
D-0007 Initial backend stack: Python 3.12 + FastAPI + SQLAlchemy + Alembic + pytest + Ruff.
D-0008 World clock/state is persisted and versioned; simulated time is authoritative rather than client-controlled.
D-0009 Economy mutations require idempotency keys and balanced ledger entries; wallet state and audit record are committed atomically.
D-0010 Multi-step rewards and property acquisition use the same transaction boundary as their authoritative state changes.
D-0011 Phase 6–15 catalogs are data-driven and seeded through the existing seed pipeline.
D-0012 Event state is persistent and dispatchable; random events are deterministic from an explicit seed.
D-0013 Business capital must originate from an owner wallet; payroll settles into employee wallets.
D-0014 Market purchases settle buyer debit, seller credit, inventory delivery and listing closure in one transaction.
D-0015 AI produces persisted proposals only; validation precedes any external executor and no AI path directly mutates authoritative state.
D-0016 Telegram is a client adapter only; domain rules remain in application services.
D-0017 Persian and English translations are persisted with English fallback.
D-0018 Anti-exploit signals are auditable records; detection does not silently mutate player state.
D-0019 Security uses salted scrypt password hashing, revocable sessions, rate limiting and audit records.
D-0020 Performance work uses bounded pagination and database indexes.
D-0021 Background jobs are persistent database records with unique idempotency keys, atomic conditional claims, worker leases, retries with backoff and dead-letter state.
D-0022 Readiness is database-backed; operational logs/metrics are separate from authoritative simulation state.
D-0023 Deployment topology is portable: API, worker and migration processes can be independently deployed against the same configured database.
D-0024 PostgreSQL production connectivity uses psycopg 3 through SQLAlchemy; SQLite remains the local development/test default. Standard PostgreSQL URLs are normalized centrally. Supabase Session Pooler is the IPv4-compatible option; Direct is preferred when the runtime has IPv6. Supabase Data API is not part of the backend SQLAlchemy access path.
D-0025 Application runtime must use a restricted PostgreSQL role; project-owner credentials are reserved for controlled administration/migrations and must never be shipped to clients.
D-0026 Operational counters are thread-safe but process-local. They are not a global source of truth and are not exposed publicly; centralized export and alerting require an authenticated multi-process design.
D-0027 Worker liveness is persisted in a dedicated worker_heartbeats table. Each worker reports periodically through an independent DB session, includes its current job when available, and marks clean shutdown; stale detection is query-based and does not itself imply alert delivery.
D-0028 Cross-process operational telemetry uses per-process snapshots persisted in operational_metric_snapshots and scraped through one designated authenticated API exporter. Prometheus is the time-series store; snapshots are not authoritative game state.
D-0029 Monitoring is opt-in. The worker publishes snapshots but never runs the metrics exporter and does not receive the metrics bearer token. Prometheus/Alertmanager management ports bind to localhost in the provided Compose profile.
D-0030 Alertmanager uses a generic webhook receiver contract. Alert rules/configuration do not mean alerts are active; activation requires a real receiver URL and a successful delivery test.

D-0031 Business payroll is an immutable payment ledger, not a direct wallet mutation. Each business/job/employee payment has a unique idempotency key; PostgreSQL row locks serialize business balance changes; dialect-native ON CONFLICT DO NOTHING prevents duplicate payment insertion. Business balance debit, employee wallet credit, payroll ledger row and audit log commit atomically. Existing legacy AuditLog idempotency records are lazily backfilled to protect retries across deployment.
D-0032 LedgerAccount.code is 128 characters because wallet account identifiers contain the full character UUID and currency UUID. Do not truncate identifiers to fit the old 64-character column.
D-0033 Event dispatch selects due events with FOR UPDATE SKIP LOCKED; travel completion is state-checked and idempotent so handler commits can be retried safely when queue completion fails.

D-0034 Persistent job claiming uses a conditional UPDATE compare-and-swap after candidate selection; concurrent PostgreSQL worker claims must never duplicate or lose jobs. CI concurrency smoke runs four workers against 24 queued jobs and verifies every job reaches completed exactly once.
