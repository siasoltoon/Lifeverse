# LIFEVERSE — MASTER BUILD MISSION

**Greenfield → Production Ready**

## Mission

Build **LifeVerse** from zero through design, implementation, testing, integration, hardening and final production verification.

Repository: `siasoltoon/Lifeverse`

This master mission is the authoritative product and engineering roadmap. Project Instructions define execution rules; persistent engineering files record actual repository state.

## PERSISTENT ENGINEERING MEMORY

Maintain inside `docs/engineering/`:

- PROJECT_STATE.md
- ARCHITECTURE_MAP.md
- PHASE_STATE.md
- TASK_STATE.md
- TEST_STATE.md
- DECISIONS.md
- CHANGELOG_ENGINEERING.md

These files allow a new ChatGPT conversation to continue without restarting the investigation.

## EXECUTION STRATEGY

Never implement a large phase blindly.

For every phase:
1. Analyze objective.
2. Break into small independent tasks.
3. Create execution plan.
4. Execute one task at a time.

Before each task:
- Inspect current state.
- Understand existing implementation.
- Avoid duplicate code.
- Avoid unnecessary rewrites.
- Preserve working functionality.
- Check architecture consistency.

During:
- Implement required changes.
- Follow architecture.
- Add error handling, logging and validation.
- Update documentation when required.

After:
- Run tests.
- Validate integration.
- Check runtime errors.
- Fix discovered problems.
- Update engineering memory.
- Commit successful changes.

If a task fails: stop progression, diagnose root cause, fix, retest and regress.

Every task must have objective, implementation steps, validation steps, test results and commit message.

## INITIAL STATE

Never assume features, files, architecture, database, API, bot or services already exist. Inspect the repository first. If empty or nearly empty, record:

**GREENFIELD PROJECT**

Existing code may be reused only after verification.

## PRODUCT GOAL

Build a complete, realistic, persistent, secure, scalable, modular, testable and production-ready online life simulation.

The player lives in a persistent online/text world with interacting systems.

Design for long-term development, many players, expandable world/economy, advanced NPCs, AI, multiplayer interactions, events and future monetization. Monetization need not be active now, but architecture must not block it.

## NON-NEGOTIABLE PRINCIPLES

### No Fake Implementation
No fake production logic, important placeholders, dummy database, fake economy, fake transactions, fake player/NPC state, fake mission completion, status-only implementation or critical TODO. Mocks are allowed only in tests for intentional isolation.

### Realism
Use realistic and validated data for countries, cities, currencies, languages, geography, population, cost of living, jobs, salaries, goods, economy and transportation. Use data-driven catalogs for changing data.

### Data-Driven Design
Countries, cities, jobs, items, vehicles, properties, missions, NPC definitions, events and skills should be data-driven rather than broadly hardcoded.

### Domain Rules
Core game rules belong in Core Domain/Game Engine. UI, Telegram, API and AI must not bypass them.

AI may generate an intent, but must never directly mutate authoritative game state:
**Intent → Validation → Game Engine → State Change → Persistence**

### Persistence
Important game state must persist across restart of server, worker or bot.

### Atomicity
Sensitive economic/state-changing operations must be atomic. Example:
Validate → Check balance → Deduct money → Add item → Record transaction.

### Test-Driven Completion
A feature is complete only after Implementation + Test + Verification + Regression.

## MULTI-CLIENT / DEPLOYMENT-AGNOSTIC ARCHITECTURE

Telegram is only one client. Core logic must not depend on Telegram, Web, Mobile or any specific UI.

Support the architecture for:
- Telegram Bot
- Telegram Mini App
- Web
- Android
- iOS

Account must be independent from Telegram:
**Player Account → Telegram / Web / Mobile identities**

All client operations go through API/Application services.

## DEPLOYMENT INDEPENDENCE

LifeVerse MUST NOT be Railway-only.

The same application architecture must support:
- Railway
- Generic VPS
- Personal server/laptop
- Local development
- GitHub-based CI/CD

Use environment-driven configuration, portable deployment/process definitions, database migrations, health checks and reproducible startup/shutdown.

