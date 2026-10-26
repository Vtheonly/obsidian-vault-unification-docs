#!/usr/bin/env python3
"""EXT-005-REVIEW mechanical verification of 003-ext005-evaluation-overlap.jsonl.

Checks (read-only; writes nothing to state):
  CHECK 1 - every evidence quote is a byte-exact substring of the referenced
            KU's excerpt field in the referenced batch.
  CHECK 2 - every evidence quote appears at the stated source lines in the
            ORIGINAL source file (off-by-one tolerance on the first line).
  CHECK 3 - every record has ku_ids from BOTH vaults (master-ai: / ai-course:).
  EXTRA   - schema-ish structural checks: required fields, id sequence,
            evidence ku_ids subset of record ku_ids, every record ku_id
            present in a batch, evidence source_path matches KU source_path.
"""
import json
import sys
from pathlib import Path

REPO = Path("/home/z/my-project/repo")
CLS_PATH = REPO / "state/classifications/003-ext005-evaluation-overlap.jsonl"
BATCHES = {
    "004": REPO / "state/knowledge-units/004-ext005-master-ai-evaluation.jsonl",
    "005": REPO / "state/knowledge-units/005-ext005-ai-course-03.6-model-evaluation.jsonl",
}
ROOTS = [
    REPO / "source-vaults/AI /Master AI",
    REPO / "source-vaults/AI /AI Course",
]

records = [json.loads(l) for l in CLS_PATH.read_text().splitlines() if l.strip()]

kus = {}  # ku_id -> KU record (with batch tag)
for tag, path in BATCHES.items():
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        ku = json.loads(line)
        kus[ku["knowledge_unit_id"]] = ku

failures = []
counts = {"quotes": 0, "byte_exact": 0, "line_ok": 0, "line_off_by_one": 0,
          "line_fail": 0, "quote_not_in_source": 0}

# ---------------- CHECK 1 + 2 + evidence structural ----------------
for rec in records:
    cid = rec["classification_id"]
    for ev in rec.get("evidence", []):
        counts["quotes"] += 1
        ku = kus.get(ev["ku_id"])
        if ku is None:
            failures.append(f"{cid}: evidence ku_id {ev['ku_id']} not found in batches")
            continue
        # source_path consistency
        if ev["source_path"] != ku["source_path"]:
            failures.append(
                f"{cid}: evidence source_path {ev['source_path']!r} != KU source_path {ku['source_path']!r}")
        excerpt = ku["excerpt"]
        q = ev["quote"]
        if q in excerpt:
            counts["byte_exact"] += 1
        else:
            failures.append(f"{cid}: CHECK1 FAIL quote not byte-exact in excerpt of {ev['ku_id']}: {q[:120]!r}")

        # CHECK 2: original source file lookup
        src = None
        for root in ROOTS:
            cand = root / ev["source_path"]
            if cand.exists():
                src = cand
                break
        if src is None:
            failures.append(f"{cid}: source file not found for path {ev['source_path']!r}")
            continue
        src_lines = src.read_text(encoding="utf-8").splitlines()
        first_line = ev["lines"][0]
        # find actual first line where quote's first line appears
        # The quote may span multiple lines; take its first line as needle.
        quote_lines = q.split("\n")
        needle = quote_lines[0].strip()
        if not needle:
            # weird empty first line; try first non-empty
            needle = next((l for l in quote_lines if l.strip()), "").strip()
        actual = None
        occurrences = []
        for i, ln in enumerate(src_lines, start=1):
            if needle and needle in ln:
                occurrences.append(i)
        if needle and occurrences:
            actual = occurrences[0]
            nearest = min(occurrences, key=lambda x: abs(x - first_line))
            delta = nearest - first_line
            if abs(delta) <= 1:
                counts["line_ok"] += 1
                if delta != 0:
                    counts["line_off_by_one"] += 1
            else:
                # check if full multi-line quote appears at the stated lines
                joined_src = "\n".join(src_lines)
                if q in joined_src:
                    # verify position: find line index of q start
                    pos = joined_src.find(q)
                    line_at_pos = joined_src[:pos].count("\n") + 1
                    if abs(line_at_pos - first_line) <= 1:
                        counts["line_ok"] += 1
                        if line_at_pos != first_line:
                            counts["line_off_by_one"] += 1
                    else:
                        counts["line_fail"] += 1
                        failures.append(
                            f"{cid}: CHECK2 FAIL {ev['ku_id']} stated first line {first_line}, "
                            f"full-quote found at line {line_at_pos}")
                else:
                    counts["line_fail"] += 1
                    fails = sorted(occurrences)[:5]
                    failures.append(
                        f"{cid}: CHECK2 FAIL {ev['ku_id']} stated first line {first_line}; "
                        f"needle first-line occurrences at {fails}")
        else:
            # needle not found as a substring of any single line; try full quote in file
            joined_src = "\n".join(src_lines)
            if q in joined_src:
                pos = joined_src.find(q)
                line_at_pos = joined_src[:pos].count("\n") + 1
                if abs(line_at_pos - first_line) <= 1:
                    counts["line_ok"] += 1
                    if line_at_pos != first_line:
                        counts["line_off_by_one"] += 1
                else:
                    counts["line_fail"] += 1
                    failures.append(
                        f"{cid}: CHECK2 FAIL {ev['ku_id']} stated {first_line}, quote at {line_at_pos}")
            else:
                counts["quote_not_in_source"] += 1
                failures.append(
                    f"{cid}: CHECK2 FAIL quote text not found in source file "
                    f"{ev['source_path']!r} (KU {ev['ku_id']}): {q[:100]!r}")

