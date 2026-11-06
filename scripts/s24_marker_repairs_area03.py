#!/usr/bin/env python3
"""S24/SYNTH-001: anchored marker-retention repairs for area 03 (5 audit findings -> 0).

All five are dropped source words in paraphrased prose; each repair restores
the source's own word at the note's corresponding sentence.

- AF-001 'adhere' (Functions and Lambda Expressions): src line 5 "They help
  adhere to the DRY Principle" -> the note's "which is exactly what the DRY
  principle demands" restored to carry 'adhere'.
- AF-002 'skews' (Outlier Detection and Treatment): src line 5 "Skews
  mean/std dev" -> the note's "they skew" restored to the source's
  subject-verb form.
- AF-003 'zooms' / AF-004 'clicking' (Plotly): src lines 24-27 "Selecting a
  region zooms into it" / "Clicking legend items hides/shows groups" -> the
  note's table paraphrased to infinitives; restored to the source gerund
  forms.
- AF-005 'envs' (Virtual Environments and Package Management): src line 55
  "**List Envs:** `conda env list`" -> the note's "List environments" label
  restored to the source's 'envs'.

Anchored, asserted, idempotent. Sources immutable.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
R = []


def add(file, bad, good, why, probe=None):
    R.append((file, bad, good, why, probe))


add(REPO / "output/Unified-Vault/03 - Python and Data Tooling/Python Programming/Functions and Lambda Expressions.md",
    "they wrap a piece of logic under a name so it can be called wherever needed, which is exactly what the **DRY principle** (Don't Repeat Yourself) demands.",
    "they wrap a piece of logic under a name so it can be called wherever needed, which helps them adhere to the **DRY principle** (Don't Repeat Yourself).",
    "AF-001 'adhere' (src 05. Functions and Lambda Expressions.md line 5: 'They help adhere to the DRY Principle')")
add(REPO / "output/Unified-Vault/03 - Python and Data Tooling/Data Cleaning and Preprocessing/Outlier Detection and Treatment.md",
    "they are never purely cosmetic: they skew the mean and the standard deviation, and they destroy linear regression models.",
    "they are never purely cosmetic: an outlier skews the mean and the standard deviation, and it destroys linear regression models.",
    "AF-002 'skews' (src 03. Outlier Detection line 5: 'Skews mean/std dev, destroys linear regression models')")
add(REPO / "output/Unified-Vault/03 - Python and Data Tooling/Python Libraries/Plotly.md",
    "| Zooming | Select a region to zoom into it |",
    "| Zooming | Selecting a region zooms into it |",
    "AF-004 'zooms' (src 06. Interactive Plotting with Plotly.md line 25: 'Selecting a region zooms into it')")
add(REPO / "output/Unified-Vault/03 - Python and Data Tooling/Python Libraries/Plotly.md",
    "| Toggles | Click legend items to hide or show groups |",
    "| Toggles | Clicking legend items hides/shows groups |",
    "AF-003 'clicking' (src line 26: 'Clicking legend items hides/shows groups')")
add(REPO / "output/Unified-Vault/03 - Python and Data Tooling/Python Environment Setup/Virtual Environments and Package Management.md",
    "4. **List environments:** `conda env list`",
    "4. **List envs:** `conda env list`",
    "AF-005 'envs' (src 04. Virtual Environments line 55: '**List Envs:** `conda env list`')")


def main() -> int:
    for file, bad, good, why, probe in R:
        text = file.read_text(encoding="utf-8")
        if probe is not None:
            done = probe in text and text.count(probe) == 1
        else:
            done = good in text and bad not in text
        if done:
            print(f"already repaired (idempotent no-op): {file.name} :: {why[:60]}")
            continue
        assert bad in text, f"anchor not found in {file.name} — refusing to guess :: {why}"
        fixed = text.replace(bad, good, 1)
        assert good in fixed, f"repair not applied in {file.name} :: {why}"
        if probe is not None:
            assert fixed.count(probe) == 1, f"probe count != 1 after repair in {file.name} :: {why}"
        file.write_text(fixed, encoding="utf-8")
        print(f"repaired: {file.name} — {why[:110]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
