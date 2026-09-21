# LifeVerse — Phase 0 Acceptance Criteria

A Phase 0 completion claim requires all criteria below to be documented and reviewable.

1. Product purpose and core gameplay loop are explicit.
2. Player lifecycle is defined.
3. World, economy, progression, social, mission, NPC, event and asset concepts are mapped.
4. Required feature areas are captured in FEATURE_MAP.md.
5. Dependencies and forbidden architectural directions are captured in DEPENDENCY_MAP.md.
6. Account identity is independent from Telegram/client identity.
7. Authoritative state mutation follows validation → Game Engine → persistence.
8. AI, if implemented later, is constrained to intent generation and cannot directly mutate state.
9. Economy value creation/destruction and transaction atomicity are explicit.
10. Data-driven catalogs are identified.
11. Persian and English localization requirements are explicit.
12. Railway is not a required application architecture dependency.
13. Law/crime/combat is explicitly approval-gated.
14. Pending product decisions are listed rather than guessed.
15. Persistent engineering memory exists and records the verified continuation point.
