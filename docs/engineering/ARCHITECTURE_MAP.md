# ARCHITECTURE MAP
Implemented foundation:
- src/lifeverse/models.py — authoritative persistent simulation state
- src/lifeverse/services.py — core/application services for phases 1–15
- src/lifeverse/services_16_25.py — event, business, market, law, combat, AI-intent, localization, anti-exploit, security and performance services
- src/lifeverse/api.py — thin existing FastAPI transport
- src/lifeverse/api_16_25.py — versioned /v1 client API
- src/lifeverse/telegram_adapter.py — client-only Telegram update parser
- migrations/ — versioned persistence schema through 0003
- tests/ — regression coverage
- .github/workflows/ci.yml — read-only CI quality gate
Dependency direction: Core/Domain → Application → Infrastructure/API/Clients.
AI flow: Intent → Validation → Game Engine/authorized executor → State Change → Persistence. AIIntentService never mutates game state during proposal.
Economy and market settlement use idempotency keys and atomic transaction boundaries.
Security includes salted scrypt password hashing, revocable persistent sessions, API rate limiting and audit logging. Password hashing follows an OWASP-compatible scrypt configuration. citeturn0search0
Performance foundations include bounded pagination, targeted indexes and bounded event dispatch; authoritative data remains in the relational database.
No Railway-specific dependency exists in core/application design.
