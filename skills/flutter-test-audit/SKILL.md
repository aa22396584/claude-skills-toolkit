---
name: flutter-test-audit
description: "Audits test strategy and missing coverage in a Flutter repository. Use when the user asks to assess tests, coverage, flaky tests, widget/golden/integration tests, critical-flow protection, database migration tests, platform-channel tests, or to build a prioritized Flutter test backlog. Reviews existing tests before generating new ones and does not equate line coverage with confidence."
---

# Flutter Test Audit

Determine which failures can escape today and what smallest test investments would
meaningfully reduce that risk.

## Workflow

1. Inventory test directories, harnesses, fixtures, mocks/fakes, golden assets,
   integration drivers, CI jobs, and coverage artifacts.
2. Map critical product flows and high-change modules to existing tests.
3. Run existing tests with the project’s pinned toolchain when safe. Record command,
   exit code, elapsed time, failed tests, and environment blockers.
4. Read `references/checklist.md` and inspect representative tests for assertion
   quality, determinism, isolation, and maintenance cost.
5. Produce a test-gap matrix and an ordered backlog. Generate tests only when the
   user asks for implementation.

## Ranking

Prioritize gaps using:

```text
risk = user_or_data_impact × change_frequency × defect_likelihood
       × observability_gap ÷ test_cost
```

Do not prioritize easy getters over payment, authentication, migration, offline,
state restoration, or release-critical flows.

## Required output

- existing test inventory and command results;
- critical flow-to-test matrix;
- flaky/nondeterministic patterns with evidence;
- missing unit/widget/golden/integration/migration/contract tests;
- top 10 test additions with purpose, boundary, fixtures, and expected assertions;
- coverage limitations and environments not exercised.
