# ARCHITECTURE MAP

## Current state
Architecture has not yet been implemented. Product-level boundaries are established only.

## Target boundaries
- core/
- application/
- infrastructure/
- api/
- clients/
- workers/

## Dependency rule
Core/domain rules are independent of clients, deployment providers, concrete persistence drivers and external AI providers.

## Authoritative mutation
Request → authentication/authorization → validation → Game Engine/Core → State Change → Persistence → Audit.

## AI boundary
AI → Intent → Validation → Game Engine → State Change → Persistence.

## Deployment boundary
Deployment adapters/configuration may differ across Railway, VPS, personal server/laptop and CI/CD. Business logic remains identical.

## Status
Architecture blueprint is Phase 1 work and must not be treated as implemented yet.
