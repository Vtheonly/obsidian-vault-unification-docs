#!/usr/bin/env python3
"""INTEG-005 probe packer: split the 374 unique remaining-cluster inventory
items (MAPDIG + MATHSOLVER + WEATHER + NLME + MASTER-INDEX) into bounded
semantic-coverage judgment groups for subagent execution.

Carry-over rule (F-0048, binding): items already judged in a prior canonical
judgment file (MEDNLP / 2D3D / SYNPATH) are NOT re-judged — 29 carry-overs
are excluded from groups here and merged verbatim (with carry_over_from
provenance) by scripts/s35_validate_judgments.py.

Denominator (F-0049 union accounting): 374 unique items = 81 MAPDIG + 91
MATHSOLVER + 78 WEATHER + 97 NLME + 35 MASTER-INDEX − 19 cross-cluster
duplicates inside the set.

Grouping (deterministic, same as S32/S33/S34):
  - each fresh item is placed by its first matching cluster in CLUSTERS
    order, then by that cluster's section (first-occurrence order), item_id
  - MASTER-INDEX table-field items have no section -> pseudo-section
    '(master index fields)' (26 broad field labels incl. 2 not first-placed
    elsewhere)
  - a group closes at MAX_ITEMS (18) or when its section ends (sections are
    never merged: related items share candidate notes, and the judge's
    context stays topically coherent)
  - sections longer than MAX_ITEMS split into consecutive chunks

Outputs (scratch, git-ignored — regenerable from committed state):
  scratch/s35-integ/groups/group-NN.json      full judgment spec per group
  scratch/s35-integ/judgments/                (subagents write group-NN.jsonl)
Committed manifest:
  reports/integration/s35-rest-groups.json

RESUME SAFETY: this packer is deterministic; a partially executed session can
re-run it (byte-identical specs) and launch judges only for group outputs
that are missing — the validator reports missing files explicitly.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path("/home/z/my-project/repo")
INVENTORY = REPO / "state/integration/inventory-v1.jsonl"
COVERAGE = REPO / "state/integration/coverage-lexical-v1.jsonl"
PRIOR_FILES = {
    "MEDNLP": REPO / "state/integration/judgments-mednlp-v1.jsonl",
    "2D3D": REPO / "state/integration/judgments-2d3d-v1.jsonl",
    "SYNPATH": REPO / "state/integration/judgments-synpath-v1.jsonl",
}
GROUPS_DIR = REPO / "scratch/s35-integ/groups"
JUDG_DIR = REPO / "scratch/s35-integ/judgments"
MANIFEST = REPO / "reports/integration/s35-rest-groups.json"

MAX_ITEMS = 18
CLUSTERS = ["MAPDIG", "MATHSOLVER", "WEATHER", "NLME", "MASTER-INDEX"]

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
   For time-series/weather items try 'forecasting', 'seasonality', 'trend',
   'lag', 'imputation', 'meteorolog*', 'reanalysis'; for segmentation items
   try 'segmentation', 'threshold', 'watershed', 'contour', 'vectorization',
   'raster'; for OCR/math-solving items try 'OCR', 'handwriting', 'LaTeX',
   'tokeniz*', 'decoder', 'beam search'; for memory/long-context items try
   'attention', 'KV cache', 'context window', 'retrieval', 'episodic',
   'associative memory', 'Hopfield', 'modern hopfield'; for broad field
   labels judge whether the vault covers the FIELD at survey depth (multiple
   notes spanning the field's core concepts) and cite the most central note.
3. Assign exactly one verdict per item:
   - 'covered': an existing note/section explains the concept at the depth
     standard — what it is, why it exists/what problem it solves, how it works
     at a conceptual level, how it relates to other vault concepts. (Project
     usage need NOT be present for 'covered' — project context is integrated
     later by the campaign.) For broad field labels (e.g. 'Transformers',
     'Time-Series AI'), 'covered' requires the vault to span the field's core
     with the cited note as a genuine anchor.
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


def placement(item: dict) -> tuple[str, str]:
    for c in CLUSTERS:
        occ = next((o for o in item["occurrences"] if o["cluster"] == c), None)
        if occ:
            return (c, occ["section"] or "(master index fields)")
    raise AssertionError(f"no S35 cluster occurrence for {item['item_id']}")


def main() -> None:
    inv = [json.loads(l) for l in INVENTORY.open(encoding="utf-8") if l.strip()]
    cov = {}
    for line in COVERAGE.open(encoding="utf-8"):
        if line.strip():
            rec = json.loads(line)
            cov[rec["item_id"]] = rec

    prior: dict[str, dict] = {}
    for src_name, path in PRIOR_FILES.items():
        for line in path.open(encoding="utf-8"):
            if line.strip():
                rec = json.loads(line)
                prior[rec["item_id"]] = {"src": src_name, "judgment": rec}

    target = [i for i in inv if any(c in i["clusters"] for c in CLUSTERS)]
    carry_over = [i for i in target if i["item_id"] in prior]
    carry_ids = {i["item_id"] for i in carry_over}
    to_judge = [i for i in target if i["item_id"] not in carry_ids]

    # section order by first occurrence in the file, cluster by cluster
    section_order: list[tuple[str, str]] = []
    for cluster in CLUSTERS:
        for i in inv:
            if cluster in i["clusters"]:
                occ = next((o for o in i["occurrences"] if o["cluster"] == cluster), None)
                if occ:
                    key = (cluster, occ["section"] or "(master index fields)")
                    if key not in section_order:
                        section_order.append(key)

    def sort_key(i: dict) -> tuple:
        return (section_order.index(placement(i)), i["item_id"])

    to_judge.sort(key=sort_key)

    groups: list[list[dict]] = []
    cur: list[dict] = []
    cur_key: tuple | None = None
    for item in to_judge:
        key = placement(item)
        if cur and (len(cur) >= MAX_ITEMS or key != cur_key):
            groups.append(cur)
            cur = []
        cur.append(item)
        cur_key = key
    if cur:
        groups.append(cur)

    GROUPS_DIR.mkdir(parents=True, exist_ok=True)
    JUDG_DIR.mkdir(parents=True, exist_ok=True)

    manifest_groups = []
    for gi, g in enumerate(groups, 1):
        sections = sorted({f"{placement(i)[0]}: {placement(i)[1]}" for i in g})
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
            seen, dedup = set(), []
            for cand in candidates:
                if cand["note"] not in seen:
                    seen.add(cand["note"])
                    dedup.append(cand)
            cluster, section = placement(item)
            spec_items.append(
                {
                    "item_id": item["item_id"],
                    "name": item["name"],
                    "alias": item.get("alias"),
                    "section": section,
                    "cluster": cluster,
                    "group_labels": item.get("group_labels", []),
                    "entity_types": item.get("entity_types", []),
                    "lexical_band": c["band"],
                    "candidate_notes": dedup,
                }
            )
        spec = {
            "group_id": gi,
            "campaign": "INTEG-005",
            "clusters": CLUSTERS,
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
                "spec": f"scratch/s35-integ/groups/group-{gi:02d}.json",
                "output": f"scratch/s35-integ/judgments/group-{gi:02d}.jsonl",
            }
        )

    manifest = {
        "campaign": "INTEG-005",
        "clusters": CLUSTERS,
        "items_total": len(target),
        "items_fresh_judged": len(to_judge),
        "items_carried_over": len(carry_over),
        "carry_over": {
            "rule": (
                "F-0048 one item = one judgment: items already judged in a prior "
                "canonical judgment file are carried over verbatim (verdict, "
                "destination, quote, rationale) with carry_over_from provenance, not "
                "re-judged — the vault is byte-identical since those judgments, and "
                "the S36 decision ledger is keyed by item id"
            ),
            "items": [
                {
                    "item_id": i["item_id"],
                    "name": i["name"],
                    "prior_file": f"judgments-{prior[i['item_id']]['src'].lower()}-v1.jsonl",
                    "prior_verdict": prior[i["item_id"]]["judgment"]["verdict"],
                }
                for i in sorted(carry_over, key=lambda x: x["item_id"])
            ],
        },
        "groups_total": len(groups),
        "max_items_per_group": MAX_ITEMS,
        "grouping": (
            "by first matching cluster (MAPDIG, MATHSOLVER, WEATHER, NLME, "
            "MASTER-INDEX order) and section (first-occurrence order), consecutive "
            "chunks at 18 items; sections never merged; MASTER-INDEX table-field "
            "items grouped under the pseudo-section '(master index fields)'"
        ),
        "lexical_hint_source": "state/integration/coverage-lexical-v1.jsonl",
        "judgment_schema": {
            "required": ["item_id", "verdict", "destination_note", "evidence_quote", "equivalent_name", "rationale", "search_terms_tried"],
            "verdicts": ["covered", "equivalent", "partial", "absent"],
        },
        "groups": manifest_groups,
    }
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"packed {len(target)} items: {len(to_judge)} fresh into {len(groups)} groups, {len(carry_over)} carried over")
    for g in manifest_groups:
        print(f"  group-{g['group_id']:02d}: {g['items']:2d} items | {', '.join(s[:44] for s in g['sections'])}")


if __name__ == "__main__":
    main()
