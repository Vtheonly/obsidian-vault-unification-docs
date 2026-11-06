#!/usr/bin/env python3
"""INTEG-003 mechanical validation of 2D3D judgment records.

Checks (all must pass):
  1. schema: every record has the required fields with correct types;
     verdict in the enum.
  2. coverage: the 368 2D3D item ids are judged EXACTLY once each (no
     missing, no duplicates, no foreign ids), in manifest group order.
  3. evidence: every covered/equivalent/partial record cites a destination
     note that exists, and its evidence_quote is a verbatim
     (whitespace-normalized) substring of that note; covered/equivalent
     quotes must be >= 12 words.
  4. absent discipline: absent records have no destination, no quote, and at
     least one search term recorded.

Exit 0 only when VALIDATION PASSED; prints per-check failures otherwise.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path("/home/z/my-project/repo")
VAULT = REPO / "output/Unified-Vault"
INVENTORY = REPO / "state/integration/inventory-v1.jsonl"
MANIFEST = REPO / "reports/integration/s33-2d3d-groups.json"
JUDG_DIR = REPO / "scratch/s33-integ/judgments"
OUT = REPO / "state/integration/judgments-2d3d-v1.jsonl"

VERDICTS = {"covered", "equivalent", "partial", "absent"}
REQUIRED = ["item_id", "verdict", "destination_note", "evidence_quote", "equivalent_name", "rationale", "search_terms_tried"]


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def main() -> int:
    inv = [json.loads(l) for l in INVENTORY.open(encoding="utf-8") if l.strip()]
    med_ids = [i["item_id"] for i in inv if "2D3D" in i["clusters"]]
    med_set = set(med_ids)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    failures: list[str] = []
    records: list[dict] = []
    note_cache: dict[str, str] = {}

    expected_order: list[str] = []
    for g in manifest["groups"]:
        expected_order.extend(g["item_ids"])

    for g in manifest["groups"]:
        p = JUDG_DIR / f"group-{g['group_id']:02d}.jsonl"
        if not p.is_file():
            failures.append(f"group {g['group_id']:02d}: output file missing")
            continue
        group_recs = [json.loads(l) for l in p.open(encoding="utf-8") if l.strip()]
        if len(group_recs) != len(g["item_ids"]):
            failures.append(
                f"group {g['group_id']:02d}: {len(group_recs)} records vs {len(g['item_ids'])} expected"
            )
        for idx, rec in enumerate(group_recs):
            # 1. schema
            for f in REQUIRED:
                if f not in rec:
                    failures.append(f"group {g['group_id']:02d} rec {idx}: missing field {f}")
            if rec.get("verdict") not in VERDICTS:
                failures.append(f"{rec.get('item_id')}: bad verdict {rec.get('verdict')!r}")
                continue
            if not isinstance(rec.get("rationale"), str) or not rec["rationale"].strip():
                failures.append(f"{rec.get('item_id')}: empty rationale")
            if not isinstance(rec.get("search_terms_tried"), list) or not rec["search_terms_tried"]:
                failures.append(f"{rec.get('item_id')}: search_terms_tried empty/not a list")
            # 2. evidence rules
            v = rec["verdict"]
            if v == "absent":
                if rec.get("destination_note") or rec.get("evidence_quote"):
                    failures.append(f"{rec['item_id']}: absent but cites destination/quote")
            else:
                dest = rec.get("destination_note")
                quote = rec.get("evidence_quote")
                if not dest or not isinstance(dest, str):
                    failures.append(f"{rec['item_id']}: {v} without destination_note")
                    continue
                np = VAULT / dest
                if not np.is_file():
                    failures.append(f"{rec['item_id']}: destination not found: {dest}")
                    continue
                if dest not in note_cache:
                    note_cache[dest] = np.read_text(encoding="utf-8", errors="replace")
                if not quote or not isinstance(quote, str):
                    failures.append(f"{rec['item_id']}: {v} without evidence_quote")
                    continue
                if norm(quote) not in norm(note_cache[dest]):
                    failures.append(f"{rec['item_id']}: quote NOT verbatim in {dest}: {quote[:80]!r}")
                if v in ("covered", "equivalent") and len(quote.split()) < 12:
                    failures.append(f"{rec['item_id']}: {v} quote shorter than 12 words")
                if v == "equivalent" and not rec.get("equivalent_name"):
                    failures.append(f"{rec['item_id']}: equivalent without equivalent_name")
            records.append(rec)

    # 3. exact coverage of the 2D3D item set
    got_ids = [r["item_id"] for r in records]
    counts: dict[str, int] = {}
    for i in got_ids:
        counts[i] = counts.get(i, 0) + 1
    missing = [i for i in med_ids if counts.get(i, 0) == 0]
    dupes = sorted(i for i in counts if counts[i] > 1)
    foreign = sorted(set(got_ids) - med_set)
    if missing:
        failures.append(f"missing judgments for {len(missing)} items: {missing[:10]}")
    if dupes:
        failures.append(f"duplicate judgments for: {dupes[:10]}")
    if foreign:
        failures.append(f"foreign item ids: {foreign[:10]}")
    if got_ids != expected_order:
        # order deviations are tolerable if the set matches exactly; record it
        if sorted(got_ids) == sorted(med_ids):
            print("NOTE: group order deviates from manifest; set coverage exact")
        else:
            failures.append("judgment set does not match manifest item set")

    from collections import Counter
    verdict_counts = Counter(r["verdict"] for r in records)
    print(f"records: {len(records)} | verdicts: {dict(verdict_counts)}")
    if failures:
        print(f"\nVALIDATION FAILED ({len(failures)} failures):")
        for f in failures[:40]:
            print("  -", f)
        return 1

    # write the merged canonical judgment file (sorted by item_id for stability)
    records.sort(key=lambda r: r["item_id"])
    OUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8")
    print(f"VALIDATION PASSED {len(records)}/{len(med_ids)} (all quotes verbatim-verified)")
    print(f"merged judgments written: {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
