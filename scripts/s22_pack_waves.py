#!/usr/bin/env python3
"""S22/SYNTH-001: pack the area-07/08/09 notes into bounded subagent waves.

Same deterministic pattern as s21_pack_waves.py (battle-tested on 100 notes):
- orientation notes (area MOC / overview) go to the FINAL wave per area
  (their links and reading order need the sibling notes to exist);
- notes with more than SOLO_THRESHOLD source words get a dedicated agent;
- the rest are packed by topical subfolder (same folder preferred), up to
  MAX_NOTES notes or MAX_WORDS source words per agent.

Output: a JSON wave plan (scratch, regenerable) + a compact per-wave listing.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOLO_THRESHOLD = 5500
MAX_NOTES = 4
MAX_WORDS = 12000

# orientation notes (written last, with the full sibling list available)
ORIENTATION = {
    "07 - Sequence Models/Chapter Overview.md",
    "08 - Attention and Transformers/Attention and Transformers MOC.md",
    "09 - NLP and Language Models/NLP and Language Models MOC.md",
}


def main() -> int:
    plan: dict[str, list[dict]] = {}
    for slug in ("area07", "area08", "area09"):
        d = json.loads((REPO / f"scratch/synth/{slug}/notes.json").read_text())
        notes = d["notes"]
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
    Path(REPO / "scratch/synth/s22-wave-plan.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\nTOTAL agent groups: {total_agents}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
