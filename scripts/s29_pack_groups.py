#!/usr/bin/env python3
"""VERIF-001 probe packer: split the 246-KU sample into bounded judgment
groups for subagent execution.

Grouping (deterministic):
  - KUs sorted by primary destination path then ku_id
  - greedy fill: a group closes when it would exceed MAX_KUS (18) or
    MAX_NOTE_KB (220) of distinct destination-note text (union of all
    destinations of its KUs)

Outputs (scratch, git-ignored — regenerable from committed state):
  scratch/s29-verify/groups/group-NN.json   full probe spec per group
  scratch/s29-verify/judgments/             (subagents write group-NN.jsonl here)
Committed manifest:
  reports/synthesis/s29-semantic-groups.json
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path("/home/z/my-project/repo")
SAMPLE = REPO / "state/synthesis/s29-semantic-sample.jsonl"
GROUPS_DIR = REPO / "scratch/s29-verify/groups"
JUDG_DIR = REPO / "scratch/s29-verify/judgments"
MANIFEST = REPO / "reports/synthesis/s29-semantic-groups.json"
VAULT = REPO / "output/Unified-Vault"

MAX_KUS = 18
MAX_NOTE_KB = 300.0


def main() -> None:
    sample = [json.loads(l) for l in SAMPLE.open(encoding="utf-8") if l.strip()]
    sample.sort(key=lambda r: (r["destinations"][0]["path"] if r["destinations"] else "",
                               r["ku_id"]))

    note_size = {}
    for rec in sample:
        for d in rec["destinations"]:
            p = d["path"]
            if p not in note_size:
                note_size[p] = (VAULT / p).stat().st_size

    groups = []
    cur, cur_notes = [], set()

    def cur_kb():
        return sum(note_size[p] for p in cur_notes) / 1024.0

    for rec in sample:
        rec_notes = {d["path"] for d in rec["destinations"]}
        new_kb = sum(note_size[p] for p in cur_notes | rec_notes) / 1024.0
        if cur and (len(cur) >= MAX_KUS or new_kb > MAX_NOTE_KB):
            groups.append(cur)
            cur, cur_notes = [], set()
            new_kb = sum(note_size[p] for p in rec_notes) / 1024.0
        cur.append(rec)
        cur_notes |= rec_notes
    if cur:
        groups.append(cur)

    GROUPS_DIR.mkdir(parents=True, exist_ok=True)
    JUDG_DIR.mkdir(parents=True, exist_ok=True)

    manifest_groups = []
    for i, g in enumerate(groups, 1):
        notes = sorted({d["path"] for r in g for d in r["destinations"]})
        spec = {
            "group_id": i,
            "instructions": (
                "Semantic preservation judgment. For EACH knowledge unit below: "
                "read its source excerpt (verbatim from the immutable source vault), "
                "then read the destination note file(s) listed for it and decide "
                "whether the excerpt's knowledge is semantically carried by the "
                "destination note(s). Verdicts: 'present' (the facts/claims/details "
                "survive, allowing legitimate rewording, restructuring and "
                "consolidation); 'partial' (core idea present but material details "
                "dropped: specific values, exceptions, caveats, examples, "
                "qualifications); 'absent' (the knowledge cannot be found); "
                "'superseded-info-retained' (Superseded KUs only: the unique "
                "information named in superseded_rationale survives in the "
                "rationale-named destination). Rules: (1) judge ONLY against the "
                "destination note(s) listed for that KU; (2) every judgment MUST "
                "include 1-3 evidence_quotes copied VERBATIM (exact characters, "
                "may span within one line or across adjacent lines) from the "
                "destination note that carry the knowledge — quotes are verified "
                "mechanically, so do not paraphrase them; (3) keep quotes short "
                "(<= 200 chars each); (4) note any quality problems observed "
                "(contradictions, degraded prose) in quality_flags; (5) for "
                "empty_section KUs judge whether the section topic's knowledge "
                "exists in the destination; (6) for frontmatter KUs judge whether "
                "the meaningful metadata (concepts/tags/status) is reflected. "
                "Write one JSON object per line to the output file, in the same "
                "order as the KU list, with fields: ku_id, verdict, "
                "destination_note (path where evidence was found), evidence_quotes "
                "(array of strings), justification (1-3 sentences), quality_flags "
                "(array, may be empty)."
            ),
            "output_file": f"scratch/s29-verify/judgments/group-{i:02d}.jsonl",
            "notes_to_read": notes,
            "note_paths_root": "output/Unified-Vault/",
            "kus": [
                {
                    "ku_id": r["ku_id"],
                    "disposition": r["disposition"],
                    "unit_type": r["unit_type"],
                    "source_path": r["source_path"],
                    "heading_path": r["heading_path"],
                    "source_lines": f"{r['line_start']}-{r['line_end']}",
                    "excerpt": r["excerpt"],
                    "destinations": [d["path"] for d in r["destinations"]],
                    **({"superseded_rationale": r["superseded_rationale"]}
                       if "superseded_rationale" in r else {}),
                }
                for r in g
            ],
        }
        out = GROUPS_DIR / f"group-{i:02d}.json"
        out.write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
        manifest_groups.append({
            "group_id": i,
            "kus": len(g),
            "distinct_notes": len(notes),
            "note_kb_total": round(sum(note_size[p] for p in notes) / 1024.0, 1),
            "spec": str(out.relative_to(REPO)),
            "output": spec["output_file"],
        })

    manifest = {
        "task_id": "VERIF-001",
        "purpose": "judgment group manifest (deterministic from committed sample)",
        "method": ("KUs sorted by primary destination then ku_id; greedy grouping "
                   f"capped at {MAX_KUS} KUs and {MAX_NOTE_KB:.0f} KB of distinct "
                   "destination-note text per group"),
        "groups_total": len(groups),
        "kus_total": sum(len(g) for g in groups),
        "groups": manifest_groups,
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
    print(f"groups: {len(groups)}; kus: {manifest['kus_total']}")
    for m in manifest_groups:
        print(f"  group {m['group_id']:2d}: {m['kus']:2d} KUs, "
              f"{m['distinct_notes']:2d} notes, {m['note_kb_total']:6.1f} KB")


if __name__ == "__main__":
    main()
