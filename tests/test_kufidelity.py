"""Tests for CAP-022: KU batch fidelity verification (kufidelity).

Covers the happy path over a genuinely extracted batch, every defect class
the checker must catch (tampered excerpt, wrong hash, duplicate ids within
and across batches, wrong vault prefix, source/manifest hash disagreement,
out-of-bounds spans, heading-crossing spans, processed records), the
relaxation flag, failure paths for unusable inputs, and determinism.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vault_unification import kufidelity, kuextract  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
KU_SCHEMA = REPO_ROOT / "schemas" / "knowledge-unit.schema.json"

VAULT_TEXT_A = "# Title\n\nFirst paragraph.\n\n## Section\n\n- one\n- two\n"
VAULT_TEXT_B = "# Other\n\nIntro text.\n\n```python\nx = 42\n```\n"


def _build_vault(tmp_path: Path) -> tuple[Path, Path]:
    root = tmp_path / "src-vault"
    (root / "notes").mkdir(parents=True)
    (root / "notes" / "a.md").write_text(VAULT_TEXT_A, encoding="utf-8")
    (root / "notes" / "b.md").write_text(VAULT_TEXT_B, encoding="utf-8")
    lines = []
    for rel in ["notes/a.md", "notes/b.md"]:
        raw = (root / rel).read_bytes()
        lines.append(json.dumps({"relpath": rel, "sha256": hashlib.sha256(raw).hexdigest(), "size": len(raw)}))
    manifest = tmp_path / "manifest.jsonl"
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return root, manifest


def _extract_batch(root: Path, manifest: Path, out: Path, scope: str = "notes") -> list[dict]:
    result = kuextract.extract_scope(
        root, scope, "vault-x", manifest, out, kus_schema=KU_SCHEMA
    )
    assert result["ok"], result
    records = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert records
    return records


def _write_batch(path: Path, records: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(r, sort_keys=True) for r in records) + "\n", encoding="utf-8"
    )


class TestHappyPath:
    def test_extracted_batch_passes(self, tmp_path):
        root, manifest = _build_vault(tmp_path)
        batch = tmp_path / "state" / "001-batch.jsonl"
        batch.parent.mkdir()
        _extract_batch(root, manifest, batch)
        report = kufidelity.check_batches(
            [batch], "vault-x", root, manifest, kus_schema=KU_SCHEMA
        )
        assert report["ok"] is True, report["batches"][0]["errors"]
        assert report["records_total"] == report["batches"][0]["records_total"]
        assert report["batches"][0]["excerpt_byte_exact"] == report["records_total"]
        assert report["batches"][0]["excerpt_hash_valid"] == report["records_total"]
        assert report["batches"][0]["structurally_pure"] == report["records_total"]
        assert report["batches"][0]["manifest_agree"] == report["records_total"]
        assert report["batches"][0]["schema_valid"] is True
        assert report["id_collisions"] == []

    def test_two_batches_no_sibling_collision_detected_when_clean(self, tmp_path):
        root, manifest = _build_vault(tmp_path)
        state = tmp_path / "state"
        state.mkdir()
        b1 = state / "001-a.jsonl"
        b2 = state / "001-b.jsonl"
        _extract_batch(root, manifest, b1, scope="notes/a.md")
        _extract_batch(root, manifest, b2, scope="notes/b.md")
        report = kufidelity.check_batches(
            [b1, b2], "vault-x", root, manifest, kus_schema=KU_SCHEMA
        )
        assert report["ok"] is True
        assert report["batches_checked"] == 2
        assert report["cross_check_batches"] == []  # both are checked; no other siblings


class TestDefectDetection:
    def _baseline(self, tmp_path):
        root, manifest = _build_vault(tmp_path)
        batch = tmp_path / "state" / "001-batch.jsonl"
        batch.parent.mkdir()
        records = _extract_batch(root, manifest, batch)
        return root, manifest, batch, records

    def test_tampered_excerpt_detected(self, tmp_path):
        root, manifest, batch, records = self._baseline(tmp_path)
        records[0]["excerpt"] = records[0]["excerpt"] + " tampered"
        _write_batch(batch, records)
        report = kufidelity.check_batches([batch], "vault-x", root, manifest, kus_schema=KU_SCHEMA)
        assert report["ok"] is False
        assert any("excerpt not byte-exact" in e for e in report["batches"][0]["errors"])

    def test_excerpt_hash_mismatch_detected(self, tmp_path):
        root, manifest, batch, records = self._baseline(tmp_path)
        records[0]["excerpt_hash"] = "0" * 64
        _write_batch(batch, records)
        report = kufidelity.check_batches([batch], "vault-x", root, manifest, kus_schema=KU_SCHEMA)
        assert report["ok"] is False
        assert any("excerpt_hash mismatch" in e for e in report["batches"][0]["errors"])

    def test_duplicate_id_within_batch_detected(self, tmp_path):
        root, manifest, batch, records = self._baseline(tmp_path)
        dup = copy.deepcopy(records[0])
        dup["line_start"] = dup["line_end"] = 3
        dup["excerpt"] = "## Section"
        dup["excerpt_hash"] = hashlib.sha256(b"## Section").hexdigest()
        records.append(dup)
        _write_batch(batch, records)
        report = kufidelity.check_batches([batch], "vault-x", root, manifest, kus_schema=KU_SCHEMA)
        assert report["ok"] is False
        assert any("duplicate knowledge_unit_id within batch" in e for e in report["batches"][0]["errors"])

    def test_id_collision_across_sibling_batches_detected(self, tmp_path):
        root, manifest, batch, records = self._baseline(tmp_path)
        other = batch.parent / "002-other.jsonl"
        _write_batch(other, records)  # identical ids in a sibling batch
        report = kufidelity.check_batches([batch], "vault-x", root, manifest, kus_schema=KU_SCHEMA)
        assert report["ok"] is False
        assert report["id_collisions"], report["id_collisions"]
        assert any("collides across batches" in e for e in report["batches"][0]["errors"])

    def test_wrong_vault_prefix_detected(self, tmp_path):
        root, manifest, batch, records = self._baseline(tmp_path)
        records[0]["source_id"] = "other-vault:" + records[0]["source_path"]
        _write_batch(batch, records)
        report = kufidelity.check_batches([batch], "vault-x", root, manifest, kus_schema=KU_SCHEMA)
        assert report["ok"] is False
        assert any("vault prefix" in e for e in report["batches"][0]["errors"])

    def test_source_hash_disagrees_with_disk_detected(self, tmp_path):
        root, manifest, batch, records = self._baseline(tmp_path)
        records[0]["source_file_hash"] = "f" * 64
        _write_batch(batch, records)
        report = kufidelity.check_batches([batch], "vault-x", root, manifest, kus_schema=KU_SCHEMA)
        assert report["ok"] is False
        assert any("source_file_hash mismatch" in e for e in report["batches"][0]["errors"])

    def test_manifest_disagreement_detected(self, tmp_path):
        root, manifest, batch, records = self._baseline(tmp_path)
        lines = manifest.read_text(encoding="utf-8").splitlines()
        entry = json.loads(lines[0])
        entry["sha256"] = "0" * 64
        lines[0] = json.dumps(entry)
        manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
        report = kufidelity.check_batches([batch], "vault-x", root, manifest, kus_schema=KU_SCHEMA)
        assert report["ok"] is False
        assert any("disagrees with baseline manifest" in e for e in report["batches"][0]["errors"])

    def test_out_of_bounds_span_detected(self, tmp_path):
        root, manifest, batch, records = self._baseline(tmp_path)
        records[0]["line_start"] = 900
        records[0]["line_end"] = 999
        _write_batch(batch, records)
        report = kufidelity.check_batches([batch], "vault-x", root, manifest, kus_schema=KU_SCHEMA)
        assert report["ok"] is False
        assert any("outside file" in e for e in report["batches"][0]["errors"])

    def test_heading_crossing_span_detected(self, tmp_path):
        root, manifest, batch, records = self._baseline(tmp_path)
        # a.md line 5 is '## Section'; build a span covering it
        rec = records[0]
        rec["line_start"], rec["line_end"] = 3, 5
        rec["excerpt"] = "\n".join(VAULT_TEXT_A.splitlines()[2:5])
        rec["excerpt_hash"] = hashlib.sha256(rec["excerpt"].encode()).hexdigest()
        _write_batch(batch, records)
        report = kufidelity.check_batches([batch], "vault-x", root, manifest, kus_schema=KU_SCHEMA)
        assert report["ok"] is False
        assert any("crosses heading" in e for e in report["batches"][0]["errors"])

    def test_empty_section_on_heading_line_is_design_conformant(self, tmp_path):
        """Regression: REGEN batch 014/015 flagged legitimate empty_section
        units (span exactly one heading line) as heading-crossing. The
        extractor design puts empty_section units ON their heading line, so
        the checker must accept the extractor's own output for a source with
        a trailing content-free heading."""
        import hashlib as _h

        root, manifest = _build_vault(tmp_path)
        batch = tmp_path / "state" / "001-batch.jsonl"
        batch.parent.mkdir()
        relpath = "notes/a.md"
        src = root / relpath
        text = src.read_text(encoding="utf-8") + "\n## Trailing Empty Heading\n"
        src.write_text(text, encoding="utf-8")
        entries = [
            json.loads(line)
            for line in manifest.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        for e in entries:
            if e["relpath"] == relpath:
                e["sha256"] = _h.sha256(src.read_bytes()).hexdigest()
        manifest.write_text(
            "\n".join(json.dumps(e) for e in entries) + "\n", encoding="utf-8"
        )
        records = _extract_batch(root, manifest, batch)
        empty_sections = [r for r in records if r["unit_type"] == "empty_section"]
        assert empty_sections, "extractor should mint an empty_section for the trailing heading"
        assert all(r["line_start"] == r["line_end"] for r in empty_sections)
        report = kufidelity.check_batches([batch], "vault-x", root, manifest, kus_schema=KU_SCHEMA)
        assert report["ok"] is True, report["batches"][0]["errors"]

    def test_empty_section_not_on_heading_line_detected(self, tmp_path):
        root, manifest, batch, records = self._baseline(tmp_path)
        rec = {
            "disposition": "Unaccounted",
            "excerpt": "plain line masquerading as empty_section",
            "excerpt_hash": hashlib.sha256(b"plain line masquerading as empty_section").hexdigest(),
            "heading_path": ["Title"],
            "knowledge_unit_id": "KU-fakeempty001",
            "line_end": 3,
            "line_start": 3,
            "source_file_hash": records[0]["source_file_hash"],
            "source_format": "markdown",
            "source_id": records[0]["source_id"],
            "source_path": records[0]["source_path"],
            "unit_type": "empty_section",
            "verification_status": {
                "accounting": "pending",
                "editorial": "pending",
                "extraction": "machine-segmented",
                "semantic": "pending",
                "technical": "pending",
            },
        }
        records.append(rec)
        _write_batch(batch, records)
        report = kufidelity.check_batches([batch], "vault-x", root, manifest, kus_schema=KU_SCHEMA)
        assert report["ok"] is False
        assert any("empty_section span must be exactly one heading line" in e for e in report["batches"][0]["errors"])

    def test_processed_record_flagged_and_relaxable(self, tmp_path):
        root, manifest, batch, records = self._baseline(tmp_path)
        records[0]["disposition"] = "Preserved"
        _write_batch(batch, records)
        report = kufidelity.check_batches([batch], "vault-x", root, manifest, kus_schema=KU_SCHEMA)
        assert report["ok"] is False
        assert any("disposition" in e for e in report["batches"][0]["errors"])
        relaxed = kufidelity.check_batches(
            [batch], "vault-x", root, manifest, kus_schema=KU_SCHEMA, allow_processed=True
        )
        assert relaxed["ok"] is True, relaxed["batches"][0]["errors"]

    def test_schema_invalid_record_detected(self, tmp_path):
        root, manifest, batch, records = self._baseline(tmp_path)
        records[0].pop("source_path")
        _write_batch(batch, records)
        report = kufidelity.check_batches([batch], "vault-x", root, manifest, kus_schema=KU_SCHEMA)
        assert report["ok"] is False
        assert report["batches"][0]["schema_valid"] is False
        assert any("schema:" in e for e in report["batches"][0]["errors"])

    def test_source_file_missing_detected(self, tmp_path):
        root, manifest, batch, records = self._baseline(tmp_path)
        (root / "notes" / "a.md").unlink()
        report = kufidelity.check_batches([batch], "vault-x", root, manifest, kus_schema=KU_SCHEMA)
        assert report["ok"] is False
        assert any("source file missing" in e for e in report["batches"][0]["errors"])


class TestFailurePaths:
    def test_missing_batch_raises(self, tmp_path):
        root, manifest = _build_vault(tmp_path)
        with pytest.raises(kufidelity.FidelityError):
            kufidelity.check_batches(
                [tmp_path / "nope.jsonl"], "vault-x", root, manifest, kus_schema=KU_SCHEMA
            )

    def test_missing_vault_root_raises(self, tmp_path):
        root, manifest = _build_vault(tmp_path)
        batch = tmp_path / "state" / "001-batch.jsonl"
        batch.parent.mkdir()
        _extract_batch(root, manifest, batch)
        with pytest.raises(kufidelity.FidelityError):
            kufidelity.check_batches(
                [batch], "vault-x", tmp_path / "no-vault", manifest, kus_schema=KU_SCHEMA
            )

    def test_empty_vault_id_raises(self, tmp_path):
        root, manifest = _build_vault(tmp_path)
        batch = tmp_path / "state" / "001-batch.jsonl"
        batch.parent.mkdir()
        _extract_batch(root, manifest, batch)
        with pytest.raises(kufidelity.FidelityError):
            kufidelity.check_batches([batch], "  ", root, manifest, kus_schema=KU_SCHEMA)

    def test_bad_manifest_json_raises(self, tmp_path):
        root, manifest = _build_vault(tmp_path)
        batch = tmp_path / "state" / "001-batch.jsonl"
        batch.parent.mkdir()
        _extract_batch(root, manifest, batch)
        manifest.write_text("not json\n", encoding="utf-8")
        with pytest.raises(kufidelity.FidelityError):
            kufidelity.check_batches([batch], "vault-x", root, manifest, kus_schema=KU_SCHEMA)


class TestDeterminism:
    def test_repeated_runs_identical_reports(self, tmp_path):
        root, manifest = _build_vault(tmp_path)
        batch = tmp_path / "state" / "001-batch.jsonl"
        batch.parent.mkdir()
        _extract_batch(root, manifest, batch)
        r1 = kufidelity.check_batches([batch], "vault-x", root, manifest, kus_schema=KU_SCHEMA)
        r2 = kufidelity.check_batches([batch], "vault-x", root, manifest, kus_schema=KU_SCHEMA)
        assert r1 == r2

    def test_vault_root_never_written(self, tmp_path):
        root, manifest = _build_vault(tmp_path)
        batch = tmp_path / "state" / "001-batch.jsonl"
        batch.parent.mkdir()
        _extract_batch(root, manifest, batch)
        before = {
            p.relative_to(root): p.stat().st_mtime_ns
            for p in root.rglob("*")
            if p.is_file()
        }
        kufidelity.check_batches([batch], "vault-x", root, manifest, kus_schema=KU_SCHEMA)
        after = {p.relative_to(root): p.stat().st_mtime_ns for p in root.rglob("*") if p.is_file()}
        assert before == after
