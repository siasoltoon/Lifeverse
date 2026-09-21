# DECISIONS

## D-0001 — Greenfield repository verified
Status: Accepted
Decision: Treat LifeVerse as greenfield because verified repository history contains only README.md and the master build mission.
Reason: No application implementation was found in the verified history.

## D-0002 — Deployment agnostic
Status: Accepted
Decision: Railway must not be an architectural dependency. Environment configuration and adapters must support multiple deployment targets.
Reason: Product engineering requirement.

## D-0003 — Domain authority
Status: Accepted
Decision: Core/Game Engine is the authoritative source of game rules and state transitions. Clients and external systems cannot directly mutate authoritative state.
Reason: Consistency, security and testability.

## D-0004 — Account identity independent of Telegram
Status: Accepted
Decision: Account identity is modeled independently from Telegram/Web/Mobile identities.
Reason: Multi-client support and portability.

## D-0005 — AI isolation
Status: Accepted
Decision: AI can propose intents/recommendations but cannot directly mutate authoritative state.
Reason: Deterministic validation, security and auditability.

## D-0006 — Approval-gated law/crime/combat
Status: Accepted
Decision: Do not implement law/crime/combat until confirmed by product specification.
Reason: Master mission explicitly gates these systems.
