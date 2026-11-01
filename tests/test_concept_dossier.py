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
    DOSSIER_DIR / "clustering-v1.json",
    DOSSIER_DIR / "generalization-v1.json",
    DOSSIER_DIR / "training-stability-v1.json",
]
V2_DOSSIER_FILES = [
    DOSSIER_DIR / "regression-v2.json",
    DOSSIER_DIR / "tree-based-v2.json",
    DOSSIER_DIR / "evaluation-v2.json",
    DOSSIER_DIR / "clustering-v2.json",
    DOSSIER_DIR / "generalization-v2.json",
    DOSSIER_DIR / "training-stability-v2.json",
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
    def test_all_domain_dossiers_exist_and_validate(self):
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
        for version in ("v1", "v2"):
            for domain, entry in report["versions"][version]["domains"].items():
                dossier = _load(DOSSIER_DIR / f"{domain.replace(' ', '-')}-{version}.json")
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


class TestV2Dossiers:
    """Session-19 dossier-v2 acceptance (handoff criteria)."""

    def test_all_v2_dossiers_exist_and_validate(self):
        schema = _load(SCHEMA_PATH)
        validator = jsonschema.Draft202012Validator(schema)
        for path in V2_DOSSIER_FILES:
            assert path.exists(), f"missing dossier {path}"
            dossier = _load(path)
            assert dossier["version"] == "v2"
            assert dossier["dossier_id"].endswith("-v2")
            validator.validate(dossier)

    def test_v2_regenerates_byte_identically(self):
        result = subprocess.run(
            [sys.executable, "scripts/ext006_dossiers.py", "--check"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert result.returncode == 0, (
            f"--check failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert result.stdout.count("CHECK OK [v1/") == 6
        assert result.stdout.count("CHECK OK [v2/") == 6

    def test_every_extension_ku_appears_in_at_least_one_v2_concept(self):
        ext_files = {
            "regression": REPO_ROOT / "state/classifications/009-disc002-dext-regression-extension.jsonl",
            "tree-based": REPO_ROOT / "state/classifications/010-disc002-dext-tree-extension.jsonl",
            "evaluation": REPO_ROOT / "state/classifications/011-disc002-dext-evaluation-extension.jsonl",
            "clustering": REPO_ROOT / "state/classifications/012-disc002-dext-clustering-extension.jsonl",
            "generalization": REPO_ROOT / "state/classifications/013-disc002-dext-generalization-extension.jsonl",
            "training-stability": REPO_ROOT / "state/classifications/014-disc002-dext-training-stability-extension.jsonl",
        }
        for domain, ext_path in ext_files.items():
            ext_kus = {
                kid
                for line in ext_path.read_text(encoding="utf-8").splitlines()
                if line.strip()
                for kid in json.loads(line)["ku_ids"]
            }
            dossier = _load(DOSSIER_DIR / f"{domain.replace(' ', '-')}-v2.json")
            v2_kus = {
                kid
                for concept in dossier["concepts"]
                for kid in concept["ku_ids"]
            }
            missing = ext_kus - v2_kus
            assert not missing, (
                f"{domain}: extension KUs missing from v2 concepts: "
                f"{sorted(missing)[:10]}"
            )

    def test_all_514_original_participating_kus_still_present(self):
        total_v1 = 0
        for path in DOSSIER_FILES:
            v1 = _load(path)
            v2 = _load(DOSSIER_DIR / v1["dossier_id"].replace("-v1", "-v2.json"))
            v1_kus = set(v1["accounting"]["participating_ku_ids"])
            v2_kus = set(v2["accounting"]["participating_ku_ids"])
            assert v1_kus <= v2_kus, (
                f"{path.name}: v1 participating KUs lost in v2"
            )
            total_v1 += len(v1_kus)
        assert total_v1 == 514, total_v1

    def test_v2_concept_counts_match_classification_records(self):
        expected = {
            "regression": (14, 33, 47),
            "tree-based": (28, 41, 69),
            "evaluation": (33, 49, 82),
            "clustering": (27, 40, 67),
            "generalization": (26, 47, 73),
            "training-stability": (36, 84, 120),
        }
        for domain, (v1_n, ext_n, v2_n) in expected.items():
            v2 = _load(DOSSIER_DIR / f"{domain.replace(' ', '-')}-v2.json")
            acc = v2["accounting"]
            assert acc["concept_count"] == v2_n, domain
            assert acc["classification_record_count"] == v2_n, domain
            report = _load(REPO_ROOT / "reports" / "extraction" /
                           "ext006-dossier-coverage.json")
            per_domain = report["versions"]["v2"]["acceptance"]["per_domain"][domain]
            assert per_domain["all_v1_participating_present_in_v2"] is True
            assert per_domain["all_extension_kus_covered"] is True

    def test_single_ku_extension_concepts_are_represented(self):
        """23 extension records carry a single KU (ADR-0013) — they must
        appear as concepts, not be dropped or merged."""
        single_ku_ids = [
            "DX-disc002-s18-regression-0008",
            "DX-disc002-s18-tree-0002",
            "DX-disc002-s18-evaluation-0019",
            "DX-disc002-s18-clustering-0016",
            "DX-disc002-s18-generalization-0017",
            "DX-disc002-s18-training-stability-0020",
        ]
        found = 0
        for path in V2_DOSSIER_FILES:
            dossier = _load(path)
            for concept in dossier["concepts"]:
                if concept["source_classification_id"] in single_ku_ids:
                    assert concept["ku_count"] == 1
                    found += 1
        assert found == len(single_ku_ids), found

    def test_v2_dossier_provenance_lists_extension_inputs(self):
        for path in V2_DOSSIER_FILES:
            dossier = _load(path)
            cls_files = [
                entry["path"] for entry in dossier["provenance"]["classification_files"]
            ]
            assert any("-dext-" in p for p in cls_files), path.name
            batch_files = [
                entry["path"] for entry in dossier["provenance"]["batches"]
            ]
            regen = [p for p in batch_files if "-regen001-" in p]
            assert len(regen) == 59, f"{path.name}: {len(regen)} regen batches"
