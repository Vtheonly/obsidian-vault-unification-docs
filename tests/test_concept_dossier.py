"""Integration tests: concept-dossier scaffolding (EXT-006).

These tests intentionally couple to the committed repository state files so
that manual drift of the derived dossiers away from the committed batches and
classifications is caught by the test suite itself. Dossiers are a derived
view: they must keep regenerating byte-identically from committed stores.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import jsonschema

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "concept-dossier.schema.json"
DOSSIER_DIR = REPO_ROOT / "state" / "dossiers"
DOSSIER_FILES = [
    DOSSIER_DIR / "regression-v1.json",
    DOSSIER_DIR / "tree-based-v1.json",
    DOSSIER_DIR / "evaluation-v1.json",
]
CATEGORY_IDS = [
    "definitions_terminology",
    "mathematical_foundations",
    "computational_mechanics",
    "alternative_explanations",
    "worked_examples_failure_cases",
    "code_implementation",
    "applications_engineering",
    "interview_misconceptions_comparisons",
    "historical_deprecated",
    "critical_distinctions",
]


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _iter_keys(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            yield key
            yield from _iter_keys(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from _iter_keys(item)


class TestConceptDossierSchema:
    def test_schema_is_valid_2020_12_with_ten_categories(self):
        schema = _load(SCHEMA_PATH)
        jsonschema.Draft202012Validator.check_schema(schema)
        assert schema["$defs"]["category_id"]["enum"] == CATEGORY_IDS
        required_categories = schema["$defs"]["concept"]["properties"][
            "categories"
        ]["required"]
        assert sorted(required_categories) == sorted(CATEGORY_IDS)

    def test_schema_forbids_disposition_fields(self):
        schema = _load(SCHEMA_PATH)
        # No concept/dossier property is named disposition, and accounting
        # carries the standing note that dossiers never assign dispositions.
        concept_props = schema["$defs"]["concept"]["properties"]
        assert "disposition" not in concept_props
        top_props = schema["properties"]
        assert "disposition" not in top_props


class TestCommittedDossiers:
    def test_all_three_domain_dossiers_exist_and_validate(self):
        schema = _load(SCHEMA_PATH)
        validator = jsonschema.Draft202012Validator(schema)
        for path in DOSSIER_FILES:
            assert path.exists(), f"missing dossier {path}"
            validator.validate(_load(path))

    def test_dossiers_regenerate_byte_identically(self):
        result = subprocess.run(
            [sys.executable, "scripts/ext006_dossiers.py", "--check"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, (
            f"--check failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

    def test_every_referenced_ku_id_exists_in_committed_batches(self):
        batch_kus = set()
        for path in sorted((REPO_ROOT / "state" / "knowledge-units").glob("*.jsonl")):
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    batch_kus.add(json.loads(line)["knowledge_unit_id"])
        for path in DOSSIER_FILES:
            dossier = _load(path)
            for concept in dossier["concepts"]:
                unknown = [k for k in concept["ku_ids"] if k not in batch_kus]
                assert not unknown, (
                    f"{path.name}: {concept['concept_id']} references "
                    f"unknown KU ids {unknown}"
                )

    def test_dossiers_never_assign_dispositions(self):
        for path in DOSSIER_FILES:
            dossier = _load(path)
            keys = set(_iter_keys(dossier))
            assert "disposition" not in keys, (
                f"{path.name} contains a disposition field"
            )
            note = dossier["accounting"]["disposition_note"]
            assert note.startswith("Dossiers reference evidence only")
            bidirectional = dossier["accounting"]["bidirectional_check"]
            assert bidirectional["every_participating_ku_covered"] is True
            assert bidirectional["every_covered_ku_participates"] is True

    def test_zero_evidence_categories_are_explicitly_marked(self):
        for path in DOSSIER_FILES:
            dossier = _load(path)
            counts = dossier["accounting"]["category_assignment_counts"]
            zero = dossier["accounting"]["zero_evidence_categories"]
            derived_zero = sorted(c for c, n in counts.items() if n == 0)
            assert sorted(zero) == derived_zero
            # every zero-evidence category is also gap-marked in every concept
            for concept in dossier["concepts"]:
                gap_cats = {g["category"] for g in concept["gaps"]
                            if g["kind"] == "no_evidence"}
                empty_cats = {c for c in CATEGORY_IDS
                              if not concept["categories"][c]["ku_ids"]}
                assert gap_cats == empty_cats, (
                    f"{path.name}: {concept['concept_id']} gap markers "
                    f"do not match empty categories"
                )

    def test_coverage_report_matches_dossiers(self):
        report = _load(REPO_ROOT / "reports" / "extraction" /
                       "ext006-dossier-coverage.json")
        for domain, entry in report["domains"].items():
            dossier = _load(DOSSIER_DIR / f"{domain.replace(' ', '-')}-v1.json")
            acc = dossier["accounting"]
            assert entry["concepts"] == acc["concept_count"]
            assert entry["participating_kus"] == acc["participating_ku_count"]
            assert entry["classification_records"] == acc[
                "classification_record_count"
            ]
            assert entry["category_assignment_counts"] == acc[
                "category_assignment_counts"
            ]
            assert entry["zero_evidence_categories"] == acc[
                "zero_evidence_categories"
            ]
