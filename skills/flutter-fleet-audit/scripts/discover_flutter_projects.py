#!/usr/bin/env python3
"""Discover Flutter projects below one or more roots without modifying them."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable

DEFAULT_EXCLUDES = {
    ".git",
    ".dart_tool",
    ".fvm",
    ".idea",
    ".vscode",
    "build",
    "node_modules",
    "Pods",
    "DerivedData",
    "vendor",
    "coverage",
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def scalar(text: str, key: str) -> str | None:
    match = re.search(rf"(?m)^{re.escape(key)}\s*:\s*([^#\n]+)", text)
    if not match:
        return None
    value = match.group(1).strip().strip("'\"")
    return value or None


def looks_like_flutter(pubspec: str) -> bool:
    return bool(
        re.search(r"(?m)^\s+sdk\s*:\s*flutter\s*$", pubspec)
        or re.search(r"(?m)^flutter\s*:\s*(?:#.*)?$", pubspec)
    )


def classify_project(path: Path, pubspec: str) -> str:
    if re.search(r"(?ms)^flutter\s*:\s*.*?plugin\s*:", pubspec):
        return "plugin"
    if (path / ".metadata").exists():
        metadata = read_text(path / ".metadata")
        if "project_type: module" in metadata:
            return "module"
        if "project_type: app" in metadata:
            return "app"
    if any((path / platform).exists() for platform in ("android", "ios", "web", "macos", "windows", "linux")):
        return "example" if path.name == "example" else "app"
    return "package"


def run_git(path: Path, args: list[str]) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(path), *args],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return proc.stdout.strip() if proc.returncode == 0 else None


def sanitize_remote(remote: str | None) -> str | None:
    if not remote:
        return None
    remote = re.sub(r"^(https?://)[^/@]+@", r"\1", remote)
    remote = re.sub(r"([?&](?:token|access_token|auth)\s*=)[^&]+", r"\1REDACTED", remote, flags=re.I)
    return remote


def platforms(path: Path) -> list[str]:
    names = ["android", "ios", "web", "macos", "windows", "linux"]
    return [name for name in names if (path / name).exists()]


def find_pubspecs(roots: Iterable[Path], excludes: set[str], max_depth: int | None) -> Iterable[Path]:
    seen: set[Path] = set()
    for root in roots:
        if not root.exists() or not root.is_dir():
            continue
        root = root.resolve()
        for current, dirs, filenames in os.walk(root):
            current_path = Path(current)
            try:
                depth = len(current_path.relative_to(root).parts)
            except ValueError:
                continue
            dirs[:] = [d for d in dirs if d not in excludes and not d.startswith(".pub-cache")]
            if max_depth is not None and depth >= max_depth:
                dirs[:] = []
            if "pubspec.yaml" in filenames:
                pubspec = current_path / "pubspec.yaml"
                resolved = pubspec.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    yield resolved


def parent_flutter_project(path: Path, all_paths: set[Path]) -> str | None:
    for parent in path.parents:
        if parent in all_paths:
            return str(parent)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roots", nargs="+", help="Directories to search")
    parser.add_argument("--output", required=True, help="Inventory JSON path")
    parser.add_argument("--exclude", action="append", default=[], help="Directory name to exclude (repeatable)")
    parser.add_argument("--max-depth", type=int, default=None, help="Maximum directory depth below each root")
    args = parser.parse_args()

    roots = [Path(os.path.expanduser(value)) for value in args.roots]
    excludes = DEFAULT_EXCLUDES | set(args.exclude)
    candidates: list[tuple[Path, str]] = []
    warnings: list[str] = []

    for root in roots:
        if not root.exists():
            warnings.append(f"root does not exist: {root}")

    for pubspec_path in find_pubspecs(roots, excludes, args.max_depth):
        text = read_text(pubspec_path)
        if looks_like_flutter(text):
            candidates.append((pubspec_path.parent.resolve(), text))

    all_project_paths = {path for path, _ in candidates}
    projects: list[dict[str, Any]] = []
    for path, pubspec in sorted(candidates, key=lambda item: str(item[0]).lower()):
        remote = sanitize_remote(run_git(path, ["remote", "get-url", "origin"]))
        status = run_git(path, ["status", "--porcelain"])
        project = {
            "id": re.sub(r"[^a-zA-Z0-9._-]+", "-", path.name).strip("-") or "flutter-project",
            "name": scalar(pubspec, "name") or path.name,
            "version": scalar(pubspec, "version"),
            "path": str(path),
            "pubspec": str(path / "pubspec.yaml"),
            "kind": classify_project(path, pubspec),
            "platforms": platforms(path),
            "parent_project": parent_flutter_project(path, all_project_paths - {path}),
            "git": {
                "branch": run_git(path, ["branch", "--show-current"]),
                "head": run_git(path, ["rev-parse", "HEAD"]),
                "last_commit_date": run_git(path, ["log", "-1", "--format=%cI"]),
                "remote": remote,
                "dirty": bool(status) if status is not None else None,
            },
        }
        projects.append(project)

    output = Path(os.path.expanduser(args.output))
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": "1.0",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "roots": [str(root.resolve()) if root.exists() else str(root) for root in roots],
        "exclude_names": sorted(excludes),
        "project_count": len(projects),
        "warnings": warnings,
        "projects": projects,
    }
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Discovered {len(projects)} Flutter project(s); wrote {output}")
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
