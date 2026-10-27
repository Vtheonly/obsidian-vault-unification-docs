#!/usr/bin/env python3
"""EXT-009: append the task record to state/task-queue.jsonl (idempotent)."""
import json
import sys

QUEUE = "state/task-queue.jsonl"

record = {
    "task_id": "EXT-009",
    "title": "Generalization/regularization domain pair (master-ai Generalization folder + AI Course 04.3 regularization files 05-07 — ai-course side scoped to the regularization-relevant subset of 04.3 with evidence; the weight-init/vanishing-gradient/hyperparameter files 01-04 are reserved for a future training-stability/optimization pair with master-ai '11 - Training')",
    "status": "ready",
    "priority": "high",
    "dependencies": ["EXT-008"],
    "inputs": [
        "source vaults (read-only): 'source-vaults/AI /AI Course' (276 files) and 'source-vaults/AI /Master AI' (333 files)",
        "state/manifests/{ai-course,master-ai}.jsonl (baseline hashes)",
        "CAP-016 vu extract-kus (vault-ids 'ai-course' and 'master-ai' - pinned)",
        "master-ai side (whole folder, exactly 2 files): '03 - Machine Learning/Generalization/01 - Bias Variance Tradeoff.md' (325 lines) + '03 - Machine Learning/Generalization/06 - Regularization Techniques.md' (199 lines), never extracted",
        "ai-course side (3 of 7 files in '04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability', each fence-balanced per F-0002 check): '05. Batch Normalization.md' (597 lines) + '06. Dropout and Regularization.md' (589 lines) + '07. Data Augmentation.md' (734 lines), never extracted",
        "state/term-maps/ pattern (regression/tree/evaluation/clustering exemplars; generalization-domain-v1.json to be built from ACTUAL batch content, pre-probed vocabulary - EXT-005/EXT-008 pattern)",
        "CAP-013 vu overlap-candidates + vu kureg-apply-overlap (word-boundary, mermaid-safe; F-0006 rules mandatory)",
        "schemas/overlap-classification.schema.json + scripts/ext008_classifications.py generator pattern (byte-exact quote verification chain X1-X9)",
        "scripts/ext006_dossiers.py DOMAINS config + schemas/concept-dossier.schema.json domain enum (additive 'generalization' extension per the EXT-008 precedent, justification recorded in the schema description)"
    ],
    "outputs": [
        "state/knowledge-units/008-ext009-master-ai-generalization.jsonl (deterministic extraction of the 2 master-ai Generalization files; every scope file extracted or explicitly excluded/failed with reason)",
        "state/knowledge-units/009-ext009-ai-course-04.3-regularization.jsonl (three deterministic single-file runs concatenated in fixed order 05, 06, 07; each part double-run byte-identical)",
        "state/term-maps/generalization-domain-v1.json (term/alias map built from the ACTUAL content of both batches, machine-verified, zero invented entries)",
        "reports/extraction/ext009-overlap-candidates.json + -pairs.jsonl (CAP-013 run over both new batches)",
        "state/classifications/006-ext009-generalization-overlap.jsonl (evidence-based classifications with byte-exact quotes and rationale per record; generator verifies quotes byte-exact before writing)",
        "scripts/ext009_fidelity.py (both batches; id-uniqueness extended over all committed batches 001-007)",
        "registry rebuilt with batches 001-009 + all classifications applied; kureg-validate clean",
        "state/dossiers/generalization-v1.json (new domain; all five dossiers regenerate byte-identically)",
        "evidence reports: coverage x4 (per part), determinism, fidelity, kureg-*, immutable-*, pytest, capabilities, review, taskqueue-validate"
    ],
    "acceptance_criteria": [
        "Every scope file has a verified extraction outcome (extraction or documented exclusion); batches double-run byte-identical (per part and full concat for the ai-course side)",
        "Fidelity: every excerpt byte-exact vs source, hashes match, ids unique within and across batches AND vs all committed ids, 0 heading crossings",
        "Term map machine-verified: every canonical term and alias occurs in an in-scope KU excerpt (no invented entries)",
        "Classifications carry byte-exact quotes verified in KU excerpts AND at original source lines; independent review verdict recorded with repairs applied before commit",
        "Sources unchanged before/after; registry validates clean; all KUs remain Unaccounted",
        "Full test suite passes; dossier regeneration byte-identical including the new generalization domain"
    ],
    "forbidden_side_effects": [
        "Do not modify source vaults",
        "Do not edit committed batches, classification files, or dossiers by hand (dossiers regenerate via script)",
        "Do not assign dispositions",
        "Do not skip the independent review for committed classifications"
    ],
    "findings": ["F-0001", "F-0002", "F-0003"],
    "notes": "SCOPE DECISION with evidence at session start (handoff left EXT-009 selection to this session): (1) RL pair (handoff candidate 2) RULED OUT - full-vault grep of ai-course for 'q-learning|reinforcement learning|policy gradient|bellman' finds 8 occurrences in 8 files, all single passing mentions (application examples, history lines), no dedicated RL content; same ill-scoped shape as SVM in EXT-008. (2) CAP-014 (handoff alternative) NOT RIPE - required before synthesis batches are accepted, and no synthesis batch exists yet (output_synthesis_started false). (3) Generalization pair (handoff candidate 1) CONFIRMED VIABLE with concentration evidence: master-ai '03 - Machine Learning/Generalization' = exactly 2 dedicated files (bias-variance decomposition/diagnosis 325 lines + regularization techniques 199 lines covering L1/L2/ridge/lasso/elastic-net, dropout, early stopping, data augmentation, label smoothing, batch norm as regularization, weight tying, transformer/LLM specifics); ai-course generalization vocabulary concentrates in DL chapter 04.3 ('bias[- ]variance' phrase is rare in ai-course: 5 occurrences in 4 files; 'overfitting|regulariz' concentrates in 04.3: dropout/reg file 55 hits, batch-norm file 14, augmentation file 5, hyperparameters file 11) and the three files 05/06/07 map section-by-section onto master-ai 06's headings (Batch Normalization section, Dropout section, Data Augmentation section) while file 06's 'Overfitting: The Central Problem' section carries the course-side generalization teaching that pairs with master-ai 01. (4) DELIBERATE PARTIAL-FOLDER SCOPE on the ai-course side, first of its kind, justified per file with headings evidence: 04.3/01 + 02 (weight initialization) and 04.3/03 (vanishing/exploding gradients) are training-stability topics reserved for a future pair with master-ai '11 - Training/Optimization/05 - Loss Spikes and Stability.md' (15583 bytes, verified present); 04.3/04 (hyperparameters/tuning: LR scaling, warmup, tuning strategies) is an optimization/tuning topic, not generalization; the CNN aggregated summary '06. Chapter Summaries/05. Normalization, Regularization and Augmentation - Summary.md' restates 04.3 teaching and is deferred to a later sweep. None of these exclusions is a preservation decision - the files remain unextracted and eligible for later batches (21 of 609 files are extracted before this task; 26 of 609 after it). All 5 in-scope files verified fence-balanced (F-0002 does not affect them).",
}

existing = [json.loads(l) for l in open(QUEUE, encoding="utf-8") if l.strip()]
if any(r.get("task_id") == "EXT-009" for r in existing):
    print("EXT-009 already queued; aborting append")
    sys.exit(1)

with open(QUEUE, "a", encoding="utf-8") as f:
    f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

print(f"appended EXT-009; queue now has {len(existing) + 1} records")
