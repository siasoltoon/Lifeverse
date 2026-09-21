# ENGINEERING CHANGELOG
2026-09-21
- Phase 0 completed and verified.
- Phases 1–15 completed, tested, verified and merged.
- Phase 16 event engine: persistent event definitions, scheduled/player/seasonal/random event creation, deterministic random selection, due-event dispatch and audit.
- Phase 17 business: persistent businesses, currency-backed capital, employee records and wallet-settled payroll.
- Phase 18 market: persistent listings and idempotent atomic buyer/seller settlement with inventory delivery.
- Phase 19 law/crime/combat: persistent cases, resolution workflow and seeded deterministic combat turns.
- Phase 20 AI: persisted intent proposal/validation/execution boundary with no direct AI state mutation.
- Phase 21 Telegram/UI: client-only Telegram update adapter and versioned API/UI capability contract.
- Phase 22 localization: persistent Persian/English translation catalog with fallback.
- Phase 23 anti-exploit: auditable exploit signals and repeated-action detection.
- Phase 24 security: salted scrypt password hashing, revocable sessions, persistent API rate limiting and audit controls.
- Phase 25 performance: bounded pagination, targeted database indexes and bounded event dispatch.
- Root causes fixed during verification: formatter/syntax issues, unused imports, rate-limit persistence, timestamp timezone normalization, SQLite-safe batch migration constraints, and portable scrypt memory settings.
- Final Phase 16–25 CI passed: Ruff format PASS, Ruff lint PASS, pytest PASS (17 passed), Alembic upgrade head PASS.
