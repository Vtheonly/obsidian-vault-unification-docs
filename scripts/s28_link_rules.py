#!/usr/bin/env python3
"""S28/SYNTH-001: generate scratch/synth/s28-link-rules.md + s28-siblings.md.

Deterministic: derives every colliding-basename path form from the canonical
structure so subagent prompts never hand-type link targets. Batch = area 20
(session 28, final synthesis batch). Generated set = areas 01-19 (sessions
20-27).
- s28-link-rules.md  — the exact path-form links for every colliding basename
                       in the generated set that an area-20 note may link to
                       (no area-20 basename itself collides vault-wide)
- s28-siblings.md    — the 17 note titles of this session's batch (linkable)
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BATCH_AREAS = ("20 - Vault and Project Context",)
GENERATED_AREAS = (
    "01 - Foundations",
    "02 - Mathematics",
    "03 - Python and Data Tooling",
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
    "15 - Agents and Tooling",
    "16 - Interpretability and Research",
    "17 - Papers",
    "18 - Projects",
    "19 - Reference and Practice",
)


def main() -> int:
    s = json.loads((REPO / "state/synthesis/canonical-structure-v1.json").read_text())
    notes = s["notes"]

    # colliding basenames vault-wide
    from collections import Counter
    c = Counter(n["path"].rsplit("/", 1)[-1][:-3] for n in notes)
    colliding = sorted(b for b, k in c.items() if k > 1)

    lines = ["# S28 link rules (exact path forms — never hand-type these)\n"]
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
        if areas & set(BATCH_AREAS):
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

    if in_batch:
        lines.append("## Colliding basenames with a copy in THIS batch (area 20)\n")
        lines.append("(These notes are being generated this session; link them path-based.)\n")
        for b, p in in_batch:
            lines.append(f"- {b} -> `[[{p[:-3]}|{b}]]`")
        lines.append("")
    else:
        lines.append("## Colliding basenames with a copy in THIS batch (area 20)\n")
        lines.append("None — no area-20 basename collides vault-wide (verified against the")
        lines.append("full 544-note canonical structure). All 17 area-20 links use the plain")
        lines.append("`[[Note Name]]` short form.\n")

    lines.append(
        "## Colliding basenames whose only copies are already generated (areas 01-19)\n"
    )
    lines.append(
        "(When an area-20 archival note names one of these topics, link the path form.)\n"
    )
    for b, p in generated:
        lines.append(f"- {b} -> `[[{p[:-3]}|{b}]]`")
    lines.append("")
    if future:
        lines.append("## Colliding basenames with NO copy in the generated set or this batch\n")
        lines.append("Do NOT link these at all (their notes do not exist yet): " + ", ".join(future) + "\n")

    lines.append("## Area orientation notes (every note links to its own)\n")
    lines.append(
        "- Area 20 notes have no area-root MOC (archival context layer) — link at least\n"
        "  two same-area siblings from the note's natural cluster:\n"
        "  navigation cluster (Master AI README, Master AI MOC, Master AI Index,\n"
        "  Master Roadmap, Learning Roadmap, Reading Orders), management-log cluster\n"
        "  (Vault Management README, Architecture Decisions Log, Completed Work Log,\n"
        "  Current Iteration Log, Next Iteration Log, Remaining Work Log, Vault Status\n"
        "  Log, Coverage Audit Log, Research Queue), ai-course cluster (AI Course\n"
        "  Master Index, AI Course Merge Report); plus topical concept notes when the\n"
        "  archived text names them (path form per the list above when colliding)"
    )
    out_dir = REPO / "scratch/synth"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "s28-link-rules.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    batch_note_paths = [n["path"] for n in notes if n["area"] in BATCH_AREAS]
    sib = [f"# S28 batch sibling titles (these {len(batch_note_paths)} notes will all exist at gate time)\n"]
    for area in BATCH_AREAS:
        sib.append(f"## {area}")
        for n in notes:
            if n["area"] == area:
                sib.append(f"- {n['title']}")
        sib.append("")
    (out_dir / "s28-siblings.md").write_text("\n".join(sib) + "\n", encoding="utf-8")
    print(f"link rules: {len(in_batch)} in-batch + {len(generated)} generated + {len(future)} future colliding basenames")
    print(f"batch notes: {len(batch_note_paths)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
