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
D-0020 Performance work uses bounded pagination and database indexes; cache/scheduler infrastructure remains isolated for later operational phases.
