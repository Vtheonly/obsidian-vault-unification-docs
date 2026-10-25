"""CLI end-to-end tests: help, exit codes, output files, safety rejections.

Every invocation is a real subprocess (python -m vault_unification) so the
tested surface is exactly what an operator sees. The subprocess gets
``src/`` on its PYTHONPATH so the tests work from a fresh clone without
installing the package (operators may equivalently ``pip install -e .``).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def cli_env() -> dict:
    env = dict(os.environ)
    src = str(REPO_ROOT / "src")
    env["PYTHONPATH"] = src + os.pathsep + env.get("PYTHONPATH", "")
    return env


def run_cli(*args: str, cwd: Path | None = None, timeout: int = 300) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "vault_unification", *args],
        cwd=cwd or REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=cli_env(),
    )


@pytest.mark.parametrize(
    "command",
    [
        "selftest",
        "check-paths",
        "inventory",
        "verify-manifest",
        "structure",
        "check-links",
        "search",
        "term-stats",
        "stats",
        "validate-registry",
        "run-tests",
        "capabilities",
    ],
)
def test_help_works(command):
    proc = run_cli(command, "--help")
    assert proc.returncode == 0, proc.stderr
    assert "usage:" in proc.stdout


def test_toplevel_help_and_version():
    proc = run_cli("--help")
    assert proc.returncode == 0
    assert "vu" in proc.stdout
    proc = run_cli("--version")
    assert proc.returncode == 0
    assert "vault_unification" in proc.stdout


def test_no_command_prints_help_and_exits_2():
    proc = run_cli()
    assert proc.returncode == 2
    assert "usage:" in proc.stdout


class TestSelftestCLI:
    def test_selftest_passes(self):
        proc = run_cli("selftest")
        assert proc.returncode == 0, proc.stdout + proc.stderr
        payload = json.loads(proc.stdout)
        assert payload["ok"] is True


class TestCheckPathsCLI:
    def test_valid_roots(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        out = tmp_path / "out"
        proc = run_cli("check-paths", "--source", str(src), "--output", str(out))
        assert proc.returncode == 0
        assert json.loads(proc.stdout)["ok"] is True

    def test_overlap_rejected(self, tmp_path):
        src = tmp_path / "src"
        (src / "inner").mkdir(parents=True)
        proc = run_cli("check-paths", "--source", str(src), "--output", str(src / "inner"))
        assert proc.returncode == 1
        payload = json.loads(proc.stdout)
        assert payload["ok"] is False


class TestInventoryCLI:
    def test_inventory_writes_manifest_and_report(self, fixture_vault, tmp_path):
        manifest = tmp_path / "inv" / "manifest.jsonl"
        report = tmp_path / "inv" / "summary.json"
        proc = run_cli(
            "inventory",
            "--root", str(fixture_vault["root"]),
            "--manifest", str(manifest),
            "--report", str(report),
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        records = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines()]
        assert len(records) == 10
        data = json.loads(report.read_text(encoding="utf-8"))
        assert data["total_files"] == 10
        assert data["report_meta"]["command"] == "inventory"

    def test_manifest_inside_source_is_refused(self, fixture_vault):
        sneaky = fixture_vault["root"] / "manifest.jsonl"
        proc = run_cli(
            "inventory",
            "--root", str(fixture_vault["root"]),
            "--manifest", str(sneaky),
        )
        assert proc.returncode == 1
        assert "protected" in proc.stderr

    def test_missing_root_fails(self, tmp_path):
        proc = run_cli(
            "inventory",
            "--root", str(tmp_path / "ghost"),
            "--manifest", str(tmp_path / "m.jsonl"),
        )
        assert proc.returncode == 1
        assert "error" in proc.stderr

    def test_verify_manifest_detects_mutation(self, fixture_vault, tmp_path):
        manifest = tmp_path / "m.jsonl"
        proc = run_cli(
            "inventory", "--root", str(fixture_vault["root"]), "--manifest", str(manifest)
        )
        assert proc.returncode == 0
        fixture_vault["note_b"].write_text("# MUTATED\n", encoding="utf-8")
        proc = run_cli(
            "verify-manifest",
            "--root", str(fixture_vault["root"]),
            "--manifest", str(manifest),
        )
        assert proc.returncode == 1
        payload = json.loads(proc.stdout)
        assert payload["diff_counts"]["changed"] == 1
        assert payload["changed"] == ["note-b.md"]


class TestStructureCLI:
    def test_structure_reports_summary(self, fixture_vault, tmp_path):
        report = tmp_path / "s.json"
        proc = run_cli(
            "structure", "--file", str(fixture_vault["note_a"]), "--report", str(report)
        )
        assert proc.returncode == 0, proc.stdout
        payload = json.loads(proc.stdout)
        assert payload["headings"] >= 3
        data = json.loads(report.read_text(encoding="utf-8"))
        assert data["result"]["frontmatter"]["title"] == "Note A"

    def test_structure_malformed_file_nonzero(self, fixture_vault):
        proc = run_cli("structure", "--file", str(fixture_vault["broken_fence"]))
        assert proc.returncode == 1
        assert any("unclosed" in e for e in json.loads(proc.stdout)["errors"])

    def test_structure_missing_file(self, tmp_path):
        proc = run_cli("structure", "--file", str(tmp_path / "ghost.md"))
        assert proc.returncode == 1


class TestCheckLinksCLI:
    def test_problems_exit_nonzero(self, fixture_vault, tmp_path):
        report = tmp_path / "links.json"
        proc = run_cli(
            "check-links", "--root", str(fixture_vault["root"]), "--report", str(report)
        )
        assert proc.returncode == 1
        payload = json.loads(proc.stdout)
        assert payload["problem_counts"]["broken"] >= 1
        assert payload["problem_counts"]["ambiguous"] == 1
        data = json.loads(report.read_text(encoding="utf-8"))
        assert data["result"]["markdown_files_checked"] == 8

    def test_clean_vault_exits_zero(self, tmp_path):
        clean = tmp_path / "clean"
        clean.mkdir()
        (clean / "a.md").write_text("# A\n\n[[b]]\n", encoding="utf-8")
        (clean / "b.md").write_text("# B\n", encoding="utf-8")
        proc = run_cli("check-links", "--root", str(clean))
        assert proc.returncode == 0, proc.stdout


class TestSearchCLI:
    def test_search_json_output(self, fixture_vault):
        proc = run_cli(
            "search", "--root", str(fixture_vault["root"]),
            "--term", "missing-note", "--mode", "exact", "--json",
        )
        assert proc.returncode == 0
        payload = json.loads(proc.stdout)
        assert payload["match_count"] == 1
        assert payload["matches"][0]["file"] == "sub/note-c.md"

    def test_search_empty_term_rejected(self, fixture_vault):
        proc = run_cli("search", "--root", str(fixture_vault["root"]), "--term", "")
        assert proc.returncode == 1
        assert "error" in proc.stderr

    def test_term_stats(self, fixture_vault, tmp_path):
        terms = tmp_path / "terms.txt"
        terms.write_text("note\nCNN|convnet\n", encoding="utf-8")
        proc = run_cli(
            "term-stats", "--root", str(fixture_vault["root"]),
            "--terms-file", str(terms),
        )
        assert proc.returncode == 0, proc.stdout
        payload = json.loads(proc.stdout)
        assert payload["terms"]["note"] >= 1

    def test_term_stats_missing_terms_file(self, fixture_vault, tmp_path):
        proc = run_cli(
            "term-stats", "--root", str(fixture_vault["root"]),
            "--terms-file", str(tmp_path / "ghost.txt"),
        )
        assert proc.returncode == 1


class TestStatsCLI:
    def test_stats_on_fixture_vault(self, fixture_vault, tmp_path):
        report = tmp_path / "stats.json"
        per_file = tmp_path / "stats.jsonl"
        proc = run_cli(
            "stats",
            "--root", str(fixture_vault["root"]),
            "--report", str(report),
            "--per-file", str(per_file),
        )
        # fixture has genuine parse errors (unclosed fence, bad frontmatter)
        # -> actionable failure, exit 1, with full reports still written
        assert proc.returncode == 1, proc.stdout + proc.stderr
        data = json.loads(report.read_text(encoding="utf-8"))
        totals = data["totals"]
        assert totals["files_discovered"] == 10  # 8 md + png + pdf
        assert totals["files_skipped_nontext"] == 2
        assert totals["text_files_analyzed"] == 6
        assert totals["text_files_with_errors"] == 2
        assert totals["words_total"] > 0
        assert "chars // 4" in data["methods"]["tokens_estimate"]
        error_paths = {u["relpath"] for u in data["unreadable_files"]}
        assert "broken-fence.md" in error_paths
        assert "malformed-frontmatter.md" in error_paths
        # per-file JSONL: one record per text-extension file (errors included)
        lines = [l for l in per_file.read_text(encoding="utf-8").splitlines() if l]
        assert len(lines) == 8
        assert all(json.loads(l)["path"] for l in lines)

    def test_stats_clean_vault_exits_zero(self, tmp_path):
        vault = tmp_path / "clean"
        vault.mkdir()
        (vault / "ok.md").write_text("# Fine\n\nAll good.\n", encoding="utf-8")
        proc = run_cli("stats", "--root", str(vault))
        assert proc.returncode == 0, proc.stdout + proc.stderr
        payload = json.loads(proc.stdout)
        assert payload["files_with_errors"] == 0

    def test_stats_binary_markdown_file_exits_nonzero(self, tmp_path):
        vault = tmp_path / "v"
        vault.mkdir()
        (vault / "ok.md").write_text("# Fine\n", encoding="utf-8")
        (vault / "bad.md").write_bytes(b"\x00\x01\x02not text")
        proc = run_cli("stats", "--root", str(vault))
        assert proc.returncode == 1
        payload = json.loads(proc.stdout)
        assert payload["files_with_errors"] == 1

    def test_stats_missing_root_exits_nonzero(self, tmp_path):
        proc = run_cli("stats", "--root", str(tmp_path / "missing"))
        assert proc.returncode == 1

    def test_stats_report_refuses_write_inside_source(self, fixture_vault, tmp_path):
        inside = fixture_vault["root"] / "stats-report.json"
        proc = run_cli(
            "stats", "--root", str(fixture_vault["root"]), "--report", str(inside)
        )
        assert proc.returncode == 1
        assert not inside.exists()


class TestValidateRegistryCLI:
    def test_repo_task_queue_valid(self, tmp_path):
        report = tmp_path / "v.json"
        proc = run_cli(
            "validate-registry",
            "--tasks", str(REPO_ROOT / "state" / "task-queue.jsonl"),
            "--report", str(report),
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        data = json.loads(report.read_text(encoding="utf-8"))
        assert data["valid"] is True

    def test_invalid_queue_nonzero(self, tmp_path):
        bad = tmp_path / "bad.jsonl"
        bad.write_text('{"task_id": "X-001", "title": "t", "status": "nope"}\n', encoding="utf-8")
        proc = run_cli(
            "validate-registry",
            "--tasks", str(bad),
            "--tasks-schema", str(REPO_ROOT / "schemas" / "task.schema.json"),
        )
        assert proc.returncode == 1
        payload = json.loads(proc.stdout)
        assert payload["problems_total"] >= 1

    def test_no_targets_is_usage_error(self):
        proc = run_cli("validate-registry")
        assert proc.returncode == 1


class TestRunTestsCLI:
    def test_run_tests_on_selftest_suite(self, tmp_path):
        json_report = tmp_path / "pytest.json"
        proc = run_cli(
            "run-tests",
            "--tests-dir", "tests/test_selftest.py",
            "--json-report", str(json_report),
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        data = json.loads(json_report.read_text(encoding="utf-8"))
        assert data["summary"]["total"] == 4
        assert data["summary"]["passed"] == 4

    def test_run_tests_on_failing_suite(self, tmp_path):
        bad_dir = tmp_path / "badtests"
        bad_dir.mkdir()
        (bad_dir / "conftest.py").write_text("", encoding="utf-8")
        (bad_dir / "test_bad.py").write_text(
            "def test_fail():\n    assert False\n", encoding="utf-8"
        )
        json_report = tmp_path / "pytest.json"
        proc = run_cli(
            "run-tests",
            "--tests-dir", str(bad_dir),
            "--json-report", str(json_report),
        )
        assert proc.returncode == 1
        data = json.loads(json_report.read_text(encoding="utf-8"))
        assert data["summary"]["failed"] >= 1


class TestCapabilitiesCLI:
    def test_declared_inventory(self, tmp_path):
        report = tmp_path / "caps.json"
        proc = run_cli("capabilities", "--report", str(report))
        assert proc.returncode == 0, proc.stdout + proc.stderr
        data = json.loads(report.read_text(encoding="utf-8"))
        ids = {c["id"] for c in data["capabilities"]}
        assert "CAP-002" in ids

    # NOTE: the CLI --verify mode is intentionally NOT tested here.
    # verify_capabilities() runs this very test file (CAP-008/009/010
    # reference it), so a CLI --verify test inside test_cli.py would recurse
    # (verify -> pytest test_cli.py -> CLI --verify -> ...). The verification
    # logic is covered in tests/test_capabilities.py at function level using
    # bounded subsets; the CLI --verify wiring itself is exercised by the
    # session evidence run recorded in reports/framework/.
