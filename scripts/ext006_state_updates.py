#!/usr/bin/env python3
"""EXT-006 state updates: task-queue completion, current-state, checkpoint.

Run AFTER the EXT-006 work is verified, BEFORE the work commit. The work
commit hash is recorded in a follow-up state commit (convention since
EXT-001).

Idempotent: safe to re-run; refuses to run if EXT-006 is already completed.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TASK_QUEUE = REPO / "state" / "task-queue.jsonl"
CURRENT_STATE = REPO / "state" / "current-state.json"
CHECKPOINT = REPO / "state" / "checkpoints" / "checkpoint-2026-10-27-ext-006.json"

TASK_ID = "EXT-006"
DATE = "2026-10-27"

TESTS_RUN = [
    {
        "step": "startup protocol",
        "command": "vu selftest + pytest + verify-manifest both vaults + registry rebuild",
        "result": "selftest exit 0; 407/407; both vaults unchanged (333 + 276); "
                  "registry rebuild valid (775 KUs, 71 classifications, 0 errors/warnings)",
        "evidence": "reports/extraction/ext006-kureg-init.json + ext006-kureg-load-*.json + "
                    "ext006-kureg-apply-*.json + ext006-kureg-validate.json + "
                    "ext006-immutable-start-{master-ai,ai-course}.json",
    },
    {
        "step": "dossier assembly",
        "command": "python3 scripts/ext006_dossiers.py (+ double run for determinism)",
        "result": "exit 0; 3 dossiers: regression-v1 (14 concepts, 61 KUs), "
                  "tree-based-v1 (28 concepts, 82 KUs), evaluation-v1 (29 concepts, "
                  "91 KUs); 234 participating KUs total = every classified KU; "
                  "double-run byte-identical; --check byte-identical vs committed",
        "evidence": "reports/extraction/ext006-dossier-coverage.json + ext006-determinism.txt",
    },
    {
        "step": "schema + committed-state integration tests",
        "command": "python3 -m pytest tests/test_concept_dossier.py -v",
        "result": "8/8 passed (schema self-validates with ten categories; committed "
                  "dossiers validate; byte-identical regeneration via --check; KU ids "
                  "exist in batches; no disposition fields; gap markers match empty "
                  "categories; coverage report consistent)",
        "evidence": "reports/extraction/ext006-pytest-report.json (suite total 415/415)",
    },
    {
        "step": "full test suite + capabilities",
        "command": "python3 -m pytest tests -q ; vu capabilities --verify",
        "result": "415 passed, 0 failed, 0 skipped (407 prior + 8 new dossier tests); "
                  "16 implemented-and-tested, 1 planned (CAP-014)",
        "evidence": "reports/extraction/ext006-pytest-report.json + ext006-capabilities.json",
    },
    {
        "step": "source immutability after all operations",
        "command": "vu verify-manifest both vaults",
        "result": "exit 0 x2; 333 + 276 unchanged, 0 added/removed/changed",
        "evidence": "reports/extraction/ext006-immutable-after-{master-ai,ai-course}.json",
    },
]

NOTES = (
    "Scope executed exactly as recorded. Concept-dossier scaffolding built for the "
    "three classified domains per docs/KNOWLEDGE_AND_PROVENANCE.md section 7. "
    "schemas/concept-dossier.schema.json (draft 2020-12; ten fixed evidence "
    "categories; no disposition fields anywhere). scripts/ext006_dossiers.py "
    "assembles one dossier per domain deterministically: one CONCEPT per "
    "classification record (label = topic; KUs = record ku_ids), each participating "
    "KU placed into >= 1 of the ten categories by rule set ext006-category-rules-v1 "
    "(unit_type rules: math_block -> mathematical_foundations, code_block -> "
    "code_implementation; heading-path keyword rules; excerpt rules: complexity "
    "notation O(...), library mention sklearn/scikit-learn, French-language "
    "alternative treatment >= 5 distinct French words; total default "
    "definitions_terminology), every assignment records its basis, per "
    "(concept, category) explicit gap markers (no_evidence / single_vault — e.g. "
    "calibration definitions present only on the master-ai side in CD-evaluation-0025). "
    "Dossiers: regression-v1 14 concepts / 61 KUs; tree-based-v1 28 concepts / 82 "
    "KUs; evaluation-v1 29 concepts / 91 KUs; 234 participating KUs total, "
    "bidirectional coverage verified both directions; zero-evidence categories "
    "explicit (interview_misconceptions_comparisons in all three domains; "
    "historical_deprecated in regression and evaluation; computational_mechanics "
    "and alternative_explanations in evaluation). Dossiers are a derived view: "
    "registry NOT reloaded (775 KUs, 71 classifications, all KUs Unaccounted — no "
    "dispositions assigned, overlap types carried as pair-level references only). "
    "Validation before writing: every referenced KU id exists in committed batches "
    "(V1), every classification id exists and is unique (V2), concept KU set equals "
    "record KU set (V3), bidirectional coverage (V4), schema validation (V5). "
    "8 new integration tests (tests/test_concept_dossier.py) guard the committed "
    "dossiers against manual drift: suite now 415/415. EXT-007 (evaluation "
    "classification addendum C1-C4) remains queued and ready; the dossier config "
    "auto-includes state/classifications/004-ext007-evaluation-addendum.jsonl once "
    "that file exists, so the evaluation dossier will be regenerated (same v1, "
    "updated provenance) as part of EXT-007's commit."
)


def main() -> int:
    # 1. Task queue: EXT-006 ready -> completed with tests_run evidence.
    lines = TASK_QUEUE.read_text(encoding="utf-8").splitlines()
    out, seen = [], False
    for line in lines:
        if not line.strip():
            out.append(line)
            continue
        rec = json.loads(line)
        if rec.get("task_id") == TASK_ID:
            if rec.get("status") == "completed":
                print(f"{TASK_ID} already completed — refusing to re-run",
                      file=sys.stderr)
                return 1
            rec["status"] = "completed"
            rec["tests_run"] = TESTS_RUN
            rec["notes"] = NOTES
            seen = True
        out.append(json.dumps(rec, ensure_ascii=False))
    if not seen:
        print(f"{TASK_ID} record not found", file=sys.stderr)
        return 1
    TASK_QUEUE.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"task-queue: {TASK_ID} -> completed with tests_run evidence")

    # 2. Current state.
    cs = json.loads(CURRENT_STATE.read_text(encoding="utf-8"))
    cs["current_task_id"] = "EXT-007"
    cs["last_verified_checkpoint"] = str(CHECKPOINT.relative_to(REPO))
    cs["notes"] = (
        "EXT-006 completed 2026-10-27 (concept-dossier scaffolding for the three "
        "classified domains: schema + deterministic generator + 3 dossiers with "
        "71 concepts over all 234 classified KUs, explicit per-category gap "
        "markers, byte-identical regeneration; 8 new tests, suite 415/415; "
        "registry untouched, all KUs remain Unaccounted). "
        "EXT-007 ready: evaluation classification addendum (candidates C1-C4 from "
        "reports/extraction/ext005-independent-confirmation.md section 3) — "
        "adopt/reject with rationale, independent review, new append-only file "
        "004-ext007-evaluation-addendum.jsonl, evaluation dossier regeneration. "
        "PUSH BLOCKER STILL OPEN: local main is 4+ commits ahead of origin/main "
        "(EXT-005 verification session commits); user will push a provided zip "
        "bundle."
    )
    kr = cs.setdefault("knowledge_registry", {})
    kr["records"] = 775
    kr["dossiers"] = {
        "store": "state/dossiers/ (derived view; regenerates via scripts/ext006_dossiers.py)",
        "schema": "schemas/concept-dossier.schema.json",
        "files": {
            "regression-v1.json": "14 concepts / 61 KUs (from 001-ext003)",
            "tree-based-v1.json": "28 concepts / 82 KUs (from 002-ext004)",
            "evaluation-v1.json": "29 concepts / 91 KUs (from 003-ext005; will "
                                  "re-generate with EXT-007 addendum records when "
                                  "committed)",
        },
        "concepts_total": 71,
        "participating_kus_total": 234,
        "rule_set": "ext006-category-rules-v1 (documented in scripts/ext006_dossiers.py)",
        "dispositions_assigned": False,
    }
    CURRENT_STATE.write_text(
        json.dumps(cs, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("current-state: current_task_id=EXT-007, dossier accounting added")

    # 3. Checkpoint.
    checkpoint = {
        "checkpoint_id": f"CHK-2026-10-27-EXT-006",
        "created_utc": "2026-10-27T00:00:00+00:00",
        "stage": "extraction",
        "task_id": TASK_ID,
        "task_status": "completed",
        "last_verified_state": {
            "framework_version": "0.5.0 (unchanged in EXT-006; no code changes)",
            "test_result": "415 passed, 0 failed, 0 skipped (407 prior + 8 new)",
            "test_evidence": "reports/extraction/ext006-pytest-report.json",
            "capabilities_evidence": "reports/extraction/ext006-capabilities.json "
                                     "(16 implemented-and-tested, 1 planned: CAP-014)",
            "registry_store": "state/knowledge-units/ (775 records in 5 committed "
                              "batches, unedited)",
            "derived_index": "state/registries/kuregistry.db (rebuilt and verified "
                             "at startup: init --force + load x5 + apply-overlap x3; "
                             "kureg-validate valid, 0 errors/warnings)",
            "classifications": {
                "paths": [
                    "state/classifications/001-ext003-regression-overlap.jsonl (14 records)",
                    "state/classifications/002-ext004-tree-based-overlap.jsonl (28 records)",
                    "state/classifications/003-ext005-evaluation-overlap.jsonl (29 records)",
                ],
                "total": 71,
                "participating_kus_total": 234,
            },
            "dossiers": {
                "schema": "schemas/concept-dossier.schema.json (draft 2020-12)",
                "generator": "scripts/ext006_dossiers.py (rule set "
                             "ext006-category-rules-v1)",
                "files": {
                    "state/dossiers/regression-v1.json": "14 concepts, 61 KUs",
                    "state/dossiers/tree-based-v1.json": "28 concepts, 82 KUs",
                    "state/dossiers/evaluation-v1.json": "29 concepts, 91 KUs",
                },
                "concepts_total": 71,
                "determinism": "double-run byte-identical + --check byte-identical "
                               "vs committed (reports/extraction/ext006-determinism.txt)",
                "gap_markers": "per (concept, category): no_evidence or single_vault",
                "dispositions_assigned": False,
            },
            "source_immutability": "verify-manifest exit 0 x4 (startup + after, both "
                                   "vaults); 333 + 276 unchanged",
            "findings_open": ["F-0001", "F-0002", "F-0003", "F-0007", "F-0008"],
            "findings_resolved": ["F-0004", "F-0005", "F-0006"],
        },
        "acceptance_criteria_met": [
            "Every dossier category lists KU ids that exist in committed batches "
            "(machine-verified V1) or an explicit empty-gap marker",
            "Every participating KU from the domain's classification records "
            "appears in at least one dossier category (bidirectional coverage V4, "
            "both directions asserted)",
            "Dossier schema valid (V5); dossiers regenerate byte-identically from "
            "committed stores (double-run cmp + --check + integration test)",
            "Overlap types NOT collapsed into dispositions (no disposition fields; "
            "registry untouched; all 775 KUs remain Unaccounted)",
            "Sources unchanged before/after; committed batches and classifications "
            "unedited (git status shows only new files)",
            "Full test suite passes (415/415); capabilities --verify passes (16+1)",
        ],
        "next_task": "EXT-007 (queued, ready): evaluation classification addendum — "
                     "adjudicate candidates C1-C4 with recorded adopt/reject "
                     "rationale; adopted records go to NEW append-only file "
                     "state/classifications/004-ext007-evaluation-addendum.jsonl "
                     "with byte-exact quote verification and independent review; "
                     "regenerate evaluation dossier (config auto-includes the "
                     "addendum once it exists)",
        "push_blocker": "STILL OPEN — local main ahead of origin/main (EXT-005 "
                        "verification commits + EXT-006); all provided PATs were "
                        "rejected 2026-10-26/27 (401). User will push a provided "
                        "zip/bundle; do NOT re-clone while local-only commits exist.",
    }
    CHECKPOINT.write_text(
        json.dumps(checkpoint, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8")
    print(f"checkpoint written: {CHECKPOINT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