Never place Railway-specific assumptions in Core Domain, Game Engine or Application contracts. Deployment topology may vary by environment while business logic remains identical.

## REQUIRED ARCHITECTURE

```
LifeVerse
├── core
│   ├── player
│   ├── economy
│   ├── world
│   ├── missions
│   ├── npc
│   ├── social
│   └── rules
├── application
│   ├── services
│   ├── commands
│   ├── workflows
│   └── use_cases
├── infrastructure
│   ├── database
│   ├── cache
│   ├── queue
│   └── external_services
├── api
├── clients
│   ├── telegram_bot
│   ├── telegram_mini_app
│   ├── web
│   └── mobile
└── workers
```

Domain is the source of truth. No client, admin path or external system may directly mutate authoritative state. All state changes follow:
Request → Permission/Validation → Game Engine → State Change → Persistence → Audit.

## PHASE 0 — PRODUCT DISCOVERY & REQUIREMENTS

Tasks:
- Repository discovery
- Product specification
- Core gameplay loop
- Player lifecycle
- World concept
- Progression
- Economy
- Social interaction
- Missions
- NPCs
- Events
- Assets
- Long-term progression
- Complete feature map: Core, World, Player, Economy, Social, Content, AI, Infrastructure, Security, Future
- Dependency map
- Measurable acceptance criteria

Completion requires requirements, feature map, dependency map and acceptance criteria.

## PHASE 1 — ARCHITECTURE & TECHNICAL BLUEPRINT

Design and verify:
- Backend
- Game Engine
- Domain
- Services
- Repositories
- Database
- API
- Bot/UI
- Workers
- Queue
- Scheduler
- Cache
- AI
- Event Bus
- Logging
- Monitoring
- Security
- Error handling
- Configuration

Create architecture diagram, module boundaries, dependency rules, domain boundaries, persistence architecture, background processing architecture and API architecture.

## PHASE 2 — PROJECT FOUNDATION

Create/verify:
- Repository/package structure
- Build/dependency configuration
- Environment and development/production configuration
- Logging
- Error handling
- CI
- Basic tests
- Formatting
- Linting
- Quality gates

Project must build, run, test and receive configuration correctly.

## PHASE 3 — DATABASE & CORE DOMAIN

Implement database, models, migrations, repositories, transactions, constraints, indexes, validation, audit records and persistence tests.

Core entities at minimum:
Player, Character, Country, City, Currency, Account/Wallet, Job, Item, Inventory, Mission, NPC, Event.

Test required CRUD and persistence behavior.

## PHASE 4 — PLAYER & CHARACTER

Implement:
Registration, identity, character creation/profile, attributes, skills, XP, level, reputation, wealth, status, location and progression.

E2E:
Register → Create Character → Save → Restart → Load.

## PHASE 5 — REAL WORLD COUNTRY & CITY

Country data:
Country, capital, region, currency, languages, population, economic metadata, cost of living.

City data:
City, country, population, region, cost of living, jobs, housing, transportation, businesses.

Implement data model, seed/import pipeline, validation, relationships, search, selection and persistence.

Adding a country/city must not require changing the Core Engine.

## PHASE 6 — WORLD ENGINE

Implement:
World clock, game time, date, day/night, seasons, location, movement, travel, city state, world state and scheduled events.

One authoritative source of truth for World State.

## PHASE 7 — ECONOMY ENGINE

Implement:
Currency, wallet, bank, accounts, income, expenses, prices, inflation, supply, demand, transactions, exchange rates and financial history.

No money may appear without a source or disappear without a reason. Important transactions require audit records.

## PHASE 8 — JOB & CAREER ENGINE

Implement:
Job catalog, requirements, skills, salary, working hours, experience, promotions, career paths, job search, job change and unemployment.

Salary/job availability may depend on country, city, economy and skills.

## PHASE 9 — SKILL & PROGRESSION ENGINE

Implement:
Attributes, skills, XP, levels, progression, rewards, achievements and milestones.

Add anti-exploit validation.

## PHASE 10 — ITEM / INVENTORY / ASSET ENGINE

