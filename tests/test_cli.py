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
        "kureg-init",
        "kureg-load",
        "kureg-query",
        "kureg-validate",
        "audit-output",
        "extract-kus",
        "ku-fidelity",
        "omission-pilot",
        "overlap-candidates",
        "kureg-apply-overlap",
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


def test_module_cli_execution_is_not_a_silent_noop():
    """Regression (finding F-0020): ``python -m vault_unification.cli`` used
    to import the module without a ``__main__`` guard and exit 0 with no
    output, silently doing nothing. It must behave exactly like the
    ``python -m vault_unification`` / ``vu`` entry points."""
    env = cli_env()
    # happy path: --version must actually execute and print
    proc = subprocess.run(
        [sys.executable, "-m", "vault_unification.cli", "--version"],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=60, env=env,
    )
    assert proc.returncode == 0, proc.stderr
    assert "vault_unification" in proc.stdout

    # failure path: a missing candidates file must exit nonzero with an
    # error, never exit 0 silently
    proc = subprocess.run(
        [sys.executable, "-m", "vault_unification.cli", "discovery-validate",
         "--candidates", str(REPO_ROOT / "does-not-exist.jsonl")],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=60, env=env,
    )
    assert proc.returncode == 1
    assert "error:" in proc.stderr


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


class TestKuRegistryCLI:
    VALID_KU = {
        "knowledge_unit_id": "KU-0001",
        "source_id": "SRC-1",
        "source_path": "vault/note.md",
        "source_file_hash": "0" * 64,
        "line_start": 1,
        "line_end": 2,
        "excerpt": "synthetic registry test record",
        "unit_type": "claim",
        "disposition": "Preserved",
        "verification_status": {},
    }

    def _write_batch(self, tmp_path, records):
        path = tmp_path / "batch.jsonl"
        with open(path, "w", encoding="utf-8") as handle:
            for rec in records:
                handle.write(json.dumps(rec) + "\n")
        return path

    def test_init_load_query_validate_end_to_end(self, tmp_path):
        db = tmp_path / "reg" / "registry.sqlite"
        report = tmp_path / "reg" / "report.json"
        proc = run_cli(
            "kureg-init", "--db", str(db),
            "--protected-root", str(tmp_path / "sources"),
            "--report", str(report),
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert json.loads(report.read_text(encoding="utf-8"))["report_meta"]["command"] == "kureg-init"

        batch = self._write_batch(tmp_path, [self.VALID_KU])
        proc = run_cli(
            "kureg-load", "--db", str(db), "--kus", str(batch),
            "--protected-root", str(tmp_path / "sources"),
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert json.loads(proc.stdout)["inserted"] == 1

        proc = run_cli(
            "kureg-query", "--db", str(db), "--disposition", "Preserved",
            "--format", "jsonl",
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        lines = [line for line in proc.stdout.splitlines() if line]
        assert len(lines) == 1
        assert json.loads(lines[0])["knowledge_unit_id"] == "KU-0001"

        proc = run_cli("kureg-validate", "--db", str(db))
        assert proc.returncode == 0, proc.stdout + proc.stderr
        payload = json.loads(proc.stdout)
        assert payload["valid"] is True
        assert payload["counts"]["total_kus"] == 1

    def test_init_refuses_db_inside_protected_root(self, tmp_path):
        sources = tmp_path / "sources"
        (sources / "vault").mkdir(parents=True)
        sneaky = sources / "vault" / "registry.sqlite"
        proc = run_cli(
            "kureg-init", "--db", str(sneaky),
            "--protected-root", str(sources),
        )
        assert proc.returncode == 1
        assert "protected" in proc.stderr

    def test_init_twice_rejected(self, tmp_path):
        db = tmp_path / "registry.sqlite"
        assert run_cli("kureg-init", "--db", str(db)).returncode == 0
        proc = run_cli("kureg-init", "--db", str(db))
        assert proc.returncode == 1
        assert "--force" in proc.stderr

    def test_init_force_recreates(self, tmp_path):
        db = tmp_path / "registry.sqlite"
        assert run_cli("kureg-init", "--db", str(db)).returncode == 0
        proc = run_cli("kureg-init", "--db", str(db), "--force")
        assert proc.returncode == 0, proc.stdout + proc.stderr

    def test_load_invalid_batch_nonzero(self, tmp_path):
        db = tmp_path / "registry.sqlite"
        assert run_cli("kureg-init", "--db", str(db)).returncode == 0
        batch = self._write_batch(tmp_path, [dict(self.VALID_KU, disposition="Deleted")])
        proc = run_cli("kureg-load", "--db", str(db), "--kus", str(batch))
        assert proc.returncode == 1
        payload = json.loads(proc.stdout)
        assert payload["valid"] is False
        assert payload["errors_total"] >= 1

    def test_load_missing_file_nonzero(self, tmp_path):
        db = tmp_path / "registry.sqlite"
        assert run_cli("kureg-init", "--db", str(db)).returncode == 0
        proc = run_cli(
            "kureg-load", "--db", str(db), "--kus", str(tmp_path / "ghost.jsonl")
        )
        assert proc.returncode == 1

    def test_load_superseded_rationale_enforced(self, tmp_path):
        db = tmp_path / "registry.sqlite"
        assert run_cli("kureg-init", "--db", str(db)).returncode == 0
        batch = self._write_batch(
            tmp_path, [dict(self.VALID_KU, disposition="Superseded")]
        )
        proc = run_cli("kureg-load", "--db", str(db), "--kus", str(batch))
        assert proc.returncode == 1
        assert "superseded_rationale" in proc.stdout

    def test_query_missing_db_nonzero(self, tmp_path):
        proc = run_cli("kureg-query", "--db", str(tmp_path / "ghost.sqlite"))
        assert proc.returncode == 1
        assert "kureg-init" in proc.stderr

    def test_validate_corrupt_db_nonzero(self, tmp_path):
        junk = tmp_path / "junk.sqlite"
        junk.write_bytes(b"garbage bytes, not sqlite")
        proc = run_cli("kureg-validate", "--db", str(junk))
        assert proc.returncode == 1
        assert "error" in proc.stderr

    def test_load_mint_ids_flag(self, tmp_path):
        db = tmp_path / "registry.sqlite"
        assert run_cli("kureg-init", "--db", str(db)).returncode == 0
        anonymous = {
            k: v for k, v in self.VALID_KU.items() if k != "knowledge_unit_id"
        }
        batch = self._write_batch(tmp_path, [anonymous])
        proc = run_cli(
            "kureg-load", "--db", str(db), "--kus", str(batch), "--mint-ids"
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert json.loads(proc.stdout)["inserted"] == 1

    def test_validate_registry_kus_uses_cross_checks(self, tmp_path):
        """validate-registry --kus must run the v1.1 cross-check rules too."""
        report = tmp_path / "vr.json"
        bad = self._write_batch(
            tmp_path, [dict(self.VALID_KU, disposition="Superseded")]
        )
        proc = run_cli("validate-registry", "--kus", str(bad), "--report", str(report))
        assert proc.returncode == 1
        payload = json.loads(proc.stdout)
        assert payload["valid"] is False
        assert payload["problems_total"] >= 1
        data = json.loads(report.read_text(encoding="utf-8"))
        assert any(
            e.get("rule") == "superseded_rationale_missing"
            for e in data["validations"]["knowledge_units"]["errors"]
        )


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


class TestExtractKusCLI:
    """CLI wiring for vu extract-kus (CAP-016)."""

    def _build_vault(self, tmp_path: Path) -> tuple[Path, Path, Path]:
        import hashlib

        root = tmp_path / "src-vault"
        (root / "notes").mkdir(parents=True)
        (root / "notes" / "a.md").write_text(
            "# A\n\nContent with $math$ and [[link]].\n\n- one\n- two\n",
            encoding="utf-8",
        )
        (root / "notes" / "b.md").write_text(
            "# B\n\nIntro.\n\n```python\nx = 42\n",  # unclosed fence on purpose
            encoding="utf-8",
        )
        lines = []
        for rel in ["notes/a.md", "notes/b.md"]:
            raw = (root / rel).read_bytes()
            lines.append(
                json.dumps({"relpath": rel, "sha256": hashlib.sha256(raw).hexdigest(), "size": len(raw)})
            )
        manifest = tmp_path / "manifest.jsonl"
        manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return root, manifest, tmp_path / "batch.jsonl"

    def test_missing_required_args_exits_2(self, tmp_path):
        proc = run_cli("extract-kus", "--root", str(tmp_path))
        assert proc.returncode == 2
        assert "usage:" in proc.stderr

    def test_happy_path_extracts_writes_batch_and_report(self, tmp_path):
        root, manifest, out = self._build_vault(tmp_path)
        report = tmp_path / "report.json"
        proc = run_cli(
            "extract-kus",
            "--root", str(root),
            "--scope", "notes",
            "--vault-id", "vault-x",
            "--manifest", str(manifest),
            "--out", str(out),
            "--report", str(report),
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert out.is_file()
        records = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
        assert records
        assert all(r["disposition"] == "Unaccounted" for r in records)
        data = json.loads(report.read_text(encoding="utf-8"))
        assert data["result"]["denominators"]["files_in_scope"] == 2
        assert data["result"]["denominators"]["files_failed"] == 0

    def test_unclosed_finding_option_links_units(self, tmp_path):
        root, manifest, out = self._build_vault(tmp_path)
        proc = run_cli(
            "extract-kus",
            "--root", str(root),
            "--scope", "notes",
            "--vault-id", "vault-x",
            "--manifest", str(manifest),
            "--out", str(out),
            "--unclosed-fence-finding", "F-0002",
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        records = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
        linked = [r for r in records if r.get("finding_ids") == ["F-0002"]]
        assert len(linked) == 1 and linked[0]["unit_type"] == "code_block"

    def test_out_inside_source_root_rejected(self, tmp_path):
        root, manifest, _ = self._build_vault(tmp_path)
        proc = run_cli(
            "extract-kus",
            "--root", str(root),
            "--scope", "notes",
            "--vault-id", "vault-x",
            "--manifest", str(manifest),
            "--out", str(root / "notes" / "batch.jsonl"),
        )
        assert proc.returncode == 1
        assert "error" in proc.stderr
        assert not (root / "notes" / "batch.jsonl").exists()

    def test_hash_mismatch_exits_one(self, tmp_path):
        root, manifest, out = self._build_vault(tmp_path)
        (root / "notes" / "a.md").write_text("# tampered\n", encoding="utf-8")
        proc = run_cli(
            "extract-kus",
            "--root", str(root),
            "--scope", "notes",
            "--vault-id", "vault-x",
            "--manifest", str(manifest),
            "--out", str(out),
        )
        assert proc.returncode == 1
        assert '"files_failed": 1' in proc.stdout
        assert '"ok": false' in proc.stdout

    def test_double_run_is_byte_identical(self, tmp_path):
        root, manifest, out = self._build_vault(tmp_path)
        first = tmp_path / "first.jsonl"
        proc1 = run_cli(
            "extract-kus", "--root", str(root), "--scope", "notes",
            "--vault-id", "vault-x", "--manifest", str(manifest), "--out", str(first),
        )
        assert proc1.returncode == 0, proc1.stderr
        proc2 = run_cli(
            "extract-kus", "--root", str(root), "--scope", "notes",
            "--vault-id", "vault-x", "--manifest", str(manifest), "--out", str(out),
        )
        assert proc2.returncode == 0, proc2.stderr
        assert first.read_bytes() == out.read_bytes()


class TestKuFidelityCLI:
    """CLI wiring for vu ku-fidelity (CAP-022)."""

    def _build_vault(self, tmp_path: Path) -> tuple[Path, Path, Path]:
        import hashlib

        root = tmp_path / "src-vault"
        (root / "notes").mkdir(parents=True)
        (root / "notes" / "a.md").write_text(
            "# A\n\nParagraph one.\n\n## Section\n\n- one\n- two\n", encoding="utf-8"
        )
        lines = []
        for rel in ["notes/a.md"]:
            raw = (root / rel).read_bytes()
            lines.append(
                json.dumps({"relpath": rel, "sha256": hashlib.sha256(raw).hexdigest(), "size": len(raw)})
            )
        manifest = tmp_path / "manifest.jsonl"
        manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
        batch = tmp_path / "state" / "001-batch.jsonl"
        batch.parent.mkdir()
        proc = run_cli(
            "extract-kus",
            "--root", str(root),
            "--scope", "notes",
            "--vault-id", "vault-x",
            "--manifest", str(manifest),
            "--out", str(batch),
        )
        assert proc.returncode == 0, proc.stderr
        return root, manifest, batch

    def test_missing_required_args_exits_2(self, tmp_path):
        proc = run_cli("ku-fidelity", "--vault-id", "vault-x")
        assert proc.returncode == 2
        assert "usage:" in proc.stderr

    def test_happy_path_exits_zero_with_report(self, tmp_path):
        root, manifest, batch = self._build_vault(tmp_path)
        report = tmp_path / "fidelity.json"
        proc = run_cli(
            "ku-fidelity",
            "--batch", str(batch),
            "--vault-id", "vault-x",
            "--vault-root", str(root),
            "--manifest", str(manifest),
            "--report", str(report),
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        data = json.loads(report.read_text(encoding="utf-8"))
        assert data["result"]["ok"] is True
        assert data["result"]["records_total"] > 0
        assert data["result"]["batches"][0]["excerpt_byte_exact"] == data["result"]["records_total"]

    def test_tampered_batch_exits_one(self, tmp_path):
        root, manifest, batch = self._build_vault(tmp_path)
        records = [json.loads(line) for line in batch.read_text(encoding="utf-8").splitlines()]
        records[0]["excerpt"] = records[0]["excerpt"] + " tampered"
        batch.write_text(
            "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n", encoding="utf-8"
        )
        proc = run_cli(
            "ku-fidelity",
            "--batch", str(batch),
            "--vault-id", "vault-x",
            "--vault-root", str(root),
            "--manifest", str(manifest),
        )
        assert proc.returncode == 1
        assert '"ok": false' in proc.stdout

    def test_report_inside_source_root_rejected(self, tmp_path):
        root, manifest, batch = self._build_vault(tmp_path)
        proc = run_cli(
            "ku-fidelity",
            "--batch", str(batch),
            "--vault-id", "vault-x",
            "--vault-root", str(root),
            "--manifest", str(manifest),
            "--report", str(root / "notes" / "fidelity.json"),
        )
        assert proc.returncode == 1
        assert "error" in proc.stderr
        assert not (root / "notes" / "fidelity.json").exists()

    def test_missing_batch_file_exits_one(self, tmp_path):
        root, manifest, _ = self._build_vault(tmp_path)
        proc = run_cli(
            "ku-fidelity",
            "--batch", str(tmp_path / "state" / "missing.jsonl"),
            "--vault-id", "vault-x",
            "--vault-root", str(root),
            "--manifest", str(manifest),
        )
        assert proc.returncode == 1
        assert "error" in proc.stderr


class TestOmissionCLI:
    """CLI wiring for vu audit-output and vu omission-pilot (CAP-012)."""

    def _build(self, dest: Path) -> dict:
        from vault_unification.omission import build_fixture

        return build_fixture(dest)

    def test_audit_output_clean_exits_zero(self, tmp_path):
        fixture = self._build(tmp_path / "fixture")
        json_report = tmp_path / "audit.json"
        proc = run_cli(
            "audit-output",
            "--source-root", fixture["sources_root"],
            "--output-root", fixture["output_root"],
            "--ku-batch", fixture["ku_batch_path"],
            "--accepted-manifest", fixture["accepted_manifest_path"],
            "--report", str(json_report),
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        data = json.loads(json_report.read_text(encoding="utf-8"))
        assert data["result"]["valid"] is True
        assert data["result"]["findings"] == []

    def test_audit_output_defects_exit_one(self, tmp_path):
        from vault_unification.omission import apply_mutation

        fixture = self._build(tmp_path / "fixture")
        mutated = tmp_path / "mutated"
        apply_mutation(fixture["output_root"], mutated, "D01")
        proc = run_cli(
            "audit-output",
            "--source-root", fixture["sources_root"],
            "--output-root", str(mutated),
            "--ku-batch", fixture["ku_batch_path"],
        )
        assert proc.returncode == 1
        assert "unique-detail-omission" in proc.stdout

    def test_audit_output_report_refused_inside_source(self, tmp_path):
        fixture = self._build(tmp_path / "fixture")
        proc = run_cli(
            "audit-output",
            "--source-root", fixture["sources_root"],
            "--output-root", fixture["output_root"],
            "--ku-batch", fixture["ku_batch_path"],
            "--report", str(Path(fixture["sources_root"]) / "report.json"),
        )
        assert proc.returncode == 1
        assert "refusing to write" in proc.stderr

    def test_omission_pilot_exits_zero(self, tmp_path):
        json_report = tmp_path / "pilot.json"
        proc = run_cli(
            "omission-pilot",
            "--dest", str(tmp_path / "pilot"),
            "--report", str(json_report),
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        data = json.loads(json_report.read_text(encoding="utf-8"))
        assert data["result"]["verdict"]["pass"] is True
        assert data["result"]["summary"]["detection_rate"] == "12/12"

    def test_omission_pilot_dest_inside_source_vaults_refused(self, tmp_path):
        protected = tmp_path / "source-vaults"
        (protected / "AI Course").mkdir(parents=True)
        proc = run_cli(
            "omission-pilot",
            "--dest", str(protected / "AI Course" / "pilot"),
            "--protected-root", str(protected),
        )
        assert proc.returncode == 1
        assert "refusing to write" in proc.stderr


class TestOverlapCandidatesCLI:
    """CAP-013 CLI: discovery + classification application end to end."""

    @staticmethod
    def _ku(ku_id, source_id, excerpt, unit_type="prose", excerpt_hash=None):
        return {
            "knowledge_unit_id": ku_id,
            "source_id": source_id,
            "source_path": source_id.split(":", 1)[1],
            "source_file_hash": "f" * 64,
            "line_start": 1,
            "line_end": len(excerpt.splitlines()),
            "excerpt": excerpt,
            "excerpt_hash": excerpt_hash or ("h" + ku_id),
            "unit_type": unit_type,
            "disposition": "Unaccounted",
            "heading_path": [],
            "verification_status": {},
        }

    def _setup(self, tmp_path):
        b1 = tmp_path / "course.jsonl"
        b1.write_text(
            json.dumps(
                self._ku(
                    "KU-c1",
                    "course:reg.md",
                    "We minimize the MSE loss with gradient descent.",
                )
            )
            + "\n",
            encoding="utf-8",
        )
        b2 = tmp_path / "master.jsonl"
        b2.write_text(
            json.dumps(
                self._ku(
                    "KU-m1",
                    "master:reg.md",
                    "MSE is our loss; gradient descent optimizes it.",
                )
            )
            + "\n",
            encoding="utf-8",
        )
        terms = tmp_path / "terms.json"
        terms.write_text(
            json.dumps({"MSE": ["mean squared error"], "gradient descent": ["GD"]}),
            encoding="utf-8",
        )
        return b1, b2, terms

    def test_discovery_end_to_end(self, tmp_path):
        b1, b2, terms = self._setup(tmp_path)
        out = tmp_path / "pairs.jsonl"
        report = tmp_path / "report.json"
        proc = run_cli(
            "overlap-candidates",
            "--batch", str(b1),
            "--batch", str(b2),
            "--terms", str(terms),
            "--out", str(out),
            "--report", str(report),
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        payload = json.loads(proc.stdout)
        assert payload["term_pairs"] >= 2
        assert payload["confirmed_term_pairs"] >= 2
        assert payload["note"].startswith("candidates only")
        lines = [json.loads(l) for l in out.read_text().splitlines() if l.strip()]
        assert len(lines) == payload["term_pairs"]
        assert json.loads(report.read_text())["report_meta"]["command"] == "overlap-candidates"

    def test_discovery_rejects_output_inside_protected_root(self, tmp_path):
        b1, b2, terms = self._setup(tmp_path)
        protected = tmp_path / "sources"
        (protected / "vault").mkdir(parents=True)
        out = protected / "vault" / "pairs.jsonl"
        proc = run_cli(
            "overlap-candidates",
            "--batch", str(b1),
            "--batch", str(b2),
            "--terms", str(terms),
            "--out", str(out),
            "--protected-root", str(protected),
        )
        assert proc.returncode == 1
        assert "protected" in proc.stderr

    def test_discovery_rejects_missing_terms_file(self, tmp_path):
        b1, b2, _ = self._setup(tmp_path)
        proc = run_cli(
            "overlap-candidates",
            "--batch", str(b1),
            "--batch", str(b2),
            "--terms", str(tmp_path / "nope.json"),
            "--out", str(tmp_path / "o.jsonl"),
        )
        assert proc.returncode == 1
        assert "error" in proc.stderr

    def test_discovery_requires_two_vaults(self, tmp_path):
        b1, _, terms = self._setup(tmp_path)
        proc = run_cli(
            "overlap-candidates",
            "--batch", str(b1),
            "--terms", str(terms),
            "--out", str(tmp_path / "o.jsonl"),
        )
        # argparse accepts a single --batch; the vault-span check rejects it
        assert proc.returncode == 1
        assert "two distinct vaults" in proc.stderr

    def test_apply_overlap_and_validate(self, tmp_path):
        b1, b2, terms = self._setup(tmp_path)
        out = tmp_path / "pairs.jsonl"
        assert (
            run_cli(
                "overlap-candidates",
                "--batch", str(b1),
                "--batch", str(b2),
                "--terms", str(terms),
                "--out", str(out),
            ).returncode
            == 0
        )
        db = tmp_path / "reg.sqlite"
        assert run_cli("kureg-init", "--db", str(db)).returncode == 0
        assert (
            run_cli("kureg-load", "--db", str(db), "--kus", str(b1)).returncode == 0
        )
        assert (
            run_cli("kureg-load", "--db", str(db), "--kus", str(b2)).returncode == 0
        )
        cls = tmp_path / "cls.jsonl"
        cls.write_text(
            json.dumps(
                {
                    "classification_id": "OC-cli-0001",
                    "task_id": "EXT-003",
                    "topic": "MSE",
                    "overlap_type": "Semantic Duplicate",
                    "ku_ids": ["KU-c1", "KU-m1"],
                    "rationale": "Both units state MSE as the regression loss.",
                    "evidence": [
                        {
                            "ku_id": "KU-c1",
                            "quote": "minimize the MSE loss",
                            "source_path": "reg.md",
                            "lines": [1],
                        },
                        {
                            "ku_id": "KU-m1",
                            "quote": "MSE is our loss",
                            "source_path": "reg.md",
                            "lines": [1],
                        },
                    ],
                    "classified_by": "EXT-003 CLI test",
                    "date": "2026-10-26",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        proc = run_cli(
            "kureg-apply-overlap", "--db", str(db), "--classifications", str(cls)
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert json.loads(proc.stdout)["inserted"] == 1

        proc = run_cli("kureg-validate", "--db", str(db))
        assert proc.returncode == 0, proc.stdout + proc.stderr
        payload = json.loads(proc.stdout)
        assert payload["overlap_classification_counts"]["classifications_total"] == 1

        # idempotent re-apply
        proc = run_cli(
            "kureg-apply-overlap", "--db", str(db), "--classifications", str(cls)
        )
        assert proc.returncode == 0
        assert json.loads(proc.stdout)["inserted"] == 0
        assert json.loads(proc.stdout)["idempotent_skipped"] == 1

    def test_apply_overlap_rejects_unknown_ku(self, tmp_path):
        b1, b2, terms = self._setup(tmp_path)
        db = tmp_path / "reg.sqlite"
        assert run_cli("kureg-init", "--db", str(db)).returncode == 0
        assert (
            run_cli("kureg-load", "--db", str(db), "--kus", str(b1)).returncode == 0
        )
        cls = tmp_path / "cls.jsonl"
        cls.write_text(
            json.dumps(
                {
                    "classification_id": "OC-cli-bad",
                    "task_id": "EXT-003",
                    "topic": "MSE",
                    "overlap_type": "Semantic Duplicate",
                    "ku_ids": ["KU-c1", "KU-missing"],
                    "rationale": "references an unloaded KU",
                    "evidence": [
                        {
                            "ku_id": "KU-c1",
                            "quote": "minimize the MSE loss",
                            "source_path": "reg.md",
                            "lines": [1],
                        }
                    ],
                    "classified_by": "EXT-003 CLI test",
                    "date": "2026-10-26",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        proc = run_cli(
            "kureg-apply-overlap", "--db", str(db), "--classifications", str(cls)
        )
        assert proc.returncode == 1
        assert "not present in the registry" in proc.stderr

    def test_validate_registry_classifications_flag(self, tmp_path):
        bad = tmp_path / "cls.jsonl"
        bad.write_text(
            json.dumps({"classification_id": "OC-bad", "overlap_type": "Nope"}) + "\n",
            encoding="utf-8",
        )
        proc = run_cli("validate-registry", "--classifications", str(bad))
        assert proc.returncode == 1
        payload = json.loads(proc.stdout)
        assert payload["valid"] is False

        good = tmp_path / "cls-good.jsonl"
        good.write_text(
            json.dumps(
                {
                    "classification_id": "OC-ok",
                    "task_id": "EXT-003",
                    "topic": "MSE",
                    "overlap_type": "Partial Overlap",
                    "ku_ids": ["KU-a", "KU-b"],
                    "rationale": "ok",
                    "evidence": [
                        {
                            "ku_id": "KU-a",
                            "quote": "q",
                            "source_path": "a.md",
                            "lines": [1],
                        }
                    ],
                    "classified_by": "test",
                    "date": "2026-10-26",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        report = tmp_path / "validation-report.json"
        proc = run_cli(
            "validate-registry",
            "--classifications", str(good),
            "--report", str(report),
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        payload = json.loads(proc.stdout)
        assert payload["valid"] is True
        detail = json.loads(report.read_text(encoding="utf-8"))
        assert detail["validations"]["overlap_classifications"]["valid"] is True
        assert (
            detail["validations"]["overlap_classifications"]["cross_checks"][
                "classifications_total"
            ]
            == 1
        )

    def test_validate_registry_still_requires_an_argument(self):
        proc = run_cli("validate-registry")
        assert proc.returncode == 1
        assert "--classifications" in proc.stderr


class TestFrame002CLI:
    """FRAME-002 end-to-end: lint-artifacts, assess-quality, drift, gate,
    repair loop, prompt checking (CAP-018..CAP-021)."""

    def _vault(self, tmp_path: Path) -> Path:
        vault = tmp_path / "vault"
        vault.mkdir()
        (vault / "good.md").write_text(
            "---\ntype: concept\n---\n\n"
            "Regression is a supervised learning task. It is defined as mapping "
            "inputs to continuous outputs. For example, predicting house prices "
            "from size. In practice we minimize a loss $L(\\theta)$ over data.\n\n"
            "$$\n\\theta^* = \\arg\\min_\\theta L(\\theta)\n$$\n",
            encoding="utf-8",
        )
        (vault / "bad.md").write_text(
            "---\ntype: concept\n---\n\nShort stub with a broken fence:\n\n"
            "```python\ndef f(:\n```\n",
            encoding="utf-8",
        )
        return vault

    def test_lint_artifacts_tree_exits_1_on_errors_and_writes_report(self, tmp_path: Path):
        vault = self._vault(tmp_path)
        report = tmp_path / "lint.json"
        proc = run_cli("lint-artifacts", str(vault), "--report", str(report))
        assert proc.returncode == 1  # bad.md has a python syntax error
        payload = json.loads(proc.stdout)
        assert payload["errors"] >= 1
        detail = json.loads(report.read_text(encoding="utf-8"))
        assert detail["result"]["summary"]["files"] == 2
        assert any("necessary" in detail["result"]["caveat"] for _ in [0])

    def test_lint_artifacts_single_file_clean_exit_0(self, tmp_path: Path):
        vault = self._vault(tmp_path)
        proc = run_cli("lint-artifacts", str(vault / "good.md"), "--no-links")
        assert proc.returncode == 0, proc.stdout + proc.stderr
        payload = json.loads(proc.stdout)
        assert payload["errors"] == 0

    def test_assess_quality_writes_assessments_jsonl(self, tmp_path: Path):
        vault = self._vault(tmp_path)
        out = tmp_path / "assessments.jsonl"
        report = tmp_path / "assess.json"
        proc = run_cli(
            "assess-quality", str(vault), "--out", str(out), "--report", str(report)
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        payload = json.loads(proc.stdout)
        assert payload["notes_assessed"] == 2
        assert payload["by_type"]["concept"] == 2
        records = [json.loads(l) for l in out.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(records) == 2
        assert records[0]["standards_version"].startswith("1.")

    def test_quality_drift_on_assessments(self, tmp_path: Path):
        vault = self._vault(tmp_path)
        out = tmp_path / "assessments.jsonl"
        run_cli("assess-quality", str(vault), "--out", str(out))
        proc = run_cli("quality-drift", "--assessments", str(out))
        assert proc.returncode == 0
        payload = json.loads(proc.stdout)
        assert payload["verdict"] in ("drift_detected", "no_systematic_drift")

    def test_quality_gate_fails_on_lint_errors(self, tmp_path: Path):
        vault = self._vault(tmp_path)
        out = tmp_path / "assessments.jsonl"
        run_cli("assess-quality", str(vault), "--out", str(out))
        expected = tmp_path / "expected.txt"
        expected.write_text("good.md\nbad.md\n", encoding="utf-8")
        proc = run_cli("quality-gate", "--assessments", str(out), "--expected", str(expected))
        assert proc.returncode == 1  # bad.md has lint errors -> gate fails
        payload = json.loads(proc.stdout)
        assert payload["verdict"] == "fail"
        assert payload["failures"] >= 1

    def test_repair_loop_end_to_end(self, tmp_path: Path):
        vault = self._vault(tmp_path)
        lint_report = tmp_path / "lint.json"
        run_cli("lint-artifacts", str(vault), "--report", str(lint_report))
        store = tmp_path / "repairs.jsonl"
        proc = run_cli(
            "repair-create", "--lint-report", str(lint_report), "--store", str(store)
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        payload = json.loads(proc.stdout)
        assert payload["tasks_total"] >= 1
        assert payload["by_status"]["open"] >= 1

        listing = json.loads(
            run_cli("repair-list", "--store", str(store)).stdout
        )
        task_id = None
        # find the task id from the store file directly
        tasks = [json.loads(l) for l in store.read_text(encoding="utf-8").splitlines() if l.strip()]
        task_id = tasks[0]["repair_id"]

        # record a fixed attempt after actually repairing the file
        bad = vault / "bad.md"
        bad.write_text(
            "---\ntype: concept\n---\n\nShort stub with a fixed fence:\n\n"
            "```python\ndef f():\n    pass\n```\n",
            encoding="utf-8",
        )
        proc = run_cli(
            "repair-record", "--store", str(store), "--id", task_id, "--outcome", "fixed"
        )
        assert proc.returncode == 0
        assert json.loads(proc.stdout)["status"] == "awaiting_verification"

        # build the targeted repair prompt for the recorded task
        prompt_path = tmp_path / "repair-prompt.json"
        proc = run_cli(
            "repair-prompt", "--store", str(store), "--id", task_id, "--out", str(prompt_path)
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert prompt_path.is_file()

        # verify the repair against the fixed note
        proc = run_cli(
            "repair-verify", "--store", str(store), "--id", task_id,
            "--note-file", str(bad),
        )
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert json.loads(proc.stdout)["verified"] is True

        # status now verified
        proc = run_cli("repair-list", "--store", str(store), "--status", "verified_fixed")
        assert json.loads(proc.stdout)["total"] == 1

    def test_check_prompt_rejects_vague_spec(self, tmp_path: Path):
        spec = {
            "objective": "write a nice note",
            "target_note": {"path": "n.md", "type": "concept"},
            "source_evidence": {"ku_ids": []},
            "requirements": ["be good"],
            "constraints": [],
            "acceptance_criteria": [{"criterion": "must be polished", "check": "vibes"}],
            "output_contract": {},
        }
        spec_path = tmp_path / "spec.json"
        spec_path.write_text(json.dumps(spec), encoding="utf-8")
        proc = run_cli("check-prompt", str(spec_path))
        assert proc.returncode == 1
        payload = json.loads(proc.stdout)
        assert payload["ok"] is False
        assert payload["failures"] >= 3

    def test_check_prompt_accepts_good_spec(self, tmp_path: Path):
        source = tmp_path / "source-note.md"
        source.write_text("# Chain Rule\n\nSource material.\n", encoding="utf-8")
        spec = {
            "objective": "Write the unified concept note for the chain rule",
            "target_note": {"path": "unified/Chain Rule.md", "type": "concept"},
            "source_evidence": {"ku_ids": [], "files": [str(source)]},
            "requirements": ["define with the standard formula"],
            "constraints": [
                "do not invent content; trace every claim to the evidence",
                "preserve unrelated content; cite sources (provenance)",
            ],
            "acceptance_criteria": [
                {"criterion": "math blocks closed", "check": "lint:MATH_BLOCK_UNCLOSED"},
                {"criterion": "correctness", "check": "manual_review"},
            ],
            "output_contract": {"path": "unified/Chain Rule.md", "format": "markdown"},
        }
        spec_path = tmp_path / "spec.json"
        spec_path.write_text(json.dumps(spec), encoding="utf-8")
        proc = run_cli("check-prompt", str(spec_path))
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert json.loads(proc.stdout)["ok"] is True
