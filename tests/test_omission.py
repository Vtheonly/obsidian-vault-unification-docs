"""CAP-012 tests: omission-detection pilot and reusable output auditor.

The pilot is the hard gate before large-scale synthesis, so these tests
exercise exactly the acceptance contract of TOOLING_FRAMEWORK.md section 9
and VERIFICATION_SPECIFICATION.md section 6:

- the clean baseline must audit with ZERO findings (no false positives);
- every planted defect must be detected AND localized to its expected KU
  and destination note (zero false negatives);
- the pilot must honestly FAIL when a defect is not detectable;
- fixture sources and the real source vaults must never be modified.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from vault_unification import omission
from vault_unification import registry as registry_mod
from vault_unification.omission import (
    DEFECTS,
    DEFECT_IDS,
    AuditError,
    apply_mutation,
    audit_output,
    build_fixture,
    run_pilot,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def fixture_dir(tmp_path_factory) -> dict:
    """One shared fixture build for the whole module (read-only afterwards)."""
    return build_fixture(tmp_path_factory.mktemp("omission-fixture"))


@pytest.fixture(scope="module")
def baseline_audit(fixture_dir) -> dict:
    return audit_output(
        fixture_dir["sources_root"],
        fixture_dir["output_root"],
        fixture_dir["ku_batch_path"],
        accepted_manifest_path=fixture_dir["accepted_manifest_path"],
    )


def _load_records(fixture_dir: dict) -> list[dict]:
    entries, _ = omission.load_jsonl_records(fixture_dir["ku_batch_path"])
    return [e["record"] for e in entries]


# ---------------------------------------------------------------------------
# fixture builder
# ---------------------------------------------------------------------------


class TestFixtureBuilder:
    def test_creates_expected_layout(self, fixture_dir):
        root = Path(fixture_dir["sources_root"]).parent
        assert (root / "sources" / "vault-a" / "backpropagation.md").is_file()
        assert (root / "sources" / "vault-b" / "backpropagation.md").is_file()
        assert (root / "output-baseline" / "Neural Networks" / "Backpropagation.md").is_file()
        assert len(list((root / "output-baseline").rglob("*.md"))) == 4
        assert Path(fixture_dir["ku_batch_path"]).is_file()
        assert Path(fixture_dir["accepted_manifest_path"]).is_file()
        assert (root / "fixture-manifest.json").is_file()

    def test_fixture_is_deterministic(self, tmp_path):
        first = build_fixture(tmp_path / "a")
        second = build_fixture(tmp_path / "b")
        assert first["ku_ids"] == second["ku_ids"]
        assert first["source_files"] == second["source_files"]
        for relpath in ("sources/vault-a/backpropagation.md", "sources/vault-b/backpropagation.md"):
            assert (tmp_path / "a" / relpath).read_bytes() == (tmp_path / "b" / relpath).read_bytes()

    def test_dest_inside_protected_root_refused(self, tmp_path):
        protected = tmp_path / "protected"
        protected.mkdir()
        with pytest.raises(Exception):
            build_fixture(protected / "inside" / "fixture", protected_roots=[protected])
        assert not (protected / "inside").exists()

    def test_ku_batch_validates_against_schema(self, fixture_dir):
        report = registry_mod.validate_ku_file(
            fixture_dir["ku_batch_path"],
            REPO_ROOT / "schemas" / "knowledge-unit.schema.json",
        )
        assert report["valid"], report["errors"]

    def test_ku_records_carry_stable_ids_and_destinations(self, fixture_dir):
        records = _load_records(fixture_dir)
        assert len(records) == 11
        for record in records:
            assert record["knowledge_unit_id"].startswith("KU-")
            assert record["disposition"] != "Unaccounted"
            assert record["destinations"], record["knowledge_unit_id"]
            assert record["excerpt"]


# ---------------------------------------------------------------------------
# auditor on the clean baseline (false-positive gate) and unit checks
# ---------------------------------------------------------------------------


class TestAuditor:
    def test_clean_baseline_zero_findings(self, baseline_audit):
        assert baseline_audit["valid"] is True
        assert baseline_audit["findings"] == [], json.dumps(
            baseline_audit["findings"], indent=1
        )
        assert baseline_audit["stats"]["kus_total"] == 11

    def test_missing_output_root_raises(self, fixture_dir, tmp_path):
        with pytest.raises(AuditError):
            audit_output(
                fixture_dir["sources_root"], tmp_path / "nope", fixture_dir["ku_batch_path"]
            )

    def test_corrupt_ku_batch_reported(self, fixture_dir, tmp_path):
        bad_batch = tmp_path / "bad.jsonl"
        bad_batch.write_text("{not json}\n", encoding="utf-8")
        result = audit_output(
            fixture_dir["sources_root"], fixture_dir["output_root"], bad_batch
        )
        assert result["valid"] is False
        assert any(f["category"] == "ku-batch-invalid" for f in result["findings"])

    def test_unaccounted_disposition_flagged(self, fixture_dir, tmp_path):
        records = _load_records(fixture_dir)
        records[0]["disposition"] = "Unaccounted"
        batch = tmp_path / "unaccounted.jsonl"
        batch.write_text(
            "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records),
            encoding="utf-8",
        )
        result = audit_output(fixture_dir["sources_root"], fixture_dir["output_root"], batch)
        assert result["valid"] is False
        assert any(f["category"] == "unaccounted-unit" for f in result["findings"])

    def test_missing_destination_file_flagged(self, fixture_dir, tmp_path):
        records = _load_records(fixture_dir)
        records[0]["destinations"] = [{"path": "Neural Networks/Gone.md", "heading": None}]
        batch = tmp_path / "gone-dest.jsonl"
        batch.write_text(
            "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records),
            encoding="utf-8",
        )
        result = audit_output(fixture_dir["sources_root"], fixture_dir["output_root"], batch)
        assert any(f["category"] == "destination-file-missing" for f in result["findings"])

    def test_missing_destination_heading_flagged(self, fixture_dir, tmp_path):
        records = _load_records(fixture_dir)
        records[0]["destinations"] = [
            {"path": "Neural Networks/Backpropagation.md", "heading": "9. Does Not Exist"}
        ]
        batch = tmp_path / "gone-heading.jsonl"
        batch.write_text(
            "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records),
            encoding="utf-8",
        )
        result = audit_output(fixture_dir["sources_root"], fixture_dir["output_root"], batch)
        assert any(f["category"] == "destination-heading-missing" for f in result["findings"])

    def test_drift_against_accepted_manifest_detected(self, fixture_dir, tmp_path):
        drifted = tmp_path / "drifted"
        shutil.copytree(fixture_dir["output_root"], drifted)
        target = drifted / "Neural Networks" / "Backpropagation.md"
        target.write_text(target.read_text(encoding="utf-8") + "\nsilent late edit\n", encoding="utf-8")
        result = audit_output(
            fixture_dir["sources_root"],
            drifted,
            fixture_dir["ku_batch_path"],
            accepted_manifest_path=fixture_dir["accepted_manifest_path"],
        )
        assert result["valid"] is False
        assert any(f["category"] == "accepted-file-changed" for f in result["findings"])
        changed = [f for f in result["findings"] if f["category"] == "accepted-file-changed"]
        assert changed[0]["ku_ids"], "drift findings must link stable KU ids"

    def test_marker_machinery_units(self):
        assert omission._norm_ws("  a \n b  c ") == "a b c"
        assert omission._term_tokens("Values, value. values; VALUE!") == [
            "values",
            "value",
            "values",
            "value",
        ]
        math = omission._math_markers("see $L = (a - y)^2$ and\n$$\nE = mc^2\n$$")
        assert "L = (a - y)^2" in math
        assert "E = mc^2" in math
        flipped = omission._math_markers("see $L = (a + y)^2$")
        assert "L = (a - y)^2" not in flipped
        assert omission._prose_word_count(["- bullet one", "- bullet two", "", "```", "code", "```"]) == 0
        assert omission._prose_word_count(["A full prose sentence right here."]) == 6


# ---------------------------------------------------------------------------
# every planted defect: detection + localization (zero false negatives)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("defect", DEFECTS, ids=DEFECT_IDS)
def test_defect_detected_and_localized(fixture_dir, baseline_audit, tmp_path, defect):
    baseline_keys = {omission._finding_key(f) for f in baseline_audit["findings"]}
    mutated = tmp_path / defect["defect_id"] / "output"
    description = apply_mutation(fixture_dir["output_root"], mutated, defect["defect_id"])
    assert description
    result = audit_output(
        fixture_dir["sources_root"],
        mutated,
        fixture_dir["ku_batch_path"],
        accepted_manifest_path=(
            fixture_dir["accepted_manifest_path"] if defect["regression"] else None
        ),
    )
    new_findings = [f for f in result["findings"] if omission._finding_key(f) not in baseline_keys]
    assert new_findings, f"{defect['defect_id']} was NOT detected"

    records = _load_records(fixture_dir)
    expected_kus = omission._resolve_expected_kus(records, defect["expected_ku"])
    assert any(set(f["ku_ids"]) & set(expected_kus) for f in new_findings), (
        f"{defect['defect_id']} detected but not localized to expected KU {expected_kus}: "
        + json.dumps([f["ku_ids"] for f in new_findings])
    )
    assert any(
        f["destination"]["path"] == defect["expected_note"] for f in new_findings
    ), f"{defect['defect_id']} detected but not localized to the expected note"


# ---------------------------------------------------------------------------
# pilot orchestration
# ---------------------------------------------------------------------------


class TestPilot:
    def test_pilot_passes_all_criteria(self, tmp_path):
        report = run_pilot(tmp_path / "pilot")
        assert report["verdict"]["pass"] is True, json.dumps(report["verdict"], indent=1)
        assert report["summary"]["detection_rate"] == "12/12"
        assert report["summary"]["localization_rate"] == "12/12"
        assert report["summary"]["false_positives_on_clean_baseline"] == 0
        assert report["summary"]["false_negatives"] == []
        assert report["source_immutability"]["sources_unchanged_during_pilot"] is True

    def test_pilot_reports_limitations(self, tmp_path):
        report = run_pilot(tmp_path / "pilot-lims")
        assert report["limitations"], "pilot must document its limitations explicitly"

    def test_pilot_fails_when_defect_undetectable(self, tmp_path, monkeypatch):
        """Honesty: an invisible mutation must FAIL the pilot, not pass it."""

        def _mut_invisible(root: Path) -> str:
            path = root / "Neural Networks" / "Backpropagation.md"
            text = path.read_text(encoding="utf-8")
            # change only a common word no marker or check covers
            path.write_text(
                text.replace("which is what makes the algorithm", "which is what renders the algorithm"),
                encoding="utf-8",
            )
            return "replaced one common word with a synonym (invisible to all checks)"

        fake_defect = {
            "defect_id": "DX99",
            "category": "undetectable-paraphrase",
            "expected_detector": "none (must fail the pilot)",
            "regression": False,
            "expected_note": omission.MAIN_NOTE_RELPATH,
            "expected_ku": ("SRC-FIXTURE-VA", "Chain Rule Foundation"),
            "mutate": _mut_invisible,
        }
        monkeypatch.setattr(omission, "DEFECTS", DEFECTS + [fake_defect])
        report = run_pilot(tmp_path / "pilot-honesty")
        assert report["verdict"]["pass"] is False
        assert "DX99" in str(report["verdict"]["failed_criteria"])
        assert report["summary"]["defects_total"] == 13

    def test_unknown_defect_id_rejected(self, fixture_dir, tmp_path):
        with pytest.raises(ValueError):
            apply_mutation(fixture_dir["output_root"], tmp_path / "x", "D99")

    def test_mutations_never_touch_baseline(self, fixture_dir, tmp_path):
        baseline_main = Path(fixture_dir["output_root"]) / "Neural Networks" / "Backpropagation.md"
        before = baseline_main.read_bytes()
        for defect_id in DEFECT_IDS:
            apply_mutation(fixture_dir["output_root"], tmp_path / defect_id, defect_id)
        after = baseline_main.read_bytes()
        assert before == after