Implement:
Item definitions, inventory, ownership, equipment, consumables, assets, vehicles, properties, item state, durability where appropriate and trading.

Each asset must have owner, type, state and acquisition source.

## PHASE 11 — HOUSING & PROPERTY

Implement:
Houses, apartments, rent, purchase, ownership, maintenance, property value, location, upgrades and utilities.

## PHASE 12 — TRANSPORTATION & TRAVEL

Implement:
Walking, public transport, vehicles, vehicle ownership, travel, inter-city and international travel, cost, time and restrictions.

## PHASE 13 — SOCIAL ENGINE

Implement:
Friends, relationships, groups, communities, reputation, social interactions, messaging, blocking and social status.

Validate all social state transitions.

## PHASE 14 — NPC ENGINE

NPCs must be real game entities, not merely chatbots.

Implement:
Identity, attributes, occupation, location, schedule, state, relationships, goals, behavior and interaction.

NPCs must have persistent Game State.

## PHASE 15 — MISSION / QUEST ENGINE

Data-driven mission engine.

Types:
Main, Side, Daily, Weekly, Dynamic, NPC and Event missions.

Implement:
Objectives, prerequisites, state, progress, rewards, failure, expiration, repeatability and dependencies.

Mission completion must be validated by the Game Engine.

## PHASE 16 — EVENT ENGINE

Implement:
World, city, economic, social, random, scheduled, seasonal and player events.

Persist event state.

## PHASE 17 — BUSINESS ENGINE

Implement:
Business creation, ownership, employees, revenue, expenses, inventory, customers, supply, demand, profit/loss, upgrades and progression.

## PHASE 18 — MARKET ENGINE

Implement:
Buy, sell, orders, pricing, supply, demand, fees, market history and trading.

Market transactions must be atomic. Add anti-manipulation controls.

## PHASE 19 — LAW / CRIME / COMBAT

Implement only if confirmed by Product Specification:
Crime, police, wanted state, law, fines, jail, legal consequences, combat and reputation.

Integrate correctly with Economy and Social.

## PHASE 20 — AI ENGINE

AI is an independent layer.

Implement where required:
Provider abstraction, local/remote AI integration, NPC intelligence, dialogue, decision support, event generation, dynamic content, context, memory, validation, fallback, rate limiting and cost control.

AI NEVER directly changes Game State:
AI → Intent → Validation → Game Engine → State Change.

## PHASE 21 — TELEGRAM / USER INTERFACE

If Telegram is used:
Commands, menus, buttons, navigation, player state, pagination, input validation, notifications, error handling, callback handling and rate limits.

UX must support a large text-based game.

## PHASE 22 — LOCALIZATION

Minimum:
- Persian
- English

Implement translation system, message catalog, parameters, pluralization, formatting, language selection and fallback.

No important user-facing text should be hardcoded in Core.

## PHASE 23 — ANTI-CHEAT / ANTI-EXPLOIT

Review:
Duplicate requests, double rewards, currency duplication, item duplication, replay, race conditions, invalid state, mission abuse, market abuse and request spam.

Use idempotency, transactions, locks where necessary, validation, audit logs and rate limits.

## PHASE 24 — SECURITY HARDENING

Implement/review:
Authentication, authorization, input validation, secret management, API security, database security, rate limiting, abuse prevention, safe error handling, exception recovery and audit logging.

## PHASE 25 — PERFORMANCE & SCALABILITY

Review:
Database queries, N+1, caching, async work, queues, background processing, concurrency, memory, CPU, large inventories, large player counts, large world state and transaction history.

## PHASE 26 — BACKGROUND JOBS / SCHEDULER

Implement as required:
Salary, rent, business processing, market updates, daily/weekly resets, NPC schedules, world events, notifications and expiration.

Jobs must be idempotent, retryable, recoverable and observable.

## PHASE 27 — COMPLETE TEST SUITE

Unit tests for game rules, economy, player, character, missions, items, skills, world, NPCs and transactions.

Integration tests for database, services, APIs, scheduler, queue, AI and Telegram.

