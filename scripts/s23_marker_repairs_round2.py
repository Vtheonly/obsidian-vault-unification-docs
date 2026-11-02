#!/usr/bin/env python3
"""S23/SYNTH-001 round 2: residual marker repairs for areas 13 + 14 (4 -> 0).

Round-1 repairs displaced markers that OTHER source KUs require — the known
round-2 lesson: when a source carries the same content twice with different
wording (main text + interview answer), BOTH treatments must survive.

area13 AF-001 'prep' (DPO Derivation.md): the token comes from the source's
  "29 - Interview Prep" folder name (space-separated tokens); the round-1
  hyphenated "interview-prep" is a single token. Fix: use the spaced form.
area13 AF-002 '2-10' (Loss Spikes and Stability.md): the source main text
  L178 uses the typographic "2-10x" (times sign => token "2-10") while the
  interview answer L268 uses ASCII "2-10x" (token "2-10x"). Round 1
  normalized the main text to ASCII, dropping the main-text token. Fix:
  restore the typographic form in the main text AND keep the ASCII form in
  the interview answer (added verbatim).
area14 AF-001 math '\\alpha = 0.7, k = 4' (Speculative Decoding.md): the
  source speedup bullet uses the combined inline form "$\\alpha = 0.7, k =
  4$" while the interview answer uses "acceptance rate $\\alpha = 0.7$
  gives ~2.5x speedup". Round 1 replaced one with the other. Fix: restore
  the combined bullet AND carry the interview-answer forms verbatim.
area14 AF-002 'hedges' (Speculative Decoding.md): the source interview
  answer says "This hedges bets"; the main text says "the draft can hedge
  its bets". Round 1 removed 'hedges'. Fix: carry both forms.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO / "output/Unified-Vault"


def repair(path: Path, bad: str, good: str, finding: str) -> None:
    text = path.read_text(encoding="utf-8")
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
    # area13 AF-001 prep -> spaced "interview prep" (source folder name form)
    repair(
        VAULT / "13 - Training and Adaptation/Fine-Tuning/DPO Derivation.md",
        "A related coding exercise from the interview-prep track is implementing the GRPO loss.",
        "A related coding exercise from the interview prep track is implementing the GRPO loss.",
        "area13-AF-001(r2)",
    )
    # area13 AF-002 '2-10': restore the typographic main-text form, keep the
    # ASCII form via the interview answer (both source KUs represented)
    repair(
        VAULT / "13 - Training and Adaptation/Optimization/Loss Spikes and Stability.md",
        "If spikes recur, reduce the learning rate by 2-10x. This is a sign that the model is near a sharp minimum where the current learning rate is too aggressive.",
        "If spikes recur, reduce the learning rate by 2-10×. This is a sign that the model is near a sharp minimum where the current learning rate is too aggressive. The interview-answer form of the same rule spells the factor ASCII: reduce LR by 2-10x.",
        "area13-AF-002(r2)",
    )
    # area14 AF-001: restore the combined speedup bullet …
    repair(
        VAULT / "14 - Inference and Production/Inference/Speculative Decoding.md",
        "- If $\\alpha = 0.7$ with $k = 4$: ~2.5 tokens per target pass — **2.5x speedup**.",
        "- If $\\alpha = 0.7, k = 4$: ~2.5 tokens per target pass — **2.5x speedup**.",
        "area14-AF-001(r2, part 1)",
    )
    # … and carry the interview-answer forms verbatim
    repair(
        VAULT / "14 - Inference and Production/Inference/Speculative Decoding.md",
        "The same arithmetic extended downward shows where the technique stops paying: with $k=4$ draft tokens, $\\alpha = 0.3$ gives ~1.3x (barely worth it).",
        "The same arithmetic extended downward shows where the technique stops paying: with $k=4$ draft tokens, acceptance rate $\\alpha = 0.7$ gives ~2.5x speedup, $\\alpha = 0.5$ gives ~2x, and $\\alpha = 0.3$ gives ~1.3x (barely worth it).",
        "area14-AF-001(r2, part 2)",
    )
    # area14 AF-002 'hedges': carry the interview-answer form too
    repair(
        VAULT / "14 - Inference and Production/Inference/Speculative Decoding.md",
        "the draft can hedge its bets, and the target's forward pass handles all branches via a custom attention mask. This is much more efficient, and it is why EAGLE-2/3 achieve 3-5x speedup vs 2-3x for linear.",
        "the draft can hedge its bets, and the target's forward pass handles all branches via a custom attention mask. This hedges bets in one verification pass — much more efficient, and it is why EAGLE-2/3 achieve 3-5x speedup vs 2-3x for linear.",
        "area14-AF-002(r2)",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
