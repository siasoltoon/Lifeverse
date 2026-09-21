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
