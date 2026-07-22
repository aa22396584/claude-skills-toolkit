#!/usr/bin/env python3
"""Aggregate validated project-audit.json files into a Markdown portfolio report."""

from __future__ import annotations

import argparse
import collections
import json
import os
from pathlib import Path
from typing import Any

SEVERITY_SCORE = {"critical": 8, "high": 5, "medium": 3, "low": 1, "info": 0}
CONFIDENCE_SCORE = {"high": 1.0, "medium": 0.7, "low": 0.4}
EVIDENCE_SCORE = {"measured": 1.0, "reproduced": 0.85, "static_candidate": 0.55}


def find_audits(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    return sorted(root.rglob("project-audit.json"))


def load(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def finding_score(finding: dict[str, Any], reach: int) -> float:
    severity = SEVERITY_SCORE.get(finding.get("severity"), 0)
    confidence = CONFIDENCE_SCORE.get(finding.get("confidence"), 0.4)
    evidence = EVIDENCE_SCORE.get(finding.get("evidence_level"), 0.55)
    reach_weight = 1.0 + min(2.0, max(0, reach - 1) * 0.2)
    return severity * confidence * evidence * reach_weight


def escape(value: Any) -> str:
    return str(value if value is not None else "—").replace("|", "\\|").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Audit directory or one project-audit.json")
    parser.add_argument("--output", required=True, help="Markdown report path")
    args = parser.parse_args()

    input_path = Path(os.path.expanduser(args.input))
    audit_paths = find_audits(input_path)
    audits: list[tuple[Path, dict[str, Any]]] = []
    invalid: list[str] = []
    for path in audit_paths:
        data = load(path)
        if data is None or data.get("schema_version") != "1.0":
            invalid.append(str(path))
        else:
            audits.append((path, data))

    pattern_projects: dict[str, set[str]] = collections.defaultdict(set)
    all_findings: list[tuple[str, dict[str, Any]]] = []
    for _, audit in audits:
        project = audit.get("project", {})
        project_id = str(project.get("id") or project.get("name") or "unknown")
        for finding in audit.get("findings", []):
            if not isinstance(finding, dict):
                continue
            all_findings.append((project_id, finding))
            pattern = finding.get("shared_pattern")
            if pattern:
                pattern_projects[str(pattern)].add(project_id)

    ranked = sorted(
        all_findings,
        key=lambda item: finding_score(item[1], len(pattern_projects.get(str(item[1].get("shared_pattern")), {item[0]}))),
        reverse=True,
    )

    lines: list[str] = []
    lines += ["# Flutter portfolio audit", "", "## Coverage", ""]
    lines.append(f"- Valid project audits: **{len(audits)}**")
    lines.append(f"- Invalid/unreadable audits: **{len(invalid)}**")
    lines.append(f"- Total findings: **{len(all_findings)}**")
    lines.append("")

    lines += ["## Project matrix", "", "| Project | Status | Risk | Confidence | Critical | High | Medium | Measured |", "|---|---|---|---|---:|---:|---:|---:|"]
    for _, audit in sorted(audits, key=lambda item: str(item[1].get("project", {}).get("name", "")).lower()):
        project = audit.get("project", {})
        summary = audit.get("summary", {})
        findings = [f for f in audit.get("findings", []) if isinstance(f, dict)]
        counts = collections.Counter(f.get("severity") for f in findings)
        measured = sum(1 for f in findings if f.get("evidence_level") == "measured")
        lines.append(
            "| {name} | {status} | {risk} | {confidence} | {critical} | {high} | {medium} | {measured} |".format(
                name=escape(project.get("name")), status=escape(summary.get("status")),
                risk=escape(summary.get("risk")), confidence=escape(summary.get("confidence")),
                critical=counts.get("critical", 0), high=counts.get("high", 0),
                medium=counts.get("medium", 0), measured=measured,
            )
        )
    lines.append("")

    lines += ["## Highest-value findings", ""]
    if not ranked:
        lines.append("No validated findings were available.")
    for index, (project_id, finding) in enumerate(ranked[:20], 1):
        pattern = finding.get("shared_pattern")
        reach = len(pattern_projects.get(str(pattern), {project_id})) if pattern else 1
        score = finding_score(finding, reach)
        lines.append(f"### {index}. {escape(finding.get('title'))}")
        lines.append("")
        lines.append(
            f"- Project: `{escape(project_id)}`; severity: **{escape(finding.get('severity'))}**; "
            f"confidence: **{escape(finding.get('confidence'))}**; evidence: **{escape(finding.get('evidence_level'))}**"
        )
        lines.append(f"- Portfolio reach: {reach}; ranking score: {score:.2f}")
        lines.append(f"- Impact: {escape(finding.get('impact'))}")
        lines.append(f"- Recommendation: {escape(finding.get('recommendation'))}")
        lines.append("")

    lines += ["## Recurring patterns", "", "| Pattern | Projects | Representative projects |", "|---|---:|---|"]
    recurring = sorted(pattern_projects.items(), key=lambda item: (-len(item[1]), item[0]))
    for pattern, projects in recurring:
        lines.append(f"| `{escape(pattern)}` | {len(projects)} | {escape(', '.join(sorted(projects)[:8]))} |")
    if not recurring:
        lines.append("| — | 0 | No shared patterns recorded |")
    lines.append("")

    lines += ["## Shared package and tooling candidates", ""]
    candidates = [(pattern, projects) for pattern, projects in recurring if len(projects) >= 3]
    if candidates:
        for pattern, projects in candidates:
            lines.append(f"- `{escape(pattern)}` affects {len(projects)} projects. Validate semantic compatibility, ownership, versioning, and migration cost before centralizing.")
    else:
        lines.append("No pattern currently meets the default three-project threshold. Consider lint rules, templates, or documentation before a runtime package.")
    lines.append("")

    lines += ["## Limitations", ""]
    if invalid:
        lines.append("The following audit files were invalid or unreadable:")
        for path in invalid:
            lines.append(f"- `{escape(path)}`")
    else:
        lines.append("This report only includes supplied, schema-version 1.0 audit files. It does not infer health for missing repositories.")
    lines.append("")

    target = Path(os.path.expanduser(args.output))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines), encoding="utf-8")
    print(f"Aggregated {len(audits)} audit(s); wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
