#!/usr/bin/env python3
"""EXT-010: persist end-of-task state (task record completion, current-state,
checkpoint). Idempotent-guarded. The work-commit hash is recorded by a
separate follow-up script after the work commit exists (EXT-009 pattern)."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
QUEUE = REPO / "state/task-queue.jsonl"
CURRENT = REPO / "state/current-state.json"
CHECKPOINT = REPO / "state/checkpoints/checkpoint-2026-10-27-ext-010.json"

TESTS_RUN = [
    {
        "step": "startup protocol (fresh session)",
        "command": "vu selftest + pytest + verify-manifest both vaults + registry rebuild (kureg-init --force + load x9 + apply-overlap x6) + kureg-validate + validate-registry --tasks",
        "evidence": "reports/extraction/ext010-{startup-pytest,immutable-start-*,kureg-*,taskqueue-validate-start}.json",
        "result": "selftest exit 0; 415/415; both vaults unchanged (333 + 276); registry rebuilt and valid (1229 KUs, 128 classifications, 372 participating) matching checkpoint-2026-10-27-ext-009 exactly; queue 14/14 valid; git clean, local == origin/main",
    },
    {
        "step": "scope decision evidence",
        "command": "python3 scripts/ext010_scope_probe.py (mdextract.extract_structure_text, CAP-003 authority) + never-extracted check against all committed batches + fence-balance probe",
        "evidence": "state/task-queue.jsonl EXT-010 record notes (full per-file scope-decision evidence)",
        "result": "EXT-009's reserved counterpart ADJUSTED with heading evidence: master-ai '05 - Loss Spikes and Stability.md' is LLM-pretraining operations, NOT init/gradient theory; true counterpart = master-ai 04/Training 07 (259 L) + 08 (293 L); all 5 scope files verified never-extracted and fence-balanced",
    },
    {
        "step": "extraction batches 010 + 011",
        "command": "vu extract-kus per file (double-run x2 per part) + scripts/ext010_concat.py fixed-order concat (+ concat double-run cmp)",
        "evidence": "reports/extraction/ext010-coverage-{master-ai-07,master-ai-08,ai-course-01,ai-course-02,ai-course-03}.json",
        "result": "batch 010 = 117 KUs (2 master-ai files 07+08); batch 011 = 382 KUs (3 ai-course files 01+02+03); 5/5 files, 0 excluded/failed; every part and both concats double-run byte-identical (batch sha256 5cc0eb42... / fc58559b...)",
    },
    {
        "step": "fidelity (both batches, id-uniqueness vs committed 001-009)",
        "command": "python3 scripts/ext010_fidelity.py",
        "evidence": "reports/extraction/ext010-fidelity-{master-ai,ai-course}.json",
        "result": "117/117 + 382/382 byte-exact excerpts + hashes + structural purity + 0 heading crossings + ids unique within/across the new batches AND vs all 1229 committed ids",
    },
    {
        "step": "term map (pre-probed vocabulary, machine-verified)",
        "command": "python3 scripts/ext010_term_probe{,2,3,4}.py (four probe rounds BEFORE writing) + python3 scripts/ext010_term_map.py",
        "evidence": "reports/extraction/ext010-term-map-verification.json",
        "result": "training-stability-domain-v1.json: 98 terms / 165 aliases / 66 cross-vault / 2 bridged ('Gaussian', 'diagnose'); every entry machine-verified in-scope; no French vocabulary; sense-collision vocabulary (attention idiom vs mechanism, spikes, norm family, scale, decay-as-shrinkage) documented in the map comment; 6 unverified entries caught and fixed by the verifier on first run",
    },
    {
        "step": "CAP-013 discovery (both full batches)",
        "command": "vu overlap-candidates --batch 010 --batch 011 --terms training-stability-domain-v1.json",
        "evidence": "reports/extraction/ext010-overlap-candidates.json + -pairs.jsonl",
        "result": "7486 term pairs, 68 cross-vault topics, 21 topics truncated at the 250-pair cap (per-KU evidence complete) — the largest discovery run of the project so far",
    },
    {
        "step": "classifications (generator chain X1-X10)",
        "command": "python3 scripts/ext010_classifications.py (twice: pre-review and post-S2)",
        "evidence": "state/classifications/007-ext010-training-stability-overlap.jsonl",
        "result": "36 records OC-ext010-0001..0036 (32 SD + 3 PO + 1 CC), 142 participating KUs, 159 byte-exact quotes; NEW X2 machine-locator (lines located at runtime from source, not hand-typed) eliminates the EXT-009 R2 hand-typed-line error class; first run caught 5 defects (2 KU-id swaps, 1 truncated KU id, 1 fan-in/fan-out hyphenation) which were fixed at source; chain X1-X9 green",
    },
    {
        "step": "independent review (read-only subagent)",
        "command": "EXT-010-REVIEW subagent (scripts/ext010_review_check.py machine checks + semantic AGREE/BORDERLINE/DISAGREE + coverage hunt + scope check + F-0009 verification)",
        "evidence": "reports/extraction/ext010-review.md + reports/extraction/ext010-review-check.json",
        "result": "PASS-WITH-NOTES: 10/10 spot quotes byte-exact at source, 34 AGREE + 2 BORDERLINE + 0 DISAGREE, no coverage gaps (0 uncovered discovery topics; embedding/landscape/derivative/practice hunts all cleared with evidence), scope decision verified legitimate, F-0009 confirmed genuine at source",
    },
    {
        "step": "repairs applied (orchestrator re-verification then regeneration)",
        "command": "python3 scripts/ext010_findings.py (R1) + generator edit (S2, corrected course KU id) + regeneration + re-run chain + re-run review-check",
        "evidence": "reports/extraction/ext010-review.md (orchestrator addendum) + state/findings.jsonl (F-0009)",
        "result": "R1 F-0009 appended (9 findings total) making the records' method-field claim true; S2 applied WITH CORRECTION — the review's course KU id was wrong (KU-892e72cc63cf286a is the L688 prose; the quote lives in KU-32b1dde0ac8ea1de, orchestrator-verified unique in-span), regeneration now 159 quotes / 142 KUs, X1-X9 green, committed files 001-006 still byte-identical to HEAD",
    },
    {
        "step": "dossier extension (R3)",
        "command": "schema enum + DOMAINS + DOSSIER_FILES edits, python3 scripts/ext006_dossiers.py (x2) + --check",
        "evidence": "reports/extraction/ext006-dossier-coverage.json",
        "result": "training-stability-v1.json generated (36 concepts / 142 KUs; ZERO zero-evidence categories — the first dossier with all ten categories populated); ALL SIX dossiers regenerate byte-identically (--check exit 0 x6); the five committed dossiers unchanged vs git HEAD; tests/test_concept_dossier.py DOSSIER_FILES updated (8/8 standalone)",
    },
    {
        "step": "registry rebuild",
        "command": "kureg-init --force + kureg-load x11 + kureg-apply-overlap x7 + kureg-validate",
        "evidence": "reports/extraction/ext010-kureg-{init,load-*,apply-*,validate}.json",
        "result": "exit 0 x19; 1728 KUs, 164 classifications (120 SD + 37 PO + 6 CC + 1 CHD), 514 participating, valid 0 errors/warnings; all 1728 KUs Unaccounted by design",
    },
    {
        "step": "final battery",
        "command": "pytest (full) + capabilities --verify + verify-manifest both vaults + validate-registry (tasks + 007-ext010)",
        "evidence": "reports/extraction/ext010-{pytest-report,capabilities,immutable-end-*,taskqueue-validate,classifications-validate}.json",
        "result": "415/415 (test_concept_dossier iterates all six dossier files internally, so the suite count is legitimately unchanged); capabilities 16 implemented-and-tested + 1 planned; both vaults unchanged (333 + 276); queue 15/15 valid; classifications file valid 0 problems",
    },
]

NOTES_ADDENDUM = (
    " COMPLETION NOTE (2026-10-27): executed in ONE session. 31 of 609 source "
    "files extracted after this task (26 before + 5; ai-course 04.3 is now 6 of "
    "7 files extracted - only 04 Hyperparameters remains, still reserved for a "
    "future optimization/tuning pair). Review PASS-WITH-NOTES with R1 (F-0009 "
    "finding appended) and S2 (two clipping-API evidence quotes added to "
    "OC-ext010-0024, with the reviewer's course KU-id misattribution corrected "
    "by orchestrator verification) applied before commit; suggestions S1/S3/S4 "
    "recorded for future sessions (S1 topic-wording style; S3 add a "
    "committed_files_unchanged field to review-check JSON; S4 dossier note: "
    "records 0014/0015 both quote fragments of master line 08 L34). NEW "
    "FINDING F-0009 (course internally inconsistent on PyTorch Conv2d default "
    "bias init; file 01 L407 'Biases are initialized to zero.' vs file 02 "
    "L68-70 and file 01 L415 uniform bound - the latter matches PyTorch's "
    "actual reset_parameters); cross-referenced from OC-ext010-0033/0036 "
    "rationales. Improvements over EXT-009: (1) the X2 machine-locator "
    "eliminates hand-typed line numbers entirely; (2) review-check emits a "
    "topic-coverage section (0 uncovered discovery topics). Deliberate "
    "non-records (single-vault in scope, review-verified): master-ai-only - "
    "transformer init recipe (GPT-2 std 0.02, residual scaling 1/sqrt(2N), "
    "zero unembedding + log(vocab) rationale, pre-norm), LoRA A/B specifics, "
    "MuP/Tensor Programs/Fixup, bias-init specials (LSTM forget gate 1.0, "
    "inverse class frequency), GELU/SiLU extension, LSTM/GRU gates and "
    "attention as solution families, transformer explosion contexts (QK "
    "scaling, FP16, 50+-layer residual dependence), spectral-radius "
    "formalism, 20-layer MNIST table, Hochreiter 1991 / Pascanu 2013 refs; "
    "ai-course-only - non-convex landscape treatment (2^N saddle points, "
    "parachute analogy), volume-knob/telephone analogies, N(0,0.01)/N(0,1) "
    "numeric analyses, Goldilocks naming, sigmoid maximization derivation, "
    "tanh table, alpha^(L-l) table, dying-ReLU detail, PReLU/ELU/SELU/LeCun "
    "coverage, orthogonal/sparse init, BN gamma/beta rationale, "
    "partners-not-substitutes, when-init-matters conditions, PyTorch-default "
    "documentation, variance-tracking hook, clip-threshold guidance, "
    "monitoring/safe-step/dashboard code. No dispositions assigned. Next: "
    "EXT-011 (to be selected with evidence; strongest candidates from the "
    "dossier gap markers and the master-ai Backpropagation/autodiff family, "
    "the 11-Training LLM-operations pair, or a further ai-course chapter)."
)


def update_task_record() -> None:
    lines = QUEUE.read_text(encoding="utf-8").splitlines()
    out = []
    found = False
    for line in lines:
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("task_id") == "EXT-010":
            found = True
            assert rec["status"] == "ready", "EXT-010 record not in ready state"
            rec["status"] = "completed"
            rec["tests_run"] = TESTS_RUN
            rec["findings"] = ["F-0001", "F-0002", "F-0003", "F-0006", "F-0009"]
            rec["notes"] = rec["notes"] + NOTES_ADDENDUM
        out.append(json.dumps(rec, ensure_ascii=False, sort_keys=True))
    assert found, "EXT-010 record not found"
    QUEUE.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"task record updated; queue still {len(out)} records")


def update_current_state() -> None:
    cs = json.loads(CURRENT.read_text(encoding="utf-8"))
    cs["current_task_id"] = "EXT-011"
    cs["last_verified_checkpoint"] = "state/checkpoints/checkpoint-2026-10-27-ext-010.json"
    cs["notes"] = (
        "EXT-010 completed 2026-10-27 in one session. Training-stability domain "
        "pair with an EVIDENCE-BASED COUNTERPART ADJUSTMENT: the EXT-009 "
        "reservation paired ai-course 04.3 files 01-03 with master-ai '11 - "
        "Training/Optimization/05 - Loss Spikes and Stability.md', but the "
        "scope probe (heading evidence) showed that file is LLM-pretraining "
        "operations, not classical init/gradient theory; the executed pair is "
        "master-ai '04 - Neural Networks/Training/07 - Initialization "
        "Schemes.md' + '08 - Vanishing and Exploding Gradients.md' (a "
        "deliberate 2-of-3 partial-folder master-ai scope; 06 Backpropagation "
        "excluded as a distinct autodiff domain). Batches 010 (117 KUs) + 011 "
        "(382 KUs) double-run byte-identical; fidelity 117/117 + 382/382 "
        "byte-exact with ids unique vs all 1229 committed; term map 98 terms / "
        "165 aliases / 66 cross-vault / 2 bridged machine-verified after four "
        "probe rounds; discovery 7486 pairs / 68 cross-vault topics / 21 "
        "truncated (largest yet); 36 evidence-based classifications (32 SD + "
        "3 PO + 1 CC; 142 KUs; 159 quotes) via a NEW X2 machine-locator that "
        "eliminates hand-typed line numbers (first run caught 5 defects); "
        "independent review EXT-010-REVIEW PASS-WITH-NOTES (34 AGREE + 2 "
        "BORDERLINE + 0 DISAGREE, no coverage gaps, scope verified, F-0009 "
        "confirmed) with R1 (F-0009 finding appended) and S2 (clipping-API "
        "evidence, reviewer's course KU-id error corrected by orchestrator "
        "verification) applied before commit; training-stability-v1 dossier "
        "(36 concepts / 142 KUs, ZERO empty categories - first such) with "
        "schema enum extended additively and all six dossiers regenerating "
        "byte-identically; registry 1728 KUs / 164 classifications / 514 "
        "participating / valid; suite 415/415; capabilities 16+1; both "
        "vaults unchanged. NEW FINDING F-0009: course internally inconsistent "
        "on the PyTorch Conv2d default bias init (zeros vs uniform bound; the "
        "uniform bound matches PyTorch's actual reset_parameters) - "
        "synthesis-time reconciliation required. 31 of 609 source files "
        "extracted. EXT-011 to be selected with evidence at next session "
        "start (candidates: master-ai backpropagation/autodiff family, the "
        "11-Training LLM-operations pair with ai-course optimization content, "
        "or a further ai-course chapter; check dossier gap markers and the "
        "task-queue notes first)."
    )
    kr = cs["knowledge_registry"]
    kr["records"] = 1728
    kr["classifications"] = (
        "state/classifications/001-ext003-regression-overlap.jsonl (14 records) + "
        "002-ext004-tree-based-overlap.jsonl (28 records) + "
        "003-ext005-evaluation-overlap.jsonl (29 records) + "
        "004-ext007-evaluation-addendum.jsonl (4 records) + "
        "005-ext008-clustering-dimreduction-overlap.jsonl (27 records) + "
        "006-ext009-generalization-overlap.jsonl (26 records) + "
        "007-ext010-training-stability-overlap.jsonl (36 records, EXT-010; "
        "ADR-0009 pair-level overlay)"
    )
    dos = kr["dossiers"]
    dos["files"]["training-stability-v1.json"] = "36 concepts / 142 KUs (from 007-ext010)"
    dos["concepts_total"] = 164
    dos["participating_kus_total"] = 514
    CURRENT.write_text(json.dumps(cs, indent=1, ensure_ascii=False) + "\n",
                       encoding="utf-8")
    print("current-state.json updated")


def write_checkpoint() -> None:
    checkpoint = {
        "checkpoint_id": "CHK-2026-10-27-EXT-010",
        "created_utc": "2026-10-27T00:00:00+00:00",
        "stage": "extraction",
        "task_id": "EXT-010",
        "task_status": "completed",
        "last_verified_state": {
            "framework_version": "0.5.0 (unchanged in EXT-010 - no framework code changes; ext010 scripts are task-local generators/checkers per the EXT-005..009 pattern)",
            "test_result": "415 passed, 0 failed, 0 skipped (test_concept_dossier iterates all six dossier files internally; suite count legitimately unchanged)",
            "test_evidence": "reports/extraction/ext010-pytest-report.json",
            "capabilities_evidence": "reports/extraction/ext010-capabilities.json (16 implemented-and-tested, 1 planned: CAP-014)",
            "registry_store": "state/knowledge-units/ (1728 records in 11 committed batches, unedited)",
            "derived_index": "state/registries/kuregistry.db (rebuilt: init --force + load x11 + apply-overlap x7; kureg-validate valid, 0 errors/warnings)",
            "classifications": {
                "paths": [
                    "state/classifications/001-ext003-regression-overlap.jsonl (14 records)",
                    "state/classifications/002-ext004-tree-based-overlap.jsonl (28 records)",
                    "state/classifications/003-ext005-evaluation-overlap.jsonl (29 records)",
                    "state/classifications/004-ext007-evaluation-addendum.jsonl (4 records)",
                    "state/classifications/005-ext008-clustering-dimreduction-overlap.jsonl (27 records)",
                    "state/classifications/006-ext009-generalization-overlap.jsonl (26 records)",
                    "state/classifications/007-ext010-training-stability-overlap.jsonl (36 records)",
                ],
                "total": 164,
                "participating_kus": 514,
            },
            "dossiers": {
                "paths": [
                    "state/dossiers/regression-v1.json (14 concepts / 61 KUs)",
                    "state/dossiers/tree-based-v1.json (28 concepts / 82 KUs)",
                    "state/dossiers/evaluation-v1.json (33 concepts / 97 KUs)",
                    "state/dossiers/clustering-v1.json (27 concepts / 64 KUs)",
                    "state/dossiers/generalization-v1.json (26 concepts / 68 KUs)",
                    "state/dossiers/training-stability-v1.json (36 concepts / 142 KUs)",
                ],
                "regeneration": "all six byte-identical (scripts/ext006_dossiers.py --check exit 0)",
                "schema_change": "schemas/concept-dossier.schema.json domain enum extended additively with 'training-stability' (justification in schema description)",
            },
            "source_immutability": "both vaults verified unchanged before and after (verify-manifest exit 0 x4)",
            "push_state": "to be pushed to origin/main at session end (user push policy: always push to main)",
        },
        "acceptance_evidence": [
            "Batches 010/011 double-run byte-identical (per part and full concat)",
            "Fidelity 117/117 + 382/382 byte-exact + ids unique vs 1229 committed (reports/extraction/ext010-fidelity-{master-ai,ai-course}.json)",
            "Term map machine-verified, zero invented entries (reports/extraction/ext010-term-map-verification.json)",
            "Discovery 7486 pairs / 68 cross-vault topics / 21 truncated (reports/extraction/ext010-overlap-candidates.json)",
            "36 classifications, 159 byte-exact quotes with MACHINE-LOCATED lines, X1-X9 green (state/classifications/007-ext010-training-stability-overlap.jsonl)",
            "Independent review PASS-WITH-NOTES; all required repairs applied (reports/extraction/ext010-review.md + orchestrator addendum)",
            "Registry rebuild valid: 1728 KUs / 164 classifications / 514 participating (reports/extraction/ext010-kureg-validate.json)",
            "Full test suite passes (415/415); capabilities --verify passes (16+1); both vaults unchanged; queue 15/15 valid",
            "New finding F-0009 recorded (state/findings.jsonl) and cross-referenced from the classification rationales",
        ],
        "next_task": "EXT-011 (to be selected at next session start with evidence): candidates - master-ai backpropagation/autodiff family (06 Backpropagation + ai-course backprop content), the 11-Training LLM-operations pair (05 Loss Spikes + 04 Mixed Precision vs ai-course optimization content), or a further ai-course chapter; consult state/manifests, the dossier gap markers, and the task-queue notes first, then append a full EXT-011 record before executing",
        "work_commit": "PENDING (recorded by the state commit)",
    }
    CHECKPOINT.write_text(json.dumps(checkpoint, indent=1, ensure_ascii=False) + "\n",
                          encoding="utf-8")
    print("checkpoint written")


if __name__ == "__main__":
    update_task_record()
    update_current_state()
    write_checkpoint()
