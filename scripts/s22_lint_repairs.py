#!/usr/bin/env python3
"""S22/SYNTH-001: anchored lint repair for area-08 Transformer Decoder Block.

Defect: the generation-steps list's Step 3 line dropped the inline-code
closing backtick (rendered as a stray '$'), producing the MATH_INLINE_ODD
lint warning. The source KU excerpt reads:

    3. **Step 3:** Feed `<BOS>, y_1, y_2`. Sample $y_3$.

source: ai-course "04. The Transformer Decoder Block - Masking and
Cross-Attention.md" line 117 (KU heading path: The Transformer Decoder
Block > How the decoder generates at inference time).

Anchored, asserted, idempotent: applies exactly one byte-level replacement,
asserts the before/after state, and is a no-op if already repaired.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TARGET = REPO / "output/Unified-Vault/08 - Attention and Transformers/Transformer Architecture/Transformer Decoder Block.md"

BAD = "3. **Step 3:** Feed `<BOS>, y_1, y_2$. Sample $y_3$."
GOOD = "3. **Step 3:** Feed `<BOS>, y_1, y_2`. Sample $y_3$."


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    if GOOD in text and BAD not in text:
        print("already repaired (idempotent no-op)")
        return 0
    assert BAD in text, "anchor not found — defect text changed, refusing to guess"
    fixed = text.replace(BAD, GOOD, 1)
    assert fixed.count(GOOD) == 1 and BAD not in fixed
    TARGET.write_text(fixed, encoding="utf-8")
    print("repaired: restored inline-code backtick in Step 3 (source line 117)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
