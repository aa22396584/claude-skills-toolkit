---
name: flutter-security-release-audit
description: "Performs a source-backed security and release-readiness audit for Flutter apps. Use when reviewing secrets, permissions, local storage, authentication tokens, TLS/network policy, WebView, deep links, platform channels, logging/privacy, Android/iOS configuration, signing, obfuscation, dependency provenance, CI release controls, or store submission readiness. Does not expose secret values and does not label theoretical patterns as exploitable without a concrete path."
---

# Flutter Security and Release Audit

Find concrete security and release risks while avoiding scanner-style alarmism.

## Safety

- Never print secret values. Report variable/file names and redacted fingerprints only.
- Do not upload source, keys, configs, or private endpoints to third-party scanners.
- Do not alter signing, entitlements, permissions, or release configuration during audit.
- A dependency CVE or suspicious API is not automatically exploitable; establish reachability,
  version, platform, and threat path.

## Workflow

1. Map data sensitivity, authentication/session flow, storage, network, WebView,
   deep-link, platform-channel, logging/analytics, and release pipeline boundaries.
2. Review `references/checklist.md` and collect exact source/config evidence.
3. Inspect Android and iOS configurations separately; do not assume parity.
4. Check dependency provenance, overrides, forks, lockfiles, and update ownership.
5. Review release reproducibility, signing isolation, environment selection,
   symbol/obfuscation handling, and rollback controls.
6. Rank by realistic attacker/user path and business impact.

## Required output

- threat-surface map;
- verified findings and unverified questions separated;
- affected platform/build variant;
- evidence with secrets redacted;
- exploit/failure prerequisites;
- recommendation, test, owner, and release urgency;
- store/release blockers distinct from hardening opportunities.
