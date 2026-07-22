# Output schema

`project-audit.json` uses schema version `1.0`.

## Required top-level fields

- `schema_version`: exactly `"1.0"`
- `project`: object with `id`, `name`, and `path`
- `summary`: object with `risk`, `confidence`, and `status`
- `findings`: array
- `commands`: array
- `limitations`: array of strings

## Finding fields

Required:

- `id`: stable within the project, such as `PERF-001`
- `category`: `performance`, `architecture`, `tests`, `security`, `release`, or `dependency`
- `title`
- `severity`: `critical`, `high`, `medium`, `low`, or `info`
- `confidence`: `high`, `medium`, or `low`
- `evidence_level`: `static_candidate`, `reproduced`, or `measured`
- `evidence`: non-empty array
- `impact`
- `verification`
- `recommendation`

Optional:

- `shared_pattern`: normalized cross-project key
- `effort`: `xs`, `s`, `m`, `l`, or `xl`
- `owners`: likely owning modules or teams
- `references`: related local docs/issues

## Evidence item

A source item:

```json
{
  "type": "source",
  "file": "lib/path/file.dart",
  "line": 42,
  "detail": "Focused description of what is present"
}
```

A command item:

```json
{
  "type": "command",
  "command": "flutter test --no-pub",
  "exit_code": 1,
  "detail": "Two tests fail in the database migration suite"
}
```

A measurement item:

```json
{
  "type": "measurement",
  "metric": "raster_frame_p99",
  "value": 24.8,
  "unit": "ms",
  "environment": "Pixel 7, profile mode, 120 Hz disabled",
  "detail": "300-frame scroll scenario, three runs"
}
```
