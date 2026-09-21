# ARCHITECTURE MAP
Implemented foundation:
- src/lifeverse/config.py — environment-driven configuration
- src/lifeverse/db.py — SQLAlchemy engine/session boundary
- src/lifeverse/domain.py — domain rules
- src/lifeverse/services.py — application services for player/world/economy/career/skills/inventory/property/travel/social/NPC/missions
- src/lifeverse/api.py — thin FastAPI transport
- src/lifeverse/models.py — persistent authoritative simulation state
- migrations/ — versioned persistence schema
- tests/ — automated regression tests
- .github/workflows/ci.yml — read-only CI quality gate
Dependency direction: Core/Domain → Application → Infrastructure/API/Clients.
Authoritative state transitions remain in application/domain services; clients and transport do not directly mutate state.
Economy transfers use idempotency keys, balanced ledger entries, wallet validation and audit records.
Property purchase and mission rewards apply multi-step state changes in one transaction boundary.
No Railway-specific dependency exists in core/application design.
