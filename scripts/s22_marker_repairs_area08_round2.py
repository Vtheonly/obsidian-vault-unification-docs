#!/usr/bin/env python3
"""S22/SYNTH-001: corrective marker repairs for area 08 (4 residual findings).

The first repair round satisfied each note's LATER KU markers but displaced
the EARLIER KU markers of the same source notes (the sources carry the same
content twice: main text + recap section, with slightly different wording
and equation spacing). Both treatments are source content; both must survive.

- Sinusoidal and Learned Positional Encodings.md (master-ai source):
  * main text (lines 33-39): "The authors hoped ..." + SPACED display
    ``\\sin(i) \\cos(\\delta) + \\cos(i) \\sin(\\delta)``;
  * recap (lines 155-161): "The original Transformer paper hypothesized ..."
    + UNSPACED display ``\\sin(i)\\cos(\\delta) + \\cos(i)\\sin(\\delta)``.
  Repair: restore the main-text treatment in "The hope that didn't pan out"
  and re-add the recap treatment as the lead-in of "Why extrapolation
  failed in practice" (mirroring the source's structure).

- Linear Attention.md (master-ai source):
  * main text (lines 54-59): TWO displays with ``\\quad \\text{where }``;
  * recap (line 166): combined display ``\\tilde{K} = E K, \\quad \\tilde{V} = F V``
    + inline ``$E, F \\in \\mathbb{R}^{k \\times n}$``.
  Repair: restore the two where-form displays and keep the compact
  restatement (both source notations coexist).
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
A08 = REPO / "output/Unified-Vault/08 - Attention and Transformers"

REPAIRS: list[dict] = [
    {
        "id": "AF-002+AF-001a (restore main-text treatment)",
        "file": A08 / "Attention Mechanism/Sinusoidal and Learned Positional Encodings.md",
        "old": (
            "The original Transformer paper hypothesized that sinusoidal encoding would **extrapolate** "
            "to longer sequences than seen in training, because $\\sin(i + \\delta)$ is a linear function "
            "of $\\sin(i)$ and $\\cos(i)$:\n\n$$\n\\sin(i + \\delta) = \\sin(i)\\cos(\\delta) + \\cos(i)\\sin(\\delta)\n$$"
        ),
        "new": (
            "The authors hoped sinusoidal encoding would **extrapolate** to longer sequences than seen "
            "in training, because $\\sin(i + \\delta)$ is a linear function of $\\sin(i)$ and $\\cos(i)$:\n\n"
            "$$\n\\sin(i + \\delta) = \\sin(i) \\cos(\\delta) + \\cos(i) \\sin(\\delta)\n$$"
        ),
    },
    {
        "id": "AF-001b (re-add recap treatment)",
        "file": A08 / "Attention Mechanism/Sinusoidal and Learned Positional Encodings.md",
        "old": (
            "### Why extrapolation failed in practice\n\nThree reasons. First, the model learns absolute patterns:"
        ),
        "new": (
            "### Why extrapolation failed in practice\n\nThe original Transformer paper hypothesized that "
            "sinusoidal encoding would extrapolate because $\\sin(i + \\delta)$ is a linear function of "
            "$\\sin(i)$ and $\\cos(i)$:\n\n$$\\sin(i + \\delta) = \\sin(i)\\cos(\\delta) + \\cos(i)\\sin(\\delta)$$\n\n"
            "The hope: the model could learn to attend by relative position. In practice, this didn't work — "
            "models trained on length 512 degrade past length 512. Why? Three reasons. First, the model learns absolute patterns:"
        ),
    },
    {
        "id": "AF-003+AF-004 (restore where-form displays, keep compact form)",
        "file": A08 / "Efficient Attention/Linear Attention.md",
        "old": (
            "$$\n\\tilde{K} = E K, \\quad \\tilde{V} = F V\n$$\n\n"
            "where $E, F \\in \\mathbb{R}^{k \\times n}$. Now $Q \\tilde{K}^T$ is $n \\times k$ instead of $n \\times n$."
        ),
        "new": (
            "$$\n\\tilde{K} = E K \\quad \\text{where } E \\in \\mathbb{R}^{k \\times n}\n$$\n"
            "$$\n\\tilde{V} = F V \\quad \\text{where } F \\in \\mathbb{R}^{k \\times n}\n$$\n\n"
            "or, compactly, $\\tilde{K} = E K, \\quad \\tilde{V} = F V$ where $E, F \\in \\mathbb{R}^{k \\times n}$. "
            "Now $Q \\tilde{K}^T$ is $n \\times k$ instead of $n \\times n$."
        ),
    },
]


def main() -> int:
    applied, skipped, failed = 0, 0, []
    for r in REPAIRS:
        text = r["file"].read_text(encoding="utf-8")
        if r["new"] in text and r["old"] not in text:
            print(f"{r['id']}: already repaired (no-op)")
            skipped += 1
            continue
        if r["old"] not in text:
            failed.append(r["id"])
            print(f"{r['id']}: ANCHOR NOT FOUND in {r['file'].name}")
            continue
        fixed = text.replace(r["old"], r["new"], 1)
        r["file"].write_text(fixed, encoding="utf-8")
        print(f"{r['id']}: repaired {r['file'].name}")
        applied += 1
    print(f"applied={applied} skipped={skipped} failed={len(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
