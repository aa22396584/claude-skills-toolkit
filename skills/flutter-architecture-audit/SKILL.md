---
name: flutter-architecture-audit
description: "Audits the architecture and maintainability of a Flutter project. Use for full project reviews involving module boundaries, feature organization, state management, dependency injection, navigation, repositories/data sources, error handling, concurrency, lifecycle/disposal, platform channels, generated code, or dependency governance. Produces source-backed findings and migration slices without automatically rewriting the app."
---

# Flutter Architecture Audit

Assess whether the codebase can evolve safely. Do not reward a project merely for
matching a named architecture; judge boundaries, ownership, and change cost.

## Workflow

1. Map entry points, packages, feature/module boundaries, navigation, state
   containers, domain/data layers, platform integrations, and generated code.
2. Trace three representative flows end to end: UI event to state, state to data,
   and failure/cancellation back to UI.
3. Read `references/checklist.md` and gather repository-relative evidence.
4. Distinguish defects from deliberate tradeoffs. Record project scale, team size,
   release pressure, and platform requirements when known.
5. Recommend incremental migration slices with tests and rollback boundaries.
   Avoid “rewrite to clean architecture” as a conclusion.

## Required output

- concise architecture map;
- strengths worth preserving;
- findings with evidence, impact, confidence, and verification;
- cyclic or ambiguous ownership boundaries;
- lifecycle/concurrency risks;
- dependency and generated-code risks;
- no more than five migration slices ordered by leverage and safety;
- explicit non-goals and uncertainties.

Never claim a memory leak from a missing-looking `dispose` without proving object
ownership and lifetime. Never condemn multiple state-management libraries without
checking whether they are intentionally isolated by module or migration stage.
