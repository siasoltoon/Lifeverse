# LifeVerse Architecture Blueprint
Core Domain → Application → Infrastructure/API/Clients.
Clients and transport never directly mutate authoritative state.
State flow: Request → authorization/validation → Game Engine/Core → transaction → persistence → audit.
Relational DB is authoritative; cache is non-authoritative.
Queue/scheduler adapters will invoke application use cases and must be idempotent, retryable and recoverable.
FastAPI is a thin transport layer. Configuration is environment-driven. No Railway-specific dependency exists in core/application.
AI, when introduced: Intent → Validation → Game Engine → State Change → Persistence.
