#!/usr/bin/env python3
"""EXT-010: append the task record to state/task-queue.jsonl (idempotent)."""
import json
import sys

QUEUE = "state/task-queue.jsonl"

record = {
    "task_id": "EXT-010",
    "title": "Training-stability domain pair (master-ai '04 - Neural Networks/Training' init/gradient files 07+08 + AI Course 04.3 files 01-03 weight-init/vanishing-exploding-gradients — the counterpart family ADJUSTED from the EXT-009 reservation on heading evidence; the '11 - Training' LLM-operations files are reserved for a future pair)",
    "status": "ready",
    "priority": "high",
    "dependencies": ["EXT-009"],
    "inputs": [
        "source vaults (read-only): 'source-vaults/AI /Master AI' (333 files) and 'source-vaults/AI /AI Course' (276 files)",
        "state/manifests/{master-ai,ai-course}.jsonl (baseline hashes)",
        "CAP-016 vu extract-kus (vault-ids 'master-ai' and 'ai-course' - pinned)",
        "master-ai side (2 of 3 files in '04 - Neural Networks/Training', each fence-balanced per F-0002 check, never extracted): '07 - Initialization Schemes.md' (259 lines, 16219 bytes) + '08 - Vanishing and Exploding Gradients.md' (293 lines, 18580 bytes)",
        "ai-course side (3 of 7 files in '04 - Neural Networks and Deep Learning Foundations/04.3 - Training Dynamics and Stability', each fence-balanced, never extracted): '01. Weight Initialization.md' (792 lines, 58081 bytes) + '02. Weight Initialization Techniques.md' (73 lines, 7496 bytes) + '03. The Vanishing and Exploding Gradient Problems.md' (1082 lines, 71416 bytes)",
        "state/term-maps/ pattern (five exemplar maps; training-stability-domain-v1.json to be built from ACTUAL batch content, pre-probed vocabulary - EXT-005/EXT-008/EXT-009 pattern)",
        "CAP-013 vu overlap-candidates + vu kureg-apply-overlap (word-boundary, mermaid-safe; F-0006 rules mandatory)",
        "schemas/overlap-classification.schema.json + scripts/ext009_classifications.py generator pattern (byte-exact quote verification chain X1-X9)",
        "scripts/ext006_dossiers.py DOMAINS config + schemas/concept-dossier.schema.json domain enum (additive 'training-stability' extension per the EXT-008/EXT-009 precedent, justification recorded in the schema description)"
    ],
    "outputs": [
        "state/knowledge-units/010-ext010-master-ai-training-stability.jsonl (two deterministic single-file runs concatenated in fixed order 07, 08; each part double-run byte-identical)",
        "state/knowledge-units/011-ext010-ai-course-04.3-init-gradients.jsonl (three deterministic single-file runs concatenated in fixed order 01, 02, 03; each part and the full concat double-run byte-identical)",
        "state/term-maps/training-stability-domain-v1.json (term/alias map built from the ACTUAL content of both batches, machine-verified, zero invented entries)",
        "reports/extraction/ext010-overlap-candidates.json + -pairs.jsonl (CAP-013 run over both new batches)",
        "state/classifications/007-ext010-training-stability-overlap.jsonl (evidence-based classifications with byte-exact quotes and rationale per record; generator verifies quotes byte-exact before writing)",
        "scripts/ext010_fidelity.py (both batches; id-uniqueness extended over all committed batches 001-009)",
        "registry rebuilt with batches 001-011 + all classifications applied; kureg-validate clean",
        "state/dossiers/training-stability-v1.json (new domain; all six dossiers regenerate byte-identically)",
        "evidence reports: coverage x5 (per part), determinism, fidelity, kureg-*, immutable-*, pytest, capabilities, review, taskqueue-validate"
    ],
    "acceptance_criteria": [
        "Every scope file has a verified extraction outcome (extraction or documented exclusion); batches double-run byte-identical (per part and full concat for both sides)",
        "Fidelity: every excerpt byte-exact vs source, hashes match, ids unique within and across batches AND vs all committed ids, 0 heading crossings",
        "Term map machine-verified: every canonical term and alias occurs in an in-scope KU excerpt (no invented entries)",
        "Classifications carry byte-exact quotes verified in KU excerpts AND at original source lines; independent review verdict recorded with repairs applied before commit",
        "Sources unchanged before/after; registry validates clean; all KUs remain Unaccounted",
        "Full test suite passes; dossier regeneration byte-identical including the new training-stability domain"
    ],
    "forbidden_side_effects": [
        "Do not modify source vaults",
        "Do not edit committed batches, classification files, or dossiers by hand (dossiers regenerate via script)",
        "Do not assign dispositions",
        "Do not skip the independent review for committed classifications"
    ],
    "findings": ["F-0001", "F-0002", "F-0003", "F-0006"],
    "notes": "SCOPE DECISION with evidence at session start (EXT-009 handoff reserved a 'training-stability pair' = master-ai '11 - Training/Optimization/05 - Loss Spikes and Stability.md' + ai-course 04.3 files 01-03 but explicitly required verifying the master-ai file covers init/gradient-stability content BEFORE committing; the same evidence-first scoping discipline as EXT-008/EXT-009): (1) COUNTERPART ADJUSTED. scripts/ext010_scope_probe.py (mdextract.extract_structure_text, CAP-003 authority) shows master-ai '05 - Loss Spikes and Stability.md' is an LLM-PRETRAINING-OPERATIONS file (headings: Why Loss Spikes Happen - bad data batches / numerical instability / optimizer state / LR issues / genuine model instability at scale; Detecting via loss/gradient-norm/weight-norm/activation monitoring; Preventing via gradient clipping, LR warmup, loss scaling FP16, weight decay, stable initialization; Handling via skip-batch, checkpoint rollback, reduce LR, switch to BF16, inspect data; Production practices) - NOT the classical init/vanishing-gradient theory that ai-course 01-03 teach. The TRUE counterpart family is master-ai '04 - Neural Networks/Training': 07 Initialization Schemes (why init matters, Xavier/Glorot tanh/sigmoid, He/Kaiming ReLU family, bias init, worked example, derivation forward/backward-pass analysis with Xavier compromise and He correction, transformer init recipe, LoRA init, MuP/Tensor Programs/Fixup research, failure modes, interview questions) pairs section-by-section with course 01 (symmetry problem, constant-init explosion/vanishing, N(0,0.01)/N(0,1) variance-mismatch, Xavier/Glorot derivation forward+backward, Kaiming factor-of-2 correction, PyTorch defaults Kaiming-uniform, manual/orthogonal/sparse init, when init matters) and course 02 (CNN zero-init catastrophe, random-init failure, Kaiming math, comparison, PyTorch impl); 08 Vanishing and Exploding Gradients (mechanism, where each happens, diagnosing, solutions ReLU family / residual connections / LayerNorm-RMSNorm / proper initialization / gradient clipping / gated LSTM-GRU / attention, math analysis incl. RNN vulnerability, detailed solution comparison, modern Transformer context, worked examples, failure modes, interview questions) pairs with course 03 (gradients as Jacobian products, sigmoid 0.25 derivative ceiling, compounding, tanh variant, exploding symptoms/causes, four solutions ReLU-family incl. dying ReLU/Leaky/PReLU + BatchNorm + residual +1-term proof + gradient clipping by norm/value, per-layer gradient-norm diagnosis, NaN monitoring, dashboards). Both master files verified never extracted (26 distinct source_paths committed, all 5 scope files absent). (2) DELIBERATE EXCLUSIONS (scope decisions, NEVER preservation decisions - files remain unextracted and eligible for later batches): master-ai '04 - Neural Networks/Training/06 - Backpropagation.md' (center of mass is reverse-mode autodiff/BPTT/op-specific gradients/distributed backprop - a distinct domain; its short V&E section does not make it an init/gradient-stability file; eligible for a future backprop/autodiff pair); master-ai '11 - Training/Optimization/05 - Loss Spikes and Stability.md' + '04 - Mixed Precision Training.md' (LLM-training-operations pair candidates for a future session; loss-spikes 'Stable Initialization' section connects to this domain but the file's center of mass is pretraining spike response); ai-course 04.3/04 'Hyperparameters and Network Configuration.md' (optimization/tuning domain per the EXT-009 scope note; reserved as before). After this task the ai-course 04.3 folder is 6 of 7 files extracted (only 04 remains). (3) CAP-014 still NOT RIPE (no synthesis batch exists; output_synthesis_started false). All 5 in-scope files verified fence-balanced with zero mdextract errors (F-0002 does not affect them). 26 of 609 source files extracted before this task.",
}

existing = [json.loads(l) for l in open(QUEUE, encoding="utf-8") if l.strip()]
if any(r.get("task_id") == "EXT-010" for r in existing):
    print("EXT-010 already queued; aborting append")
    sys.exit(1)

with open(QUEUE, "a", encoding="utf-8") as f:
    f.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")

print(f"appended EXT-010; queue now has {len(existing) + 1} records")
