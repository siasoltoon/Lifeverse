# ARCHITECTURE MAP
Implemented foundation:
- src/lifeverse/config.py — environment-driven configuration
- src/lifeverse/db.py — SQLAlchemy engine/session boundary
- src/lifeverse/domain.py — domain rules
- src/lifeverse/services.py — application service layer
- src/lifeverse/api.py — thin FastAPI transport
- migrations/ — versioned persistence schema
- tests/ — automated tests
- .github/workflows/ci.yml — CI quality gate
Dependency direction: Core/Domain → Application → Infrastructure/API/Clients.
Clients and transport do not directly mutate authoritative state.
No Railway-specific dependency exists in core/application design.
