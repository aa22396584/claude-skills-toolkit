# Fleet audit workflow

## Project identity

A directory is a Flutter candidate when its `pubspec.yaml` contains `sdk: flutter`
or a top-level Flutter configuration and has Flutter source or platform metadata.
Classify candidates as:

- `app`: runnable application with platform directories or application metadata;
- `package`: reusable Dart/Flutter package;
- `plugin`: package with Flutter plugin platform declarations;
- `module`: add-to-app Flutter module;
- `example`: nested example application;
- `unknown`: insufficient evidence.

Keep monorepo members separate when they have their own `pubspec.yaml`. Preserve a
`parent_project` relationship rather than collapsing them or reporting identical
findings twice.

## Exclusions

Skip dependency, generated, and cache directories such as `.git`, `.dart_tool`,
`build`, `.fvm`, `node_modules`, `Pods`, `DerivedData`, and vendored SDK trees.
Do not skip a repository only because it is old; mark activity separately.

## Batching

Use five projects per batch by default. After each batch:

1. validate all JSON reports;
2. update `run-manifest.json` atomically;
3. summarize new high-confidence findings;
4. record blockers and continue with unaffected projects.

## Resume behavior

On restart, read the manifest and inventory. Reuse a completed audit only when the
project HEAD commit matches the saved commit. If HEAD changed, mark it `stale` and
re-audit affected sections.

## Command evidence

Store a compact command record:

```json
{
  "command": "flutter test --no-pub",
  "cwd": "<redacted-project-path>",
  "exit_code": 1,
  "elapsed_seconds": 18.2,
  "output_file": "commands/flutter-test.txt",
  "truncated": false
}
```

Do not embed megabytes of logs in project JSON. Reference a local output file and
quote only the lines needed to support a finding.
