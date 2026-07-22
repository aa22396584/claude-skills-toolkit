# Flutter test checklist

## Unit and domain

- Business rules include boundary, invalid, cancellation, and error cases.
- Time, randomness, UUIDs, network, storage, and platform services are controllable.
- Serialization and schema evolution have compatibility fixtures.
- State reducers/notifiers cover concurrent and stale-response behavior.

## Widget

- Loading, empty, error, partial, success, retry, disabled, and accessibility states.
- Navigation and dialog flows assert outcomes, not implementation trivia.
- Tests avoid broad `pumpAndSettle` when perpetual animations/timers exist.
- Keys and finders reflect user-visible semantics where possible.

## Golden

- Stable fonts, locale, pixel ratio, theme, and platform assumptions.
- Goldens target high-value visual contracts rather than every screen.
- Diff review and regeneration commands are reproducible.

## Integration and end-to-end

- Authentication, onboarding, purchase/subscription, offline recovery, deep links,
  notification entry, database migration, and critical platform integrations.
- Tests isolate external systems or use controlled test environments.
- Artifacts include logs/screenshots/traces needed to diagnose CI failures.

## Flake risks

- Wall-clock sleeps, live network calls, shared mutable state, unordered assertions,
  leaked timers, unawaited futures, port collisions, and environment-dependent paths.
- Tests that pass only when run alone or in a fixed order.

## Coverage interpretation

Line coverage is a navigation metric, not proof. Highlight untested branches,
state transitions, failure modes, and platform boundaries even when line coverage
is high.