E2E:
Register → Character → Country → City → Job → Income → Expense → Mission → XP → Level → Item → Travel → NPC → Social → Event → Economy → Persistence → Restart → Recovery.

Failure tests:
Invalid input, duplicates, timeout, DB failure, queue failure, AI failure, scheduler failure, concurrent transaction, restart and recovery.

## PHASE 28 — OBSERVABILITY

Implement:
Structured logging, error tracking, audit logs, economy logs, player transaction logs, security logs, performance metrics and health checks.

Keep logging structured and useful; avoid uncontrolled noise.

## PHASE 29 — DEPLOYMENT

Implement and verify:
Environment configuration, production configuration, startup/shutdown, migrations, health checks, workers, scheduler, queue, recovery, restart and reproducible deployment.

Verify supported deployment targets without making the system Railway-dependent.

## PHASE 30 — DOCUMENTATION

Document:
Architecture, setup, environment, database, API, game systems, economy, missions, NPCs, AI, deployment, testing and development workflow.

## PHASE 31 — FULL END-TO-END SYSTEM TEST

Run a realistic player journey:

Registration
→ Character Creation
→ Country
→ City
→ Job
→ Earn Money
→ Spend Money
→ Mission
→ XP
→ Level
→ Inventory
→ Asset
→ Travel
→ NPC
→ Social Interaction
→ Event
→ Economy
→ Persistence
→ Restart
→ Recovery

No state may be lost or corrupted.

## PHASE 32 — FINAL PRODUCTION AUDIT

Audit the entire repository.

No remaining:
- Critical TODO
- Important placeholder
- Fake implementation
- Broken integration
- Failing test
- Critical security issue
- Critical exploit
- Corrupted persistence
- Critical race condition
- Deployment blocker
- Undocumented critical system

## FINAL ACCEPTANCE

LifeVerse is FINAL / PRODUCTION READY only when:
- required phases are completed
- all tasks are verified
- tests pass
- regression passes
- database is stable
- persistence is correct
- economy is trustworthy
- Game State consistency is preserved
- anti-exploit controls are appropriate
- security is appropriate
- performance is acceptable
- deployment is reproducible
- no core feature is fake
- final audit succeeds

## TEST RULE

Never make tests green by:
- deleting tests
- weakening assertions
- removing validation
- ignoring errors
- faking features

Failure flow:
Diagnose → Fix Implementation → Test Again → Regression.

## ARCHITECTURE CHANGE RULE

If current architecture becomes unsuitable:
Analyze the problem, document the decision, update architecture and migrate safely. Do not create intentional technical debt merely to finish faster.

## FEATURE DISCOVERY

If a necessary system is discovered during development, add it to the Feature Map and roadmap. Do not omit essential functionality merely because it was not explicitly listed above.

## REPORTING

After every task report:
Task ID, review, implementation, changed files, tests, test result, regression result, problems found/fixed and final status.

At phase completion report:
PHASE X COMPLETED, tasks, tests, failures/fixes, architecture changes, regression result and next phase.

At final completion report:
all phases, task/test/regression counts, failures and fixes, architecture, database, player/character, world, economy, jobs, missions, NPC, AI, social, security, anti-exploit, performance, deployment, documentation, remaining problems and final audit.

## START

Step 1: Inspect repository.
Step 2: If empty, record GREENFIELD PROJECT DETECTED.
Step 3: Execute Phase 0.
Step 4: Create Product Specification and Feature Map.
Step 5: Design Architecture Blueprint.
Step 6: Begin real implementation.
Step 7: Execute the roadmap using Review → Plan → Implement → Test → Verify → Fix → Regression → Complete.

Continue automatically to the next verified phase when the requested execution scope and available tools allow it; do not claim work that was not actually executed or verified.

## FINAL GOAL

Build a large-scale online life simulation with:
**Realistic World + Persistent Player + Dynamic Economy + Jobs + Skills + Missions + NPCs + Social Systems + Events + AI + Scalable Infrastructure**

Only after complete verification may the project be declared:

**FINAL / PRODUCTION READY**
