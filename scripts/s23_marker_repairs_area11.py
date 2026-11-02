#!/usr/bin/env python3
"""S23/SYNTH-001: anchored marker repairs for area 11 (Foundation Models and
Multimodal) — 3 findings -> 0.

AF-001 'outdated' (Code Models.md): source "04 - Code Models.md" L130
  "**Outdated library knowledge**: libraries evolve; models trained a year ago
  may not know current APIs." The note paraphrased to "goes stale".

AF-002 'thoughts' (Reasoning Models.md): source "03 - Reasoning Models.md"
  L234 "[[15 - AI Agents/Reasoning/06 - Tree of Thoughts and Self
  Consistency|Self-Consistency]] — non-RL approach to similar problems."
  The tree-of-thoughts half of the gloss was folded away.

AF-003 'pre-bert' (Embedding Models for Retrieval.md): source "02 - Embedding
  Models for Retrieval.md" L222 "[[...Contextual Embeddings ELMo to BERT|
  Contextual Embeddings]] — pre-BERT history." The gloss was rewritten and the
  exact hyphenated term lost.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO / "output/Unified-Vault"


def repair(path: Path, bad: str, good: str, finding: str) -> None:
    text = path.read_text(encoding="utf-8")
    # additive repairs keep `bad` as a substring of `good`; require exactly one
    if text.count(good) == 1 and text.count(bad) == (1 if bad in good else 0):
        print(f"already repaired (idempotent no-op): {finding}")
        return
    assert text.count(bad) == 1, (
        f"{finding}: anchor not found (or not unique) in {path.name} — refusing to guess"
    )
    fixed = text.replace(bad, good, 1)
    assert fixed.count(good) == 1
    if bad not in good:
        assert bad not in fixed
    path.write_text(fixed, encoding="utf-8")
    print(f"repaired {finding} in {path.name}")


def main() -> int:
    # AF-001 outdated
    repair(
        VAULT / "11 - Foundation Models and Multimodal/Foundation Models/Code Models.md",
        "Library knowledge goes stale: libraries evolve, and models trained a year ago may not know current APIs.",
        "Outdated library knowledge: libraries evolve, and models trained a year ago may not know current APIs.",
        "AF-001",
    )
    # AF-002 thoughts
    repair(
        VAULT / "11 - Foundation Models and Multimodal/Foundation Models/Reasoning Models.md",
        "Chain-of-thought prompting is the technique that reasoning models internalize; self-consistency is a non-RL approach to similar problems (sample several CoTs and vote).",
        "Chain-of-thought prompting is the technique that reasoning models internalize; tree-of-thoughts search with self-consistency is the non-RL approach to similar problems (sample several thoughts and vote).",
        "AF-002",
    )
    # AF-003 pre-bert
    repair(
        VAULT / "11 - Foundation Models and Multimodal/Foundation Models/Embedding Models for Retrieval.md",
        "- [[Contextual Embeddings ELMo to BERT]] — the encoder lineage.",
        "- [[Contextual Embeddings ELMo to BERT]] — the pre-BERT history of the encoder lineage.",
        "AF-003",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
