"""Unit tests for path safety and source immutability enforcement."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vault_unification import inventory as inventory_mod  # noqa: E402
from vault_unification.pathsafety import (  # noqa: E402
    PathSafetyError,
    assert_source_immutable,
    ensure_dest_safe,
    validate_roots,
)


class TestValidateRoots:
    def test_valid_source_and_disjoint_output(self, tmp_path):
        src = tmp_path / "source"
        out = tmp_path / "output"
        src.mkdir()
        result = validate_roots(src, out)
        assert result.ok, result.problems

    def test_missing_source_is_rejected(self, tmp_path):
        result = validate_roots(tmp_path / "does-not-exist", tmp_path / "out")
        assert not result.ok
        assert any("does not exist" in p for p in result.problems)

    def test_file_source_is_rejected(self, tmp_path):
        src = tmp_path / "not-a-dir"
        src.write_text("x")
        result = validate_roots(src, tmp_path / "out")
        assert not result.ok
        assert any("not a directory" in p for p in result.problems)

    def test_output_inside_source_rejected(self, tmp_path):
        src = tmp_path / "source"
        src.mkdir()
        (src / "vault").mkdir()
        result = validate_roots(src, src / "vault")
        assert not result.ok
        assert any("inside the source root" in p for p in result.problems)

    def test_source_inside_output_rejected(self, tmp_path):
        out = tmp_path / "output"
        out.mkdir()
        (out / "source").mkdir()
        result = validate_roots(out / "source", out)
        assert not result.ok
        assert any("inside the output root" in p for p in result.problems)

    def test_identical_roots_rejected(self, tmp_path):
        src = tmp_path / "source"
        src.mkdir()
        result = validate_roots(src, src)
        assert not result.ok
        assert any("identical" in p for p in result.problems)

    def test_no_output_ok(self, tmp_path):
        src = tmp_path / "source"
        src.mkdir()
        result = validate_roots(src)
        assert result.ok
        assert result.output is None

    def test_symlinked_source_reported(self, tmp_path):
        real = tmp_path / "real-source"
        real.mkdir()
        link = tmp_path / "link-source"
        os.symlink(real, link)
        result = validate_roots(link, tmp_path / "out")
        assert not result.ok
        assert any("symlink" in p for p in result.problems)


class TestEnsureDestSafe:
    def test_dest_outside_source_ok(self, tmp_path):
        src = tmp_path / "source"
        src.mkdir()
        dest = ensure_dest_safe(tmp_path / "out" / "report.json", [src])
        assert dest.name == "report.json"

    def test_dest_inside_source_rejected(self, tmp_path):
        src = tmp_path / "source"
        (src / "sub").mkdir(parents=True)
        with pytest.raises(PathSafetyError, match="protected"):
            ensure_dest_safe(src / "sub" / "report.json", [src])

    def test_dest_equal_to_source_rejected(self, tmp_path):
        src = tmp_path / "source"
        src.mkdir()
        with pytest.raises(PathSafetyError):
            ensure_dest_safe(src, [src])

    def test_symlinked_dest_rejected(self, tmp_path):
        src = tmp_path / "source"
        src.mkdir()
        outside = tmp_path / "outside"
        outside.mkdir()
        sneaky = src / "sneaky.json"
        os.symlink(outside / "x.json", sneaky)
        with pytest.raises(PathSafetyError, match="symlink"):
            ensure_dest_safe(sneaky, [src])

    def test_multiple_protected_roots(self, tmp_path):
        src1 = tmp_path / "v1"
        src2 = tmp_path / "v2"
        src1.mkdir()
        src2.mkdir()
        ok = ensure_dest_safe(tmp_path / "out.json", [src1, src2])
        assert ok
        with pytest.raises(PathSafetyError):
            ensure_dest_safe(src2 / "nested.json", [src1, src2])


class TestSourceImmutability:
    def test_unchanged_source_detected(self, fixture_vault):
        before = inventory_mod.manifest_records(inventory_mod.scan_root(fixture_vault["root"]))
        after = inventory_mod.manifest_records(inventory_mod.scan_root(fixture_vault["root"]))
        report = assert_source_immutable(before, after)
        assert report["source_unchanged"]

    def test_changed_source_detected(self, fixture_vault):
        before = inventory_mod.manifest_records(inventory_mod.scan_root(fixture_vault["root"]))
        fixture_vault["note_b"].write_text("# Note B MUTATED\n", encoding="utf-8")
        after = inventory_mod.manifest_records(inventory_mod.scan_root(fixture_vault["root"]))
        report = assert_source_immutable(before, after)
        assert not report["source_unchanged"]
        assert report["changed"] == ["note-b.md"]

    def test_added_and_removed_files_detected(self, fixture_vault):
        before = inventory_mod.manifest_records(inventory_mod.scan_root(fixture_vault["root"]))
        new_file = fixture_vault["root"] / "new.md"
        new_file.write_text("# New\n", encoding="utf-8")
        fixture_vault["note_c"].unlink()
        after = inventory_mod.manifest_records(inventory_mod.scan_root(fixture_vault["root"]))
        report = assert_source_immutable(before, after)
        assert report["added"] == ["new.md"]
        assert report["removed"] == ["sub/note-c.md"]
        assert not report["source_unchanged"]


class TestAtomicWrites:
    """L-08 fix: atomic temp+fsync+rename writes for every framework artifact."""

    def test_atomic_write_text_roundtrip(self, tmp_path):
        from vault_unification.pathsafety import atomic_write_text

        dest = tmp_path / "nested" / "out.json"
        atomic_write_text(dest, '{"a": 1}\n')
        assert dest.read_text(encoding="utf-8") == '{"a": 1}\n'

    def test_atomic_write_replaces_existing_content(self, tmp_path):
        from vault_unification.pathsafety import atomic_write_text

        dest = tmp_path / "out.txt"
        dest.write_text("OLD", encoding="utf-8")
        atomic_write_text(dest, "NEW")
        assert dest.read_text(encoding="utf-8") == "NEW"

    def test_atomic_write_leaves_no_temp_files(self, tmp_path):
        from vault_unification.pathsafety import atomic_write_text

        dest = tmp_path / "out.jsonl"
        atomic_write_text(dest, "line\n")
        leftovers = [p for p in tmp_path.iterdir() if p.name.startswith(".")]
        assert leftovers == []

    def test_atomic_write_failure_cleans_temp_and_keeps_old(self, tmp_path):
        # unwritable directory forces the write to fail AFTER mkstemp;
        # the old file must remain intact and no temp file may survive
        import os
        from vault_unification.pathsafety import atomic_write_bytes

        dest = tmp_path / "out.bin"
        atomic_write_bytes(dest, b"OLD")
        real_replace = os.replace

        def failing_replace(src, dst):
            raise OSError("simulated crash before rename")

        os.replace = failing_replace
        try:
            with pytest.raises(OSError):
                atomic_write_bytes(dest, b"NEW-TRUNCATED")
        finally:
            os.replace = real_replace
        assert dest.read_bytes() == b"OLD"
        leftovers = [p for p in tmp_path.iterdir() if p.name.startswith(".")]
        assert leftovers == []

    def test_atomic_write_replaces_symlink_rather_than_following(self, tmp_path):
        # L-09 mitigation: a symlink at the destination must be REPLACED,
        # not followed, so writes cannot be redirected through it
        from vault_unification.pathsafety import atomic_write_text

        target = tmp_path / "evil-target.txt"
        target.write_text("VICTIM", encoding="utf-8")
        dest = tmp_path / "out.txt"
        dest.write_text("OLD", encoding="utf-8")
        dest.unlink()
        dest.symlink_to(target)
        atomic_write_text(dest, "REPLACED")
        assert not dest.is_symlink()
        assert dest.read_text(encoding="utf-8") == "REPLACED"
        assert target.read_text(encoding="utf-8") == "VICTIM"

    def test_reporting_uses_atomic_writes(self, tmp_path):
        # write_json_report must go through the atomic helper
        import vault_unification.reporting as reporting

        called = {}
        original = reporting.atomic_write_text

        def spy(dest, text):
            called["dest"] = str(dest)
            return original(dest, text)

        reporting.atomic_write_text = spy
        try:
            reporting.write_json_report(tmp_path / "r" / "report.json", "cmd", {"ok": True})
        finally:
            reporting.atomic_write_text = original
        assert "report.json" in called["dest"]
