# LifeVerse — Dependency Map

## Rules
Dependencies point toward lower-level contracts and domain abstractions. Core must not depend on clients, deployment vendors or concrete external providers.

## Layers
Core Domain
→ Application/use cases
→ Infrastructure/API/adapters
→ Clients

## Domain dependency groups
- Account/Character depends on identity and world-location contracts.
- Jobs depend on character skills, location and economy.
- Economy depends on currency/account ownership and transaction rules.
- Inventory/assets depend on ownership and transaction rules.
- Property depends on location, ownership and economy.
- Travel depends on location, transportation, economy and world time.
- Social depends on player/NPC identities and relationship rules.
- Missions depend on player state plus relevant world/economy/social events and reward rules.
- NPC depends on world time/location and relationship/domain state.
- Events can affect multiple systems but must resolve through domain/application commands.
- Business depends on ownership, employees, inventory, market and economy.
- Market depends on assets/items, currency, orders, supply/demand and atomic transaction rules.

## Infrastructure dependencies
- Database implements persistence contracts.
- Queue implements asynchronous job contracts.
- Scheduler triggers idempotent application workflows.
- Cache is an optimization, never the authoritative source of state.
- External services are adapters behind interfaces.
- API maps transport requests to application commands.
- Clients call API/application interfaces only.

## Forbidden dependencies
- Core → Telegram/Web/Mobile
- Core → Railway-specific APIs
- Core → concrete database driver
- Core → concrete AI provider
- Client → direct database mutation
- AI → direct authoritative state mutation
- Cache → sole source of authoritative state