# ---------------- CHECK 3 + structural ----------------
struct_fail = []
cross_vault_ok = 0
for rec in records:
    cid = rec["classification_id"]
    prefixes = set()
    for ku_id in rec["ku_ids"]:
        if ku_id not in kus:
            struct_fail.append(f"{cid}: ku_id {ku_id} not in any batch")
        else:
            prefixes.add(kus[ku_id]["source_id"].split(":", 1)[0])
    if "master-ai" in prefixes and "ai-course" in prefixes:
        cross_vault_ok += 1
    else:
        struct_fail.append(f"{cid}: CHECK3 FAIL vault prefixes {sorted(prefixes)}")
    # required fields
    for f in ["classification_id", "task_id", "topic", "overlap_type", "ku_ids",
              "rationale", "evidence", "classified_by", "date"]:
        if f not in rec:
            struct_fail.append(f"{cid}: missing required field {f}")
    # evidence ku_ids subset of record ku_ids
    ev_ids = {ev["ku_id"] for ev in rec.get("evidence", [])}
    missing_ev = ev_ids - set(rec["ku_ids"])
    if missing_ev:
        struct_fail.append(f"{cid}: evidence ku_ids not in record ku_ids: {sorted(missing_ev)}")
    # both vaults represented in evidence?
    ev_prefixes = {kus[e["ku_id"]]["source_id"].split(":", 1)[0] for e in rec.get("evidence", [])}
    if not ({"master-ai", "ai-course"} <= ev_prefixes):
        struct_fail.append(f"{cid}: evidence does not cover both vaults: {sorted(ev_prefixes)}")

# id sequence
expected = [f"OC-ext005-{i:04d}" for i in range(1, len(records) + 1)]
ids = [r["classification_id"] for r in records]
if ids != expected:
    struct_fail.append(f"id sequence mismatch: {ids}")

# participation stats
participating = {}
for rec in records:
    for ku_id in rec["ku_ids"]:
        participating.setdefault(ku_id, []).append(rec["classification_id"])

unclassified_master = [ku for ku_id, ku in kus.items()
                       if ku["source_id"].startswith("master-ai:") and ku_id not in participating]
unclassified_course = [ku_id for ku_id in kus
                       if kus[ku_id]["source_id"].startswith("ai-course:") and ku_id not in participating]

print(f"records: {len(records)}")
print(f"CHECK1: quotes checked={counts['quotes']} byte-exact={counts['byte_exact']} "
      f"failed={counts['quotes'] - counts['byte_exact']}")
print(f"CHECK2: line_ok={counts['line_ok']} (of which off-by-one={counts['line_off_by_one']}) "
      f"line_fail={counts['line_fail']} quote_not_in_source={counts['quote_not_in_source']}")
print(f"CHECK3: cross-vault records {cross_vault_ok}/{len(records)}")
print(f"structural failures: {len(struct_fail)}")
for f in struct_fail:
    print("  STRUCT:", f)
print(f"evidence/quote failures: {len(failures)}")
for f in failures:
    print("  FAIL:", f)
print(f"participating KUs: {len(participating)} "
      f"(master-ai: {sum(1 for k in participating if kus[k]['source_id'].startswith('master-ai:'))}, "
      f"ai-course: {sum(1 for k in participating if kus[k]['source_id'].startswith('ai-course:'))})")
print(f"unclassified master-ai KUs: {len(unclassified_master)}")
for ku in unclassified_master:
    print(f"  UNCLASS-MASTER: {ku['knowledge_unit_id']} L{ku['line_start']}-{ku['line_end']} "
          f"[{ku['heading_path']}] {ku['excerpt'][:90].replace(chr(10),' | ')!r}")
print(f"unclassified ai-course KUs: {len(unclassified_course)}/{sum(1 for k in kus.values() if k['source_id'].startswith('ai-course:'))}")
