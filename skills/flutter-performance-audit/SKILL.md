---
name: flutter-performance-audit
description: "Performs an evidence-first performance audit of a Flutter application or package. Use when the user asks to profile, optimize, diagnose jank, slow startup, high memory, large images, excessive rebuilds/layout, raster cost, Platform Views, app size, or a full Flutter performance review. Separates static candidates from reproduced and measured issues and produces benchmark or trace plans. Does not automatically modify code or call every expensive widget a bug."
---

# Flutter Performance Audit

Find performance work that can be demonstrated, not merely imagined.

## Rules

1. Audit in profile/release conditions when measuring. Debug timing is diagnostic,
   not a release performance result.
2. Separate UI/Dart, raster/GPU, platform, I/O, memory, startup, and build-size
   hypotheses.
3. A matching widget name is only a navigation signal. Inspect constraints,
   subtree size, animation frequency, image dimensions, and runtime path.
4. Record device, OS, Flutter revision, renderer/backend, refresh rate, scenario,
   warm-up, run count, and distribution for measurements.
5. Do not edit code until a baseline and verification method exist.

## Workflow

### 1. Establish representative scenarios

Identify at most five user journeys: cold start, warm start, longest scroll,
transition/animation, image-heavy screen, map/WebView/camera screen, or known
complaint. Tie every measurement to one scenario.

### 2. Static candidate scan

Read `references/checklist.md`. Review facts produced by
`collect_project_facts.py`, then open every cited source location. Inspect:

- repaint and compositing boundaries;
- intrinsic/double layout and unbounded shrink-wrapped lists;
- image decode dimensions, cache churn, and animated formats;
- synchronous parsing, mapping, crypto, compression, and database work;
- rebuild ownership and broad state subscriptions;
- Platform View overlap, clipping, opacity, and transforms;
- startup initialization and plugin registration;
- asset and binary size contributors.

### 3. Baseline

Use existing benchmark/integration harnesses first. For frame measurements, capture
at least enough frames to report count, P50, P90, P99, and missed-frame rate.
Avoid averages alone. Repeat comparable runs and preserve raw output.

### 4. Root-cause isolation

Change one variable per experiment. Examples: image decode target, blur disabled,
state subscription narrowed, background work moved, Platform View overlay removed.
A/B results need the same device, build mode, scenario, and sample method.

### 5. Report

For each item include category, evidence level, source/trace evidence, affected
scenario, expected mechanism, baseline, verification experiment, regression risk,
and confidence. If no profile environment exists, provide a measurement plan and
keep findings at `static_candidate`.
