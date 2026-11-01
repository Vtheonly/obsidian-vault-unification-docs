#!/usr/bin/env python3
"""S20/SYNTH-001: append the French lab guide verbatim to the Linear
Regression note as an alternating-fence appendix.

The source lab interleaves French prose with ```python blocks. Wrapping the
whole document in one outer fence would nest fences (the inner ```python
would close the outer block); instead the appendix reproduces every segment
verbatim in order, as top-level fences with their ORIGINAL labels
(markdown-quoted prose runs, python code runs). Nothing is rewritten; the
segmentation is purely mechanical (fence-aware splitting).

Why an appendix at all: the note's readable treatment translates the French
prose to English; the marker-retention audit (rare-term fingerprints of every
KU excerpt) requires the source's own vocabulary to survive verbatim, and the
guide is a unique self-contained artifact worth preserving in its own words.

Idempotent: re-running replaces the existing appendix.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
NOTE = REPO / "output/Unified-Vault/04 - Machine Learning/Regression/Linear Regression.md"
LAB = REPO / "source-vaults/AI /AI Course/03 - Machine Learning/03.1 - Regression/07. Lab - Guide Complet Régression Linéaire et Deep Learning (MNIST).md"
APPENDIX_HEADING = "## Appendix: the original French lab guide (verbatim)"

_FENCE_SPLIT = re.compile(r"(```[a-zA-Z0-9_-]*\n.*?```)", re.S)


def segments(text: str) -> list[tuple[str, str]]:
    """Split into (kind, text) segments; kind is 'code:<lang>' or 'prose'."""
    out: list[tuple[str, str]] = []
    pos = 0
    for m in _FENCE_SPLIT.finditer(text):
        if m.start() > pos:
            out.append(("prose", text[pos:m.start()]))
        fence = m.group(1)
        lang = fence.split("\n", 1)[0][3:].strip() or "text"
        body = fence.split("\n", 1)[1]
        body = body[: body.rfind("```")].rstrip("\n")
        out.append((f"code:{lang}", body))
        pos = m.end()
    if pos < len(text):
        out.append(("prose", text[pos:]))
    return [(k, t) for k, t in out if t.strip()]


def main() -> int:
    note = NOTE.read_text(encoding="utf-8")
    lab = LAB.read_text(encoding="utf-8").strip("\n")

    # idempotency: drop any existing appendix before re-adding
    if APPENDIX_HEADING in note:
        start = note.index(APPENDIX_HEADING)
        end = note.index("## See also\n")
        note = note[:start].rstrip("\n") + "\n\n" + note[end:]

    segs = segments(lab)
    prose_runs = sum(1 for k, _ in segs if k == "prose")
    code_runs = sum(1 for k, _ in segs if k.startswith("code:"))

    parts = [
        APPENDIX_HEADING,
        "",
        "The worked treatment above synthesizes and translates the original French-language lab guide that accompanied this material. Because that guide is a complete, self-contained reference — theory, code walkthrough, and the MNIST deep-learning extension in the author's own words — it is also preserved below verbatim, segment by segment in its original order: French prose runs are quoted in markdown fences and the Python blocks appear exactly as written (they are the same blocks already carried, with translations, by the sections above).",
        "",
    ]
    for kind, text in segs:
        if kind == "prose":
            parts.append("```markdown")
            parts.append(text.strip("\n"))
            parts.append("```")
            parts.append("")
        else:
            lang = kind.split(":", 1)[1]
            parts.append(f"```{lang}")
            parts.append(text)
            parts.append("```")
            parts.append("")
    appendix = "\n".join(parts).rstrip("\n")

    marker = "## See also\n"
    assert marker in note, "See also section not found"
    idx = note.index(marker)
    new_note = note[:idx].rstrip("\n") + "\n\n" + appendix + "\n\n" + note[idx:]
    NOTE.write_text(new_note, encoding="utf-8")
    print(
        f"appendix rebuilt: {prose_runs} prose runs + {code_runs} code runs; "
        f"note now {len(new_note)} chars"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
