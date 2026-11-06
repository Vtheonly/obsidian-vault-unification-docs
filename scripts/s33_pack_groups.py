#!/usr/bin/env python3
"""INTEG-003 probe packer: split the 291 2D3D inventory items into bounded
semantic-coverage judgment groups for subagent execution.

Grouping (deterministic):
  - items sorted by (2D3D section order of first occurrence, item_id)
  - a group closes at MAX_ITEMS (18) or when its section ends (sections are
    never merged: related items share candidate notes, and the judge's
    context stays topically coherent)
  - sections longer than MAX_ITEMS split into consecutive chunks

Group spec carries per-item lexical hints (band + candidate notes from
coverage-lexical-v1.jsonl) — hints only; judges must search for equivalent
concepts under different names before concluding 'absent'.

Outputs (scratch, git-ignored — regenerable from committed state):
  scratch/s33-integ/groups/group-NN.json      full judgment spec per group
  scratch/s33-integ/judgments/                (subagents write group-NN.jsonl)
Committed manifest:
  reports/integration/s33-2d3d-groups.json
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path("/home/z/my-project/repo")
INVENTORY = REPO / "state/integration/inventory-v1.jsonl"
COVERAGE = REPO / "state/integration/coverage-lexical-v1.jsonl"
GROUPS_DIR = REPO / "scratch/s33-integ/groups"
JUDG_DIR = REPO / "scratch/s33-integ/judgments"
MANIFEST = REPO / "reports/integration/s33-2d3d-groups.json"

MAX_ITEMS = 18

INSTRUCTIONS = """\
You are judging SEMANTIC COVERAGE of inventory items against a delivered
Obsidian knowledge vault (read-only; 544 notes under the given root).

For EACH item in this group, decide whether the vault already explains the
concept at the DEPTH STANDARD, using this procedure:

1. Read the per-item lexical hints (band + candidate notes). 'title'/'heading'
   bands mean a note/heading with the same surface name exists; 'partial' means
   a substring-related title/heading exists; 'body-*' means occurrences in
   note bodies; 'none' means no lexical trace — but terminology may differ
   (e.g. 'Message Passing Neural Networks' vs a 'Graph Neural Networks' note).
2. Read the candidate notes (only those relevant). Use Grep/Glob on the vault
   root to search for the item's name, alias, acronyms, and ALTERNATIVE
   TERMINOLOGY (British/American variants, expanded/abbreviated forms,
   hypernym concepts under which the item might be explained as a section).
   Grep is cheap; use several search terms per item before concluding absent.
3. Assign exactly one verdict per item:
   - 'covered': an existing note/section explains the concept at the depth
     standard — what it is, why it exists/what problem it solves, how it works
     at a conceptual level, how it relates to other vault concepts. (Project
     usage need NOT be present for 'covered' — project context is integrated
     later by the campaign.)
   - 'equivalent': covered under a DIFFERENT name (e.g. the item 'K-Nearest
     Neighbour Matching' is explained inside an American-spelling note on
     nearest-neighbor methods). Cite the destination and quote evidence; give
     the covering concept name in 'equivalent_name'.
   - 'partial': the concept is mentioned or only superficially explained
     (a bare mention, a definition without the why/how, a passing example) —
     the right home exists but the explanation is below the depth standard.
   - 'absent': no adequate explanation anywhere in the vault after a genuine
     search (record the search terms you tried in 'search_terms_tried').
4. EVIDENCE RULE (mechanically validated): for 'covered'/'equivalent', give a
   verbatim quote (>= 12 words, copied EXACTLY including punctuation) from the
   destination note that demonstrates the depth. For 'partial', give the best
   verbatim quote from the note that shows what IS there. Quotes are checked
   as exact substrings of the cited note — do not paraphrase, do not fix
   typos, copy a contiguous span.
5. Destination notes are paths RELATIVE to the vault root (as given in the
   hints). You may cite any note in the vault, not only hinted ones.

OUTPUT: write exactly one JSON object per item (JSON Lines, UTF-8) to the
given output path, in the same order as the input items, with fields:
  item_id, verdict (covered|equivalent|partial|absent),
  destination_note (relative path or null),
  evidence_quote (verbatim quote or null),
  equivalent_name (string or null),
  rationale (1-3 sentences: what you found and why the verdict fits),
  search_terms_tried (list of the grep terms you used for this item)

