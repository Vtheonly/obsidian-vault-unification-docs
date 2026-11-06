#!/usr/bin/env python3
"""EXT-008: state updates (task record, current-state, checkpoint).

Run AFTER all EXT-008 work is verified. Appends the completed EXT-008 record
(with tests_run evidence) to state/task-queue.jsonl, updates
state/current-state.json, and writes the checkpoint.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

TASK_RECORD = {
    "task_id": "EXT-008",
    "title": "Clustering/dimensionality-reduction domain pair (SCOPE CHANGE from SVM — decided with evidence per the task's own contingency clause: master-ai has no dedicated SVM content; 16 occurrences in 11 files are all passing mentions: roadmap checkbox, history timeline, LlamaIndex 'support vector indexes', linear-attention 'kernel')",
    "priority": "high",
    "status": "completed",
    "dependencies": ["EXT-007"],
    "findings": ["F-0001", "F-0002", "F-0003"],
    "inputs": [
        "master-ai side: '03 - Machine Learning/Unsupervised Learning/04 - Clustering and Dimensionality Reduction.md' (152 lines, never extracted)",
        "ai-course side: '03 - Machine Learning/03.5 - K-Means Clustering' (1 file) + '03 - Machine Learning/03.8 - Dimensionality Reduction' (2 files), never extracted",
        "state/term-maps/ pattern (regression/tree/evaluation exemplars; clustering-domain-v1.json built from ACTUAL batch content, pre-probed vocabulary — EXT-005 pattern)",
        "schemas/overlap-classification.schema.json + scripts/ext005/007_classifications.py generator pattern (byte-exact quote verification chain)",
        "scripts/ext006_dossiers.py DOMAINS config + schemas/concept-dossier.schema.json domain enum (extended additively with 'clustering', justification recorded in the schema description)",
    ],
    "outputs": [
        "state/knowledge-units/006-ext008-master-ai-unsupervised.jsonl (27 KUs, double-run byte-identical, sha256 090573e4...)",
        "state/knowledge-units/007-ext008-ai-course-clustering-dimreduction.jsonl (87 KUs = 41 from 03.5 + 46 from 03.8, two deterministic single-scope runs concatenated in fixed order, each part double-run byte-identical, concat re-verified, sha256 0a49a9fe...)",
        "scripts/ext008_fidelity.py (both batches; ID-uniqueness check extended to also cover committed batches 001-005)",
        "state/term-maps/clustering-domain-v1.json (51 terms, 22 aliases, 32 cross-vault, 3 bridged; every entry machine-verified in-scope; French alias 'regroupement' verified at ai-course 03.5 L4)",
        "reports/extraction/ext008-overlap-candidates.json + -pairs.jsonl (934 pairs, 35 cross-vault topics, 0 truncated)",
        "state/classifications/005-ext008-clustering-dimreduction-overlap.jsonl (27 records: 22 SD + 4 PO + 1 CC; 64 participating KUs; 92 byte-exact quotes; generator chain X1-X9)",
        "reports/extraction/ext008-review.md (independent EXT-008-REVIEW, PASS-WITH-NOTES; all repairs R1-R3 + suggestions S1-S5 applied, orchestrator addendum recorded)",
        "state/dossiers/clustering-v1.json (27 concepts / 64 KUs; schema domain enum extended; all four dossiers regenerate byte-identically)",
        "registry rebuilt (init --force + load x7 + apply-overlap x5) and valid; task-queue/current-state/checkpoint/handoff updates",
    ],
    "acceptance_criteria": [
        "Every scope file has a verified extraction outcome (extraction or documented exclusion); batches double-run byte-identical",
        "Fidelity: every excerpt byte-exact vs source, hashes match, ids unique within and across batches, 0 heading crossings",
        "Term map machine-verified: every canonical term and alias occurs in an in-scope KU excerpt (no invented entries)",
        "Classifications carry byte-exact quotes verified in KU excerpts AND at original source lines; independent review verdict recorded with repairs applied before commit",
        "Sources unchanged before/after; registry validates clean; all KUs remain Unaccounted",
        "Full test suite passes; dossier regeneration byte-identical including the new clustering domain",
    ],
    "forbidden_side_effects": [
        "Do not modify source vaults",
        "Do not edit committed batches, classification files, or dossiers by hand (dossiers regenerate via script)",
        "Do not assign dispositions",
        "Do not skip the independent review for committed classifications",
    ],
    "notes": (
        "SCOPE CHANGE decided with evidence at session start per the task record's own contingency clause "
        "('Alternative next tasks if SVM proves ill-scoped at session start (decide with evidence): ... another "
        "domain pair from the unextracted Master AI files'): full-vault search found master-ai has NO dedicated "
        "SVM content (Supervised Learning holds only Regression + Decision Trees/Gradient Boosting; the 16 "
        "SVM/kernel occurrences in 11 files are passing mentions — roadmap checkbox 'SVM, kNN', history-timeline "
        "entries, 'support vector indexes' about vector DBs in LlamaIndex, and 'kernel' in the linear-attention "
        "papers sense). The clustering/dimensionality-reduction pair (master-ai Unsupervised Learning/04 vs "
        "ai-course 03.5 + 03.8) has rich real content on both sides. Executed end-to-end per the EXT-005 "
        "two-sided pattern: batch 006 = master-ai file (43... corrected: 27 KUs, 1/1 files, double-run "
        "byte-identical, sha256 090573e4...); batch 007 = ai-course two folders as two deterministic "
        "single-scope runs concatenated in fixed order (03.5: 41 KUs 1/1 files; 03.8: 46 KUs 2/2 files; parts "
        "and full concat double-run byte-identical, sha256 0a49a9fe...). Fidelity scripts/ext008_fidelity.py: "
        "27/27 + 87/87 byte-exact excerpts + hashes + structural purity + 0 heading crossings + unique ids "
        "within/across new batches AND vs all 775 committed ids (extension over the EXT-005 checker). Term map "
        "built from ACTUAL batch content after two probe rounds (state/term-maps/clustering-domain-v1.json: 51 "
        "terms, 22 aliases, 32 cross-vault, 3 BRIDGED terms — 'choosing k'/'choose k'/'number of clusters', "
        "'nonlinear'/'non-linear', 'sklearn'/'scikit-learn'; French probe found only 'regroupement' at 03.5 L4, "
        "included as clustering alias; spurious-match source 'scale' -> 'large-scale' documented in the map "
        "comment). CAP-013 discovery: 318... corrected: 114 KUs in scope, 934 pairs, 35 cross-vault topics, 0 "
        "truncated. 27 evidence-based classifications in 005-ext008 (22 SD + 4 PO + 1 CC; 64 participating "
        "KUs; 92 byte-exact quotes; generator scripts/ext008_classifications.py chain X1-X9 verifies every "
        "quote byte-exact in the KU excerpt AND at the stated original-source line, plus cross-vault, schema, "
        "sequential ids, no duplicate quotes anywhere in the file, and committed classification files 001-004 "
        "byte-unchanged). Independent review EXT-008-REVIEW (read-only subagent): PASS-WITH-NOTES — 89/89 "
        "quotes byte-exact at exactly the stated source lines (0 off-by-one), 27/27 cross-vault, 26 AGREE + 1 "
        "AGREE-BORDERLINE + 0 DISAGREE, 0 coverage gaps, no duplication vs committed records, append-only "
        "discipline verified. ALL repairs R1-R3 (rationale wording: 0001 simplicity master-only; 0024 UMAP "
        "determinism course-only, shared core = PCA-vs-t-SNE contrast; 0022 cross-reference + comparative-"
        "framing fix) and ALL suggestions S1-S5 (0003 intra/inter scoping; 0006 challenge-premise KU + "
        "heuristicality/failure-mode distinction; 0015 TL;DR/compression credit fix + EDA KU; 0025 baseline-"
        "attribute scoping; 0026 standard-tools quote) applied after orchestrator re-verification; final 27 "
        "records, 64 KUs, 92 quotes (3 new quotes each verified at source line before adding). R4: schema "
        "domain enum extended additively with 'clustering' (justification in schema description); "
        "scripts/ext006_dossiers.py DOMAINS extended; clustering-v1.json generated (27 concepts / 64 KUs; "
        "zero-evidence categories: interview_misconceptions_comparisons, historical_deprecated); all FOUR "
        "dossiers regenerate byte-identically (--check exit 0 x4); tests/test_concept_dossier.py DOSSIER_FILES "
        "extended + test renamed (suite still 415/415). Registry rebuilt: init --force + load x7 (298+65+94+43"
        "+275+27+87 = 889 KUs) + apply-overlap x5 (14+28+29+4+27 = 102 classifications, 0 rejected) + "
        "kureg-validate valid (889 KUs, 102 classifications, 304 participating KUs, all KUs Unaccounted; "
        "by type 67 SD + 31 PO + 3 CC + 1 CHD). Sources unchanged before/after (verify-manifest exit 0 x4). "
        "Deliberate non-records (verified single-vault in scope): silhouette (master-ai only; ai-course "
        "silhouette teaching lives in batch 005/03.6 — cross-batch connection noted for synthesis), curse of "
        "dimensionality (ai-course only), K-Means++/n_init/K-Medians (ai-course only), mini-batch k-means + "
        "vector-DB ANN indexing (master-ai only), SVD/eigendecomption/covariance mechanics + Student-t/"
        "crowding + Riemannian/fuzzy-topology mechanics (ai-course only), VAE/denoising/contractive variants "
        "(master-ai only). No dispositions assigned. Next: EXT-009 queued."
    ),
    "tests_run": [
        {
            "step": "startup protocol (inherited from the EXT-007 session)",
            "command": "vu selftest + pytest + verify-manifest both vaults + kureg-validate",
            "result": "selftest exit 0; 415/415; both vaults unchanged (333 + 276); registry valid (775 KUs, 75 classifications, 240 participating)",
            "evidence": "reports/extraction/ext007-immutable-{master-ai,ai-course}.json + ext007-kureg-final-validate.json",
        },
        {
            "step": "scope decision (SVM -> clustering)",
            "command": "full-vault grep for support vector|SVM|kernel trick|kernel method + ML folder listing",
            "result": "master-ai has NO dedicated SVM content (16 occurrences in 11 files, all passing mentions); contingency clause invoked with evidence",
            "evidence": "session transcript + task record notes",
        },
        {
            "step": "extraction master-ai (batch 006)",
            "command": "extract-kus --root 'source-vaults/AI /Master AI' --scope '03 - Machine Learning/Unsupervised Learning/04 - Clustering and Dimensionality Reduction.md' --vault-id master-ai (+ double-run cmp)",
            "result": "exit 0; 1/1 files, 27 KUs; byte-identical (sha256 090573e4149209781e92b71e51b936ffd59d1e4fa997ef8b886c2a78d1f95f4f)",
            "evidence": "reports/extraction/ext008-coverage-master-ai.json + ext008-determinism-master-ai.txt",
        },
        {
            "step": "extraction ai-course (batch 007, two-scope concat)",
            "command": "extract-kus x2 (03.5, 03.8) + fixed-order concatenation (+ double-run cmp per part AND full concat)",
            "result": "exit 0; 41 + 46 = 87 KUs over 3/3 files; parts and concat byte-identical (sha256 0a49a9fedf00667cbd295ec3869b473de82582577ccdfeffd338e52275b447df)",
            "evidence": "reports/extraction/ext008-coverage-ai-course-03.5.json + ext008-coverage-ai-course-03.8.json + ext008-determinism-ai-course.txt",
        },
        {
            "step": "fidelity both batches",
            "command": "python3 scripts/ext008_fidelity.py",
            "result": "exit 0; 27/27 + 87/87 byte-exact excerpts + hashes + structural purity + 0 heading crossings + unique ids within/across new batches and vs 775 committed ids",
            "evidence": "reports/extraction/ext008-fidelity-{master-ai,ai-course}.json",
        },
        {
            "step": "term map build + verification",
            "command": "python3 scripts/ext008_term_map.py (after two probe rounds)",
            "result": "exit 0 first run (51 terms, 22 aliases, 32 cross-vault, 3 bridged; every entry machine-verified in-scope; one French alias regroupement)",
            "evidence": "reports/extraction/ext008-term-map-verification.json + state/term-maps/clustering-domain-v1.json",
        },
        {
            "step": "CAP-013 discovery",
            "command": "vu overlap-candidates --batch 006 --batch 007 --terms clustering-domain-v1.json",
            "result": "exit 0; 114 KUs in scope, 934 pairs, 35 cross-vault topics, 0 hash duplicates, 0 truncated topics",
            "evidence": "reports/extraction/ext008-overlap-candidates.json + -pairs.jsonl",
        },
        {
            "step": "classification generation",
            "command": "python3 scripts/ext008_classifications.py",
            "result": "exit 0 pre-review (27 records, 89 quotes) and final post-review (27 records, 92 quotes); every quote verified byte-exact in excerpts AND at original source lines; schema + X1-X9 valid",
            "evidence": "state/classifications/005-ext008-clustering-dimreduction-overlap.jsonl + stdout",
        },
        {
            "step": "independent review",
            "command": "EXT-008-REVIEW subagent (read-only)",
            "result": "PASS-WITH-NOTES: 89/89 quotes byte-exact (0 off-by-one), 27/27 cross-vault, 26 AGREE + 1 AGREE-BORDERLINE + 0 DISAGREE, 0 coverage gaps, no duplication vs committed records, append-only verified; 3 required repairs (R1-R3 wording) + R4 process + 5 suggestions (S1-S5)",
            "evidence": "reports/extraction/ext008-review.md",
        },
        {
            "step": "repairs applied (orchestrator re-verified each claim first)",
            "command": "edit scripts/ext008_classifications.py + regenerate",
            "result": "R1-R3 + S1-S5 applied (each new quote verified at its source line BEFORE adding: 03.5 L106, t-SNE file L42, t-SNE file L6); final 27 records (22 SD + 4 PO + 1 CC), 64 participating KUs, 92 byte-exact quotes; committed classification files 001-004 byte-unchanged",
            "evidence": "reports/extraction/ext008-review.md orchestrator addendum",
        },
        {
            "step": "dossier extension (R4)",
            "command": "schema enum extension + scripts/ext006_dossiers.py DOMAINS + regenerate x2 + --check",
            "result": "clustering-v1.json: 27 concepts / 64 KUs (zero-evidence: interview_misconceptions_comparisons, historical_deprecated); all four dossiers byte-identical (--check exit 0 x4); regression/tree/evaluation dossiers byte-unchanged vs EXT-007 state",
            "evidence": "reports/extraction/ext006-dossier-coverage.json (updated) + state/dossiers/clustering-v1.json",
        },
        {
            "step": "registry rebuild (R4)",
            "command": "kureg-init --force + kureg-load x7 + kureg-apply-overlap x5 + kureg-validate",
            "result": "exit 0 x13; 889 KUs, 102 classifications (14+28+29+4+27), 0 rejected, valid 0 errors/warnings; 304 participating KUs; all 889 Unaccounted",
            "evidence": "reports/extraction/ext008-kureg-*.json",
        },
        {
            "step": "full test suite + capabilities + immutability + validations",
            "command": "pytest -q; vu capabilities --verify; vu verify-manifest x2; vu validate-registry --tasks + --classifications",
            "result": "415/415; 16 implemented-and-tested + 1 planned; both vaults unchanged (333 + 276); task queue valid; 005-ext008 valid",
            "evidence": "reports/extraction/ext008-pytest-report.json + ext008-capabilities.json + ext008-immutable-{master-ai,ai-course}.json + ext008-taskqueue-validate.json",
        },
    ],
}


def main() -> int:
    # 1. Append EXT-008 completed record to the task queue.
    tq = REPO / "state" / "task-queue.jsonl"
    lines = [l for l in tq.read_text(encoding="utf-8").splitlines() if l.strip()]
    existing_ids = []
    for l in lines:
        rec = json.loads(l)
        existing_ids.append(rec.get("task_id"))
        if rec.get("task_id") == "EXT-008":
            # replace the ready placeholder with the completed record
            lines[lines.index(l)] = json.dumps(TASK_RECORD, ensure_ascii=False, sort_keys=True)
            break
    else:
        lines.append(json.dumps(TASK_RECORD, ensure_ascii=False, sort_keys=True))
    tq.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("task-queue: EXT-008 completed record written; ids:", existing_ids)

    # 2. Update current-state.json
    cs_path = REPO / "state" / "current-state.json"
    cs = json.loads(cs_path.read_text(encoding="utf-8"))
    cs["last_verified_checkpoint"] = "state/checkpoints/checkpoint-2026-10-27-ext-008.json"
    cs["current_task_id"] = "EXT-009"
    cs["notes"] = (
        "EXT-008 completed 2026-10-27 (clustering/dimensionality-reduction domain pair — SCOPE CHANGE from "
        "SVM with evidence: master-ai has no dedicated SVM content, contingency clause invoked; batches 006 "
        "(27 KUs) + 007 (87 KUs, two-scope concat) double-run byte-identical; term map 51 terms/22 aliases "
        "machine-verified; 27 evidence-based classifications (22 SD + 4 PO + 1 CC, 64 KUs, 92 byte-exact "
        "quotes); independent review PASS-WITH-NOTES with all repairs R1-R3 + suggestions S1-S5 applied; "
        "clustering-v1 dossier (27 concepts); registry 889 KUs / 102 classifications / 304 participating; "
        "suite 415/415; schema domain enum extended additively). EXT-009 ready (next unextracted domain or "
        "CAP-014 — decide at session start). PUSH BLOCKER STILL OPEN: local main is 8+ commits ahead of "
        "origin/main; the session delivered a zip + git bundle for the user to push personally."
    )
    kr = cs["knowledge_registry"]
    kr["records"] = 889
    kr["classifications"] = (
        "state/classifications/001-ext003-regression-overlap.jsonl (14 records) + "
        "002-ext004-tree-based-overlap.jsonl (28 records) + "
        "003-ext005-evaluation-overlap.jsonl (29 records) + "
        "004-ext007-evaluation-addendum.jsonl (4 records) + "
        "005-ext008-clustering-dimreduction-overlap.jsonl (27 records, EXT-008; ADR-0009 pair-level overlay)"
    )
    kr["dossiers"]["files"]["clustering-v1.json"] = "27 concepts / 64 KUs (from 005-ext008)"
    kr["dossiers"]["concepts_total"] = 102
    kr["dossiers"]["participating_kus_total"] = 304
    cs_path.write_text(json.dumps(cs, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("current-state.json updated")

    # 3. Write the checkpoint.
    cp = {
        "checkpoint_id": "CHK-2026-10-27-EXT-008",
        "created_utc": "2026-10-27T00:00:00+00:00",
        "stage": "extraction",
        "task_id": "EXT-008",
        "task_status": "completed",
        "last_verified_state": {
            "framework_version": "0.5.0 (unchanged in EXT-008 — no framework code changes)",
            "test_result": "415 passed, 0 failed, 0 skipped",
            "test_evidence": "reports/extraction/ext008-pytest-report.json",
            "capabilities_evidence": "reports/extraction/ext008-capabilities.json (16 implemented-and-tested, 1 planned: CAP-014)",
            "registry_store": "state/knowledge-units/ (889 records in 7 committed batches, unedited)",
            "derived_index": "state/registries/kuregistry.db (rebuilt: init --force + load x7 + apply-overlap x5; kureg-validate valid, 0 errors/warnings)",
            "classifications": {
                "paths": [
                    "state/classifications/001-ext003-regression-overlap.jsonl (14 records)",
                    "state/classifications/002-ext004-tree-based-overlap.jsonl (28 records)",
                    "state/classifications/003-ext005-evaluation-overlap.jsonl (29 records)",
                    "state/classifications/004-ext007-evaluation-addendum.jsonl (4 records)",
                    "state/classifications/005-ext008-clustering-dimreduction-overlap.jsonl (27 records)",
                ],
                "total": 102,
                "participating_kus": 304,
            },
            "dossiers": {
                "paths": [
                    "state/dossiers/regression-v1.json (14 concepts / 61 KUs)",
                    "state/dossiers/tree-based-v1.json (28 concepts / 82 KUs)",
                    "state/dossiers/evaluation-v1.json (33 concepts / 97 KUs)",
                    "state/dossiers/clustering-v1.json (27 concepts / 64 KUs)",
                ],
                "regeneration": "all four byte-identical (scripts/ext006_dossiers.py --check exit 0 x4)",
                "schema_change": "schemas/concept-dossier.schema.json domain enum extended additively with 'clustering' (justification in schema description)",
            },
            "source_immutability": "both vaults verified unchanged before and after (verify-manifest exit 0 x4)",
            "scope_change": "SVM -> clustering/dimensionality reduction, decided with evidence per the task record's contingency clause (master-ai has no dedicated SVM content)",
        },
        "acceptance_evidence": [
            "Batches 006/007 double-run byte-identical (reports/extraction/ext008-determinism-{master-ai,ai-course}.txt)",
            "Fidelity 27/27 + 87/87 byte-exact + unique ids vs 775 committed (reports/extraction/ext008-fidelity-{master-ai,ai-course}.json)",
            "Term map machine-verified, zero invented entries (reports/extraction/ext008-term-map-verification.json)",
            "Discovery 934 pairs / 35 cross-vault topics / 0 truncated (reports/extraction/ext008-overlap-candidates.json)",
            "27 classifications, 92 byte-exact quotes, X1-X9 chain green (state/classifications/005-ext008-clustering-dimreduction-overlap.jsonl)",
            "Independent review PASS-WITH-NOTES, all repairs applied (reports/extraction/ext008-review.md + orchestrator addendum)",
            "Registry rebuild valid: 889 KUs / 102 classifications / 304 participating (reports/extraction/ext008-kureg-validate.json)",
            "Full test suite passes (415/415); capabilities --verify passes (16+1)",
        ],
        "next_task": "EXT-009 (to be selected at next session start): remaining unextracted Master AI ML files (Generalization: Bias-Variance Tradeoff + Regularization Techniques; Reinforcement Learning x4 files) or CAP-014 source-to-output coverage reports; the standing rule applies: never work in a fresh clone while local-only commits exist",
        "push_blocker": "STILL OPEN — local main ahead of origin/main (EXT-005 verification + EXT-006 + EXT-007 + EXT-008 commits); all provided PATs were rejected 2026-10-26/27 (401). User pushes the delivered zip/bundle; do NOT re-clone while local-only commits exist.",
    }
    cp_path = REPO / "state" / "checkpoints" / "checkpoint-2026-10-27-ext-008.json"
    cp_path.write_text(json.dumps(cp, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("checkpoint written:", cp_path.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
