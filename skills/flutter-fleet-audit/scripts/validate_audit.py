#!/usr/bin/env python3
"""Validate evidence and required fields in a project-audit.json file."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SEVERITIES = {"critical", "high", "medium", "low", "info"}
CONFIDENCE = {"high", "medium", "low"}
EVIDENCE_LEVELS = {"static_candidate", "reproduced", "measured"}
CATEGORIES = {"performance", "architecture", "tests", "security", "release", "dependency"}
REQUIRED_FINDING = {
    "id", "category", "title", "severity", "confidence", "evidence_level",
    "evidence", "impact", "verification", "recommendation",
}


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def validate_evidence(item: Any, prefix: str, errors: list[str]) -> None:
    require(isinstance(item, dict), f"{prefix} must be an object", errors)
    if not isinstance(item, dict):
        return
    kind = item.get("type")
    require(kind in {"source", "command", "measurement", "trace", "test"}, f"{prefix}.type is invalid", errors)
    require(bool(item.get("detail")), f"{prefix}.detail is required", errors)
    if kind == "source":
        require(isinstance(item.get("file"), str) and bool(item.get("file")), f"{prefix}.file is required", errors)
        require(isinstance(item.get("line"), int) and item.get("line", 0) > 0, f"{prefix}.line must be positive", errors)
        if isinstance(item.get("file"), str):
            require(not item["file"].startswith(("/", "~")), f"{prefix}.file must be repository-relative", errors)
    elif kind == "command":
        require(bool(item.get("command")), f"{prefix}.command is required", errors)
        require(isinstance(item.get("exit_code"), int), f"{prefix}.exit_code must be an integer", errors)
    elif kind == "measurement":
        for field in ("metric", "value", "unit", "environment"):
            require(field in item and item[field] not in (None, ""), f"{prefix}.{field} is required", errors)


def validate(data: Any) -> list[str]:
    errors: list[str] = []
    require(isinstance(data, dict), "root must be an object", errors)
    if not isinstance(data, dict):
        return errors
    require(data.get("schema_version") == "1.0", "schema_version must be '1.0'", errors)
    for field in ("project", "summary", "findings", "commands", "limitations"):
        require(field in data, f"missing top-level field: {field}", errors)
    project = data.get("project")
    require(isinstance(project, dict), "project must be an object", errors)
    if isinstance(project, dict):
        for field in ("id", "name", "path"):
            require(bool(project.get(field)), f"project.{field} is required", errors)
    findings = data.get("findings")
    require(isinstance(findings, list), "findings must be an array", errors)
    if isinstance(findings, list):
        ids: set[str] = set()
        for index, finding in enumerate(findings):
            prefix = f"findings[{index}]"
            require(isinstance(finding, dict), f"{prefix} must be an object", errors)
            if not isinstance(finding, dict):
                continue
            missing = REQUIRED_FINDING - finding.keys()
            require(not missing, f"{prefix} missing fields: {', '.join(sorted(missing))}", errors)
            finding_id = finding.get("id")
            require(isinstance(finding_id, str) and bool(finding_id), f"{prefix}.id is required", errors)
            if isinstance(finding_id, str):
                require(finding_id not in ids, f"duplicate finding id: {finding_id}", errors)
                ids.add(finding_id)
            require(finding.get("category") in CATEGORIES, f"{prefix}.category is invalid", errors)
            require(finding.get("severity") in SEVERITIES, f"{prefix}.severity is invalid", errors)
            require(finding.get("confidence") in CONFIDENCE, f"{prefix}.confidence is invalid", errors)
            require(finding.get("evidence_level") in EVIDENCE_LEVELS, f"{prefix}.evidence_level is invalid", errors)
            evidence = finding.get("evidence")
            require(isinstance(evidence, list) and len(evidence) > 0, f"{prefix}.evidence must be non-empty", errors)
            if isinstance(evidence, list):
                for evidence_index, item in enumerate(evidence):
                    validate_evidence(item, f"{prefix}.evidence[{evidence_index}]", errors)
            if finding.get("evidence_level") == "measured":
                require(any(isinstance(item, dict) and item.get("type") == "measurement" for item in evidence or []), f"{prefix} is measured but has no measurement evidence", errors)
    require(isinstance(data.get("commands"), list), "commands must be an array", errors)
    limitations = data.get("limitations")
    require(isinstance(limitations, list) and all(isinstance(item, str) for item in limitations), "limitations must be an array of strings", errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit", help="project-audit.json path")
    args = parser.parse_args()
    path = Path(args.audit)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"invalid JSON: {exc}", file=sys.stderr)
        return 2
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1
    print(f"Validation passed: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
