#!/usr/bin/env python3
"""INTEG-005 mechanical validation of remaining-cluster judgment records.

Checks (all must pass):
  1. schema: every record has the required fields with correct types;
     verdict in the enum.
  2. coverage: the 374 unique MAPDIG+MATHSOLVER+WEATHER+NLME+MASTER-INDEX
     item ids are judged EXACTLY once each (no missing, no duplicates, no
     foreign ids) — 345 fresh group records + 29 carried over from prior
     canonical judgment files (F-0048; manifest carry-over list re-validated
     against the same vault state).
  3. evidence: every covered/equivalent/partial record cites a destination
     note that exists, and its evidence_quote is a verbatim
     (whitespace-normalized) substring of that note; covered/equivalent
     quotes must be >= 12 words.
  4. absent discipline: absent records have no destination, no quote, and at
     least one search term recorded.

Exit 0 only when VALIDATION PASSED; prints per-check failures otherwise.
Missing group files are reported individually so a partially executed
session can resume by launching judges only for the missing groups.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path("/home/z/my-project/repo")
VAULT = REPO / "output/Unified-Vault"
INVENTORY = REPO / "state/integration/inventory-v1.jsonl"
MANIFEST = REPO / "reports/integration/s35-rest-groups.json"
JUDG_DIR = REPO / "scratch/s35-integ/judgments"
OUT = REPO / "state/integration/judgments-rest-v1.jsonl"
PRIOR_FILES = {
    "judgments-mednlp-v1.jsonl": REPO / "state/integration/judgments-mednlp-v1.jsonl",
    "judgments-2d3d-v1.jsonl": REPO / "state/integration/judgments-2d3d-v1.jsonl",
    "judgments-synpath-v1.jsonl": REPO / "state/integration/judgments-synpath-v1.jsonl",
}

VERDICTS = {"covered", "equivalent", "partial", "absent"}
REQUIRED = ["item_id", "verdict", "destination_note", "evidence_quote", "equivalent_name", "rationale", "search_terms_tried"]


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def check_record(rec: dict, failures: list[str], note_cache: dict[str, str], where: str) -> None:
    """Schema + evidence checks shared by fresh and carried-over records."""
    for f in REQUIRED:
        if f not in rec:
            failures.append(f"{where}: missing field {f}")
    if rec.get("verdict") not in VERDICTS:
        failures.append(f"{where}: bad verdict {rec.get('verdict')!r}")
        return
    if not isinstance(rec.get("rationale"), str) or not rec["rationale"].strip():
        failures.append(f"{where}: empty rationale")
    if not isinstance(rec.get("search_terms_tried"), list) or not rec["search_terms_tried"]:
        failures.append(f"{where}: search_terms_tried empty/not a list")
    v = rec["verdict"]
    if v == "absent":
        if rec.get("destination_note") or rec.get("evidence_quote"):
            failures.append(f"{where}: absent but cites destination/quote")
        return
    dest = rec.get("destination_note")
    quote = rec.get("evidence_quote")
    if not dest or not isinstance(dest, str):
        failures.append(f"{where}: {v} without destination_note")
        return
    np = VAULT / dest
    if not np.is_file():
        failures.append(f"{where}: destination not found: {dest}")
        return
    if dest not in note_cache:
        note_cache[dest] = np.read_text(encoding="utf-8", errors="replace")
    if not quote or not isinstance(quote, str):
        failures.append(f"{where}: {v} without evidence_quote")
        return
    if norm(quote) not in norm(note_cache[dest]):
        failures.append(f"{where}: quote NOT verbatim in {dest}: {quote[:80]!r}")
    if v in ("covered", "equivalent") and len(quote.split()) < 12:
        failures.append(f"{where}: {v} quote shorter than 12 words")
    if v == "equivalent" and not rec.get("equivalent_name"):
        failures.append(f"{where}: equivalent without equivalent_name")


def main() -> int:
    inv = [json.loads(l) for l in INVENTORY.open(encoding="utf-8") if l.strip()]
    clusters = {"MAPDIG", "MATHSOLVER", "WEATHER", "NLME", "MASTER-INDEX"}
    target_ids = [i["item_id"] for i in inv if clusters & set(i["clusters"])]
    target_set = set(target_ids)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    failures: list[str] = []
    records: list[dict] = []
    note_cache: dict[str, str] = {}

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
            check_record(rec, failures, note_cache, f"group {g['group_id']:02d} rec {idx} ({rec.get('item_id')})")
            records.append(rec)

    # ---- carry-over records (manifest carry_over list) ----
    carry_meta = manifest["carry_over"]["items"]
    prior_records: dict[str, dict] = {}
    for pf in PRIOR_FILES.values():
        for line in pf.open(encoding="utf-8"):
            if line.strip():
                pr = json.loads(line)
                prior_records[pr["item_id"]] = pr
    for cm in carry_meta:
        iid = cm["item_id"]
        if iid not in prior_records:
            failures.append(f"carry-over {iid}: not found in prior judgment file")
            continue
        pr = dict(prior_records[iid])
        check_record(pr, failures, note_cache, f"carry-over {iid}")
        pr["carry_over_from"] = cm["prior_file"]
        pr["rationale"] = pr["rationale"] + " [Carried over from the " + cm["prior_file"] + " record (same item, multi-cluster membership; vault byte-identical since).]"
        records.append(pr)

    # ---- exact coverage of the remaining-cluster item set ----
    got_ids = [r["item_id"] for r in records]
    counts: dict[str, int] = {}
    for i in got_ids:
        counts[i] = counts.get(i, 0) + 1
    missing = [i for i in target_ids if counts.get(i, 0) == 0]
    dupes = sorted(i for i in counts if counts[i] > 1)
    foreign = sorted(set(got_ids) - target_set)
    if missing:
        failures.append(f"missing judgments for {len(missing)} items: {missing[:10]}")
    if dupes:
        failures.append(f"duplicate judgments for: {dupes[:10]}")
    if foreign:
        failures.append(f"foreign item ids: {foreign[:10]}")

    from collections import Counter

    verdict_counts = Counter(r["verdict"] for r in records)
    carried = sum(1 for r in records if r.get("carry_over_from"))
    print(
        f"records: {len(records)} ({carried} carried over) | "
        f"verdicts: {dict(verdict_counts)}"
    )
    if failures:
        print(f"\nVALIDATION FAILED ({len(failures)} failures):")
        for f in failures[:40]:
            print("  -", f)
        return 1

    # write the merged canonical judgment file (sorted by item_id for stability)
    records.sort(key=lambda r: r["item_id"])
    OUT.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records),
        encoding="utf-8",
    )
    print(f"VALIDATION PASSED {len(records)}/{len(target_ids)} (all quotes verbatim-verified)")
    print(f"merged judgments written: {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
