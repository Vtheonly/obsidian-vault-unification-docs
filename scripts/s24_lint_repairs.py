#!/usr/bin/env python3
"""S24/SYNTH-001: anchored lint repairs for the areas 01-03 batch.

Three real rendering defects (unescaped pipes inside inline math in TABLE
cells break the cells in Obsidian; the linter's TABLE_CELL_MISMATCH /
BRACKET_UNBALANCED warnings are correct) plus one prose bracket artifact.
All four notes are UNCOMMITTED session-24 output; the repairs run BEFORE
the gate chain so the batch lands with 0 avoidable warnings.

Keep-both discipline (session-23 round-2 lesson): the audit's math markers
carry the SOURCE-VERBATIM unescaped forms (KU-a91cd91 for the cosine
distance table, KU-9384b7f for the z-score rule). Where the verbatim form
lives ONLY in the broken table cell, the repair escapes the cell AND adds
the verbatim form in adjacent prose, so both the lint and the audit pass.

1. "Outlier Detection and Treatment.md" line 92: table cell `Flag if $|Z| > 3$`
   -> `Flag if $\\|Z\\| > 3$`. The verbatim `$|Z| > 3$` marker is already
   satisfied by the note's prose (line 53: "if $|Z| > 3$, the point is an
   outlier"), so only the cell needs escaping.
2. "Cosine Similarity.md" line 252: Manhattan table cell
   `$\\sum_i |x_i - y_i|$` -> `$\\sum_i \\|x_i - y_i\\|$`, plus a prose
   sentence carrying the verbatim `$\\sum_i |x_i - y_i|$` (marker source:
   master-ai '03 - Cosine Similarity.md' lines 253-262, KU-a91cd91).
3. "Cosine Similarity.md" line 254: Jaccard table cell
   `$\\frac{|A \\cap B|}{|A \\cup B|}$` -> escaped pipes, plus the same
   prose sentence carries the verbatim fraction (KU-a91cd91).
4. "NumPy.md" line 61: prose inline-code `[0, 1)` -> math `$[0, 1)$` (an
   interval is math per editorial conventions v1 #4; the `[0, 1)` inside
   the note's python fence stays verbatim and satisfies the code
   fingerprint).

Documented, NOT repaired (verbatim-source artifacts, same class as the
nine s23 dollar-price warnings): the MATH_INLINE_ODD warnings in
"AI vs ML vs DL.md" ($0.04/$0.001–$0.06, source master-ai '02 - AI vs ML
vs DL vs GenAI vs Agentic AI.md' line 263), "Introduction to Machine
Learning.md" and "Types of Learning.md" (($350,000), source ai-course
'08. Foundations of Machine Learning (Summary).md' line 90).

Anchored, asserted, idempotent.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

REPAIRS = [
    {
        "file": REPO / "output/Unified-Vault/03 - Python and Data Tooling/Data Cleaning and Preprocessing/Outlier Detection and Treatment.md",
        "bad": "| Decision rule | Flag if $|Z| > 3$ | Flag if outside $Q1 - 1.5 \\times IQR$ and $Q3 + 1.5 \\times IQR$ |",
        "good": "| Decision rule | Flag if $\\|Z\\| > 3$ | Flag if outside $Q1 - 1.5 \\times IQR$ and $Q3 + 1.5 \\times IQR$ |",
        "why": "unescaped |Z| pipes split the table cell; verbatim marker kept by prose line 53 (KU-9384b7f)",
    },
    {
        "file": REPO / "output/Unified-Vault/02 - Mathematics/Linear Algebra/Cosine Similarity.md",
        "bad": "| Manhattan (L1)         | $\\sum_i |x_i - y_i|$                       | $[0, \\infty)$ | Sparse data, robust to outliers             |",
        "good": "| Manhattan (L1)         | $\\sum_i \\|x_i - y_i\\|$                    | $[0, \\infty)$ | Sparse data, robust to outliers             |",
        "why": "unescaped |x_i - y_i| pipes split the table cell (KU-a91cd91)",
    },
    {
        "file": REPO / "output/Unified-Vault/02 - Mathematics/Linear Algebra/Cosine Similarity.md",
        "bad": "| Jaccard                | $\\frac{|A \\cap B|}{|A \\cup B|}$            | $[0, 1]$   | Sets (e.g., token overlap)                   |",
        "good": "| Jaccard                | $\\frac{\\|A \\cap B\\|}{\\|A \\cup B\\|}$   | $[0, 1]$   | Sets (e.g., token overlap)                   |",
        "why": "unescaped |A cap B|/|A cup B| pipes split the table cell (KU-a91cd91)",
    },
    {
        "file": REPO / "output/Unified-Vault/03 - Python and Data Tooling/Python Libraries/NumPy.md",
        "bad": "The random constructors cover the three everyday cases: uniform floats in `[0, 1)`, standard normal samples",
        "good": "The random constructors cover the three everyday cases: uniform floats in $[0, 1)$, standard normal samples",
        "why": "inline-code [0, 1) carries unbalanced brackets; the interval is math (conventions v1 #4)",
    },
]

# keep-both prose for the cosine table: carries the SOURCE-VERBATIM unescaped
# math forms so the audit math markers (KU-a91cd91) stay satisfied after the
# table cells are escaped.
PROSE_ANCHOR = {
    "file": REPO / "output/Unified-Vault/02 - Mathematics/Linear Algebra/Cosine Similarity.md",
    "bad": "## Production implications",
    "good": (
        "The table's math is worth reading once outside the grid: the Manhattan entry is the "
        "sum of absolute per-dimension differences $\\sum_i |x_i - y_i|$, and the Jaccard entry "
        "is the set-overlap ratio $\\frac{|A \\cap B|}{|A \\cup B|}$ — the size of the "
        "intersection over the size of the union.\n\n"
        "## Production implications"
    ),
    "why": "keep-both: verbatim unescaped math forms for audit markers (KU-a91cd91) after cell escaping",
    "contains_bad": True,  # good text embeds the bad anchor (insertion repair)
    "idempotence_marker": "sum of absolute per-dimension differences",
}


def main() -> int:
    for t in REPAIRS + [PROSE_ANCHOR]:
        text = t["file"].read_text(encoding="utf-8")
        # idempotency: the insertion-unique part of `good` already present
        marker = t.get("idempotence_marker") or t["good"]
        if marker in text and (t.get("contains_bad") or t["bad"] not in text):
            print(f"already repaired (idempotent no-op): {t['file'].name}")
            continue
        assert t["bad"] in text, f"anchor not found in {t['file'].name} — refusing to guess"
        fixed = text.replace(t["bad"], t["good"], 1)
        assert marker in fixed, f"repair marker missing after replace in {t['file'].name}"
        if not t.get("contains_bad"):
            assert t["bad"] not in fixed, f"bad anchor still present after replace in {t['file'].name}"
        t["file"].write_text(fixed, encoding="utf-8")
        print(f"repaired: {t['file'].name} — {t['why']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
