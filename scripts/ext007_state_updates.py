#!/usr/bin/env python3
"""EXT-007 state updates: task-queue completion + EXT-008 append,
current-state, checkpoint. Run BEFORE the EXT-007 work commit; the work commit
hash is recorded in the follow-up state commit (convention since EXT-001)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TASK_QUEUE = REPO / "state" / "task-queue.jsonl"
CURRENT_STATE = REPO / "state" / "current-state.json"
CHECKPOINT = REPO / "state" / "checkpoints" / "checkpoint-2026-10-27-ext-007.json"

TASK_ID = "EXT-007"

TESTS_RUN = [
    {
        "step": "startup protocol (inherited from EXT-006 session start)",
        "command": "vu selftest + pytest + verify-manifest both vaults + registry rebuild",
        "result": "selftest exit 0; 407/407; both vaults unchanged; registry "
                  "rebuild valid (775 KUs, 71 classifications)",
        "evidence": "reports/extraction/ext006-kureg-*.json + "
                    "ext006-immutable-start-{master-ai,ai-course}.json",
    },
    {
        "step": "candidate verification before adjudication",
        "command": "quote location probe + original-source line checks",
        "result": "all C1-C4 quotes located byte-exact in committed batches "
                  "004/005 and at their original source lines (14/14 checks); "
                  "one candidate-report quote needed re-anchoring (C3 'loss "
                  "determines' sentence is a mid-sentence fragment on line "
                  "139, not a sentence-initial one)",
        "evidence": "session script ext007 probe + source-line check "
                    "(superseded by the generator's built-in X2 check)",
    },
    {
        "step": "adjudication + addendum generation",
        "command": "python3 scripts/ext007_classifications.py",
        "result": "ALL FOUR candidates ADOPTED (C1 SD, C2 PO, C3 PO, C4 SD); "
                  "pre-repair draft: 4 records, 12 quotes, 10 KUs; every "
                  "quote verified byte-exact in KU excerpts AND at original "
                  "source lines; 003-ext005 byte-unchanged (sha256 before/after)",
        "evidence": "state/classifications/004-ext007-evaluation-addendum.jsonl "
                    "+ scripts/ext007_classifications.py (verification chain X1-X8)",
    },
    {
        "step": "independent review",
        "command": "EXT-007-REVIEW read-only subagent",
        "result": "PASS-WITH-NOTES: 12/12 quotes byte-exact in excerpts; 12/12 "
                  "at exactly the stated source lines (0 off-by-one); 4/4 "
                  "cross-vault; 4 AGREE + 0 BORDERLINE + 0 DISAGREE; coverage "
                  "complete (no missed adopt/reject); append-only discipline "
                  "verified (003 sha256 == git HEAD == EXT-006 dossier "
                  "provenance); 3 required repairs (R1-R3, rationale wording) "
                  "+ 1 process action (R4) + 5 suggestions (S1-S5)",
        "evidence": "reports/extraction/ext007-review.md",
    },
    {
        "step": "repairs applied (orchestrator re-verified each claim first)",
        "command": "edit scripts/ext007_classifications.py + regenerate",
        "result": "R1-R3 wording fixes + S1-S5 evidence extensions applied "
                  "(each new quote verified at its source line BEFORE adding: "
                  "both-roles L139, gradient clause L30, course Huber L141); "
                  "final: 4 records (2 SD + 2 PO), 14 byte-exact quotes, 11 "
                  "participating KUs (6 first-time ai-course participants); "
                  "003-ext005 still byte-unchanged",
        "evidence": "reports/extraction/ext007-review.md orchestrator addendum",
    },
    {
        "step": "registry rebuild with addendum (R4)",
        "command": "vu kureg-apply-overlap 004-ext007 + kureg-validate",
        "result": "4 inserted, 0 rejected; valid, 0 errors/warnings; 775 KUs, "
                  "75 classifications, 240 participating KUs; all KUs remain "
                  "Unaccounted",
        "evidence": "reports/extraction/ext007-kureg-apply-overlap.json + "
                    "ext007-kureg-validate.json",
    },
    {
        "step": "evaluation dossier regeneration (R4)",
        "command": "python3 scripts/ext006_dossiers.py (x2 + --check)",
        "result": "evaluation-v1.json regenerated with the addendum: 33 "
                  "concepts (29+4), 97 participating KUs; double-run "
                  "byte-identical; --check exit 0 for all three dossiers",
        "evidence": "reports/extraction/ext006-dossier-coverage.json (updated)",
    },
    {
        "step": "full test suite + capabilities + immutability + validations",
        "command": "pytest -q; vu capabilities --verify; vu verify-manifest x2; "
                   "vu validate-registry --tasks + --classifications",
        "result": "415/415; 16 implemented-and-tested + 1 planned; both vaults "
                  "unchanged (333 + 276); task queue valid; addendum valid",
        "evidence": "reports/extraction/ext007-pytest-report.json + "
                    "ext007-capabilities.json + ext007-immutable-{master-ai,"
                    "ai-course}.json + ext007-taskqueue-validate.json + "
                    "ext007-classifications-validate.json",
    },
]

NOTES = (
    "Scope executed per task record. All four unreviewed candidates C1-C4 "
    "(from reports/extraction/ext005-independent-confirmation.md section 3) "
    "were verified against committed batches AND original source lines, then "
    "ADOPTED as OC-ext007-0001 (SD: report-multiple-metrics discipline, "
    "distinct from OC-ext005-0026's which-metric business decision), "
    "OC-ext007-0002 (PO: degenerate majority-prediction pattern transferred "
    "to pixel accuracy — master-ai states the pattern for classification "
    "accuracy only, has zero segmentation content), OC-ext007-0003 (PO: "
    "loss-vs-metric role distinction — master-ai assigns the loss role in "
    "passing, course states the principle + divergence practice + "
    "constant-gradient rationale), OC-ext007-0004 (SD: macro-averaged metrics "
    "for imbalanced data — companion to OC-ext005-0015 which covers only the "
    "PR-AUC half; separate record because 003-ext005 is append-only). New "
    "append-only file 004-ext007-evaluation-addendum.jsonl; 003-ext005 "
    "byte-unchanged throughout (sha256-verified). Independent review "
    "PASS-WITH-NOTES (12/12 quotes byte-exact at exact source lines, 4 AGREE "
    "/ 0 DISAGREE); all repairs R1-R3 and suggestions S1-S5 applied after "
    "orchestrator re-verification (final: 14 quotes, 11 KUs). Registry: 75 "
    "classifications, 240 participating KUs, 775 KUs all Unaccounted. "
    "Evaluation dossier regenerated (33 concepts) — derived-view property "
    "demonstrated in-repo. EXT-008 appended (SVM domain pair, ready)."
)

EXT008_RECORD = {
    "task_id": "EXT-008",
    "title": ("Extract the SVM/kernel-methods domain pair (AI Course 03.4 + "
              "Master AI SVM content) and classify its cross-vault overlap"),
    "priority": "high",
    "status": "ready",
    "dependencies": ["EXT-007"],
    "findings": ["F-0001", "F-0002", "F-0003"],
    "inputs": [
        "source-vaults/AI /AI Course/03 - Machine Learning/03.4 - Support Vector Machines (verify exact folder name at session start)",
        "master-ai SVM content (locate at session start: search '03 - Machine Learning' for SVM/kernel sections; EXT-002 batch 002 covers supervised learning — check whether SVM KUs are already extracted there before re-extracting)",
        "state/term-maps/ pattern (regression/tree/evaluation exemplars; build svm-domain-v1.json from ACTUAL batch content, pre-probe vocabulary before writing — EXT-005 pattern)",
        "schemas/overlap-classification.schema.json + scripts/ext00X_classifications.py generator pattern (byte-exact quote verification chain)",
        "scripts/ext006_dossiers.py DOMAINS config (add svm domain entry after classification; dossiers regenerate deterministically)",
    ],
    "outputs": [
        "state/knowledge-units/006-ext008-*.jsonl (+ 007- if master-ai side is a separate batch) — double-run byte-identical",
        "scripts/ext008_fidelity.py (EXT-005 pattern, both batches if two)",
        "state/term-maps/svm-domain-v1.json (machine-verified, zero invented entries)",
        "reports/extraction/ext008-overlap-candidates.json (+ pairs JSONL) via vu overlap-candidates",
        "state/classifications/005-ext008-svm-overlap.jsonl (evidence-based, byte-exact quotes)",
        "reports/extraction/ext008-review.md (independent read-only review, all repairs applied pre-commit)",
        "state/dossiers/svm-v1.json (extend scripts/ext006_dossiers.py DOMAINS; update concept-dossier schema domain enum if needed — schema change requires documented justification)",
        "registry rebuild + validate; task-queue/current-state/checkpoint/handoff updates",
    ],
    "acceptance_criteria": [
        "Every scope file has a verified extraction outcome (extraction or documented exclusion); batches double-run byte-identical",
        "Fidelity: every excerpt byte-exact vs source, hashes match, ids unique within and across batches, 0 heading crossings",
        "Term map machine-verified: every canonical term and alias occurs in an in-scope KU excerpt (no invented entries)",
        "Classifications carry byte-exact quotes verified in KU excerpts AND at original source lines; independent review verdict recorded with repairs applied before commit",
        "Sources unchanged before/after; registry validates clean; all KUs remain Unaccounted",
        "Full test suite passes; dossier regeneration byte-identical including the new svm domain",
    ],
    "forbidden_side_effects": [
        "Do not modify source vaults",
        "Do not edit committed batches, classification files, or dossiers by hand (dossiers regenerate via script)",
        "Do not assign dispositions",
        "Do not skip the independent review for committed classifications",
    ],
    "notes": ("Alternative next tasks if SVM proves ill-scoped at session "
              "start (decide with evidence): CAP-014 source-to-output coverage "
              "reports (required before synthesis batches are accepted, but no "
              "synthesis batch exists yet), or another domain pair from the "
              "unextracted Master AI files (consult state/manifests and the "
              "registry coverage report). The standing rule applies: never "
              "work in a fresh clone while local-only commits exist."),
}


def main() -> int:
    # 1. Task queue: EXT-007 queued -> completed; append EXT-008.
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
    out.append(json.dumps(EXT008_RECORD, ensure_ascii=False))
    TASK_QUEUE.write_text("\n".join(out) + "\n", encoding="utf-8")
    print("task-queue: EXT-007 -> completed; EXT-008 appended (ready)")

    # 2. Current state.
    cs = json.loads(CURRENT_STATE.read_text(encoding="utf-8"))
    cs["current_task_id"] = "EXT-008"
    cs["last_verified_checkpoint"] = str(CHECKPOINT.relative_to(REPO))
    cs["notes"] = (
        "EXT-007 completed 2026-10-27 (evaluation classification addendum: all "
        "four C1-C4 candidates adopted after verification — 2 SD + 2 PO, 14 "
        "byte-exact quotes, 11 KUs; independent review PASS-WITH-NOTES with "
        "all repairs applied; registry now 75 classifications / 240 "
        "participating KUs; evaluation dossier regenerated with 33 concepts). "
        "EXT-008 ready (SVM/kernel-methods domain pair). PUSH BLOCKER STILL "
        "OPEN: local main is 6+ commits ahead of origin/main; the session "
        "delivered a zip + git bundle for the user to push personally."
    )
    kr = cs.setdefault("knowledge_registry", {})
    kr["dossiers"]["files"]["evaluation-v1.json"] = (
        "33 concepts / 97 KUs (from 003-ext005 + 004-ext007)")
    kr["dossiers"]["concepts_total"] = 75
    kr["dossiers"]["participating_kus_total"] = 240
    CURRENT_STATE.write_text(
        json.dumps(cs, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("current-state: current_task_id=EXT-008, dossier counts updated")

    # 3. Checkpoint.
    checkpoint = {
        "checkpoint_id": "CHK-2026-10-27-EXT-007",
        "created_utc": "2026-10-27T00:00:00+00:00",
        "stage": "extraction",
        "task_id": TASK_ID,
        "task_status": "completed",
        "last_verified_state": {
            "framework_version": "0.5.0 (unchanged in EXT-007)",
            "test_result": "415 passed, 0 failed, 0 skipped",
            "test_evidence": "reports/extraction/ext007-pytest-report.json",
            "capabilities_evidence": "reports/extraction/ext007-capabilities.json "
                                     "(16 implemented-and-tested, 1 planned: CAP-014)",
            "registry_store": "state/knowledge-units/ (775 records in 5 committed "
                              "batches, unedited)",
            "derived_index": "state/registries/kuregistry.db (apply-overlap "
                             "applied for the addendum on top of the EXT-006 "
                             "rebuild; kureg-validate valid, 0 errors/warnings)",
            "classifications": {
                "paths": [
                    "state/classifications/001-ext003-regression-overlap.jsonl (14 records)",
                    "state/classifications/002-ext004-tree-based-overlap.jsonl (28 records)",
                    "state/classifications/003-ext005-evaluation-overlap.jsonl (29 records, byte-unchanged)",
                    "state/classifications/004-ext007-evaluation-addendum.jsonl (4 records, NEW)",
                ],
                "total": 75,
                "by_overlap_type": {"Semantic Duplicate": 45,
                                    "Partial Overlap": 27,
                                    "Complementary Content": 2,
                                    "Conflict or Historical Difference": 1},
                "participating_kus_total": 240,
            },
            "dossiers": {
                "files": {
                    "state/dossiers/regression-v1.json": "14 concepts, 61 KUs",
                    "state/dossiers/tree-based-v1.json": "28 concepts, 82 KUs",
                    "state/dossiers/evaluation-v1.json": "33 concepts, 97 KUs (regenerated with addendum)",
                },
                "concepts_total": 75,
                "determinism": "double-run byte-identical + --check exit 0 (all three)",
                "dispositions_assigned": False,
            },
            "source_immutability": "verify-manifest exit 0 x2 this task "
                                   "(startup checks under EXT-006 evidence); "
                                   "333 + 276 unchanged",
            "findings_open": ["F-0001", "F-0002", "F-0003", "F-0007", "F-0008"],
            "findings_resolved": ["F-0004", "F-0005", "F-0006"],
            "independent_review": "reports/extraction/ext007-review.md "
                                  "(EXT-007-REVIEW, PASS-WITH-NOTES; R1-R3 + "
                                  "S1-S5 applied post-review, each "
                                  "machine-verified; orchestrator addendum "
                                  "documents the delta)",
        },
        "acceptance_criteria_met": [
            "Every candidate C1-C4 received an explicit adopt decision with "
            "recorded rationale (all four adopted; none rejected — each "
            "verified against committed batches and original source lines "
            "first)",
            "Every adopted record carries byte-exact quote evidence from both "
            "vaults (generator verifies in excerpts AND at original source "
            "lines before writing; 14/14)",
            "Adopted set passed independent read-only review (PASS-WITH-NOTES; "
            "all repairs applied before commit)",
            "Committed 003-ext005 file byte-unchanged (sha256 verified "
            "before/after; addendum went to the new 004-ext007 file)",
            "Sources unchanged; full suite 415/415; kureg-validate clean "
            "(775 KUs, 75 classifications, 240 participating)",
        ],
        "next_task": "EXT-008 (ready): SVM/kernel-methods domain pair — verify "
                     "scope at session start (check whether master-ai SVM "
                     "content overlaps batch 002's supervised-learning scope), "
                     "extract both sides, build machine-verified term map, "
                     "classify with byte-exact evidence, independent review, "
                     "extend the dossier generator DOMAINS config",
        "push_blocker": "STILL OPEN — local main ahead of origin/main by 6+ "
                        "commits (EXT-005 verification + EXT-006 + EXT-007); "
                        "user pushes the delivered zip/bundle personally; do "
                        "NOT re-clone while local-only commits exist.",
    }
    CHECKPOINT.write_text(
        json.dumps(checkpoint, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8")
    print(f"checkpoint written: {CHECKPOINT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
