# Flutter architecture checklist

## Boundaries and ownership

- Feature modules have explicit APIs rather than cross-feature internal imports.
- UI, state, domain policy, persistence, and transport concerns have identifiable owners.
- Shared folders are cohesive, not dumping grounds.
- Packages do not depend cyclically or reach around abstractions.
- Generated code is not manually edited and has reproducible generation commands.

## State and data flow

- State lifetime matches screen/application lifetime.
- Async work has cancellation, stale-result, duplicate-request, and error paths.
- UI does not silently own long-lived repositories or clients.
- Cache/source-of-truth behavior is explicit.
- Optimistic updates define rollback and conflict behavior.

## Lifecycle and concurrency

- Controllers, subscriptions, observers, ports, and native handles have owners.
- Disposal occurs exactly once and at the correct boundary.
- Isolate/platform-channel messages define serialization and error behavior.
- App lifecycle transitions do not duplicate initialization or lose work.

## Navigation and deep links

- Route arguments and restoration behavior are explicit.
- Authentication redirects avoid loops and stale navigation contexts.
- Deep links validate input and define unsupported-route behavior.

## Dependency governance

- Direct dependencies are actually used and constrained intentionally.
- Overrides, git/path dependencies, abandoned packages, and forked plugins have owners.
- SDK/toolchain pinning is reproducible across local and CI environments.
- Platform-specific workarounds are documented with removal conditions.

## Change safety

- Critical boundaries can be tested without booting the entire app.
- Migrations are incremental and backwards compatible where needed.
- Observability makes failures diagnosable rather than swallowed.
