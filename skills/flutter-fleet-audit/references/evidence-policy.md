# Evidence policy

## Evidence levels

| Level | Meaning | Valid examples |
|---|---|---|
| `static_candidate` | Source/configuration suggests a possible issue, but runtime impact is unproven | expensive widget pattern, missing target image size, broad rebuild boundary |
| `reproduced` | A deterministic scenario or failing check demonstrates the behavior | repeatable test failure, reproducible crash, consistent layout overflow |
| `measured` | Quantitative data demonstrates impact | frame timing, memory peak, startup duration, binary size, benchmark distribution |

Never silently promote a static candidate to measured.

## Confidence

- `high`: direct source or command evidence with a clear causal path.
- `medium`: evidence is real but impact or ownership still needs verification.
- `low`: weak signal, indirect inference, or incomplete environment.

Low-confidence observations normally belong in `questions_or_gaps` unless their
potential severity is critical.

## Severity

- `critical`: realistic compromise, data loss, release blocker, or widespread crash.
- `high`: major user-facing failure, severe performance regression, or high-risk defect.
- `medium`: meaningful reliability, maintainability, performance, or test gap.
- `low`: localized improvement with limited current impact.
- `info`: inventory or context, not a defect.

Severity is impact, not confidence. Keep the two fields independent.

## Minimum evidence for a finding

Every finding must include at least one evidence item. Source evidence requires a
repository-relative path and positive line number. Command evidence requires the
command and exit code. Measurement evidence requires metric, unit, environment,
and sample description.

## Forbidden claims without measurement

Do not claim that code “causes jank,” “leaks memory,” “blocks the UI thread,” or
“improves performance by X%” from source inspection alone. Use conditional wording
and provide a verification experiment.
