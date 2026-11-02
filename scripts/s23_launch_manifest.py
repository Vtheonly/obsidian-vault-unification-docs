#!/usr/bin/env python3
"""S23/SYNTH-001: emit the per-group launch manifest for orchestrator use.

Reads scratch/synth/s23-wave-plan.json and prints, per group, the exact bundle
paths, canonical output paths, note types and KU counts — everything the
orchestrator needs to compose subagent prompts.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

def main() -> int:
    plan = json.loads((REPO / "scratch/synth/s23-wave-plan.json").read_text())
    manifest = []
    for slug, groups in plan["areas"].items():
        notes_by_path = {n["path"]: n for n in json.loads((REPO / f"scratch/synth/{slug}/notes.json").read_text())["notes"]}
        for gi, g in enumerate(groups, 1):
            entries = []
            for n in g["notes"]:
                entries.append(
                    {
                        "bundle": f"scratch/synth/{slug}/bundles/{n['bundle'].split('/')[-1]}",
                        "out": f"output/Unified-Vault/{n['path']}",
                        "title": n["title"],
                        "type": n["type"],
                        "index": n["index"],
                        "kus": n["ku_count"],
                        "src_words": n["source_words"],
                    }
                )
            manifest.append(
                {
                    "group": f"{slug}-g{gi:02d}",
                    "slug": slug,
                    "orientation": bool(g.get("orientation_wave")),
                    "notes": entries,
                    "total_src_words": sum(e["src_words"] for e in entries),
                }
            )
    (REPO / "scratch/synth/s23-launch-manifest.json").write_text(json.dumps(manifest, indent=1))
    for m in manifest:
        print(f"{m['group']}{' [ORIENT]' if m['orientation'] else ''}: {len(m['notes'])} notes, {m['total_src_words']} words")
        for e in m["notes"]:
            print(f"    {e['index']:02d} [{e['type']}] {e['kus']} KUs -> {e['out']}")
    print(f"\n{len(manifest)} groups, {sum(len(m['notes']) for m in manifest)} notes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
