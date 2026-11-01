"""Unit + CLI tests: rule-driven disposition assignment (DISP-001, ADR-0014).

Covers the engine rules (R1 dossier member, R2 multi-feeder note, R3 sole
feeder, R4 archival context, X exceptions), the registry overlay semantics
(apply / idempotent skip / revision / validation failures), the F-0023
NULL-heading destination dedup regression, and the CLI surface.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vault_unification import dispositions as disp  # noqa: E402
from vault_unification import kuregistry as kureg  # noqa: E402
from vault_unification.dispositions import DispositionError  # noqa: E402


def _ku(kid, source_id, unit_type="prose", excerpt="content", lines=(1, 2)):
    return {
        "knowledge_unit_id": kid,
        "source_id": source_id,
        "source_path": source_id.split(":", 1)[1],
        "source_file_hash": "0" * 64,
        "source_format": "markdown",
        "heading_path": ["H"],
        "line_start": lines[0],
        "line_end": lines[1],
        "excerpt": excerpt,
        "excerpt_hash": "1" * 64,
        "unit_type": unit_type,
        "disposition": "Unaccounted",
        "verification_status": {},
    }


@pytest.fixture()
def fixture(tmp_path):
    """A tiny but complete project slice: 6 KUs, one dossier, a mapping."""
    kus = [
        # R1: dossier concept member (also sole feeder of its note)
        _ku("KU-0000000000000001", "v1:a/Topic A.md"),
        # R2: two files feeding one note
        _ku("KU-0000000000000002", "v1:b/Shared Topic.md"),
        _ku("KU-0000000000000003", "v2:b/Shared Topic.md"),
        # R3: sole feeder
        _ku("KU-0000000000000004", "v2:c/Solo Topic.md"),
        # R4: archival context area
        _ku("KU-0000000000000005", "v2:20 - Vault and Project Context/Master Roadmap.md"),
        # X1-style exception: the real Qs4 stub path (matches EXCEPTION_KEYS)
        _ku("KU-0000000000000006",
            "ai-course:09 - Quizzes and Question Banks/03. Question Series/Qs4.md",
            excerpt="use this in the 2d to 3d "),
    ]
    batch = tmp_path / "batch.jsonl"
    with batch.open("w", encoding="utf-8") as fh:
        for ku in kus:
            fh.write(json.dumps(ku) + "\n")

    dossier = {
        "dossier_id": "test-v2",
        "domain": "regression",
        "version": "v2",
        "rule_set": "ext006-category-rules-v1",
        "generated_by": "test",
        "provenance": {"batches": [], "classification_files": []},
        "concepts": [
            {
                "concept_id": "CD-test-0001",
                "label": "Topic A",
                "source_classification_id": "OC-ext999-0001",
                "overlap_type": "Semantic Duplicate",
                "ku_ids": ["KU-0000000000000001"],
                "ku_count": 1,
                "by_vault": {"ai-course": [], "master-ai": []},
                "categories": {},
                "gaps": [],
            }
        ],
        "accounting": {},
    }
    dossier_path = tmp_path / "dossier-v2.json"
    dossier_path.write_text(json.dumps(dossier), encoding="utf-8")

    mapping = [
        {"vault": "v1", "source_path": "a/Topic A.md",
         "canonical_paths": ["04 - Machine Learning/Regression/Topic A.md"],
         "multi": False, "rationale": "r", "mapped_by": "test", "date": "2026-11-01"},
        {"vault": "v1", "source_path": "b/Shared Topic.md",
         "canonical_paths": ["04 - Machine Learning/Regression/Shared Topic.md"],
         "multi": False, "rationale": "r", "mapped_by": "test", "date": "2026-11-01"},
        {"vault": "v2", "source_path": "b/Shared Topic.md",
         "canonical_paths": ["04 - Machine Learning/Regression/Shared Topic.md"],
         "multi": False, "rationale": "r", "mapped_by": "test", "date": "2026-11-01"},
        {"vault": "v2", "source_path": "c/Solo Topic.md",
         "canonical_paths": ["04 - Machine Learning/Regression/Solo Topic.md"],
         "multi": False, "rationale": "r", "mapped_by": "test", "date": "2026-11-01"},
        {"vault": "v2", "source_path": "20 - Vault and Project Context/Master Roadmap.md",
         "canonical_paths": ["20 - Vault and Project Context/Master Roadmap.md"],
         "multi": False, "rationale": "roadmap", "mapped_by": "test", "date": "2026-11-01"},
        {"vault": "ai-course",
         "source_path": "09 - Quizzes and Question Banks/03. Question Series/Qs4.md",
         "canonical_paths": ["19 - Reference and Practice/Quizzes/Question Series/Conceptual Questions.md"],
         "multi": False, "rationale": "r", "mapped_by": "test", "date": "2026-11-01"},
    ]
    mapping_path = tmp_path / "mapping.jsonl"
    with mapping_path.open("w", encoding="utf-8") as fh:
        for rec in mapping:
            fh.write(json.dumps(rec) + "\n")
    return {
        "tmp_path": tmp_path, "kus": kus, "batch": str(batch),
        "dossier": str(dossier_path), "mapping": str(mapping_path),
    }


class TestAssignRules:
    def test_rules_assign_expected_dispositions(self, fixture):
        records, report = disp.assign_dispositions(
            [fixture["batch"]], [fixture["dossier"]], fixture["mapping"]
        )
        by_ku = {r["ku_id"]: r for r in records}
        assert by_ku["KU-0000000000000001"]["disposition"] == "Consolidated"
        assert by_ku["KU-0000000000000001"]["rule_id"] == "DISP-R1"
        assert by_ku["KU-0000000000000001"]["source_refs"] == ["CD-test-0001"]
        assert by_ku["KU-0000000000000002"]["disposition"] == "Consolidated"
        assert by_ku["KU-0000000000000002"]["rule_id"] == "DISP-R2"
        assert by_ku["KU-0000000000000003"]["disposition"] == "Consolidated"
        assert by_ku["KU-0000000000000004"]["disposition"] == "Preserved"
        assert by_ku["KU-0000000000000004"]["rule_id"] == "DISP-R3"
        assert by_ku["KU-0000000000000005"]["disposition"] == "Contextualized"
        assert by_ku["KU-0000000000000005"]["rule_id"] == "DISP-R4"
        assert by_ku["KU-0000000000000006"]["disposition"] == "Contextualized"
        assert by_ku["KU-0000000000000006"]["rule_id"].startswith("DISP-X")
        assert report["kus_total"] == 6
        assert report["by_disposition"].get("Unaccounted", 0) == 0

    def test_every_record_carries_destinations(self, fixture):
        records, _ = disp.assign_dispositions(
            [fixture["batch"]], [fixture["dossier"]], fixture["mapping"]
        )
        for r in records:
            assert r["destinations"], r
            for d in r["destinations"]:
                assert d["path"].endswith(".md")

    def test_missing_mapping_record_fails(self, fixture, tmp_path):
        kus = [_ku("KU-0000000000000009", "v1:z/Unmapped.md")]
        batch = tmp_path / "batch2.jsonl"
        batch.write_text(json.dumps(kus[0]) + "\n", encoding="utf-8")
        with pytest.raises(DispositionError, match="no file-mapping record"):
            disp.assign_dispositions([str(batch)], [fixture["dossier"]],
                                     fixture["mapping"])

    def test_v1_dossier_rejected(self, fixture, tmp_path):
        dossier = json.loads(Path(fixture["dossier"]).read_text())
        dossier["version"] = "v1"
        p = tmp_path / "dossier-v1.json"
        p.write_text(json.dumps(dossier), encoding="utf-8")
        with pytest.raises(DispositionError, match="v2 dossier"):
            disp.assign_dispositions([fixture["batch"]], [str(p)],
                                     fixture["mapping"])

    def test_ledger_write_is_deterministic(self, fixture, tmp_path):
        records, _ = disp.assign_dispositions(
            [fixture["batch"]], [fixture["dossier"]], fixture["mapping"]
        )
        a = tmp_path / "ledger-a.jsonl"
        b = tmp_path / "ledger-b.jsonl"
        sha_a = disp.write_ledger(records, a)
        sha_b = disp.write_ledger(records, b)
        assert sha_a == sha_b
        assert a.read_bytes() == b.read_bytes()


class TestApplyDispositions:
    KU_SCHEMA = Path(__file__).resolve().parents[1] / "schemas" / "knowledge-unit.schema.json"

    def _db(self, fixture, tmp_path):
        db = tmp_path / "reg.sqlite"
        kureg.init_registry(db, force=True)
        kureg.load_jsonl(db, fixture["batch"], schema_path=self.KU_SCHEMA)
        return db

    def _ledger(self, fixture, tmp_path):
        records, _ = disp.assign_dispositions(
            [fixture["batch"]], [fixture["dossier"]], fixture["mapping"]
        )
        path = tmp_path / "ledger.jsonl"
        with path.open("w", encoding="utf-8") as fh:
            for r in records:
                fh.write(json.dumps(r) + "\n")
        return str(path)

    def test_apply_sets_effective_dispositions(self, fixture, tmp_path):
        db = self._db(fixture, tmp_path)
        result = kureg.apply_dispositions(db, self._ledger(fixture, tmp_path))
        assert result["applied"] == 6
        assert result["counts_after_apply"]["by_disposition"].get("Unaccounted", 0) == 0
        counts = kureg.validate_registry_db(db)["counts"]
        assert counts["by_disposition"].get("Unaccounted", 0) == 0
        assert counts["by_disposition"]["Consolidated"] == 3

    def test_reapply_is_idempotent(self, fixture, tmp_path):
        db = self._db(fixture, tmp_path)
        ledger = self._ledger(fixture, tmp_path)
        kureg.apply_dispositions(db, ledger)
        result = kureg.apply_dispositions(db, ledger)
        assert result["applied"] == 0
        assert result["revised"] == 0
        assert result["idempotent_skipped"] == 6

    def test_revision_updates_effective_state(self, fixture, tmp_path):
        db = self._db(fixture, tmp_path)
        ledger = self._ledger(fixture, tmp_path)
        kureg.apply_dispositions(db, ledger)
        revised = tmp_path / "ledger2.jsonl"
        lines = Path(ledger).read_text().splitlines()
        out = []
        for line in lines:
            rec = json.loads(line)
            if rec["ku_id"] == "KU-0000000000000004":
                rec["disposition"] = "Superseded"
                rec["rationale"] = "better treatment exists elsewhere; unique info kept"
            out.append(json.dumps(rec))
        revised.write_text("\n".join(out) + "\n", encoding="utf-8")
        result = kureg.apply_dispositions(db, str(revised))
        assert result["revised"] == 1
        assert result["idempotent_skipped"] == 5
        counts = kureg.validate_registry_db(db)["counts"]
        assert counts["by_disposition"]["Superseded"] == 1

    def test_unknown_ku_id_rejected(self, fixture, tmp_path):
        db = self._db(fixture, tmp_path)
        ledger = tmp_path / "bad.jsonl"
        ledger.write_text(json.dumps({
            "ku_id": "KU-doesnotexist0000", "disposition": "Preserved",
            "destinations": [{"path": "x.md", "heading": None}],
            "rule_id": "DISP-R3", "rationale": "r",
            "assigned_by": "t", "date": "2026-11-01"}) + "\n",
            encoding="utf-8")
        with pytest.raises(kureg.RegistryError, match="unknown ku_id"):
            kureg.apply_dispositions(db, str(ledger))

    def test_superseded_without_rationale_rejected(self, fixture, tmp_path):
        db = self._db(fixture, tmp_path)
        ledger = tmp_path / "bad.jsonl"
        ledger.write_text(json.dumps({
            "ku_id": "KU-0000000000000004", "disposition": "Superseded",
            "destinations": [{"path": "x.md", "heading": None}],
            "rule_id": "DISP-R3", "rationale": "  ",
            "assigned_by": "t", "date": "2026-11-01"}) + "\n",
            encoding="utf-8")
        with pytest.raises(kureg.RegistryError, match="Superseded without rationale"):
            kureg.apply_dispositions(db, str(ledger))

    def test_f0023_null_heading_destinations_do_not_duplicate(self, fixture, tmp_path):
        """F-0023 regression: N KUs sharing one NULL-heading destination must
        produce exactly ONE destinations row (UNIQUE(path, heading) cannot
        dedupe NULL headings)."""
        db = self._db(fixture, tmp_path)
        kureg.apply_dispositions(db, self._ledger(fixture, tmp_path))
        conn = sqlite3.connect(str(db))
        n_rows = conn.execute("SELECT COUNT(*) FROM destinations").fetchone()[0]
        n_orphans = conn.execute(
            "SELECT COUNT(*) FROM destinations d WHERE NOT EXISTS ("
            "SELECT 1 FROM ku_destinations kd "
            "WHERE kd.destination_id = d.destination_id)"
        ).fetchone()[0]
        conn.close()
        assert n_rows == 5  # 5 distinct canonical paths in the fixture
        assert n_orphans == 0


class TestAssignDispositionsCLI:
    def test_end_to_end_cli(self, fixture, tmp_path):
        from vault_unification.cli import main

        out = tmp_path / "ledger.jsonl"
        report = tmp_path / "report.json"
        rc = main([
            "assign-dispositions",
            "--ku-batch", fixture["batch"],
            "--dossier", fixture["dossier"],
            "--file-mapping", fixture["mapping"],
            "--out", str(out),
            "--report", str(report),
        ])
        assert rc == 0
        payload = json.loads(report.read_text(encoding="utf-8"))
        assert payload["ledger_records"] == 6
        assert payload["result"]["kus_total"] == 6
        records = [json.loads(l) for l in out.read_text().splitlines() if l.strip()]
        assert len(records) == 6

    def test_output_into_source_vault_rejected(self, fixture, tmp_path):
        from vault_unification.cli import main

        protected = tmp_path / "sources"
        protected.mkdir()
        rc = main([
            "assign-dispositions",
            "--ku-batch", fixture["batch"],
            "--dossier", fixture["dossier"],
            "--file-mapping", fixture["mapping"],
            "--out", str(protected / "ledger.jsonl"),
            "--protected-root", str(protected),
        ])
        assert rc == 1


class TestCommittedLedger:
    """The committed session-19 ledger and mapping stay consistent."""

    LEDGER = Path("state/dispositions/001-disp001-rule-driven.jsonl")
    MAPPING = Path("state/synthesis/file-mapping-v1.jsonl")

    def test_committed_ledger_covers_every_ku_exactly_once(self):
        repo = Path(__file__).resolve().parents[1]
        batch_kus = set()
        for p in sorted((repo / "state" / "knowledge-units").glob("*.jsonl")):
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    batch_kus.add(json.loads(line)["knowledge_unit_id"])
        ledger_kus = []
        for line in (repo / self.LEDGER).read_text(encoding="utf-8").splitlines():
            if line.strip():
                ledger_kus.append(json.loads(line)["ku_id"])
        assert len(ledger_kus) == len(batch_kus) == 27536
        assert set(ledger_kus) == batch_kus
        assert len(set(ledger_kus)) == len(ledger_kus)

    def test_committed_ledger_has_no_unaccounted_or_needs_review(self):
        repo = Path(__file__).resolve().parents[1]
        for line in (repo / self.LEDGER).read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                assert rec["disposition"] not in ("Unaccounted", "Needs review")
                assert rec["rule_id"].startswith("DISP-")
                assert rec["rationale"]
                for d in rec["destinations"]:
                    assert d["path"].endswith(".md")

    def test_committed_mapping_covers_all_609_files(self):
        repo = Path(__file__).resolve().parents[1]
        files = set()
        for vault, root in [("ai-course", repo / "source-vaults/AI /AI Course"),
                            ("master-ai", repo / "source-vaults/AI /Master AI")]:
            for p in root.rglob("*.md"):
                files.add((vault, p.relative_to(root).as_posix()))
        mapped = set()
        for line in (repo / self.MAPPING).read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                mapped.add((rec["vault"], rec["source_path"]))
        assert mapped == files and len(mapped) == 609

    def test_committed_structure_note_count(self):
        repo = Path(__file__).resolve().parents[1]
        structure = json.loads(
            (repo / "state" / "synthesis" / "canonical-structure-v1.json")
            .read_text(encoding="utf-8"))
        acc = structure["accounting"]
        assert acc["source_files"] == 609
        assert acc["canonical_notes"] == len(structure["notes"]) == 544
        assert acc["areas"] == 20
        assert acc["source_files_by_vault"] == {"ai-course": 276, "master-ai": 333}
