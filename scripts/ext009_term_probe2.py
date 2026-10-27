#!/usr/bin/env python3
"""EXT-009 probe round 2: BN abbreviation variants, augmentation specifics,
and sense-ambiguity checks (noise / translation / shift / scaling contexts)."""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BATCH_008 = REPO_ROOT / "state" / "knowledge-units" / "008-ext009-master-ai-generalization.jsonl"
BATCH_009 = REPO_ROOT / "state" / "knowledge-units" / "009-ext009-ai-course-04.3-regularization.jsonl"

PROBES = [
    "batch norm", "BN", "batchnorm", "BatchNorm",
    "inference", "rescale", "resize", "zoom",
    "brightness", "contrast", "grayscale", "Gaussian noise",
    "generalization gap", "validation error", "test error", "training error",
    "weight penalty", "weight penalties",
    "variance reduction", "noise reduction",
    "data leakage", "distribution shift",
    "transformation", "pipeline",
    "residual", "skip connection",
    "momentum", "learning rate",
    "random erasing", "erasing",
    "feature extraction", "transfer learning",
    "variance tradeoff", "sweet spot",
]


def main() -> int:
    kus = []
    for path in (BATCH_008, BATCH_009):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                kus.append(json.loads(line))
    by_vault = {"ai-course": [], "master-ai": []}
    for r in kus:
        by_vault[r["source_id"].split(":", 1)[0]].append(r)
    vault_text = {v: "\n".join(r["excerpt"] for r in rs).casefold() for v, rs in by_vault.items()}

    def match(text: str, needle: str) -> bool:
        pat = re.compile(rf"(?<!\w){re.escape(needle.casefold())}(?!\w)", re.IGNORECASE)
        return bool(pat.search(text))

    print(f"{'probe':28s} {'master':7s} {'course':7s}")
    print("-" * 44)
    for p in PROBES:
        m = match(vault_text["master-ai"], p)
        c = match(vault_text["ai-course"], p)
        print(f"{p:28s} {str(m):7s} {str(c):7s}{'  <-- cross-vault' if m and c else ''}")

    # context dump for sense-ambiguous tokens
    print("\n=== context: 'noise' in master-ai (sense check) ===")
    for r in by_vault["master-ai"]:
        for line in r["excerpt"].splitlines():
            if re.search(r"(?<!\w)noise(?!\w)", line, re.IGNORECASE):
                print("  |", line.strip()[:100])
                break
    print("\n=== context: 'translation'/'shift' in master-ai ===")
    for r in by_vault["master-ai"]:
        for line in r["excerpt"].splitlines():
            if re.search(r"(?<!\w)(translation|shift)(?!\w)", line, re.IGNORECASE):
                print("  |", line.strip()[:100])
                break
    print("\n=== context: 'scaling' in master-ai ===")
    for r in by_vault["master-ai"]:
        for line in r["excerpt"].splitlines():
            if re.search(r"(?<!\w)scaling(?!\w)", line, re.IGNORECASE):
                print("  |", line.strip()[:100])
                break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
