---
name: flutter-fleet-audit
description: "Orchestrates evidence-first audits across many Flutter repositories. Use when the user asks to scan, inventory, compare, review, or audit all/multiple Flutter apps or repos; asks for a Flutter portfolio health report; wants to spend large model context on cross-repo analysis; or invokes flutter-fleet-audit by name. Discovers projects from pubspec.yaml, gathers deterministic facts, delegates performance/architecture/test/security checks, saves resumable progress, and produces a cross-project priority matrix. Defaults to read-only. Does not trigger for a question about one isolated widget unless the user explicitly requests a full project audit."
---

# Flutter Fleet Audit

Audit a portfolio of Flutter repositories without turning filename matches into
unsupported conclusions. Build an inventory, collect evidence, audit in bounded
batches, and synthesize a portfolio roadmap.

## Non-negotiable rules

1. **Read-only by default.** Do not edit source, lockfiles, generated files,
   signing files, CI configuration, or dependency versions unless the user
   separately asks for implementation.
2. **Never run mutating convenience commands** during an audit. Prohibited by
   default: `dart fix --apply`, `flutter pub upgrade`, `flutter create .`,
   broad format commands, migrations, code generators, and release publishing.
3. **A code pattern is not proof of impact.** Label source-only observations as
   `static_candidate`. Use `reproduced` only when a repeatable scenario exists;
   use `measured` only when trace, benchmark, memory, size, or timing data exists.
4. **Every finding needs evidence.** Include repository-relative file and line,
   command output, test failure, trace marker, or benchmark result. If evidence
   is missing, move the item to `questions_or_gaps`, not `findings`.
5. **Redact secrets and credentials.** Never copy token values, signing secrets,
   keystore passwords, private URLs with embedded credentials, or full user home
   paths into shared reports.
6. **Preserve uncertainty.** State what was not run, what platform was not
   available, and what requires a device or production workload.
7. **Do not compare projects unfairly.** Normalize by project kind, activity,
   supported platforms, and available tests before ranking.

## Audit modes

Choose the narrowest mode that satisfies the request.

| Mode | Work performed | Commands |
|---|---|---|
| `inventory` | Discover projects and collect metadata only | Git and Python read-only commands |
| `standard` | Static facts plus targeted source review and existing checks | `dart analyze` / `flutter test --no-pub` when safe and available |
| `deep` | Standard plus profile traces, build-size analysis, device scenarios, and repeated measurements | Requires suitable SDK, device, and explicit environment availability |

If the user says “all projects” without a mode, use `standard`. Do not block on a
missing device; complete static work and mark measurement gaps.

## Phase 1 — Establish the run

Resolve project roots from the request. When roots are omitted, inspect common
locations such as the current directory, `~/workspace`, `~/repos`, `~/code`,
`~/dev`, and `~/Documents`, then record the roots that actually exist. Avoid an
interactive question when a safe automatic choice is available.

Create an output directory outside source repositories when possible:

```text
.flutter-fleet-audit/
├── inventory.json
├── run-manifest.json
├── projects/<project-id>/
└── portfolio-report.md
```

The manifest must include mode, roots, exclusions, started time, completed
projects, failed projects, skipped projects, and limitations. Update it after
every batch so the run can resume.

## Phase 2 — Discover projects

Use the bundled discovery script:

```bash
python3 <skill-dir>/scripts/discover_flutter_projects.py \
  <root-1> <root-2> \
  --output <output-dir>/inventory.json
```

Read `references/workflow.md` before deciding what counts as an independent
project. Nested example apps, packages, and monorepo members must be represented
without double-counting their parent as an identical workload.

For each project, collect:

- package name, version, project kind, platforms, and SDK constraints;
- current Git branch, sanitized remote, dirty state, and last commit date;
- dependency families, source/test size, assets, and CI presence;
- whether Flutter/Dart commands are available;
- whether generated or vendored code dominates the repository.

## Phase 3 — Collect deterministic facts

Run the facts script for every selected project:

```bash
python3 <skill-dir>/scripts/collect_project_facts.py \
  <project-path> \
  --output <output-dir>/projects/<project-id>/facts.json
```

Treat pattern counts as navigation aids only. Open the cited source around each
candidate before creating a finding. Do not paste huge files into context; read
focused ranges and progressively disclose supporting references.

## Phase 4 — Triage and batch

Group projects by kind and activity:

- actively maintained applications;
- active packages/plugins;
- dormant but shipped applications;
- examples, experiments, forks, generated mirrors, and archived projects.

Audit high-value groups first. A reasonable default score is:

```text
priority = production_weight + recent_activity + user_impact
           + evidence_of_failures + shared_pattern_leverage
```

Do not use repository size alone as a risk score. Process a default batch of five
projects, save the manifest, and continue until the selected inventory is done.

## Phase 5 — Per-project audit

For each application, apply the sibling skills when available:

1. `flutter-performance-audit`
2. `flutter-architecture-audit`
3. `flutter-test-audit`
4. `flutter-security-release-audit`

If sibling skill activation is unavailable, read their `SKILL.md` and references
from the installed skill collection. Each project must produce both
`project-audit.json` and a concise `project-report.md` based on the templates in
`assets/`.

Before accepting a JSON audit, run:

```bash
python3 <skill-dir>/scripts/validate_audit.py \
  <output-dir>/projects/<project-id>/project-audit.json
```

Fix schema or evidence failures before synthesis. Do not lower the validator’s
requirements merely to make an audit pass.

## Phase 6 — Command policy

Use existing project toolchains and pinning when present (`fvm`, mise, asdf,
Melos, workspace scripts). Prefer `--no-pub` to avoid changing dependency state.

Safe candidates, when available:

```bash
flutter --version
dart --version
dart analyze --format machine
flutter test --no-pub
flutter test --coverage --no-pub
```

Do not claim success from truncated output. Record command, working directory,
exit code, elapsed time, and whether output was incomplete. If dependency setup
is missing, report the blocker rather than running an upgrade.

For expensive checks, select representative projects based on product value and
risk. Static-audit every project; deep-profile only where the environment can
produce comparable measurements.

## Phase 7 — Synthesis

After validating all project audits, activate `flutter-portfolio-synthesis` or
run:

```bash
python3 <skill-dir>/scripts/aggregate_audits.py \
  <output-dir> \
  --output <output-dir>/portfolio-report.md
```

The final portfolio report must contain:

- inventory coverage and exclusions;
- project health matrix;
- top findings ranked by severity, confidence, evidence, reach, and effort;
- recurring patterns with affected-project counts;
- reusable package/tooling candidates;
- measurement and test gaps;
- a 30/60/90-day roadmap;
- exact limitations and commands not run.

## Completion criteria

The run is complete only when every selected project is marked `complete`,
`skipped` with a reason, or `blocked` with a reproducible blocker. Never present a
partial portfolio as complete. Report both audited project count and total
selected project count.
