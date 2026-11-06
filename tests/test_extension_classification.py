"""Unit tests: term-level dossier-extension classification validation (ADR-0013).

Covers the session-19 record class: schema shape (single-KU records are
legitimate), file-level cross-checks, and the batch cross-checks that would
have caught F-0022 (empty evidence lines) before commit.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vault_unification import registry as reg  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
EXT_SCHEMA = REPO_ROOT / "schemas" / "dossier-extension-classification.schema.json"
EXT_FILES = {
    "regression": REPO_ROOT / "state/classifications/009-disc002-dext-regression-extension.jsonl",
    "tree-based": REPO_ROOT / "state/classifications/010-disc002-dext-tree-extension.jsonl",
    "evaluation": REPO_ROOT / "state/classifications/011-disc002-dext-evaluation-extension.jsonl",
    "clustering": REPO_ROOT / "state/classifications/012-disc002-dext-clustering-extension.jsonl",
    "generalization": REPO_ROOT / "state/classifications/013-disc002-dext-generalization-extension.jsonl",
    "training-stability": REPO_ROOT / "state/classifications/014-disc002-dext-training-stability-extension.jsonl",
}

VALID_EXT = {
    "classification_id": "DX-test-0001",
    "task_id": "DISC-002",
    "topic": "example term — corpus extension evidence",
    "overlap_type": "Complementary Content",
    "ku_ids": ["KU-a"],
    "rationale": "one corpus location carries concept content for the term",
    "evidence": [
        {
            "ku_id": "KU-a",
            "quote": "Example term: a definition.",
            "source_path": "folder/note.md",
            "lines": [4],
        }
    ],
    "classified_by": "test",
    "date": "2026-11-01",
    "method": "unit test",
    "candidate_ref": "test fixture",
}

VALID_KU_RECORD = {
    "knowledge_unit_id": "KU-a",
    "source_id": "test-vault:folder/note.md",
    "source_path": "folder/note.md",
    "source_file_hash": "0" * 64,
    "source_format": "markdown",
    "heading_path": ["H"],
    "line_start": 4,
    "line_end": 5,
    "excerpt": "Example term: a definition.\nSecond line.",
    "excerpt_hash": "1" * 64,
    "unit_type": "prose",
    "disposition": "Unaccounted",
    "verification_status": {},
}


def write_jsonl(path: Path, records: list[dict]) -> Path:
    with open(path, "w", encoding="utf-8") as handle:
        for rec in records:
            handle.write(json.dumps(rec) + "\n")
    return path


class TestExtensionClassificationSchema:
    def test_schema_is_valid_draft_2020_12(self):
        import jsonschema

        schema = json.loads(EXT_SCHEMA.read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator.check_schema(schema)

    def test_single_ku_record_is_legitimate(self, tmp_path):
        path = write_jsonl(tmp_path / "ext.jsonl", [VALID_EXT])
        report = reg.validate_extension_classification_file(path, EXT_SCHEMA)
        assert report["valid"], report["errors"]

    def test_empty_evidence_lines_rejected(self, tmp_path):
        """The F-0022 regression test: lines must be non-empty."""
        bad = json.loads(json.dumps(VALID_EXT))
        bad["evidence"][0]["lines"] = []
        path = write_jsonl(tmp_path / "ext.jsonl", [bad])
        report = reg.validate_extension_classification_file(path, EXT_SCHEMA)
        assert not report["valid"]
        assert any("non-empty" in e["error"] for e in report["errors"])

    def test_pair_level_minitems_2_not_required(self, tmp_path):
        """Unlike overlap records, one KU is enough (no cross-vault rule)."""
        rec = json.loads(json.dumps(VALID_EXT))
        rec["classification_id"] = "DX-test-0002"
        path = write_jsonl(tmp_path / "ext.jsonl", [rec])
        report = reg.validate_extension_classification_file(path, EXT_SCHEMA)
        assert report["valid"], report["errors"]

    def test_duplicate_classification_ids_rejected(self, tmp_path):
        path = write_jsonl(tmp_path / "ext.jsonl", [VALID_EXT, VALID_EXT])
        report = reg.validate_extension_classification_file(path, EXT_SCHEMA)
        assert not report["valid"]
        assert any(e["rule"] == "duplicate_classification_id" for e in report["errors"])

    def test_evidence_ku_set_mismatch_rejected(self, tmp_path):
        bad = json.loads(json.dumps(VALID_EXT))
        bad["ku_ids"] = ["KU-a", "KU-b"]
        path = write_jsonl(tmp_path / "ext.jsonl", [bad])
        report = reg.validate_extension_classification_file(path, EXT_SCHEMA)
        assert not report["valid"]
        assert any(e["rule"] == "evidence_ku_set_mismatch" for e in report["errors"])


class TestExtensionClassificationBatchCrossChecks:
    def _batch(self, tmp_path):
        return write_jsonl(tmp_path / "batch.jsonl", [VALID_KU_RECORD])

    def test_consistent_evidence_passes(self, tmp_path):
        rec = json.loads(json.dumps(VALID_EXT))
        rec["evidence"][0]["lines"] = [4, 5]
        rec["evidence"][0]["quote"] = "Example term: a definition.\nSecond line."
        path = write_jsonl(tmp_path / "ext.jsonl", [rec])
        report = reg.validate_extension_classification_file(
            path, EXT_SCHEMA, ku_batches=[self._batch(tmp_path)]
        )
        assert report["valid"], report["errors"]
        assert report["batch_cross_checks"]["status"] == "run"
        assert report["batch_cross_checks"]["errors"] == 0

    def test_lines_not_matching_ku_span_rejected(self, tmp_path):
        rec = json.loads(json.dumps(VALID_EXT))
        rec["evidence"][0]["lines"] = [4]
        path = write_jsonl(tmp_path / "ext.jsonl", [rec])
        report = reg.validate_extension_classification_file(
            path, EXT_SCHEMA, ku_batches=[self._batch(tmp_path)]
        )
        assert not report["valid"]
        assert any(e["rule"] == "evidence_lines_mismatch" for e in report["errors"])

    def test_quote_not_byte_exact_rejected(self, tmp_path):
        rec = json.loads(json.dumps(VALID_EXT))
        rec["evidence"][0]["lines"] = [4, 5]
        rec["evidence"][0]["quote"] = "Example term: a definition."
        path = write_jsonl(tmp_path / "ext.jsonl", [rec])
        report = reg.validate_extension_classification_file(
            path, EXT_SCHEMA, ku_batches=[self._batch(tmp_path)]
        )
        assert not report["valid"]
        assert any(e["rule"] == "evidence_quote_not_byte_exact" for e in report["errors"])

    def test_source_path_mismatch_rejected(self, tmp_path):
        rec = json.loads(json.dumps(VALID_EXT))
        rec["evidence"][0]["lines"] = [4, 5]
        rec["evidence"][0]["quote"] = "Example term: a definition.\nSecond line."
        rec["evidence"][0]["source_path"] = "other/note.md"
        path = write_jsonl(tmp_path / "ext.jsonl", [rec])
        report = reg.validate_extension_classification_file(
            path, EXT_SCHEMA, ku_batches=[self._batch(tmp_path)]
        )
        assert not report["valid"]
        assert any(e["rule"] == "evidence_source_path_mismatch" for e in report["errors"])

    def test_unknown_ku_id_rejected(self, tmp_path):
        rec = json.loads(json.dumps(VALID_EXT))
        rec["ku_ids"] = ["KU-zzz"]
        rec["evidence"][0]["ku_id"] = "KU-zzz"
        path = write_jsonl(tmp_path / "ext.jsonl", [rec])
        report = reg.validate_extension_classification_file(
            path, EXT_SCHEMA, ku_batches=[self._batch(tmp_path)]
        )
        assert not report["valid"]
        assert any(e["rule"] == "unknown_ku_id" for e in report["errors"])

    def test_missing_batch_file_reports_error(self, tmp_path):
        path = write_jsonl(tmp_path / "ext.jsonl", [VALID_EXT])
        report = reg.validate_extension_classification_file(
            path, EXT_SCHEMA, ku_batches=[tmp_path / "missing.jsonl"]
        )
        assert not report["valid"]


class TestCommittedExtensionFiles:
    """The repaired committed files must pass schema + cross-checks.

    Batch cross-checks over all 70 committed batches are exercised in the
    session-19 report (reports/dossier-ext/s19-f0022-repair-report.json and
    the validate-registry runs recorded there); here we keep the test fast
    with the schema + file-level cross-checks over the real files.
    """

    @pytest.mark.parametrize("domain", sorted(EXT_FILES))
    def test_committed_file_validates(self, domain):
        report = reg.validate_extension_classification_file(
            EXT_FILES[domain], EXT_SCHEMA
        )
        assert report["valid"], report["errors"]
        assert report["records_total"] == report["records_valid"]

    def test_expected_record_counts(self):
        expected = {
            "regression": 33, "tree-based": 41, "evaluation": 49,
            "clustering": 40, "generalization": 47, "training-stability": 84,
        }
        for domain, path in EXT_FILES.items():
            records = [
                json.loads(line)
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            assert len(records) == expected[domain], domain

    def test_repair_script_is_idempotent_check(self):
        """scripts/s19_repair_ext_evidence.py --check reports zero drift."""
        import subprocess

        result = subprocess.run(
            [sys.executable, "scripts/s19_repair_ext_evidence.py", "--check"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert "changed=   0" in result.stdout
