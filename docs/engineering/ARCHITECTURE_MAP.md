# ARCHITECTURE MAP
Authoritative persistent state:
- src/lifeverse/models.py — simulation state
- src/lifeverse/jobs.py — persistent background job state, atomic claim, leases, retries and worker execution
- src/lifeverse/services.py — core/application services for phases 1–15
- src/lifeverse/services_16_25.py — phases 16–25 application/domain services
- src/lifeverse/observability.py — readiness, bounded operational metrics and timed structured logging
- src/lifeverse/production.py — deployment profile contract
- src/lifeverse/worker.py — portable worker process and registered domain handlers
- src/lifeverse/api.py — HTTP transport and database-backed readiness
- src/lifeverse/api_16_25.py — versioned /v1 client API
- src/lifeverse/telegram_adapter.py — client-only Telegram update parser
- migrations/ — versioned persistence schema through 0004
- tests/ — unit, integration, API, reliability and production-audit regression coverage
- Dockerfile / docker-compose.yml — portable deployment topology
Dependency direction: Core/Domain → Application → Infrastructure/API/Clients.
Background flow: enqueue → persistent queued state → atomic claim → leased running state → domain handler → completed OR retry/dead-letter → audit/logging.
AI flow: Intent → Validation → Game Engine/authorized executor → State Change → Persistence. AIIntentService never mutates game state during proposal.
Economy and market settlement use idempotency keys and atomic transaction boundaries.
Security includes salted scrypt password hashing, revocable persistent sessions, API rate limiting and audit logging.
Performance uses bounded pagination and database indexes; background work is persistent rather than in-memory-only.
No Railway-specific dependency exists in core/application design; Railway is one deployment profile among local/VPS/CI.