Do not modify any file in the vault. Write ONLY your output JSONL file.
"""


def main() -> None:
    inv = [json.loads(l) for l in INVENTORY.open(encoding="utf-8") if l.strip()]
    cov = {}
    for line in COVERAGE.open(encoding="utf-8"):
        if line.strip():
            rec = json.loads(line)
            cov[rec["item_id"]] = rec

    med = [i for i in inv if "2D3D" in i["clusters"]]
    # section order by first occurrence in the file
    section_order: list[str] = []
    for i in med:
        for occ in i["occurrences"]:
            if occ["cluster"] == "2D3D" and occ["section"] not in section_order:
                section_order.append(occ["section"])
    med.sort(
        key=lambda i: (
            section_order.index(next(o["section"] for o in i["occurrences"] if o["cluster"] == "2D3D")),
            i["item_id"],
        )
    )

    groups: list[list[dict]] = []
    cur: list[dict] = []
    cur_section: str | None = None
    for item in med:
        section = next(o["section"] for o in item["occurrences"] if o["cluster"] == "2D3D")
        if cur and (len(cur) >= MAX_ITEMS or section != cur_section):
            groups.append(cur)
            cur = []
        cur.append(item)
        cur_section = section
    if cur:
        groups.append(cur)

    GROUPS_DIR.mkdir(parents=True, exist_ok=True)
    JUDG_DIR.mkdir(parents=True, exist_ok=True)

    manifest_groups = []
    for gi, g in enumerate(groups, 1):
        sections = sorted(
            {
                next(o["section"] for o in i["occurrences"] if o["cluster"] == "2D3D")
                for i in g
            }
        )
        out_path = JUDG_DIR / f"group-{gi:02d}.jsonl"
        spec_items = []
        for item in g:
            c = cov[item["item_id"]]
            candidates = []
            for m in c["title_matches"][:3]:
                candidates.append({"note": m["note"], "why": f"title match ({m['kind']})"})
            for m in c["heading_matches"][:3]:
                candidates.append({"note": m["note"], "why": "heading match", "heading": m.get("heading")})
            for m in c["body"]["top_notes"][:2]:
                candidates.append({"note": m["note"], "why": f"body x{m['count']}"})
            # dedupe by note, keep first
            seen, dedup = set(), []
            for cand in candidates:
                if cand["note"] not in seen:
                    seen.add(cand["note"])
                    dedup.append(cand)
            spec_items.append(
                {
                    "item_id": item["item_id"],
                    "name": item["name"],
                    "alias": item.get("alias"),
                    "section": next(o["section"] for o in item["occurrences"] if o["cluster"] == "2D3D"),
                    "group_labels": item.get("group_labels", []),
                    "entity_types": item.get("entity_types", []),
                    "lexical_band": c["band"],
                    "candidate_notes": dedup,
                }
            )
        spec = {
            "group_id": gi,
            "campaign": "INTEG-003",
            "cluster": "2D3D",
            "sections": sections,
            "vault_root": "output/Unified-Vault",
            "instructions": INSTRUCTIONS,
            "items": spec_items,
            "output_path": str(out_path.relative_to(REPO)),
        }
        (GROUPS_DIR / f"group-{gi:02d}.json").write_text(
            json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        manifest_groups.append(
            {
                "group_id": gi,
                "sections": sections,
                "items": len(spec_items),
                "item_ids": [i["item_id"] for i in spec_items],
                "spec": f"scratch/s33-integ/groups/group-{gi:02d}.json",
                "output": f"scratch/s33-integ/judgments/group-{gi:02d}.jsonl",
            }
        )

    manifest = {
        "campaign": "INTEG-003",
        "cluster": "2D3D",
        "items_total": len(med),
        "groups_total": len(groups),
        "max_items_per_group": MAX_ITEMS,
        "grouping": "by 2D3D section (first-occurrence order), consecutive chunks at 18 items; sections never merged",
        "lexical_hint_source": "state/integration/coverage-lexical-v1.jsonl",
        "judgment_schema": {
            "required": ["item_id", "verdict", "destination_note", "evidence_quote", "equivalent_name", "rationale", "search_terms_tried"],
            "verdicts": ["covered", "equivalent", "partial", "absent"],
        },
        "groups": manifest_groups,
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"packed {len(med)} 2D3D items into {len(groups)} groups")
    for g in manifest_groups:
        print(f"  group-{g['group_id']:02d}: {g['items']:2d} items | {', '.join(s[:40] for s in g['sections'])}")


if __name__ == "__main__":
    main()
