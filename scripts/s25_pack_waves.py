#!/usr/bin/env python3
"""S25/SYNTH-001: pack the areas 15-19 notes into bounded waves.

Same deterministic pattern as s21..s24_pack_waves.py (battle-tested on 328
notes):
- orientation notes (area MOC / subarea MOC) go to the FINAL wave per area;
- notes with more than SOLO_THRESHOLD source words get a dedicated agent;
- the rest are packed by topical subfolder (same folder preferred), up to
MAX_NOTES notes or MAX_WORDS source words per agent;
- area 17: the Swin Transformer note (s24 pull-forward) already exists on
disk and is NEVER regenerated — it is excluded from generation groups.

Output: a JSON wave plan (scratch, regenerable) + a compact per-wave listing.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOLO_THRESHOLD = 5500
MAX_NOTES = 4
MAX_WORDS = 12000

SLUGS = ("area15", "area16", "area17", "area18", "area19")

# orientation notes (written last, with the full sibling list available)
ORIENTATION = {
    "15 - Agents and Tooling/Agents and Tooling MOC.md",
    "16 - Interpretability and Research/Interpretability and Research MOC.md",
    "17 - Papers/Papers MOC.md",
    "18 - Projects/Projects MOC.md",
    "19 - Reference and Practice/Glossary/Glossary MOC.md",
    "19 - Reference and Practice/Interview Prep/Interview Prep MOC.md",
}

# already on disk from session 24 (s24 pull-forward) — assess/gate/audit only
EXCLUDE_FROM_GENERATION = {
    "17 - Papers/Attention and Transformers/Swin Transformer.md",
}


def main() -> int:
    plan: dict[str, list[dict]] = {}
    for slug in SLUGS:
        d = json.loads((REPO / f"scratch/synth/{slug}/notes.json").read_text())
        notes = [n for n in d["notes"] if n["path"] not in EXCLUDE_FROM_GENERATION]
        orientation = [n for n in notes if n["path"] in ORIENTATION]
        big = [n for n in notes if n["path"] not in ORIENTATION and n["source_words"] > SOLO_THRESHOLD]
        rest = [n for n in notes if n["path"] not in ORIENTATION and n["source_words"] <= SOLO_THRESHOLD]
        # topical packing: sort by subfolder, then descending size
        rest.sort(key=lambda n: (n["path"].rsplit("/", 1)[0], -n["source_words"]))
        groups: list[list[dict]] = []
        for n in big:
            groups.append([n])
        current: list[dict] = []
        for n in rest:
            if current and (
                len(current) >= MAX_NOTES
                or sum(x["source_words"] for x in current) + n["source_words"] > MAX_WORDS
                or current[0]["path"].rsplit("/", 1)[0] != n["path"].rsplit("/", 1)[0]
            ):
                groups.append(current)
                current = []
            current.append(n)
        if current:
            groups.append(current)
        # orientation wave LAST for this area (siblings exist by then)
        plan[slug] = [{"notes": g} for g in groups]
        if orientation:
            plan[slug].append({"notes": orientation, "orientation_wave": True})

    out = {
        "solo_threshold": SOLO_THRESHOLD,
        "max_notes_per_agent": MAX_NOTES,
        "max_source_words_per_agent": MAX_WORDS,
        "areas": plan,
    }
    total_agents = sum(len(v) for v in plan.values())
    out["agent_count"] = total_agents
    for slug, groups in plan.items():
        print(f"== {slug}: {len(groups)} agent groups ==")
        for i, g in enumerate(groups, 1):
            words = sum(n["source_words"] for n in g["notes"])
            label = " [ORIENTATION]" if g.get("orientation_wave") else ""
            print(
                f"  g{i:02d}{label}: {len(g['notes'])} notes, {words} src words :: "
                + "; ".join(f"{n['index']:02d}:{n['path'].split('/', 1)[1]}" for n in g["notes"])
            )
    Path(REPO / "scratch/synth/s25-wave-plan.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\nTOTAL agent groups: {total_agents}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
