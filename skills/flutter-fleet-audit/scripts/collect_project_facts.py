#!/usr/bin/env python3
"""Collect deterministic, read-only facts from a Flutter project."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

SKIP_DIRS = {
    ".git", ".dart_tool", ".fvm", ".idea", ".vscode", "build", "node_modules",
    "Pods", "DerivedData", "coverage", "vendor", "generated", ".symlinks",
}

PATTERNS: dict[str, str] = {
    "backdrop_filter": r"\bBackdropFilter\s*\(",
    "image_blur": r"\bImageFilter\.blur\s*\(",
    "shader_mask": r"\bShaderMask\s*\(",
    "opacity_widget": r"\bOpacity\s*\(",
    "intrinsic_layout": r"\bIntrinsic(?:Height|Width)\s*\(",
    "shrink_wrap_true": r"\bshrinkWrap\s*:\s*true\b",
    "save_layer_clip": r"Clip\.antiAliasWithSaveLayer",
    "repaint_boundary": r"\bRepaintBoundary\s*\(",
    "custom_painter": r"\bCustomPainter\b",
    "platform_view": r"\b(?:AndroidView|UiKitView|PlatformViewLink|WebViewWidget|GoogleMap)\s*\(",
    "network_image": r"\bImage\.network\s*\(",
    "decode_target": r"\bcache(?:Width|Height)\s*:",
    "isolate_work": r"\b(?:Isolate\.run|compute)\s*\(",
    "json_decode": r"\bjsonDecode\s*\(",
    "set_state": r"\bsetState\s*\(",
    "riverpod_watch": r"\bref\.watch\s*\(",
    "bloc_builder": r"\bBlocBuilder\s*<",
    "stream_builder": r"\bStreamBuilder\s*<",
    "future_builder": r"\bFutureBuilder\s*<",
    "unrestricted_webview_js": r"JavaScriptMode\.unrestricted",
    "cleartext_url": r"[\"']http://[^\"']+",
    "method_channel": r"\bMethodChannel\s*\(",
    "todo_fixme": r"\b(?:TODO|FIXME)\b",
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".heic", ".avif"}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def parse_pubspec_sections(text: str, wanted: set[str]) -> dict[str, list[str]]:
    result = {key: [] for key in wanted}
    current: str | None = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        top = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(?:#.*)?$", raw)
        if top:
            current = top.group(1) if top.group(1) in wanted else None
            continue
        if current:
            dep = re.match(r"^\s{2}([A-Za-z0-9_-]+)\s*:", raw)
            if dep:
                result[current].append(dep.group(1))
    return result


def iter_files(root: Path, suffixes: set[str] | None = None) -> Iterable[Path]:
    for current, dirs, filenames in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        current_path = Path(current)
        for filename in filenames:
            path = current_path / filename
            if suffixes is None or path.suffix.lower() in suffixes:
                yield path


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def git_value(root: Path, args: list[str]) -> str | None:
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *args], text=True,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            timeout=5, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return proc.stdout.strip() if proc.returncode == 0 else None


def scan_patterns(root: Path, dart_files: list[Path], max_matches: int) -> tuple[dict[str, int], dict[str, list[dict[str, Any]]]]:
    counts: Counter[str] = Counter()
    matches: dict[str, list[dict[str, Any]]] = {name: [] for name in PATTERNS}
    compiled = {name: re.compile(pattern) for name, pattern in PATTERNS.items()}
    for path in dart_files:
        text = read_text(path)
        for line_no, line in enumerate(text.splitlines(), 1):
            for name, regex in compiled.items():
                if regex.search(line):
                    counts[name] += 1
                    if len(matches[name]) < max_matches:
                        matches[name].append({
                            "file": relative(path, root),
                            "line": line_no,
                            "excerpt": line.strip()[:240],
                        })
    return dict(sorted(counts.items())), {k: v for k, v in matches.items() if v}


def count_lines(paths: list[Path]) -> int:
    total = 0
    for path in paths:
        try:
            with path.open("r", encoding="utf-8", errors="replace") as handle:
                total += sum(1 for _ in handle)
        except OSError:
            pass
    return total


def find_ci(root: Path) -> list[str]:
    candidates = [
        ".github/workflows", ".gitlab-ci.yml", "bitrise.yml", "codemagic.yaml",
        "codemagic.yml", "Jenkinsfile", "azure-pipelines.yml", "melos.yaml",
    ]
    return [item for item in candidates if (root / item).exists()]


def project_kind(root: Path, pubspec: str) -> str:
    if re.search(r"(?ms)^flutter\s*:\s*.*?plugin\s*:", pubspec):
        return "plugin"
    metadata = read_text(root / ".metadata")
    match = re.search(r"project_type:\s*(\w+)", metadata)
    if match:
        return match.group(1)
    if any((root / p).exists() for p in ("android", "ios", "web", "macos", "windows", "linux")):
        return "app"
    return "package"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", help="Flutter project directory")
    parser.add_argument("--output", required=True, help="Facts JSON path")
    parser.add_argument("--max-matches", type=int, default=20, help="Maximum source locations per pattern")
    parser.add_argument("--largest-files", type=int, default=15, help="Number of largest Dart/assets to record")
    args = parser.parse_args()

    root = Path(os.path.expanduser(args.project)).resolve()
    pubspec_path = root / "pubspec.yaml"
    if not pubspec_path.exists():
        parser.error(f"pubspec.yaml not found under {root}")
    pubspec = read_text(pubspec_path)
    if not (re.search(r"(?m)^\s+sdk\s*:\s*flutter\s*$", pubspec) or re.search(r"(?m)^flutter\s*:", pubspec)):
        parser.error(f"{root} does not appear to be a Flutter project")

    dart_files = list(iter_files(root, {".dart"}))
    lib_files = [p for p in dart_files if p.is_relative_to(root / "lib")]
    test_files = [p for p in dart_files if p.is_relative_to(root / "test") or p.is_relative_to(root / "integration_test")]
    generated_files = [p for p in dart_files if p.name.endswith((".g.dart", ".freezed.dart", ".gr.dart", ".mocks.dart"))]
    pattern_counts, pattern_matches = scan_patterns(root, dart_files, max(1, args.max_matches))

    sizes = []
    for path in dart_files:
        try:
            sizes.append((path.stat().st_size, relative(path, root)))
        except OSError:
            pass
    sizes.sort(reverse=True)

    assets = []
    for path in iter_files(root, IMAGE_EXTENSIONS):
        try:
            assets.append((path.stat().st_size, relative(path, root)))
        except OSError:
            pass
    assets.sort(reverse=True)

    sections = parse_pubspec_sections(pubspec, {"dependencies", "dev_dependencies", "dependency_overrides"})
    platforms = [name for name in ("android", "ios", "web", "macos", "windows", "linux") if (root / name).exists()]

    output = {
        "schema_version": "1.0",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "project": {
            "name": re.search(r"(?m)^name\s*:\s*([^#\n]+)", pubspec).group(1).strip() if re.search(r"(?m)^name\s*:\s*([^#\n]+)", pubspec) else root.name,
            "path": str(root),
            "kind": project_kind(root, pubspec),
            "platforms": platforms,
            "git_head": git_value(root, ["rev-parse", "HEAD"]),
            "git_branch": git_value(root, ["branch", "--show-current"]),
            "git_last_commit_date": git_value(root, ["log", "-1", "--format=%cI"]),
            "git_dirty": bool(git_value(root, ["status", "--porcelain"])),
        },
        "dependencies": sections,
        "source": {
            "dart_files": len(dart_files),
            "lib_files": len(lib_files),
            "test_files": len(test_files),
            "generated_files": len(generated_files),
            "dart_lines": count_lines(dart_files),
            "lib_lines": count_lines(lib_files),
            "test_lines": count_lines(test_files),
            "largest_dart_files": [
                {"file": name, "bytes": size} for size, name in sizes[: max(1, args.largest_files)]
            ],
        },
        "assets": {
            "image_count": len(assets),
            "image_bytes": sum(size for size, _ in assets),
            "largest_images": [
                {"file": name, "bytes": size} for size, name in assets[: max(1, args.largest_files)]
            ],
        },
        "tooling": {
            "ci_or_workspace_files": find_ci(root),
            "analysis_options": (root / "analysis_options.yaml").exists(),
            "pubspec_lock": (root / "pubspec.lock").exists(),
            "fvm": (root / ".fvm").exists() or (root / ".fvmrc").exists(),
        },
        "pattern_counts": pattern_counts,
        "pattern_matches": pattern_matches,
        "interpretation_warning": "Pattern matches are navigation evidence, not proof of runtime impact or vulnerability.",
    }

    target = Path(os.path.expanduser(args.output))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Collected facts for {root.name}; wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
