from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "flutter-fleet-audit" / "scripts"


def run_script(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


class ScriptTests(unittest.TestCase):
    def make_project(self, root: Path, name: str = "sample_app") -> Path:
        project = root / name
        (project / "lib").mkdir(parents=True)
        (project / "test").mkdir()
        (project / "assets").mkdir()
        (project / "pubspec.yaml").write_text(
            "name: sample_app\nversion: 1.0.0\ndependencies:\n  flutter:\n    sdk: flutter\n  riverpod: ^2.0.0\ndev_dependencies:\n  flutter_test:\n    sdk: flutter\nflutter:\n  uses-material-design: true\n",
            encoding="utf-8",
        )
        (project / "lib" / "main.dart").write_text(
            "import 'package:flutter/widgets.dart';\nWidget buildIt() => BackdropFilter(filter: ImageFilter.blur(), child: Image.network('https://example.com/a.png'));\n",
            encoding="utf-8",
        )
        (project / "test" / "smoke_test.dart").write_text("void main() {}\n", encoding="utf-8")
        (project / "assets" / "large.png").write_bytes(b"0" * 1024)
        return project

    def test_discovery_and_facts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = self.make_project(root)
            inventory = root / "inventory.json"
            proc = run_script("discover_flutter_projects.py", str(root), "--output", str(inventory))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            data = json.loads(inventory.read_text(encoding="utf-8"))
            self.assertEqual(data["project_count"], 1)
            self.assertEqual(data["projects"][0]["name"], "sample_app")

            facts = root / "facts.json"
            proc = run_script("collect_project_facts.py", str(project), "--output", str(facts))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            data = json.loads(facts.read_text(encoding="utf-8"))
            self.assertEqual(data["source"]["test_files"], 1)
            self.assertGreaterEqual(data["pattern_counts"]["backdrop_filter"], 1)
            self.assertEqual(data["assets"]["image_count"], 1)

    def test_validator(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "project-audit.json"
            path.write_text(json.dumps({
                "schema_version": "1.0",
                "project": {"id": "p", "name": "p", "path": "/tmp/p"},
                "summary": {"risk": "medium", "confidence": "high", "status": "complete"},
                "findings": [{
                    "id": "PERF-001", "category": "performance", "title": "Candidate",
                    "severity": "medium", "confidence": "high", "evidence_level": "static_candidate",
                    "evidence": [{"type": "source", "file": "lib/main.dart", "line": 1, "detail": "evidence"}],
                    "impact": "possible impact", "verification": "measure", "recommendation": "change after proof",
                }],
                "commands": [], "limitations": [],
            }), encoding="utf-8")
            proc = run_script("validate_audit.py", str(path))
            self.assertEqual(proc.returncode, 0, proc.stderr)

            data = json.loads(path.read_text(encoding="utf-8"))
            data["findings"][0]["evidence"] = []
            path.write_text(json.dumps(data), encoding="utf-8")
            proc = run_script("validate_audit.py", str(path))
            self.assertNotEqual(proc.returncode, 0)

    def test_aggregate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            audit = root / "project-audit.json"
            audit.write_text(json.dumps({
                "schema_version": "1.0",
                "project": {"id": "p", "name": "Project P", "path": "/tmp/p"},
                "summary": {"risk": "high", "confidence": "high", "status": "complete"},
                "findings": [{
                    "id": "TEST-001", "category": "tests", "title": "Missing migration test",
                    "severity": "high", "confidence": "high", "evidence_level": "reproduced",
                    "evidence": [{"type": "test", "detail": "migration is not covered"}],
                    "impact": "upgrade risk", "verification": "add fixture", "recommendation": "add migration test",
                    "shared_pattern": "migration-test-gap",
                }],
                "commands": [], "limitations": [],
            }), encoding="utf-8")
            report = root / "portfolio.md"
            proc = run_script("aggregate_audits.py", str(root), "--output", str(report))
            self.assertEqual(proc.returncode, 0, proc.stderr)
            text = report.read_text(encoding="utf-8")
            self.assertIn("Project P", text)
            self.assertIn("Missing migration test", text)


if __name__ == "__main__":
    unittest.main()
