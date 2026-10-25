"""Unit/integration tests for inventory, hashing and manifest diffing."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vault_unification import inventory as inv  # noqa: E402
from tests.conftest import sha256_file  # noqa: E402


class TestScanRoot:
    def test_counts_match_fixture(self, fixture_vault):
        scan = inv.scan_root(fixture_vault["root"])
        # fixture files: 8 markdown + 1 png + 1 pdf = 10 total, 0 unreadable
        assert scan["total_files"] == 10
        assert scan["counts"]["markdown"] == 8
        assert scan["counts"]["image"] == 1
        assert scan["counts"]["pdf"] == 1
        assert scan["counts"]["unreadable"] == 0

    def test_hashes_are_correct_sha256(self, fixture_vault):
        scan = inv.scan_root(fixture_vault["root"])
        by_rel = {rec["relpath"]: rec for rec in scan["files"]}
        assert by_rel["note-a.md"]["sha256"] == sha256_file(fixture_vault["note_a"])
        assert by_rel["image.png"]["sha256"] == sha256_file(fixture_vault["image"])

    def test_deterministic_order(self, fixture_vault):
        first = [rec["relpath"] for rec in inv.scan_root(fixture_vault["root"])["files"]]
        second = [rec["relpath"] for rec in inv.scan_root(fixture_vault["root"])["files"]]
        assert first == sorted(first)
        assert first == second

    def test_missing_root_raises(self, tmp_path):
        with pytest.raises(NotADirectoryError):
            inv.scan_root(tmp_path / "missing")

    def test_file_as_root_raises(self, fixture_vault):
        with pytest.raises(NotADirectoryError):
            inv.scan_root(fixture_vault["note_a"])

    def test_unreadable_file_is_explicit(self, fixture_vault):
        locked = fixture_vault["root"] / "locked.md"
        locked.write_text("# Locked\n", encoding="utf-8")
        os.chmod(locked, 0o000)
        try:
            if os.geteuid() == 0:
                pytest.skip("running as root: permission bits not enforceable")
            try:
                locked.read_text(encoding="utf-8")
                pytest.skip("environment does not enforce read permission bits")
            except PermissionError:
                pass  # expected
            scan = inv.scan_root(fixture_vault["root"])
            assert scan["counts"]["unreadable"] == 1
            error_rels = {rec["relpath"] for rec in scan["errors"]}
            assert "locked.md" in error_rels
            assert any("hash failed" in rec.get("error", "") for rec in scan["errors"])
        finally:
            os.chmod(locked, 0o644)

    def test_symlink_recorded_not_followed(self, fixture_vault):
        link = fixture_vault["root"] / "link-to-a.md"
        link.symlink_to(fixture_vault["note_a"])
        scan = inv.scan_root(fixture_vault["root"])
        rec = next(r for r in scan["files"] + scan["errors"] if r["relpath"] == "link-to-a.md")
        assert rec["is_symlink"] is True
        assert rec["sha256"] is None

    def test_classification(self, fixture_vault):
        scan = inv.scan_root(fixture_vault["root"])
        by_rel = {rec["relpath"]: rec for rec in scan["files"]}
        assert by_rel["note-a.md"]["class"] == "markdown"
        assert by_rel["doc.pdf"]["class"] == "pdf"
        assert by_rel["image.png"]["class"] == "image"


class TestManifestRoundTrip:
    def test_write_and_load_manifest(self, fixture_vault, tmp_path):
        scan = inv.scan_root(fixture_vault["root"])
        manifest = tmp_path / "manifest.jsonl"
        count = inv.write_manifest(manifest, inv.manifest_records(scan))
        assert count == 10
        loaded = inv.load_manifest(manifest)
        assert loaded == inv.manifest_records(scan)

    def test_load_manifest_rejects_malformed_line(self, tmp_path):
        bad = tmp_path / "bad.jsonl"
        bad.write_text('{"relpath": "a.md", "sha256": "x"}\nnot json\n', encoding="utf-8")
        with pytest.raises(ValueError, match="line 2"):
            inv.load_manifest(bad)

    def test_load_manifest_rejects_missing_fields(self, tmp_path):
        bad = tmp_path / "bad.jsonl"
        bad.write_text('{"relpath": "a.md"}\n', encoding="utf-8")
        with pytest.raises(ValueError, match="relpath.*sha256|sha256.*relpath"):
            inv.load_manifest(bad)


class TestDiffManifests:
    def test_identical_manifests(self, fixture_vault):
        records = inv.manifest_records(inv.scan_root(fixture_vault["root"]))
        diff = inv.diff_manifests(records, records)
        assert diff["counts"] == {
            "before": 10,
            "after": 10,
            "added": 0,
            "removed": 0,
            "changed": 0,
            "unchanged": 10,
        }

    def test_change_detection_by_hash(self, fixture_vault):
        before = inv.manifest_records(inv.scan_root(fixture_vault["root"]))
        fixture_vault["note_a"].write_text("# mutated\n", encoding="utf-8")
        after = inv.manifest_records(inv.scan_root(fixture_vault["root"]))
        diff = inv.diff_manifests(before, after)
        assert diff["changed"] == ["note-a.md"]
        assert diff["counts"]["unchanged"] == 9

    def test_mutation_then_restore_yields_no_diff(self, fixture_vault):
        original = fixture_vault["note_a"].read_text(encoding="utf-8")
        before = inv.manifest_records(inv.scan_root(fixture_vault["root"]))
        fixture_vault["note_a"].write_text("# mutated\n", encoding="utf-8")
        fixture_vault["note_a"].write_text(original, encoding="utf-8")
        after = inv.manifest_records(inv.scan_root(fixture_vault["root"]))
        diff = inv.diff_manifests(before, after)
        assert diff["changed"] == []

    def test_manifest_json_serializable(self, fixture_vault, tmp_path):
        manifest = tmp_path / "m.jsonl"
        inv.write_manifest(manifest, inv.manifest_records(inv.scan_root(fixture_vault["root"])))
        for line in manifest.read_text(encoding="utf-8").splitlines():
            json.loads(line)
