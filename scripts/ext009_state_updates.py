#!/usr/bin/env python3
"""EXT-009: state updates (task record, current-state, checkpoint).

Run AFTER all EXT-009 work is verified. Replaces the ready EXT-009 record in
state/task-queue.jsonl with the completed record (with tests_run evidence),
updates state/current-state.json, and writes the checkpoint.

Optionally pass the work-commit hash as argv[1] to record it in the task
record and checkpoint (second, state-recording invocation).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

WORK_COMMIT = sys.argv[1] if len(sys.argv) > 1 else None

TESTS_RUN = [
    {
        "step": "startup protocol (fresh session continuing the interrupted EXT-009 session)",
        "command": "vu selftest + pytest + verify-manifest both vaults + kureg-validate",
        "result": "selftest exit 0; 415/415; both vaults unchanged (333 + 276); registry valid (889 KUs, 102 classifications, 304 participating)",
        "evidence": "reports/extraction/ext009-immutable-start-{master-ai,ai-course}.json + ext009-kureg-validate-start.json",
    },
    {
        "step": "push-blocker resolution (session boundary)",
        "command": "git push origin main (fresh PAT) + git ls-remote verification",
        "result": "PUSHED 7d9e65f..58ad0fa (EXT-005..EXT-008 commits) to origin/main; blocker RESOLVED; docs commit 7041d47 records it",
        "evidence": "docs/agent-handoff/next-agent.md (push-success note), git log",
    },
    {
        "step": "scope decision (inherited from the interrupted session, independently re-verifiable from the task record notes)",
        "command": "full-vault greps (RL vocabulary; 'bias[- ]variance'; 'overfitting|regulariz' concentration; SVM re-check not needed - EXT-008 precedent)",
        "result": "RL ruled out (8 passing mentions in 8 ai-course files); generalization pair confirmed; ai-course side scoped to 04.3 files 05/06/07 with per-file justification",
        "evidence": "state/task-queue.jsonl EXT-009 record notes (scope-decision evidence recorded in full)",
    },
    {
        "step": "extraction batch 008 (master-ai Generalization, 2 files)",
        "command": "vu extract-kus --root 'source-vaults/AI /Master AI' --scope '03 - Machine Learning/Generalization' --vault-id master-ai (+ double-run cmp)",
        "result": "106 KUs, 2/2 files, 0 excluded/failed; byte-identical double-run (sha256 2e258f18016bcfa0...)",
        "evidence": "reports/extraction/ext009-coverage-master-ai.json",
    },
    {
        "step": "extraction batch 009 (ai-course 04.3 regularization files 05/06/07)",
        "command": "vu extract-kus per file (05, 06, 07) + scripts/ext009_concat.py fixed-order concat (+ double-run cmp per part and full)",
        "result": "234 KUs (3 parts), 3/3 files, 0 excluded/failed; parts and concat byte-identical (sha256 479e1eda83549ddb...)",
        "evidence": "reports/extraction/ext009-coverage-ai-course-{05,06,07}.json",
    },
    {
        "step": "fidelity (both batches, id-uniqueness vs all committed batches 001-007)",
        "command": "python3 scripts/ext009_fidelity.py",
        "result": "106/106 + 234/234 byte-exact excerpts + hashes + structural purity + 0 heading crossings + ids unique within/across batches AND vs all 889 committed ids",
        "evidence": "reports/extraction/ext009-fidelity-{master-ai,ai-course}.json",
    },
    {
        "step": "term map (pre-probed vocabulary, machine-verified)",
        "command": "python3 scripts/ext009_term_probe.py + ext009_term_probe2.py (probe BEFORE writing) + python3 scripts/ext009_term_map.py",
        "result": "generalization-domain-v1.json: 65 terms / 40 aliases / 38 cross-vault / 2 bridged (hyperparameter, test set); every term/alias verified in-scope; no French vocabulary in scope (probe-verified); sense-collision vocabulary documented in the map comment",
        "evidence": "reports/extraction/ext009-term-map-verification.json",
    },
    {
        "step": "CAP-013 discovery (both full batches)",
        "command": "vu overlap-candidates (batches 008+009, generalization terms)",
        "result": "2961 pairs, 40 cross-vault topics, 5 topics truncated at the 250-pair cap (per-KU evidence complete)",
        "evidence": "reports/extraction/ext009-overlap-candidates.json + -pairs.jsonl",
    },
    {
        "step": "classifications (generator chain X1-X9)",
        "command": "python3 scripts/ext009_classifications.py",
        "result": "006-ext009-generalization-overlap.jsonl: 26 records OC-ext009-0001..0026 (21 SD + 3 PO + 2 CC), 68 participating KUs, 88 byte-exact quotes, every quote verified in KU excerpts AND at original source lines; committed files 001-005 byte-unchanged",
        "evidence": "state/classifications/006-ext009-generalization-overlap.jsonl + reports/extraction/ext009-classifications-validate.json",
    },
    {
        "step": "independent review (read-only subagent)",
        "command": "EXT-009-REVIEW subagent (scripts/ext009_review_check.py)",
        "result": "PASS-WITH-NOTES: 86/86 quotes byte-exact at exactly the stated source lines (0 off-by-one), 25/25 cross-vault, 25 AGREE + 0 BORDERLINE + 0 DISAGREE, ONE coverage gap (CG-1 LayerNorm cluster), 4 line-reference wording errors, scope decision verified legitimate",
        "evidence": "reports/extraction/ext009-review.md",
    },
    {
        "step": "repairs applied (orchestrator re-verification then regeneration)",
        "command": "python3 scripts/ext009_classifications.py (after R1/R2/S1-S5 edits)",
        "result": "R1 OC-ext009-0026 added (LayerNorm preference, SD, master L123 x course L551) + 0018 clause fixed; R2 four line refs corrected (L115+L254-269, L455-456, L422, L190); S1-S5 applied (S5 recorded in the handoff's synthesis connections); regenerated: 26 records / 88 quotes / 68 KUs, X1-X9 green; addendum appended to the review report",
        "evidence": "reports/extraction/ext009-review.md (orchestrator addendum)",
    },
    {
        "step": "dossier extension (R3)",
        "command": "schema enum + DOMAINS extension, python3 scripts/ext006_dossiers.py (x2) + --check",
        "result": "generalization-v1.json generated (26 concepts / 68 KUs; zero-evidence: computational_mechanics, interview_misconceptions_comparisons); ALL FIVE dossiers regenerate byte-identically (--check exit 0 x5); tests/test_concept_dossier.py DOSSIER_FILES updated",
        "evidence": "reports/extraction/ext006-dossier-coverage.json",
    },
    {
        "step": "registry rebuild",
        "command": "kureg-init --force + kureg-load x9 + kureg-apply-overlap x6 + kureg-validate",
        "result": "exit 0 x16; 1229 KUs, 128 classifications (88 SD + 34 PO + 5 CC + 1 CHD), 372 participating, valid 0 errors/warnings; all 1229 KUs Unaccounted by design",
        "evidence": "reports/extraction/ext009-kureg-{init,load-*,apply-*,validate}.json",
    },
    {
        "step": "final battery",
        "command": "pytest (full) + capabilities --verify + verify-manifest both vaults + validate-registry (tasks + 006-ext009)",
        "result": "415/415; capabilities 16 implemented-and-tested + 1 planned (all verified); both vaults unchanged (333 + 276); queue 14/14 valid, classifications valid 0 problems",
        "evidence": "reports/extraction/ext009-{pytest-report,capabilities,immutable-end-*,taskqueue-validate}.json",
    },
]

TASK_RECORD = {
    "task_id": "EXT-009",
    "title": "Generalization/regularization domain pair (master-ai Generalization folder + AI Course 04.3 regularization files 05-07 — ai-course side scoped to the regularization-relevant subset of 04.3 with evidence; the weight-init/vanishing-gradient/hyperparameter files 01-04 are reserved for a future training-stability/optimization pair with master-ai '11 - Training')",
    "priority": "high",
    "status": "completed",
    "dependencies": ["EXT-008"],
    "findings": ["F-0001", "F-0002", "F-0003"],
    "inputs": [
        "master-ai side (whole folder, exactly 2 files): '03 - Machine Learning/Generalization/01 - Bias Variance Tradeoff.md' (325 lines) + '06 - Regularization Techniques.md' (199 lines), never extracted",
        "ai-course side (3 of 7 files in '04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability', each fence-balanced per F-0002 check): '05. Batch Normalization.md' (597 lines) + '06. Dropout and Regularization.md' (589 lines) + '07. Data Augmentation.md' (734 lines), never extracted",
        "state/term-maps/ pattern (regression/tree/evaluation/clustering exemplars; generalization-domain-v1.json built from ACTUAL batch content, pre-probed vocabulary — EXT-005/EXT-008 pattern)",
        "CAP-013 vu overlap-candidates + vu kureg-apply-overlap (word-boundary, mermaid-safe; F-0006 rules mandatory)",
        "schemas/overlap-classification.schema.json + scripts/ext008_classifications.py generator pattern (byte-exact quote verification chain X1-X9)",
        "scripts/ext006_dossiers.py DOMAINS config + schemas/concept-dossier.schema.json domain enum (additive 'generalization' extension per the EXT-008 precedent, justification recorded in the schema description)",
    ],
    "outputs": [
        "state/knowledge-units/008-ext009-master-ai-generalization.jsonl (106 KUs, 2/2 files, double-run byte-identical, sha256 2e258f18016bcfa0...)",
        "state/knowledge-units/009-ext009-ai-course-04.3-regularization.jsonl (234 KUs = three deterministic single-file runs concatenated in fixed order 05, 06, 07; each part and the full concat double-run byte-identical, sha256 479e1eda83549ddb...)",
        "scripts/ext009_fidelity.py (both batches; ID-uniqueness check extended over committed batches 001-007)",
        "state/term-maps/generalization-domain-v1.json (65 terms, 40 aliases, 38 cross-vault, 2 bridged; every entry machine-verified in-scope; no French vocabulary in scope)",
        "reports/extraction/ext009-overlap-candidates.json + -pairs.jsonl (2961 pairs, 40 cross-vault topics, 5 topics truncated at the 250-pair cap)",
        "state/classifications/006-ext009-generalization-overlap.jsonl (26 records: 21 SD + 3 PO + 2 CC; 68 participating KUs; 88 byte-exact quotes; OC-ext009-0026 added at review per CG-1/R1; generator chain X1-X9)",
        "reports/extraction/ext009-review.md (independent EXT-009-REVIEW, PASS-WITH-NOTES; all repairs R1-R2 + suggestions S1-S5 applied, orchestrator addendum recorded)",
        "state/dossiers/generalization-v1.json (26 concepts / 68 KUs; schema domain enum extended additively with 'generalization'; all five dossiers regenerate byte-identically)",
        "registry rebuilt (init --force + load x9 + apply-overlap x6) and valid (1229 KUs, 128 classifications, 372 participating); task-queue/current-state/checkpoint/handoff updates",
    ],
    "acceptance_criteria": [
        "Every scope file has a verified extraction outcome (extraction or documented exclusion); batches double-run byte-identical (per part and full concat for the ai-course side)",
        "Fidelity: every excerpt byte-exact vs source, hashes match, ids unique within and across batches AND vs all committed ids, 0 heading crossings",
        "Term map machine-verified: every canonical term and alias occurs in an in-scope KU excerpt (no invented entries)",
        "Classifications carry byte-exact quotes verified in KU excerpts AND at original source lines; independent review verdict recorded with repairs applied before commit",
        "Sources unchanged before/after; registry validates clean; all KUs remain Unaccounted",
        "Full test suite passes; dossier regeneration byte-identical including the new generalization domain",
    ],
    "forbidden_side_effects": [
        "Do not modify source vaults",
        "Do not edit committed batches, classification files, or dossiers by hand (dossiers regenerate via script)",
        "Do not assign dispositions",
        "Do not skip the independent review for committed classifications",
    ],
    "notes": (
        "FIRST PARTIAL-FOLDER ai-course scope (3 of 7 files in 04.3), justified per file with headings evidence and "
        "recorded in the task record's scope-decision notes (weight-init/vanishing-gradient files reserved for a "
        "future training-stability pair with master-ai '11 - Training/Optimization/05 - Loss Spikes and "
        "Stability.md'; hyperparameters file is optimization/tuning; the CNN chapter-summary restatement is "
        "deferred). Executed as the first TWO-SESSION task: the extracting session completed batches, term map, "
        "discovery, classifications, and the independent review, and applied part of the review repairs before "
        "being interrupted (tool-infrastructure failure); the completing session re-verified the startup battery, "
        "verified every review claim at source independently, applied the remaining repairs (R1 record + 0018 "
        "clause, R2 line refs, S1-S5), and completed R3. Batch 008 = 106 KUs from the 2 master-ai Generalization "
        "files (double-run byte-identical); batch 009 = 234 KUs from ai-course 04.3 files 05/06/07 (three "
        "single-file runs concat'd in fixed order; parts + concat double-run byte-identical). Fidelity 106/106 + "
        "234/234 byte-exact + ids unique vs 889 committed. Term map 65 terms / 40 aliases / 38 cross-vault / 2 "
        "bridged, machine-verified, zero invented entries, no French vocabulary in scope. Discovery 2961 pairs / "
        "40 cross-vault topics / 5 truncated at the 250-pair cap (per-KU evidence complete). 26 evidence-based "
        "classifications (21 SD + 3 PO + 2 CC; 68 KUs; 88 byte-exact quotes; OC-ext009-0026 LayerNorm-preference "
        "added at review per CG-1). Independent review EXT-009-REVIEW: PASS-WITH-NOTES — 86/86 quotes byte-exact "
        "at exactly the stated source lines (0 off-by-one), 25/25 cross-vault, 25 AGREE + 0 BORDERLINE + 0 "
        "DISAGREE; repairs R1 (LayerNorm record + 0018 master-only clause correction) and R2 (four rationale "
        "line-reference errors) applied; suggestions S1-S5 applied (S5 as handoff synthesis-connections notes); "
        "orchestrator addendum records every repair. generalization-v1 dossier (26 concepts / 68 KUs); schema "
        "domain enum extended additively; ALL FIVE dossiers regenerate byte-identically. Registry 1229 KUs / 128 "
        "classifications / 372 participating / valid. Suite 415/415; capabilities 16+1. Deliberate non-records "
        "(single-vault in scope, review-verified): master-ai-only — bias-variance decomposition derivation, "
        "double descent / interpolation regimes, LLM-specific levers (LoRA, SFT, prompt overfitting), elastic net "
        "+ ridge/lasso prior interpretations, weight tying, RMSNorm, text/audio augmentation lists; ai-course-"
        "only — BN four-step math, ICS + Santurkar caveat, running statistics / eval-mode mechanics, GN/IN "
        "alternatives, Bernoulli-mask algebra, mixup/cutmix/RandAugment mechanics, Gaussian-noise/random-erasing "
        "implementations, invariance philosophy. PUSH BLOCKER RESOLVED at session start (7d9e65f..58ad0fa pushed "
        "to origin/main with a fresh PAT; docs commit 7041d47). 26 of 609 source files extracted after this "
        "task. No dispositions assigned. Next: EXT-010 (training-stability pair reserved by this task's scope "
        "notes, or CAP-014 — decide with evidence at session start)."
    ),
    "tests_run": TESTS_RUN,
}


def main() -> int:
    if WORK_COMMIT:
        TASK_RECORD["commit"] = WORK_COMMIT

    # 1. Replace the ready EXT-009 record with the completed record.
    tq = REPO / "state" / "task-queue.jsonl"
    lines = [l for l in tq.read_text(encoding="utf-8").splitlines() if l.strip()]
    seen = False
    for i, l in enumerate(lines):
        rec = json.loads(l)
        if rec.get("task_id") == "EXT-009":
            lines[i] = json.dumps(TASK_RECORD, ensure_ascii=False, sort_keys=True)
            seen = True
            break
    if not seen:
        lines.append(json.dumps(TASK_RECORD, ensure_ascii=False, sort_keys=True))
    tq.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("task-queue: EXT-009 completed record written (replaced ready placeholder)" if seen
          else "task-queue: EXT-009 completed record appended")

    # 2. Update current-state.json
    cs_path = REPO / "state" / "current-state.json"
    cs = json.loads(cs_path.read_text(encoding="utf-8"))
    cs["last_verified_checkpoint"] = "state/checkpoints/checkpoint-2026-10-27-ext-009.json"
    cs["current_task_id"] = "EXT-010"
    cs["notes"] = (
        "EXT-009 completed 2026-10-27 across TWO sessions (interrupted mid-repair by a tool-infrastructure "
        "failure; the completing session re-verified the review claims at source before applying the remaining "
        "repairs). Generalization/regularization domain pair — FIRST PARTIAL-FOLDER ai-course scope (04.3 files "
        "05/06/07 of 7, per-file justification in the task record): batches 008 (106 KUs, master-ai "
        "Generalization 2 files) + 009 (234 KUs) double-run byte-identical; term map 65 terms / 40 aliases / 38 "
        "cross-vault / 2 bridged, machine-verified; 26 evidence-based classifications (21 SD + 3 PO + 2 CC, 68 "
        "KUs, 88 byte-exact quotes, OC-ext009-0026 added at review per CG-1); independent review "
        "PASS-WITH-NOTES with all repairs R1-R2 + suggestions S1-S5 applied; generalization-v1 dossier (26 "
        "concepts, schema enum extended additively, all five dossiers byte-identical); registry 1229 KUs / 128 "
        "classifications / 372 participating; suite 415/415. PUSH BLOCKER RESOLVED this session: "
        "7d9e65f..58ad0fa (EXT-005..EXT-008) pushed to origin/main with a fresh PAT (docs commit 7041d47). "
        "EXT-010 ready to be selected at next session start (training-stability pair reserved by EXT-009's "
        "scope notes: master-ai '11 - Training/Optimization/05 - Loss Spikes and Stability.md' + ai-course 04.3 "
        "files 01-03; or CAP-014 — decide with evidence)."
    )
    kr = cs["knowledge_registry"]
    kr["records"] = 1229
    kr["classifications"] = (
        "state/classifications/001-ext003-regression-overlap.jsonl (14 records) + "
        "002-ext004-tree-based-overlap.jsonl (28 records) + "
        "003-ext005-evaluation-overlap.jsonl (29 records) + "
        "004-ext007-evaluation-addendum.jsonl (4 records) + "
        "005-ext008-clustering-dimreduction-overlap.jsonl (27 records) + "
        "006-ext009-generalization-overlap.jsonl (26 records, EXT-009; ADR-0009 pair-level overlay)"
    )
    kr["dossiers"]["files"]["generalization-v1.json"] = "26 concepts / 68 KUs (from 006-ext009)"
    kr["dossiers"]["concepts_total"] = 128
    kr["dossiers"]["participating_kus_total"] = 372
    cs_path.write_text(json.dumps(cs, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("current-state.json updated")

    # 3. Write the checkpoint.
    cp = {
        "checkpoint_id": "CHK-2026-10-27-EXT-009",
        "created_utc": "2026-10-27T00:00:00+00:00",
        "stage": "extraction",
        "task_id": "EXT-009",
        "task_status": "completed",
        "last_verified_state": {
            "framework_version": "0.5.0 (unchanged in EXT-009 — no framework code changes)",
            "test_result": "415 passed, 0 failed, 0 skipped",
            "test_evidence": "reports/extraction/ext009-pytest-report.json",
            "capabilities_evidence": "reports/extraction/ext009-capabilities.json (16 implemented-and-tested, 1 planned: CAP-014)",
            "registry_store": "state/knowledge-units/ (1229 records in 9 committed batches, unedited)",
            "derived_index": "state/registries/kuregistry.db (rebuilt: init --force + load x9 + apply-overlap x6; kureg-validate valid, 0 errors/warnings)",
            "classifications": {
                "paths": [
                    "state/classifications/001-ext003-regression-overlap.jsonl (14 records)",
                    "state/classifications/002-ext004-tree-based-overlap.jsonl (28 records)",
                    "state/classifications/003-ext005-evaluation-overlap.jsonl (29 records)",
                    "state/classifications/004-ext007-evaluation-addendum.jsonl (4 records)",
                    "state/classifications/005-ext008-clustering-dimreduction-overlap.jsonl (27 records)",
                    "state/classifications/006-ext009-generalization-overlap.jsonl (26 records)",
                ],
                "total": 128,
                "participating_kus": 372,
            },
            "dossiers": {
                "paths": [
                    "state/dossiers/regression-v1.json (14 concepts / 61 KUs)",
                    "state/dossiers/tree-based-v1.json (28 concepts / 82 KUs)",
                    "state/dossiers/evaluation-v1.json (33 concepts / 97 KUs)",
                    "state/dossiers/clustering-v1.json (27 concepts / 64 KUs)",
                    "state/dossiers/generalization-v1.json (26 concepts / 68 KUs)",
                ],
                "regeneration": "all five byte-identical (scripts/ext006_dossiers.py --check exit 0 x5)",
                "schema_change": "schemas/concept-dossier.schema.json domain enum extended additively with 'generalization' (justification in schema description)",
            },
            "source_immutability": "both vaults verified unchanged before and after (verify-manifest exit 0 x4)",
            "push_state": "RESOLVED — 7d9e65f..58ad0fa pushed to origin/main (2026-10-27, fresh PAT); local main == origin/main before the EXT-009 commits",
        },
        "acceptance_evidence": [
            "Batches 008/009 double-run byte-identical (per part and full concat)",
            "Fidelity 106/106 + 234/234 byte-exact + unique ids vs 889 committed (reports/extraction/ext009-fidelity-{master-ai,ai-course}.json)",
            "Term map machine-verified, zero invented entries (reports/extraction/ext009-term-map-verification.json)",
            "Discovery 2961 pairs / 40 cross-vault topics / 5 truncated (reports/extraction/ext009-overlap-candidates.json)",
            "26 classifications, 88 byte-exact quotes, X1-X9 chain green (state/classifications/006-ext009-generalization-overlap.jsonl)",
            "Independent review PASS-WITH-NOTES, all repairs applied (reports/extraction/ext009-review.md + orchestrator addendum)",
            "Registry rebuild valid: 1229 KUs / 128 classifications / 372 participating (reports/extraction/ext009-kureg-validate.json)",
            "Full test suite passes (415/415); capabilities --verify passes (16+1)",
        ],
        "next_task": "EXT-010 (to be selected at next session start with evidence): training-stability pair (master-ai '11 - Training/Optimization/05 - Loss Spikes and Stability.md' + ai-course 04.3 files 01-03, reserved by the EXT-009 scope notes) or CAP-014 source-to-output coverage reports (required before synthesis batches are accepted; no synthesis batch exists yet)",
    }
    if WORK_COMMIT:
        cp["work_commit"] = WORK_COMMIT
    cp_path = REPO / "state" / "checkpoints" / "checkpoint-2026-10-27-ext-009.json"
    cp_path.write_text(json.dumps(cp, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("checkpoint written:", cp_path.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
