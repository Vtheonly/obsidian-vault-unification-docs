#!/usr/bin/env python3
"""S28/SYNTH-001: pack the area-20 notes into bounded waves.

Same deterministic pattern and output format as s21..s25_pack_waves.py
(battle-tested on 328+ notes):
- area 20 has NO orientation notes (no area-root MOC — the archival context
  layer), so every note is a content note;
- notes with more than SOLO_THRESHOLD source words get a dedicated agent;
- the rest are packed by natural cluster (master-ai management logs travel
  together; navigation notes travel together; ai-course notes travel
  together — the sibling context each note must link to), up to MAX_NOTES
  notes or MAX_WORDS source words per agent.

Output: a JSON wave plan (scratch, regenerable) + a compact per-wave listing.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SOLO_THRESHOLD = 5500
MAX_NOTES = 4
MAX_WORDS = 12000

SLUGS = ("area20",)

# cluster affinity: notes in the same cluster are packed together so the
# agent sees the sibling context it must link to
CLUSTERS = {
    "ai-course": (
        "20 - Vault and Project Context/AI Course Master Index.md",
        "20 - Vault and Project Context/AI Course Merge Report.md",
    ),
    "management-log": (
        "20 - Vault and Project Context/Architecture Decisions Log.md",
        "20 - Vault and Project Context/Completed Work Log.md",
        "20 - Vault and Project Context/Coverage Audit Log.md",
        "20 - Vault and Project Context/Current Iteration Log.md",
        "20 - Vault and Project Context/Next Iteration Log.md",
        "20 - Vault and Project Context/Remaining Work Log.md",
        "20 - Vault and Project Context/Vault Status Log.md",
        "20 - Vault and Project Context/Vault Management README.md",
        "20 - Vault and Project Context/Research Queue.md",
    ),
    "navigation": (
        "20 - Vault and Project Context/Learning Roadmap.md",
        "20 - Vault and Project Context/Master AI Index.md",
        "20 - Vault and Project Context/Master AI MOC.md",
        "20 - Vault and Project Context/Master AI README.md",
        "20 - Vault and Project Context/Master Roadmap.md",
        "20 - Vault and Project Context/Reading Orders.md",
    ),
}
CLUSTER_ORDER = ("ai-course", "management-log", "navigation")


def cluster_of(path: str) -> str:
    for name in CLUSTER_ORDER:
        if path in CLUSTERS[name]:
            return name
    return "zz-misc"


def main() -> int:
    plan: dict[str, list[dict]] = {}
    for slug in SLUGS:
        d = json.loads((REPO / f"scratch/synth/{slug}/notes.json").read_text())
        notes = list(d["notes"])
        big = [n for n in notes if n["source_words"] > SOLO_THRESHOLD]
        rest = [n for n in notes if n["source_words"] <= SOLO_THRESHOLD]

        groups: list[list[dict]] = []
        # big notes get dedicated agents first (descending size)
        for n in sorted(big, key=lambda x: -x["source_words"]):
            groups.append([n])

        # pack the rest by cluster, descending size within cluster
        rest.sort(key=lambda n: (CLUSTER_ORDER.index(cluster_of(n["path"])), -n["source_words"]))
        current: list[dict] = []
        for n in rest:
            if current and (
                len(current) >= MAX_NOTES
                or sum(x["source_words"] for x in current) + n["source_words"] > MAX_WORDS
                or cluster_of(current[0]["path"]) != cluster_of(n["path"])
            ):
                groups.append(current)
                current = []
            current.append(n)
        if current:
            groups.append(current)

        plan[slug] = [{"notes": g} for g in groups]

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
            print(
                f"  g{i:02d}: {len(g['notes'])} notes, {words} src words :: "
                + "; ".join(f"{n['index']:02d}:{n['path'].split('/', 1)[1]}" for n in g["notes"])
            )
    Path(REPO / "scratch/synth/s28-wave-plan.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(f"\nTOTAL agent groups: {total_agents}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
