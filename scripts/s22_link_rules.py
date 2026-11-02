#!/usr/bin/env python3
"""S22/SYNTH-001: generate scratch/synth/s22-link-rules.md + s22-siblings.md.

Deterministic: derives every colliding-basename path form from the canonical
structure so subagent prompts never hand-type link targets. Two files:
- s22-link-rules.md  — the exact path-form links for every colliding basename
                       that has a copy in the generated set (areas 04-09)
- s22-siblings.md    — the 63 note titles of this session's batch (linkable)
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BATCH_AREAS = ("07 - Sequence Models", "08 - Attention and Transformers", "09 - NLP and Language Models")
GENERATED_AREAS = ("04 - Machine Learning", "05 - Neural Network Foundations", "06 - Computer Vision")


def main() -> int:
    s = json.loads((REPO / "state/synthesis/canonical-structure-v1.json").read_text())
    notes = s["notes"]

    # colliding basenames vault-wide
    from collections import Counter
    c = Counter(n["path"].rsplit("/", 1)[-1][:-3] for n in notes)
    colliding = sorted(b for b, k in c.items() if k > 1)

    lines = ["# S22 link rules (exact path forms — never hand-type these)\n"]
    lines.append("Every basename below exists in MULTIPLE places vault-wide. Links to it")
    lines.append("MUST use the exact path form shown (no `.md` suffix). Links to any OTHER")
    lines.append("note use the plain `[[Note Name]]` short form.\n")

    in_batch: list[tuple[str, str]] = []
    generated: list[tuple[str, str]] = []
    future: list[str] = []
    for b in colliding:
        paths = [n["path"] for n in notes if n["path"].rsplit("/", 1)[-1][:-3] == b]
        area_of = {p.split("/", 1)[0] for p in paths}
        if area_of & set(BATCH_AREAS):
            for p in paths:
                if p.split("/", 1)[0] in BATCH_AREAS:
                    in_batch.append((b, p))
                elif p.split("/", 1)[0] in GENERATED_AREAS:
                    generated.append((b, p))
        elif area_of & set(GENERATED_AREAS):
            # both copies in 04-06 or one in 04-06 + future area: link the
            # generated topical copy (the second copy is mostly area 19 quizzes)
            for p in paths:
                if p.split("/", 1)[0] in GENERATED_AREAS:
                    generated.append((b, p))
        else:
            future.append(b)

    lines.append("## Colliding basenames with a copy in THIS batch (areas 07-09)\n")
    for b, p in in_batch:
        lines.append(f"- {b} -> `[[{p[:-3]}|{b}]]`")
    lines.append("")
    lines.append("## Colliding basenames whose topical copy is already generated (areas 04-06)\n")
    lines.append("(Link these path forms when the target is the topical concept, not the quiz copy.)\n")
    for b, p in generated:
        lines.append(f"- {b} -> `[[{p[:-3]}|{b}]]`")
    lines.append("")
    if future:
        lines.append("## Colliding basenames with NO copy in the generated set yet\n")
        lines.append("Do NOT link these at all (their notes do not exist yet): " + ", ".join(future) + "\n")

    lines.append("## Area orientation notes (every note links to its own)\n")
    lines.append("- Area 07 notes link: `[[07 - Sequence Models/Chapter Overview|Chapter Overview]]`")
    lines.append("- Area 08 notes link: `[[Attention and Transformers MOC]]`")
    lines.append("- Area 09 notes link: `[[NLP and Language Models MOC]]`")
    (REPO / "scratch/synth/s22-link-rules.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    sib = ["# S22 batch sibling titles (these 63 notes will all exist at gate time)\n"]
    for area in BATCH_AREAS:
        sib.append(f"## {area}")
        for n in notes:
            if n["area"] == area:
                sib.append(f"- {n['title']}")
        sib.append("")
    (REPO / "scratch/synth/s22-siblings.md").write_text("\n".join(sib) + "\n", encoding="utf-8")
    print(f"link rules: {len(in_batch)} in-batch + {len(generated)} generated + {len(future)} future colliding basenames")
    print("\n".join(lines[:40]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
