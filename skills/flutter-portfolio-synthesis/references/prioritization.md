# Portfolio prioritization

## Suggested score

Use a transparent score, then sanity-check it rather than treating it as truth:

```text
value = severity_weight × confidence_weight × evidence_weight
        × reach_weight × production_weight
        - effort_weight - migration_risk_weight
```

Suggested relative weights:

| Dimension | Values |
|---|---|
| Severity | critical 8, high 5, medium 3, low 1, info 0 |
| Confidence | high 1.0, medium 0.7, low 0.4 |
| Evidence | measured 1.0, reproduced 0.85, static candidate 0.55 |
| Reach | logarithmic by affected production projects; avoid linear domination |
| Effort | xs 0.5, s 1, m 2, l 4, xl 7 |

Do not let an arbitrary score override a critical release/security blocker.

## Shared package test

Recommend centralization only when:

1. at least three active projects implement substantially the same behavior;
2. semantics and release compatibility are genuinely shared;
3. the API boundary can remain smaller than duplicated implementations;
4. ownership, versioning, migration, and deprecation are defined;
5. centralization does not create a high-blast-radius dependency for trivial code.

Alternatives include a lint rule, code template, CI check, reference implementation,
or documentation rather than a runtime package.

## Roadmap buckets

- 0–30 days: verified critical/high release, security, crash, and data risks.
- 31–60 days: measurement/test foundations and repeated medium/high patterns.
- 61–90 days: package consolidation, architecture migrations, and build/toolchain work.

Every roadmap item needs a success metric and rollback or stop condition.
