# LifeVerse — Product Specification

## Status
Phase 0 working specification. This document is authoritative for product scope until a later documented decision supersedes it.

## Product
LifeVerse is a persistent online life simulation in which a player creates a character, lives in a data-driven world, earns and spends money, develops skills and relationships, works, travels, owns assets, completes missions, interacts with NPCs and experiences world events.

## Core gameplay loop
1. Create or load a persistent account and character.
2. Establish a location and initial circumstances.
3. Choose activities such as work, learning, social interaction, travel, missions or asset management.
4. Resolve actions through authoritative domain rules.
5. Persist state and audit important changes.
6. Progress through skills, wealth, relationships, assets, reputation and opportunities.
7. React to dynamic world/economic/social events.
8. Repeat with increasingly broad choices and consequences.

## Player lifecycle
Account → identity linkage → character creation → initial world placement → active simulation → progression → temporary/inactive state → recovery/resume. Account identity is independent of any client identity.

## World model
The world is data-driven and initially based on real-world countries, cities, currencies and realistic economic metadata. World state includes authoritative time, locations, movement/travel state, city state and scheduled/dynamic events.

## Core systems
- Player and character
- Countries, cities and world
- Economy and financial history
- Jobs and careers
- Skills and progression
- Items, inventory and assets
- Housing/property
- Transportation/travel
- Social relationships and groups
- NPCs
- Missions/quests
- Events
- Business
- Market
- Security and anti-exploit
- Localization
- Background processing
- Observability
- Optional law/crime/combat only after product validation
- AI as an isolated intent-producing layer, if/where product requirements justify it

## Authoritative state-change flow
Request → authentication/authorization → validation → Game Engine/Core rules → state change → persistence → audit.

AI follows: AI intent → validation → Game Engine → state change → persistence.

## Clients
Telegram, Telegram Mini App, Web, Android and iOS are clients, not sources of domain truth. Client support is introduced only where justified by product needs.

## Economy principles
Every creation or destruction of value must have a documented source/reason. Transactions are atomic, idempotent where applicable and auditable.

## Data-driven catalogs
Countries, cities, currencies, jobs, skills, items, vehicles, properties, missions, NPC definitions, events and similar catalogs must be externalized from core rule logic so data can evolve without changing the engine.

## Localization
Persian and English are minimum supported languages. User-facing text belongs in localization catalogs rather than core rules.

## Scope decisions pending
- Exact initial gameplay content volume
- Law/crime/combat inclusion
- Monetization activation
- Initial client priority
- Exact AI provider strategy
- Exact database/queue/cache technology

Pending choices must not leak into core domain contracts before approval.
