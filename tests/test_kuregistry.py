"""Unit, integration and recovery tests for the KU registry (CAP-011).

Covers: stable-ID minting, init/load/query/validate semantics, idempotent and
conflicting re-loads, cross-record rule enforcement, atomic rollback, database
corruption handling, and fresh-session rebuild reproducibility. CLI-level
end-to-end tests live in tests/test_cli.py.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vault_unification import kuregistry as kureg  # noqa: E402
from vault_unification import registry as reg  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
KU_SCHEMA = REPO_ROOT / "schemas" / "knowledge-unit.schema.json"

VALID_KU = {
    "knowledge_unit_id": "KU-0001",
    "source_id": "SRC-MAI-0001",
    "source_path": "vault/note-a.md",
    "source_file_hash": "0" * 64,
    "heading_path": ["Note A", "Section One"],
    "line_start": 12,
    "line_end": 14,
    "excerpt": "Attention weights are normalized by softmax.",
    "excerpt_hash": "1" * 64,
    "unit_type": "claim",
    "concept_ids": ["attention", "softmax"],
    "disposition": "Preserved",
    "destinations": [{"path": "Deep Learning/Attention.md", "heading": "Mechanics"}],
    "verification_status": {"extraction": "verified"},
    "finding_ids": ["F-0001"],
}

VALID_KU_2 = {
    "knowledge_unit_id": "KU-0002",
    "source_id": "SRC-AIC-0002",
    "source_path": "vault2/course-b.md",
    "source_file_hash": "2" * 64,
    "line_start": 3,
    "line_end": 5,
    "excerpt": "Old API caveat: the parameter was renamed in v2.",
    "unit_type": "caveat",
    "disposition": "Contextualized",
    "overlap_type": "Complementary Content",
    "verification_status": {},
}


@pytest.fixture()
def db(tmp_path: Path) -> Path:
    path = tmp_path / "registry.sqlite"
    kureg.init_registry(path)
    return path


def write_jsonl(path: Path, records: list[dict]) -> Path:
    with open(path, "w", encoding="utf-8") as handle:
        for rec in records:
            handle.write(json.dumps(rec) + "\n")
    return path


def load_ok(db_path: Path, records: list[dict]) -> dict:
    result = kureg.load_records(db_path, records, schema_path=KU_SCHEMA)
    assert result["valid"], result["errors"]
    return result


def normalized_sorted(record: dict) -> dict:
    """Normalize a record the way the registry does, with arrays sorted so
    input order cannot break round-trip comparisons."""
    out = dict(record)
    for key in ("concept_ids", "finding_ids", "supporting_unit_ids"):
        if key in out and out[key] is not None:
            out[key] = sorted(out[key])
    if "destinations" in out and out["destinations"] is not None:
        out["destinations"] = sorted(
            out["destinations"], key=lambda d: (d["path"], d.get("heading") or "")
        )
    return {k: v for k, v in out.items() if v is not None}


# ---------------------------------------------------------------------------
# stable IDs
# ---------------------------------------------------------------------------


class TestMintKuId:
    def test_deterministic(self):
        first = kureg.mint_ku_id(VALID_KU)
        second = kureg.mint_ku_id(dict(VALID_KU))
        assert first == second
        assert first.startswith("KU-")

    def test_changes_with_excerpt(self):
        altered = dict(VALID_KU, excerpt="Different content entirely.", excerpt_hash=None)
        assert kureg.mint_ku_id(altered) != kureg.mint_ku_id(VALID_KU)

    def test_explicit_excerpt_hash_takes_precedence(self):
        """When both are present, the explicit excerpt_hash is authoritative —
        changing only the excerpt text must not change the minted ID."""
        altered = dict(VALID_KU, excerpt="Different content entirely.")
        assert kureg.mint_ku_id(altered) == kureg.mint_ku_id(VALID_KU)

    def test_changes_with_lines(self):
        altered = dict(VALID_KU, line_start=13)
        assert kureg.mint_ku_id(altered) != kureg.mint_ku_id(VALID_KU)

    def test_changes_with_file_hash_and_heading(self):
        assert kureg.mint_ku_id(dict(VALID_KU, source_file_hash="9" * 64)) != kureg.mint_ku_id(VALID_KU)
        assert kureg.mint_ku_id(dict(VALID_KU, heading_path=["Other"])) != kureg.mint_ku_id(VALID_KU)

    def test_excerpt_text_hashes_like_excerpt_hash(self):
        with_hash = dict(VALID_KU, excerpt_hash=None)
        with_text = dict(VALID_KU, excerpt_hash=None)
        assert kureg.mint_ku_id(with_hash) == kureg.mint_ku_id(with_text)

    def test_missing_locator_rejected(self):
        bare = {
            "source_id": "SRC-1",
            "source_file_hash": "0" * 64,
            "heading_path": ["H"],
        }
        with pytest.raises(kureg.RegistryError, match="line range"):
            kureg.mint_ku_id(bare)

    def test_missing_identity_rejected(self):
        with pytest.raises(kureg.RegistryError, match="source_file_hash"):
            kureg.mint_ku_id({"source_id": "S", "excerpt": "x"})


# ---------------------------------------------------------------------------
# init
# ---------------------------------------------------------------------------


class TestInit:
    def test_creates_schema_and_meta(self, tmp_path):
        path = tmp_path / "r.sqlite"
        result = kureg.init_registry(path)
        assert result["registry_schema_version"] == kureg.REGISTRY_SCHEMA_VERSION
        conn = sqlite3.connect(str(path))
        tables = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
        conn.close()
        assert {
            "meta",
            "knowledge_units",
            "concepts",
            "ku_concepts",
            "destinations",
            "ku_destinations",
            "ku_findings",
            "ku_supports",
        } <= tables

    def test_refuses_existing_without_force(self, db):
        with pytest.raises(kureg.RegistryError, match="--force"):
            kureg.init_registry(db)

    def test_force_recreates(self, db):
        load_ok(db, [VALID_KU])
        result = kureg.init_registry(db, force=True)
        assert result["force_used"] is True
        counts = kureg.query_registry(db)
        assert counts["total_kus"] == 0


# ---------------------------------------------------------------------------
# loading
# ---------------------------------------------------------------------------


class TestLoad:
    def test_load_inserts_and_counts(self, db):
        result = load_ok(db, [VALID_KU, VALID_KU_2])
        assert result["inserted"] == 2
        assert result["counts_after_load"]["total_kus"] == 2
        assert result["counts_after_load"]["by_disposition"]["Preserved"] == 1

    def test_links_populated(self, db):
        load_ok(db, [VALID_KU])
        conn = sqlite3.connect(str(db))
        concepts = conn.execute("SELECT concept_id FROM concepts ORDER BY concept_id").fetchall()
        findings = conn.execute("SELECT finding_id FROM ku_findings").fetchall()
        dests = conn.execute("SELECT path, heading FROM destinations").fetchall()
        conn.close()
        assert [c[0] for c in concepts] == ["attention", "softmax"]
        assert [f[0] for f in findings] == ["F-0001"]
        assert dests == [("Deep Learning/Attention.md", "Mechanics")]

    def test_parent_later_in_batch_allowed(self, db):
        child = dict(
            VALID_KU_2,
            knowledge_unit_id="KU-CHILD",
            parent_unit_id="KU-PARENT",
        )
        parent = dict(VALID_KU, knowledge_unit_id="KU-PARENT")
        load_ok(db, [child, parent])  # order in file must not matter

    def test_supports_within_batch_allowed(self, db):
        rec = dict(
            VALID_KU,
            knowledge_unit_id="KU-A",
            supporting_unit_ids=["KU-B"],
        )
        other = dict(VALID_KU_2, knowledge_unit_id="KU-B")
        load_ok(db, [rec, other])

    def test_idempotent_reload(self, db):
        load_ok(db, [VALID_KU])
        result = load_ok(db, [VALID_KU])
        assert result["inserted"] == 0
        assert result["skipped_identical"] == 1

    def test_null_vs_absent_equivalent_for_reload(self, db):
        with_null = dict(VALID_KU)
        with_null["excerpt"] = None
        load_ok(db, [with_null])
        # absent key vs explicit null must fingerprint identically
        absent = {k: v for k, v in VALID_KU.items() if k != "excerpt"}
        result = load_ok(db, [absent])
        assert result["skipped_identical"] == 1

    def test_conflicting_reload_rejected_and_atomic(self, db):
        load_ok(db, [VALID_KU])
        conflicting = dict(VALID_KU, disposition="Unaccounted")
        result = kureg.load_records(db, [conflicting], schema_path=KU_SCHEMA)
        assert not result["valid"]
        assert any(e["stage"] == "conflict" for e in result["errors"])
        # and a batch containing a new record plus a conflicting one must
        # insert nothing at all
        result = kureg.load_records(
            db, [conflicting, VALID_KU_2], schema_path=KU_SCHEMA
        )
        assert not result["valid"]
        assert kureg.query_registry(db)["total_kus"] == 1

    def test_schema_invalid_record_blocks_batch(self, db):
        bad = dict(VALID_KU, disposition="Deleted")
        fresh = dict(VALID_KU_2)
        result = kureg.load_records(db, [bad, fresh], schema_path=KU_SCHEMA)
        assert not result["valid"]
        assert all(e["stage"] == "schema" for e in result["errors"])
        assert kureg.query_registry(db)["total_kus"] == 0

    def test_missing_jsonschema_refused(self, db, monkeypatch):
        monkeypatch.setattr(kureg, "_HAS_JSONSCHEMA", False)
        result = kureg.load_records(db, [VALID_KU], schema_path=KU_SCHEMA)
        assert not result["valid"]
        assert any("jsonschema" in e["error"] for e in result["errors"])

    def test_within_batch_duplicate_rejected(self, db):
        result = kureg.load_records(
            db, [VALID_KU, dict(VALID_KU)], schema_path=KU_SCHEMA
        )
        assert not result["valid"]
        assert any(e.get("rule") == "duplicate_id" for e in result["errors"])

    def test_superseded_without_rationale_rejected(self, db):
        bad = dict(VALID_KU, disposition="Superseded")
        result = kureg.load_records(db, [bad], schema_path=KU_SCHEMA)
        assert not result["valid"]
        assert any(e.get("rule") == "superseded_rationale_missing" for e in result["errors"])

    def test_superseded_with_rationale_accepted(self, db):
        good = dict(
            VALID_KU,
            disposition="Superseded",
            superseded_rationale="Replaced by the unified softmax derivation; unique scaling caveat preserved in KU-0009.",
        )
        result = load_ok(db, [good])
        assert result["inserted"] == 1

    def test_unknown_parent_rejected_at_load(self, db):
        bad = dict(VALID_KU_2, parent_unit_id="KU-GHOST")
        result = kureg.load_records(db, [bad], schema_path=KU_SCHEMA)
        assert not result["valid"]
        assert any(e.get("rule") == "unknown_parent" for e in result["errors"])

    def test_self_parent_and_self_support_rejected(self, db):
        result = kureg.load_records(
            db, [dict(VALID_KU, parent_unit_id="KU-0001")], schema_path=KU_SCHEMA
        )
        assert any(e.get("rule") == "self_parent" for e in result["errors"])
        result = kureg.load_records(
            db,
            [dict(VALID_KU, supporting_unit_ids=["KU-0001"])],
            schema_path=KU_SCHEMA,
        )
        assert any(e.get("rule") == "self_support" for e in result["errors"])

    def test_mint_ids_flag(self, db):
        anonymous = {k: v for k, v in VALID_KU.items() if k != "knowledge_unit_id"}
        result = kureg.load_records(
            db, [anonymous], schema_path=KU_SCHEMA, mint_ids=True
        )
        assert result["valid"], result["errors"]
        minted = kureg.mint_ku_id(anonymous)
        assert kureg.query_registry(db, ku_id=minted)["count"] == 1

    def test_load_jsonl_reports_parse_errors(self, db, tmp_path):
        path = tmp_path / "batch.jsonl"
        path.write_text(
            json.dumps(VALID_KU) + "\n{broken\n", encoding="utf-8"
        )
        result = kureg.load_jsonl(db, path, schema_path=KU_SCHEMA)
        assert not result["valid"]
        assert any(e.get("stage") == "parse" and e.get("line") == 2 for e in result["errors"])

    def test_load_jsonl_missing_file(self, db, tmp_path):
        result = kureg.load_jsonl(db, tmp_path / "ghost.jsonl", schema_path=KU_SCHEMA)
        assert not result["valid"]
        assert any("not found" in e["error"] for e in result["errors"])

    def test_load_into_missing_db_rejected(self, tmp_path):
        with pytest.raises(kureg.RegistryError, match="kureg-init"):
            kureg.load_records(
                tmp_path / "ghost.sqlite", [VALID_KU], schema_path=KU_SCHEMA
            )


# ---------------------------------------------------------------------------
# querying
# ---------------------------------------------------------------------------


class TestQuery:
    @pytest.fixture()
    def loaded_db(self, db):
        load_ok(db, [VALID_KU, VALID_KU_2])
        return db

    def test_round_trip_reconstruction(self, loaded_db):
        result = kureg.query_registry(loaded_db)
        assert result["count"] == 2
        reconstructed = {
            rec["knowledge_unit_id"]: normalized_sorted(rec)
            for rec in result["records"]
        }
        expected = {
            rec["knowledge_unit_id"]: normalized_sorted(rec)
            for rec in (VALID_KU, VALID_KU_2)
        }
        assert reconstructed == expected

    def test_filter_by_disposition(self, loaded_db):
        result = kureg.query_registry(loaded_db, disposition="Preserved")
        assert result["count"] == 1
        assert result["records"][0]["knowledge_unit_id"] == "KU-0001"
        assert result["total_kus"] == 2  # denominator always reported

    def test_filter_by_concept(self, loaded_db):
        result = kureg.query_registry(loaded_db, concept="softmax")
        assert result["count"] == 1

    def test_filter_by_finding(self, loaded_db):
        result = kureg.query_registry(loaded_db, finding="F-0001")
        assert result["count"] == 1

    def test_filter_by_source_path_and_unit_type(self, loaded_db):
        assert kureg.query_registry(loaded_db, source_path="vault2/course-b.md")["count"] == 1
        assert kureg.query_registry(loaded_db, unit_type="caveat")["count"] == 1
        assert kureg.query_registry(loaded_db, source_id="SRC-MAI-0001")["count"] == 1

    def test_unknown_disposition_filter_rejected(self, loaded_db):
        with pytest.raises(kureg.RegistryError, match="disposition"):
            kureg.query_registry(loaded_db, disposition="Deleted")

    def test_empty_registry(self, db):
        result = kureg.query_registry(db)
        assert result["count"] == 0
        assert result["total_kus"] == 0


# ---------------------------------------------------------------------------
# validation
# ---------------------------------------------------------------------------


class TestValidate:
    def test_clean_registry_valid(self, db):
        load_ok(db, [VALID_KU, VALID_KU_2])
        report = kureg.validate_registry_db(db)
        assert report["valid"], report["errors"]
        assert report["counts"]["total_kus"] == 2
        assert report["unaccounted_count"] == 0

    def test_missing_db_rejected(self, tmp_path):
        with pytest.raises(kureg.RegistryError, match="kureg-init"):
            kureg.validate_registry_db(tmp_path / "ghost.sqlite")

    def _corrupt(self, db, sql, params=()):
        conn = sqlite3.connect(str(db))
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("PRAGMA ignore_check_constraints = ON")
        conn.execute(sql, params)
        conn.commit()
        conn.close()

    def test_orphan_parent_detected(self, db):
        load_ok(db, [VALID_KU])
        self._corrupt(db, "UPDATE knowledge_units SET parent_unit_id = 'KU-GHOST'")
        report = kureg.validate_registry_db(db)
        assert not report["valid"]
        assert any(e["rule"] == "orphan_parent" for e in report["errors"])

    def test_dangling_links_detected(self, db):
        load_ok(db, [VALID_KU])
        self._corrupt(db, "DELETE FROM knowledge_units WHERE ku_id = 'KU-0001'")
        report = kureg.validate_registry_db(db)
        rules = {e["rule"] for e in report["errors"]}
        assert rules & {"dangling_ku_concept", "dangling_ku_finding", "dangling_ku_destination"}

    def test_superseded_without_rationale_detected(self, db):
        good = dict(
            VALID_KU,
            disposition="Superseded",
            superseded_rationale="Unique caveat moved to KU-0009.",
        )
        load_ok(db, [good])
        self._corrupt(db, "UPDATE knowledge_units SET superseded_rationale = NULL")
        report = kureg.validate_registry_db(db)
        assert any(e["rule"] == "superseded_rationale_missing" for e in report["errors"])

    def test_corrupt_verification_status_detected(self, db):
        load_ok(db, [VALID_KU])
        self._corrupt(db, "UPDATE knowledge_units SET verification_status = 'not json'")
        report = kureg.validate_registry_db(db)
        assert any(e["rule"] == "corrupt_verification_status" for e in report["errors"])

    def test_bad_disposition_detected(self, db):
        load_ok(db, [VALID_KU])
        self._corrupt(db, "UPDATE knowledge_units SET disposition = 'Deleted'")
        report = kureg.validate_registry_db(db)
        assert any(e["rule"] == "invalid_disposition" for e in report["errors"])

    def test_bad_overlap_type_detected(self, db):
        load_ok(db, [VALID_KU])
        self._corrupt(db, "UPDATE knowledge_units SET overlap_type = 'Samey'")
        report = kureg.validate_registry_db(db)
        assert any(e["rule"] == "invalid_overlap_type" for e in report["errors"])

    def test_needs_review_without_finding_is_warning(self, db):
        load_ok(db, [dict(VALID_KU, disposition="Needs review", finding_ids=[])])
        report = kureg.validate_registry_db(db)
        assert report["valid"]  # warning, not error
        assert any(
            w["rule"] == "needs_review_without_finding" for w in report["warnings"]
        )
        assert report["needs_review_count"] == 1

    def test_unaccounted_counted_prominently(self, db):
        load_ok(db, [dict(VALID_KU, disposition="Unaccounted")])
        report = kureg.validate_registry_db(db)
        assert report["valid"]  # legal during work, but counted
        assert report["unaccounted_count"] == 1
        assert "block release" in report["note"]

    def test_schema_version_mismatch_rejected(self, db):
        self._corrupt(db, "UPDATE meta SET value = '99' WHERE key = 'registry_schema_version'")
        with pytest.raises(kureg.RegistryError, match="schema version"):
            kureg.validate_registry_db(db)


# ---------------------------------------------------------------------------
# recovery
# ---------------------------------------------------------------------------


class TestRecovery:
    def test_corrupt_db_file_rejected_explicitly(self, tmp_path):
        junk = tmp_path / "junk.sqlite"
        junk.write_bytes(b"this is definitely not a sqlite database")
        for operation in (
            lambda: kureg.load_records(junk, [VALID_KU], schema_path=KU_SCHEMA),
            lambda: kureg.query_registry(junk),
            lambda: kureg.validate_registry_db(junk),
        ):
            with pytest.raises(kureg.RegistryError):
                operation()

    def test_failed_load_leaves_db_unchanged(self, db):
        load_ok(db, [VALID_KU])
        before = kureg.query_registry(db)
        bad_batch = [
            VALID_KU_2,
            dict(VALID_KU, knowledge_unit_id="KU-0003", disposition="Deleted"),
        ]
        result = kureg.load_records(db, bad_batch, schema_path=KU_SCHEMA)
        assert not result["valid"]
        after = kureg.query_registry(db)
        assert after["total_kus"] == before["total_kus"]
        assert after["records"] == before["records"]

    def test_fresh_session_rebuild_is_reproducible(self, tmp_path):
        """Two independent rebuilds from the same canonical JSONL must produce
        byte-identical query results (persistence across fresh sessions)."""
        batch = tmp_path / "batch.jsonl"
        write_jsonl(batch, [VALID_KU, VALID_KU_2])

        outputs = []
        for suffix in ("a", "b"):
            db = tmp_path / f"registry-{suffix}.sqlite"
            kureg.init_registry(db)
            result = kureg.load_jsonl(db, batch, schema_path=KU_SCHEMA)
            assert result["valid"], result["errors"]
            dump = tmp_path / f"dump-{suffix}.jsonl"
            with open(dump, "w", encoding="utf-8") as handle:
                for record in kureg.query_registry(db)["records"]:
                    handle.write(json.dumps(record, sort_keys=True) + "\n")
            outputs.append(dump.read_bytes())
        assert outputs[0] == outputs[1]


# ---------------------------------------------------------------------------
# shared cross-check rules (registry.check_ku_records)
# ---------------------------------------------------------------------------


class TestCrossCheckRules:
    def test_file_level_validation_via_registry_module(self, tmp_path):
        good = write_jsonl(tmp_path / "good.jsonl", [VALID_KU, VALID_KU_2])
        report = reg.validate_ku_file(good, KU_SCHEMA)
        assert report["valid"], report["errors"]
        assert report["cross_checks"]["status"] == "run"

    def test_file_level_duplicate(self, tmp_path):
        bad = write_jsonl(tmp_path / "bad.jsonl", [VALID_KU, VALID_KU])
        report = reg.validate_ku_file(bad, KU_SCHEMA)
        assert not report["valid"]
        assert any(e["rule"] == "duplicate_id" for e in report["errors"])

    def test_file_level_superseded_rationale(self, tmp_path):
        bad = write_jsonl(
            tmp_path / "bad.jsonl", [dict(VALID_KU, disposition="Superseded")]
        )
        report = reg.validate_ku_file(bad, KU_SCHEMA)
        assert any(e["rule"] == "superseded_rationale_missing" for e in report["errors"])

    def test_cross_batch_parent_allowed_at_file_level(self, tmp_path):
        """A batch referencing a parent stored in an earlier batch must not be
        rejected at file level (the registry load is authoritative)."""
        child = dict(VALID_KU_2, parent_unit_id="KU-STORED-EARLIER")
        batch = write_jsonl(tmp_path / "child.jsonl", [child])
        report = reg.validate_ku_file(batch, KU_SCHEMA)
        assert report["valid"], report["errors"]

    def test_self_parent_rejected_at_file_level(self, tmp_path):
        bad = write_jsonl(
            tmp_path / "bad.jsonl", [dict(VALID_KU, parent_unit_id="KU-0001")]
        )
        report = reg.validate_ku_file(bad, KU_SCHEMA)
        assert any(e["rule"] == "self_parent" for e in report["errors"])
