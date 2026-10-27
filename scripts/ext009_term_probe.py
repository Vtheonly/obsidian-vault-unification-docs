#!/usr/bin/env python3
"""EXT-009: probe candidate vocabulary for the generalization/regularization
domain term map against the ACTUAL content of batches 008 + 009 BEFORE the
map is written (EXT-005/EXT-008 discipline: no invented entries, spurious
match sources documented up front).

Read-only; prints a per-term vault-coverage matrix and mermaid/code-fence
context flags for the hazardous short tokens (L1/L2 etc.).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BATCH_008 = REPO_ROOT / "state" / "knowledge-units" / "008-ext009-master-ai-generalization.jsonl"
BATCH_009 = REPO_ROOT / "state" / "knowledge-units" / "009-ext009-ai-course-04.3-regularization.jsonl"

CANDIDATES = {
    # bias-variance / generalization core
    "bias": [], "variance": [], "bias-variance": ["bias variance"],
    "overfitting": ["overfit"], "underfitting": ["underfit"],
    "generalization": ["generalize", "generalizes"],
    "irreducible": [], "decomposition": [], "tradeoff": ["trade-off"],
    "model complexity": [], "learning curve": [],
    "double descent": [], "ensembling": ["ensemble"],
    "memorization": ["memorize"],
    # regularization core
    "regularization": ["regularize", "regularized"],
    "L1": [], "L2": [],
    "ridge": [], "lasso": [], "elastic net": [],
    "weight decay": [], "penalty": ["penalties"],
    "dropout": [], "early stopping": [],
    "data augmentation": ["augmentation", "augment"],
    "label smoothing": [], "batch normalization": [],
    "weight tying": [], "implicit regularization": [],
    # dropout mechanics
    "co-adaptation": ["coadaptation"],
    "training mode": [], "evaluation mode": ["eval mode", "inference mode"],
    "scaling": ["inverted dropout"],
    "dropout rate": ["drop rate", "drop probability"],
    # BN mechanics
    "gamma": [], "beta": [], "moving average": [],
    "internal covariate shift": ["covariate shift"],
    "normalization": ["normalize", "normalizing"],
    # augmentation specifics
    "horizontal flip": ["flipping", "flips"],
    "rotation": ["rotations", "rotate"],
    "crop": ["cropping", "random crop"],
    "translation": ["shift", "shifting"],
    "color jitter": ["jitter"],
    "cutout": [], "mixup": [], "cutmix": [],
    "test-time augmentation": [],
    # shared cross-cutting
    "validation": ["validation set", "validation loss", "validation data"],
    "test set": ["test data"], "training set": ["training data"],
    "hyperparameter": ["hyperparameters"],
    "PyTorch": ["torch"], "sklearn": ["scikit-learn"],
    "epoch": ["epochs"], "AdamW": [], "SGD": [],
    "transformer": ["transformers"], "LLM": ["language model"],
    "fine-tuning": ["fine-tune", "finetuning"],
    "noise": [], "sparsity": ["sparse"],
    "capacity": [], "smoothness": [],
}


def main() -> int:
    kus = []
    for path in (BATCH_008, BATCH_009):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                kus.append(json.loads(line))

    by_vault: dict[str, list[dict]] = {"ai-course": [], "master-ai": []}
    for r in kus:
        by_vault[r["source_id"].split(":", 1)[0]].append(r)
    vault_text = {
        v: "\n".join(r["excerpt"] for r in rs).casefold()
        for v, rs in by_vault.items()
    }

    def match(text: str, needle: str) -> bool:
        pat = re.compile(rf"(?<!\w){re.escape(needle.casefold())}(?!\w)", re.IGNORECASE)
        return bool(pat.search(text))

    print(f"batch 008 (master-ai): {len(by_vault['master-ai'])} KUs; batch 009 (ai-course): {len(by_vault['ai-course'])} KUs\n")
    print(f"{'term/alias':38s} {'master':7s} {'course':7s}")
    print("-" * 54)
    missing = []
    for term, aliases in CANDIDATES.items():
        row = []
        for label, needle in [("term", term)] + [("alias", a) for a in aliases]:
            m = match(vault_text["master-ai"], needle)
            c = match(vault_text["ai-course"], needle)
            row.append((needle, m, c))
            if not m and not c:
                missing.append(f"{label} {needle!r} (term {term!r})")
        # print each surface form on its own line for clarity
        for needle, m, c in row:
            flag = "  <-- cross-vault" if m and c else ""
            print(f"{term + ' | ' + needle:52s} {str(m):7s} {str(c):7s}{flag}")
    print("\n=== ABSENT FROM BOTH VAULTS (would be invented) ===")
    for x in missing:
        print(" ", x)

    # mermaid / fence context for hazardous short tokens
    print("\n=== hazard probe: L1/L2 occurrence contexts (mermaid? code?) ===")
    for r in kus:
        ex = r["excerpt"]
        for tok in ("L1", "L2"):
            if re.search(rf"(?<!\w){tok}(?!\w)", ex, re.IGNORECASE):
                ut = r.get("unit_type")
                first = ex.strip().splitlines()[0][:80] if ex.strip() else ""
                print(f"  [{ut}] {r['knowledge_unit_id']}: {tok} | {first!r}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
