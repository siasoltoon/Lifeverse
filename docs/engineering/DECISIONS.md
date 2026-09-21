# DECISIONS
D-0001 Greenfield repository verified.
D-0002 Deployment-agnostic architecture; Railway is not a core dependency.
D-0003 Core/Game Engine owns authoritative state transitions.
D-0004 Account identity is independent from Telegram/Web/Mobile identities.
D-0005 AI is isolated and intent-only until validated by the Game Engine.
D-0006 Law/crime/combat remains approval-gated.
D-0007 Initial backend stack: Python 3.12 + FastAPI + SQLAlchemy + Alembic + pytest + Ruff. Portable and behind architectural boundaries.
