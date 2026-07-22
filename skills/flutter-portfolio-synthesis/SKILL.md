---
name: flutter-portfolio-synthesis
description: "Synthesizes validated audits from multiple Flutter projects into an objective portfolio report. Use when the user wants a cross-project matrix, recurring-pattern analysis, shared package candidates, team-wide standards, investment prioritization, or a 30/60/90-day Flutter improvement roadmap. Requires evidence-backed project audits and does not invent findings for missing projects."
---

# Flutter Portfolio Synthesis

Turn project-level evidence into portfolio decisions without erasing differences
between products, packages, platforms, and lifecycle stages.

## Preconditions

Accept only validated `project-audit.json` inputs. Record missing, stale, blocked,
and skipped projects. Do not infer their health from repository names or size.

## Workflow

1. Normalize severity, confidence, evidence level, project kind, activity, and effort.
2. Deduplicate findings only when they share the same causal pattern, not merely the
   same keyword.
3. Read `references/prioritization.md` and rank individual and shared opportunities.
4. Identify reusable-package candidates, but also document reasons to keep behavior
   local: differing product semantics, release cadence, platform constraints, or ownership.
5. Produce an executive report and a machine-readable pattern summary.

## Required output

- coverage and comparability statement;
- per-project matrix;
- top portfolio findings with representative evidence;
- recurring patterns and affected-project counts;
- candidates for shared packages, lint rules, templates, CI jobs, and test harnesses;
- measurement foundation gaps;
- 30/60/90-day roadmap with owners/effort when available;
- explicit limitations.

Never rank low-confidence static candidates above measured high-impact issues merely
because they occur in more repositories.
