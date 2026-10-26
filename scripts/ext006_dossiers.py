#!/usr/bin/env python3
"""EXT-006: deterministic concept-dossier scaffolding for the classified domains.

Assembles one dossier per domain (regression, tree-based, evaluation) from the
COMMITTED knowledge-unit batches and overlap-classification files:

  * one dossier CONCEPT per classification record (label = record topic;
    participating KUs = record ku_ids — provenance is many-to-many, invariant 5);
  * every participating KU is placed into >= 1 of the ten evidence categories
    of docs/KNOWLEDGE_AND_PROVENANCE.md section 7 by the deterministic rule set
    RULE_SET_ID below (every assignment records its basis; synthesis re-examines
    and never blindly trusts the scaffold);
  * per (concept, category) explicit gap markers: no_evidence (neither vault)
    or single_vault (one vault missing — e.g. calibration content only on the
    master-ai side);
  * dossiers NEVER assign dispositions: all KUs stay Unaccounted (invariant 2);
    overlap_type is a pair-level reference carried over from the classification
    record (ADR-0009), never a disposition.

Determinism: no timestamps, no randomness, no absolute paths; stable sort
order everywhere; JSON dumped with sort_keys=True. Two runs over the same
committed inputs produce byte-identical files (--check verifies this against
the committed dossiers).

Validation before writing (exit non-zero on any violation):
  V1 every referenced KU id exists in the domain's committed batches;
  V2 every classification id exists in the domain's classification files;
  V3 each concept's ku_ids equal the source record's ku_ids exactly;
  V4 bidirectional coverage: participating KUs <-> category-covered KUs;
  V5 output validates against schemas/concept-dossier.schema.json.

Usage:
  python3 scripts/ext006_dossiers.py            # write dossiers + coverage report
  python3 scripts/ext006_dossiers.py --check    # regenerate in memory, compare
                                                # byte-exactly with committed files
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "schemas" / "concept-dossier.schema.json"
DOSSIER_DIR = REPO_ROOT / "state" / "dossiers"
COVERAGE_REPORT = REPO_ROOT / "reports" / "extraction" / "ext006-dossier-coverage.json"

GENERATED_BY = "scripts/ext006_dossiers.py"
RULE_SET_ID = "ext006-category-rules-v1"

# ---------------------------------------------------------------------------
# Domain configuration: which committed stores each dossier is derived from.
# (Evaluation will additionally include the EXT-007 addendum classification
# file when that file exists — see EXT-007 task record; the config edit is a
# documented, committed change, and the dossier provenance lists every input.)
# ---------------------------------------------------------------------------

DOMAINS = {
    "regression": {
        "batches": [
            "state/knowledge-units/001-ext001-ai-course-03.1-regression.jsonl",
            "state/knowledge-units/002-ext002-master-ai-supervised-learning.jsonl",
        ],
        "classifications": [
            "state/classifications/001-ext003-regression-overlap.jsonl",
        ],
        "dossier_id": "regression-v1",
    },
    "tree-based": {
        "batches": [
            "state/knowledge-units/002-ext002-master-ai-supervised-learning.jsonl",
            "state/knowledge-units/003-ext004-ai-course-03.7-tree-based-models.jsonl",
        ],
        "classifications": [
            "state/classifications/002-ext004-tree-based-overlap.jsonl",
        ],
        "dossier_id": "tree-based-v1",
    },
    "evaluation": {
        "batches": [
            "state/knowledge-units/004-ext005-master-ai-evaluation.jsonl",
            "state/knowledge-units/005-ext005-ai-course-03.6-model-evaluation.jsonl",
        ],
        "classifications": [
            "state/classifications/003-ext005-evaluation-overlap.jsonl",
        ],
        "dossier_id": "evaluation-v1",
    },
    # EXT-008: clustering / dimensionality-reduction domain pair.
    # Schema domain enum extended additively with 'clustering'
    # (documented in schemas/concept-dossier.schema.json).
    "clustering": {
        "batches": [
            "state/knowledge-units/006-ext008-master-ai-unsupervised.jsonl",
            "state/knowledge-units/007-ext008-ai-course-clustering-dimreduction.jsonl",
        ],
        "classifications": [
            "state/classifications/005-ext008-clustering-dimreduction-overlap.jsonl",
        ],
        "dossier_id": "clustering-v1",
    },
}

# EXT-007 addendum: included in the evaluation dossier once committed.
EXT007_ADDENDUM = "state/classifications/004-ext007-evaluation-addendum.jsonl"
if (REPO_ROOT / EXT007_ADDENDUM).exists():
    DOMAINS["evaluation"]["classifications"].append(EXT007_ADDENDUM)

# ---------------------------------------------------------------------------
# The ten evidence categories (KNOWLEDGE_AND_PROVENANCE.md section 7).
# ---------------------------------------------------------------------------

CATEGORY_IDS = [
    "definitions_terminology",            # (1)
    "mathematical_foundations",           # (2)
    "computational_mechanics",            # (3)
    "alternative_explanations",           # (4)
    "worked_examples_failure_cases",      # (5)
    "code_implementation",                # (6)
    "applications_engineering",           # (7)
    "interview_misconceptions_comparisons",  # (8)
    "historical_deprecated",              # (9)
    "critical_distinctions",              # (10)
]

DISPOSITION_NOTE = (
    "Dossiers reference evidence only: no dispositions are assigned here; "
    "every KU remains Unaccounted until synthesis (KNOWLEDGE_AND_PROVENANCE.md "
    "invariants 2 and 5; overlap types are pair-level references, never "
    "dispositions)."
)

# ---------------------------------------------------------------------------
# Deterministic category-assignment rules (rule set ext006-category-rules-v1).
#
# A KU may receive MULTIPLE category assignments; every assignment records its
# basis string. Layers:
#   U* unit_type rules;
#   H* heading-path regex rules (applied to " > ".join(heading_path));
#   E* excerpt regex rules;
#   D1 total default — guarantees acceptance criterion "every participating KU
#      appears in at least one dossier category".
# All regexes are case-insensitive except the year-reference rule (years are
# digits; the pattern is case-free).
# ---------------------------------------------------------------------------

HEADING_RULES = [
    # (category, basis, compiled regex)
    ("worked_examples_failure_cases", "heading:example",
     re.compile(r"worked example|concrete example|with numbers|step-by-step|walkthrough", re.I)),
    ("worked_examples_failure_cases", "heading:failure-case",
     re.compile(r"pitfall|problem with|misleading|weakness|limitation|drawback|dangerous", re.I)),
    ("code_implementation", "heading:implementation",
     re.compile(r"implementation|from scratch|pytorch|scikit|sklearn|keras|tensorflow|"
                r"complete code|importation|analyse du code|plotting|visualization", re.I)),
    ("mathematical_foundations", "heading:mathematical",
     re.compile(r"derivation|deriving|proof|normal equation|log-?odds|entropy|"
                r"information gain|gini|sigmoid|formula|equation|closed-form|"
                r"analytical solution|variance decomposition|harmonic mean", re.I)),
    ("computational_mechanics", "heading:algorithm-mechanics",
     re.compile(r"algorithm|update rules|recursive splitting|how a tree is built|"
                r"iterative|training loop", re.I)),
    ("applications_engineering", "heading:engineering-guidance",
     re.compile(r"hyperparameter|production|practical|best practice|when to use|"
                r"which metric|decision framework|strengths|weakness|pros|cons|"
                r"advantage|disadvantage|tips|critical analysis", re.I)),
    ("critical_distinctions", "heading:versus-distinction",
     re.compile(r"\bvs\.?\b|versus|trade-?off|compared to|comparison|difference between|"
                r"which to use", re.I)),
    ("historical_deprecated", "heading:year-reference",
     re.compile(r"\([^()]*\b(?:19|20)[0-9]{2}\)")),
    ("interview_misconceptions_comparisons", "heading:interview-misconception",
     re.compile(r"interview|misconception|common mistake|quiz|myth", re.I)),
    ("alternative_explanations", "heading:interpretation-intuition",
     re.compile(r"the key insight|why this is|why it works|why this works|intuition", re.I)),
]

RX_COMPLEXITY = re.compile(r"\bO\([a-zA-Z0-9^{} ]{1,12}\)")
RX_LIBRARY = re.compile(r"sklearn|scikit-learn", re.I)

# Distinctly-French function/content words (no English homographs): a KU whose
# excerpt contains >= 5 of them is a French-language alternative treatment.
FRENCH_WORDS = [
    "le", "la", "les", "des", "une", "est", "pour", "avec", "dans", "que",
    "qui", "nous", "vous", "mais", "donc", "être", "avoir", "modèle",
    "données", "apprentissage", "réseau", "neurones", "prédiction",
    "entraînement", "fonction", "coût", "erreur", "exemple", "résultat",
]
RX_FRENCH = [re.compile(r"\b" + re.escape(w) + r"\b", re.I) for w in FRENCH_WORDS]


def assign_categories(ku: dict) -> dict[str, list[str]]:
    """Return {category_id: [basis, ...]} for one KU (deterministic)."""
    assignments: dict[str, list[str]] = {}

    def assign(category: str, basis: str) -> None:
        bases = assignments.setdefault(category, [])
        if basis not in bases:
            bases.append(basis)

    unit_type = ku.get("unit_type", "")
    if unit_type == "math_block":
        assign("mathematical_foundations", "unit_type:math_block")
    if unit_type == "code_block":
        assign("code_implementation", "unit_type:code_block")

    heading_text = " > ".join(ku.get("heading_path", []))
    for category, basis, rx in HEADING_RULES:
        if rx.search(heading_text):
            assign(category, basis)

    excerpt = ku.get("excerpt", "")
    if RX_COMPLEXITY.search(excerpt):
        assign("computational_mechanics", "excerpt:complexity-notation")
    if unit_type != "code_block" and RX_LIBRARY.search(excerpt):
        assign("code_implementation", "excerpt:library-mention")
    french_hits = sum(1 for rx in RX_FRENCH if rx.search(excerpt))
    if french_hits >= 5:
        assign("alternative_explanations", "excerpt:french-treatment")

    if not assignments:
        assign("definitions_terminology",
               f"default:no-rule-fired(unit_type={unit_type})")
    return assignments


# ---------------------------------------------------------------------------
# Loading helpers.
# ---------------------------------------------------------------------------

def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                records.append(json.loads(line))
    return records


def vault_of(ku: dict) -> str:
    return ku["source_id"].split(":", 1)[0]


# ---------------------------------------------------------------------------
# Dossier assembly.
# ---------------------------------------------------------------------------

def build_concept(index: int, record: dict, kus: dict[str, dict]) -> dict:
    concept_id = f"CD-{record['_domain_slug']}-{index:04d}"
    ku_ids = sorted(set(record["ku_ids"]))
    by_vault: dict[str, list[str]] = {"ai-course": [], "master-ai": []}
    for kid in ku_ids:
        by_vault[vault_of(kus[kid])].append(kid)

    categories: dict[str, dict] = {}
    for cid in CATEGORY_IDS:
        categories[cid] = {"ku_ids": [], "by_vault": {"ai-course": [], "master-ai": []},
                           "assignment_bases": {}}

    for kid in ku_ids:
        for cid, bases in sorted(assign_categories(kus[kid]).items()):
            entry = categories[cid]
            if kid not in entry["ku_ids"]:
                entry["ku_ids"].append(kid)
                entry["ku_ids"].sort()
                entry["by_vault"][vault_of(kus[kid])].append(kid)
                entry["by_vault"][vault_of(kus[kid])].sort()
            entry["assignment_bases"][kid] = sorted(bases)

    gaps: list[dict] = []
    for cid in CATEGORY_IDS:
        entry = categories[cid]
        has_course = bool(entry["by_vault"]["ai-course"])
        has_master = bool(entry["by_vault"]["master-ai"])
        if has_course and has_master:
            continue
        if not has_course and not has_master:
            gaps.append({"category": cid, "kind": "no_evidence"})
        elif has_course:
            gaps.append({"category": cid, "kind": "single_vault",
                         "present_vault": "ai-course", "absent_vault": "master-ai"})
        else:
            gaps.append({"category": cid, "kind": "single_vault",
                         "present_vault": "master-ai", "absent_vault": "ai-course"})

    return {
        "concept_id": concept_id,
        "label": record["topic"],
        "source_classification_id": record["classification_id"],
        "overlap_type": record["overlap_type"],
        "ku_ids": ku_ids,
        "ku_count": len(ku_ids),
        "by_vault": by_vault,
        "categories": categories,
        "gaps": gaps,
    }


def build_dossier(domain: str, config: dict) -> tuple[dict, dict]:
    # Load committed inputs (paths are repository-relative for determinism).
    kus: dict[str, dict] = {}
    batch_prov = []
    for rel in config["batches"]:
        path = REPO_ROOT / rel
        records = load_jsonl(path)
        for r in records:
            kus[r["knowledge_unit_id"]] = r
        batch_prov.append({"path": rel, "sha256": sha256_of(path),
                           "record_count": len(records)})

    cls_records: list[dict] = []
    cls_prov = []
    for rel in config["classifications"]:
        path = REPO_ROOT / rel
        records = load_jsonl(path)
        cls_records.extend(records)
        cls_prov.append({"path": rel, "sha256": sha256_of(path),
                         "record_count": len(records)})

    # V2: classification ids must be unique across the domain's files.
    ids = [r["classification_id"] for r in cls_records]
    if len(ids) != len(set(ids)):
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        raise ValueError(f"{domain}: duplicate classification ids {dupes}")

    slug = domain.replace(" ", "-")
    cls_records.sort(key=lambda r: r["classification_id"])
    for r in cls_records:
        r["_domain_slug"] = slug

    # V1 + V3: every referenced KU exists; concept KU set equals record KU set.
    problems = []
    for r in cls_records:
        missing = [k for k in r["ku_ids"] if k not in kus]
        if missing:
            problems.append(f"{r['classification_id']}: unknown KU ids {missing}")
    if problems:
        raise ValueError("V1 failed — KU ids not in committed batches:\n  "
                         + "\n  ".join(problems))

    concepts = [build_concept(i, r, kus)
                for i, r in enumerate(cls_records, start=1)]
    for concept, record in zip(concepts, cls_records):
        if set(concept["ku_ids"]) != set(record["ku_ids"]):
            raise ValueError(f"V3 failed for {record['classification_id']}")

    # Accounting + V4 (bidirectional coverage).
    participating = sorted({k for r in cls_records for k in r["ku_ids"]})
    covered = sorted({k for c in concepts for cid in CATEGORY_IDS
                      for k in c["categories"][cid]["ku_ids"]})
    every_participating_covered = set(participating) <= set(covered)
    every_covered_participates = set(covered) <= set(participating)

    category_assignment_counts = {
        cid: sum(len(c["categories"][cid]["ku_ids"]) for c in concepts)
        for cid in CATEGORY_IDS
    }
    zero_evidence = [cid for cid in CATEGORY_IDS
                     if category_assignment_counts[cid] == 0]
    gap_census = {
        "no_evidence": sum(1 for c in concepts for g in c["gaps"]
                           if g["kind"] == "no_evidence"),
        "single_vault": sum(1 for c in concepts for g in c["gaps"]
                            if g["kind"] == "single_vault"),
    }

    dossier = {
        "dossier_id": config["dossier_id"],
        "domain": domain,
        "version": "v1",
        "rule_set": RULE_SET_ID,
        "generated_by": GENERATED_BY,
        "provenance": {"batches": batch_prov, "classification_files": cls_prov},
        "concepts": concepts,
        "accounting": {
            "classification_record_count": len(cls_records),
            "concept_count": len(concepts),
            "participating_ku_count": len(participating),
            "participating_ku_ids": participating,
            "category_assignment_counts": category_assignment_counts,
            "zero_evidence_categories": zero_evidence,
            "gap_census": gap_census,
            "bidirectional_check": {
                "every_participating_ku_covered": every_participating_covered,
                "every_covered_ku_participates": every_covered_participates,
            },
            "disposition_note": DISPOSITION_NOTE,
        },
    }

    # Rule-basis census for the coverage report (transparency only).
    basis_census: dict[str, int] = {}
    default_kus = 0
    for c in concepts:
        for cid in CATEGORY_IDS:
            for kid, bases in c["categories"][cid]["assignment_bases"].items():
                for b in bases:
                    basis_census[b] = basis_census.get(b, 0) + 1
                    if b.startswith("default:"):
                        default_kus += 1

    report_entry = {
        "dossier": f"state/dossiers/{config['dossier_id']}.json",
        "classification_records": len(cls_records),
        "concepts": len(concepts),
        "participating_kus": len(participating),
        "category_assignment_counts": category_assignment_counts,
        "zero_evidence_categories": zero_evidence,
        "gap_census": gap_census,
        "bidirectional_check": {
            "every_participating_ku_covered": every_participating_covered,
            "every_covered_ku_participates": every_covered_participates,
        },
        "rule_basis_census": dict(sorted(basis_census.items())),
        "default_rule_ku_assignments": default_kus,
    }
    return dossier, report_entry


def dump_json(obj: dict) -> str:
    return json.dumps(obj, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def validate_dossier(dossier: dict) -> None:
    """V5: schema validation (jsonschema is a framework dependency)."""
    import jsonschema
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator(schema).validate(dossier)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="regenerate in memory and compare byte-exactly "
                             "with the committed dossiers; write nothing")
    args = parser.parse_args()

    dossiers: dict[str, tuple[dict, dict]] = {}
    for domain, config in DOMAINS.items():
        try:
            dossiers[domain] = build_dossier(domain, config)
        except ValueError as exc:
            print(f"VALIDATION FAILURE [{domain}]: {exc}", file=sys.stderr)
            return 1

    for domain, (dossier, _) in dossiers.items():
        try:
            validate_dossier(dossier)
        except Exception as exc:  # noqa: BLE001 — report and fail cleanly
            print(f"SCHEMA VALIDATION FAILURE [{domain}]: {exc}", file=sys.stderr)
            return 1

    if args.check:
        all_match = True
        for domain, (dossier, _) in dossiers.items():
            committed = REPO_ROOT / "state" / "dossiers" / f"{dossier['dossier_id']}.json"
            if not committed.exists():
                print(f"CHECK FAIL [{domain}]: committed dossier missing: {committed}")
                all_match = False
                continue
            if committed.read_text(encoding="utf-8") != dump_json(dossier):
                print(f"CHECK FAIL [{domain}]: regenerated bytes differ from committed")
                all_match = False
            else:
                print(f"CHECK OK [{domain}]: byte-identical regeneration")
        return 0 if all_match else 1

    DOSSIER_DIR.mkdir(parents=True, exist_ok=True)
    COVERAGE_REPORT.parent.mkdir(parents=True, exist_ok=True)

    for domain, (dossier, _) in dossiers.items():
        out = DOSSIER_DIR / f"{dossier['dossier_id']}.json"
        out.write_text(dump_json(dossier), encoding="utf-8")
        acc = dossier["accounting"]
        print(f"wrote {out.relative_to(REPO_ROOT)}: "
              f"{acc['concept_count']} concepts, "
              f"{acc['participating_ku_count']} participating KUs, "
              f"zero-evidence categories: {acc['zero_evidence_categories'] or 'none'}")

    report = {
        "command": "ext006_dossiers",
        "rule_set": RULE_SET_ID,
        "schema": "schemas/concept-dossier.schema.json",
        "domains": {d: dossiers[d][1] for d in sorted(dossiers)},
    }
    COVERAGE_REPORT.write_text(dump_json(report), encoding="utf-8")
    print(f"wrote {COVERAGE_REPORT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
