#!/usr/bin/env python3
"""S24/SYNTH-001: generate scratch/synth/s24-link-rules.md + s24-siblings.md.

Deterministic: derives every colliding-basename path form from the canonical
structure so subagent prompts never hand-type link targets. Batch = areas
01-03 (user-directed "chapters 0 to 4"; area 04 was completed in session 20)
plus the user-directed Swin Transformer pull-forward note from area 17.
- s24-link-rules.md  — the exact path-form links for every colliding basename
                       that has a copy in THIS batch or in the generated set
                       (areas 04-14)
- s24-siblings.md    — the 68 note titles of this session's batch (linkable)
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BATCH_AREAS = (
    "01 - Foundations",
    "02 - Mathematics",
    "03 - Python and Data Tooling",
)
# user-directed pull-forward: the single area-17 note synthesized this session
BATCH_EXTRA_NOTES = (
    "17 - Papers/Attention and Transformers/Swin Transformer.md",
)
GENERATED_AREAS = (
    "04 - Machine Learning",
    "05 - Neural Network Foundations",
    "06 - Computer Vision",
    "07 - Sequence Models",
    "08 - Attention and Transformers",
    "09 - NLP and Language Models",
    "10 - Large Language Models",
    "11 - Foundation Models and Multimodal",
    "12 - Generative Models",
    "13 - Training and Adaptation",
    "14 - Inference and Production",
)


def main() -> int:
    s = json.loads((REPO / "state/synthesis/canonical-structure-v1.json").read_text())
    notes = s["notes"]

    # colliding basenames vault-wide
    from collections import Counter
    c = Counter(n["path"].rsplit("/", 1)[-1][:-3] for n in notes)
    colliding = sorted(b for b, k in c.items() if k > 1)

    lines = ["# S24 link rules (exact path forms — never hand-type these)\n"]
    lines.append("Every basename below exists in MULTIPLE places vault-wide. Links to it")
    lines.append("MUST use the exact path form shown (no `.md` suffix). Links to any OTHER")
    lines.append("note use the plain `[[Note Name]]` short form.\n")

    def area_of(p: str) -> str:
        return p.split("/", 1)[0]

    in_batch: list[tuple[str, str]] = []
    generated: list[tuple[str, str]] = []
    future: list[str] = []
    for b in colliding:
        paths = [n["path"] for n in notes if n["path"].rsplit("/", 1)[-1][:-3] == b]
        areas = {area_of(p) for p in paths}
        batch_copy = [p for p in paths if area_of(p) in BATCH_AREAS]
        if batch_copy or b.rsplit("/", 1)[-1] in {x.rsplit("/", 1)[-1][:-3] for x in BATCH_EXTRA_NOTES}:
            for p in paths:
                if area_of(p) in BATCH_AREAS:
                    in_batch.append((b, p))
                elif area_of(p) in GENERATED_AREAS:
                    generated.append((b, p))
        elif areas & set(GENERATED_AREAS):
            for p in paths:
                if area_of(p) in GENERATED_AREAS:
                    generated.append((b, p))
        else:
            future.append(b)

    lines.append("## Colliding basenames with a copy in THIS batch (areas 01-03)\n")
    lines.append("(These notes are being generated this session; link them path-based.)\n")
    for b, p in in_batch:
        lines.append(f"- {b} -> `[[{p[:-3]}|{b}]]`")
    lines.append("")
    lines.append("## Colliding basenames whose topical copy is already generated (areas 04-14)\n")
    lines.append("(Link these path forms when the target is the topical concept, not the quiz/papers copy.)\n")
    for b, p in generated:
        lines.append(f"- {b} -> `[[{p[:-3]}|{b}]]`")
    lines.append("")
    if future:
        lines.append("## Colliding basenames with NO copy in the generated set or this batch\n")
        lines.append("Do NOT link these at all (their notes do not exist yet): " + ", ".join(future) + "\n")

    lines.append("## Area orientation notes (every note links to its own)\n")
    lines.append("- Area 01 notes link: `[[Foundations MOC]]`")
    lines.append("- Area 02 notes link: `[[Mathematics MOC]]`")
    lines.append("- Area 03 notes link: `[[Python Language Overview]]` (area-root overview — area 03 has no separate MOC)")
    lines.append(
        "- The Swin Transformer paper note links `[[Attention and Transformers MOC]]` as its "
        "topical hub (the area-17 Papers MOC is not generated yet; per conventions v1 #7 "
        "links resolve within the generated set — Papers-area sibling links are added at "
        "the cross-batch consistency pass)"
    )
    out_dir = REPO / "scratch/synth"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "s24-link-rules.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    batch_note_paths = [
        n["path"]
        for n in notes
        if n["area"] in BATCH_AREAS or n["path"] in BATCH_EXTRA_NOTES
    ]
    sib = [f"# S24 batch sibling titles (these {len(batch_note_paths)} notes will all exist at gate time)\n"]
    for area in BATCH_AREAS:
        sib.append(f"## {area}")
        for n in notes:
            if n["area"] == area:
                sib.append(f"- {n['title']}")
        sib.append("")
    sib.append("## 17 - Papers (this session's pull-forward)")
    for n in notes:
        if n["path"] in BATCH_EXTRA_NOTES:
            sib.append(f"- {n['title']}")
    sib.append("")
    (out_dir / "s24-siblings.md").write_text("\n".join(sib) + "\n", encoding="utf-8")
    print(f"link rules: {len(in_batch)} in-batch + {len(generated)} generated + {len(future)} future colliding basenames")
    print(f"batch notes: {len(batch_note_paths)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
