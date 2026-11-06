#!/usr/bin/env python3
"""EXT-009: build the generalization/regularization domain term map from
ACTUAL batch content.

Scope: batch 008 (master-ai '03 - Machine Learning/Generalization' — 01 Bias
Variance Tradeoff + 06 Regularization Techniques, 2 files, 106 KUs) + batch
009 (ai-course 04.3 files 05 Batch Normalization + 06 Dropout and
Regularization + 07 Data Augmentation, 3 files, 234 KUs). 340 KUs total.

Guarantees enforced before writing state/term-maps/generalization-domain-v1.json:
- every canonical term AND every alias actually occurs (case-insensitive,
  word-boundary) inside at least one KU excerpt in scope — no invented
  vocabulary (probe rounds 1+2 ran first: scripts/ext009_term_probe{,2}.py);
- per-term vault coverage is reported (cross-vault / single-vault preview);
- the map matches the CAP-013 terms format {term: [aliases]}; _-prefixed
  keys are documentation and ignored by the loader.

Writes reports/extraction/ext009-term-map-verification.json. Exits non-zero
on any unverified term/alias. Read-only with respect to source vaults.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BATCH_008 = REPO_ROOT / "state" / "knowledge-units" / "008-ext009-master-ai-generalization.jsonl"
BATCH_009 = REPO_ROOT / "state" / "knowledge-units" / "009-ext009-ai-course-04.3-regularization.jsonl"
OUT = REPO_ROOT / "state" / "term-maps" / "generalization-domain-v1.json"
REPORT = REPO_ROOT / "reports" / "extraction" / "ext009-term-map-verification.json"

TERM_MAP: dict[str, list[str]] = {
    # --- bias-variance / generalization core ---
    "bias": [],  # cross-vault; note sense: statistical bias vs BN 'bias term' (course)
    "variance": [],  # cross-vault; note sense: error variance vs BN batch variance (course)
    "bias-variance": ["bias variance"],  # master-ai only
    "overfitting": ["overfit"],
    "underfitting": ["underfit"],  # master-ai only
    "generalization": ["generalize", "generalizes"],
    "irreducible": [],  # master-ai only
    "decomposition": [],  # master-ai only
    "tradeoff": ["trade-off"],  # master-ai only
    "model complexity": [],  # master-ai only
    "learning curve": [],  # master-ai only
    "double descent": [],  # master-ai only
    "ensemble": ["ensembling"],  # canonical + master-ai variant both in scope
    "memorize": ["memorization"],  # canonical cross-vault; -ation form course-only
    "capacity": [],
    # --- evaluation protocol vocabulary ---
    "validation": ["validation set", "validation data", "validation loss"],
    "test set": ["test data"],  # BRIDGE: 'test set' master-ai / 'test data' ai-course
    "training set": ["training data"],
    # --- regularization core ---
    "regularization": ["regularize", "regularized", "implicit regularization"],
    "L1": [],  # cross-vault; see hazards note in _COMMENT (mermaid + code contexts exist)
    "L2": [],
    "ridge": [],  # master-ai only
    "elastic net": [],  # master-ai only
    "weight decay": [],
    "penalty": ["penalties"],
    "dropout": [],
    "early stopping": [],
    "data augmentation": ["augmentation"],
    "label smoothing": [],
    # --- batch normalization (compound form is the cross-vault bridge) ---
    "batchnorm": ["BatchNorm", "batch norm", "BN"],  # compound cross-vault; 'batch norm' master-ai; 'BN' ai-course
    "normalization": ["normalize", "normalizing"],
    "covariate shift": ["internal covariate shift"],  # ai-course only
    "gamma": [],  # ai-course only (BN scale parameter)
    "beta": [],  # ai-course only (BN shift parameter)
    "moving average": [],  # ai-course only (BN running statistics)
    # --- dropout mechanics ---
    "co-adaptation": [],  # cross-vault (deep concept both vaults state)
    "inverted dropout": [],  # cross-vault
    "training mode": [],  # ai-course only
    "evaluation mode": ["eval mode"],  # ai-course only
    "dropout rate": [],  # ai-course only
    "scaling": [],  # cross-vault BUT sense-collision: dropout scaling vs master-ai Scaling Laws link
    "inference": [],  # cross-vault; sense: dropout-at-inference vs LLM inference
    # --- augmentation specifics ---
    "crop": ["cropping", "random crop"],  # 'crop' cross-vault (master-ai lists random crops)
    "rotation": ["rotations", "rotate"],  # 'rotate' cross-vault
    "horizontal flip": ["flipping", "flips"],  # ai-course only
    "translation": ["shift", "shifting"],  # SENSE-COLLISION: geometric (course) vs back-translation / pitch shift (master)
    "color jitter": ["jitter"],
    "mixup": [],  # cross-vault
    "cutmix": [],  # cross-vault
    "cutout": [],  # ai-course only
    "random erasing": ["erasing"],  # ai-course only
    "grayscale": [],  # ai-course only
    "Gaussian noise": [],  # ai-course only
    "noise": [],  # cross-vault; senses: irreducible noise / noise injection / batch-statistics noise / Gaussian augmentation
    # --- cross-cutting shared vocabulary ---
    "sparse": ["sparsity"],  # cross-vault ('sparse' both; 'sparsity' ai-course)
    "hyperparameter": ["hyperparameters"],  # BRIDGE: singular ai-course / plural master-ai
    "PyTorch": ["torch"],
    "sklearn": [],  # master-ai only
    "epoch": ["epochs"],
    "AdamW": [],
    "SGD": [],
    "transformer": ["transformers"],
    "LLM": [],  # master-ai only
    "fine-tuning": [],  # master-ai only
    "pipeline": [],
}

_COMMENT = (
    "Generalization/regularization domain term/alias map for EXT-009 "
    "cross-vault candidate discovery (CAP-013). Canonical term -> aliases. "
    "Built from the actual content of batch 008 (master-ai '03 - Machine "
    "Learning/Generalization' — 01 Bias Variance Tradeoff + 06 Regularization "
    "Techniques, 2 files, 106 KUs) and batch 009 (ai-course '04.3 - Training "
    "Dynamics and Stability' files 05 Batch Normalization + 06 Dropout and "
    "Regularization + 07 Data Augmentation — the regularization-relevant "
    "subset of that folder, 3 of 7 files, 234 KUs; three deterministic "
    "single-file runs concatenated in fixed order); every term and alias is "
    "verified to occur inside at least one in-scope KU excerpt by "
    "scripts/ext009_term_map.py after two probe rounds "
    "(scripts/ext009_term_probe{,2}.py; "
    "reports/extraction/ext009-term-map-verification.json). HEADING-ONLY "
    "vocabulary correctly EXCLUDED (EXT-004 rule: headings are not KU-excerpt "
    "evidence): 'lasso' and 'weight tying' exist only as master-ai section "
    "headings ('### L1 (Lasso)', '## Weight Tying') and never inside a KU "
    "excerpt; 'scikit-learn', 'smoothness', 'test-time augmentation', "
    "'drop rate', 'drop probability', 'inference mode', 'coadaptation', "
    "'augment', 'language model', 'fine-tune' are absent from both batches. "
    "BRIDGE aliases deliberately connect different surface forms of the same "
    "concept across vaults: 'batchnorm' (cross-vault compound) with 'batch "
    "norm' (master-ai) and 'BN' (ai-course); 'test set' (master-ai) with "
    "'test data' (ai-course); 'hyperparameter' (ai-course) with "
    "'hyperparameters' (master-ai); 'regularize' (master-ai) with "
    "'regularized' (ai-course). KNOWN SPURIOUS/SENSE-COLLISION SOURCES, "
    "recorded here so classification dismisses or adjudicates them with "
    "evidence: (1) 'noise' — master-ai uses it for irreducible noise, noise "
    "injection, and batch-statistics noise; ai-course for Gaussian-noise "
    "augmentation; (2) 'translation'/'shift' — ai-course geometric "
    "transformations vs master-ai 'back-translation' (text augmentation) and "
    "'pitch shift' (audio augmentation) — both sides ARE augmentation senses "
    "but of different operations; (3) 'scaling' — dropout/inverted-dropout "
    "scaling (both vaults) vs master-ai 'Scaling Laws' pretraining link; (4) "
    "'L1'/'L2' — occur in one mermaid diagram (KU-8612af2c187e43bf) and in "
    "python code blocks; CAP-013 mermaid-node-suspect flagging and "
    "code-fence handling apply (F-0006); (5) 'bias'/'variance' — statistical "
    "senses (master-ai core) vs BN parameter names 'beta'/'gamma' and batch "
    "variance (ai-course); (6) 'inference' — dropout-at-inference (master-ai "
    "pitfall list) vs LLM inference contexts. Keys starting with _ are "
    "documentation and ignored by the loader."
)

FRENCH_PROBES = [
    "surapprentissage", "régularisation", "augmentation de données",
    "normalisation par lot", "abandon", "bruit", "découpage", "généralisation",
]


def main() -> int:
    kus = []
    for path in (BATCH_008, BATCH_009):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                kus.append(json.loads(line))

    by_vault: dict[str, list[str]] = {"ai-course": [], "master-ai": []}
    for r in kus:
        by_vault[r["source_id"].split(":", 1)[0]].append(r["excerpt"])
    vault_text = {v: "\n".join(excerpts).casefold() for v, excerpts in by_vault.items()}

    def match(text: str, needle: str) -> bool:
        pat = re.compile(rf"(?<!\w){re.escape(needle.casefold())}(?!\w)", re.IGNORECASE)
        return bool(pat.search(text))

    errors: list[str] = []
    coverage: dict[str, dict] = {}
    for term, aliases in TERM_MAP.items():
        entry: dict[str, object] = {}
        for label, needle in [("term", term)] + [("alias", a) for a in aliases]:
            in_v = {v: match(t, needle) for v, t in vault_text.items()}
            if not any(in_v.values()):
                errors.append(f"{label} {needle!r} (term {term!r}) occurs in NO in-scope excerpt")
            entry[needle] = {v: bool(ok) for v, ok in in_v.items()}
        coverage[term] = entry

    cross_vault_terms = [
        t for t, entry in coverage.items()
        if any(all(entry[n][v] for v in ("ai-course", "master-ai")) for n in entry)
    ]
    bridged_terms = [
        t for t, entry in coverage.items()
        if t not in cross_vault_terms
        and any(entry[n]["ai-course"] for n in entry)
        and any(entry[n]["master-ai"] for n in entry)
    ]

    french_found = [p for p in FRENCH_PROBES if match(vault_text["ai-course"], p)]

    report = {
        "command": "scripts/ext009_term_map.py",
        "scope_kus": len(kus),
        "scope": {
            "master-ai": "batch 008 (Generalization: 01 Bias Variance Tradeoff + 06 Regularization Techniques, 2 files, 106 KUs)",
            "ai-course": "batch 009 (04.3 files 05 Batch Normalization + 06 Dropout and Regularization + 07 Data Augmentation, 3 files, 234 KUs)",
        },
        "terms_count": len(TERM_MAP),
        "aliases_count": sum(len(v) for v in TERM_MAP.values()),
        "cross_vault_terms": sorted(cross_vault_terms),
        "cross_vault_terms_count": len(cross_vault_terms),
        "bridged_terms": sorted(bridged_terms),
        "bridged_terms_count": len(bridged_terms),
        "french_probe": {
            "probes": FRENCH_PROBES,
            "found": french_found,
            "conclusion": (
                "no French vocabulary in scope (unlike the 03.5 'regroupement' case in EXT-008); "
                "no French aliases included"
                if not french_found
                else f"French hits: {french_found} — adjudicate before including"
            ),
        },
        "per_term_coverage": coverage,
        "errors": errors,
        "ok": not errors,
    }
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, indent=2))
        REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return 1

    payload_out = {"_comment": _COMMENT, **dict(TERM_MAP)}
    OUT.write_text(json.dumps(payload_out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "terms_count": len(TERM_MAP),
        "aliases_count": sum(len(v) for v in TERM_MAP.values()),
        "cross_vault_terms_count": len(cross_vault_terms),
        "bridged_terms_count": len(bridged_terms),
        "french_found": french_found,
        "out": str(OUT.relative_to(REPO_ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
