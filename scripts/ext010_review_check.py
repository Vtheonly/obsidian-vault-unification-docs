#!/usr/bin/env python3
"""EXT-010-REVIEW machine checks: independently re-verify the WRITTEN
classification file state/classifications/007-ext010-training-stability-overlap.jsonl
against the committed batches and the ORIGINAL source files.

This script shares no state with scripts/ext010_classifications.py: it reads
only the written JSONL. For every record and every evidence entry it checks:
  R1  the quote is byte-exact inside the referenced KU's excerpt (batch file);
  R2  the quote is byte-exact at its STATED lines in the ORIGINAL source file
      and those lines lie inside the KU's own span (0 off-by-one tolerance);
  R3  evidence ku_ids == record ku_ids;
  R4  the record is cross-vault (both ai-course and master-ai);
  R5  the record validates against schemas/overlap-classification.schema.json;
  R6  classification ids are unique and sequential;
  R7  no duplicate quotes file-wide;
  R8  committed classification files 001-006 are byte-identical to their
      git-HEAD versions (append-only discipline).

It also emits a COVERAGE section for the human/LLM reviewer:
  - participating KU counts per vault and per source file;
  - the cross-vault topics from the CAP-013 discovery report that have NO
    classification record touching their KU pairs (candidate coverage gaps
    the reviewer must adjudicate).

Writes reports/extraction/ext010-review-check.json; exits non-zero on any
machine failure. Read-only with respect to source vaults.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import jsonschema

REPO = Path(__file__).resolve().parents[1]
BATCHES = [
    REPO / "state/knowledge-units/010-ext010-master-ai-training-stability.jsonl",
    REPO / "state/knowledge-units/011-ext010-ai-course-04.3-init-gradients.jsonl",
]
COMMITTED = [
    "state/classifications/001-ext003-regression-overlap.jsonl",
    "state/classifications/002-ext004-tree-based-overlap.jsonl",
    "state/classifications/003-ext005-evaluation-overlap.jsonl",
    "state/classifications/004-ext007-evaluation-addendum.jsonl",
    "state/classifications/005-ext008-clustering-dimreduction-overlap.jsonl",
    "state/classifications/006-ext009-generalization-overlap.jsonl",
]
FILE = REPO / "state/classifications/007-ext010-training-stability-overlap.jsonl"
SCHEMA = REPO / "schemas/overlap-classification.schema.json"
DISCOVERY = REPO / "reports/extraction/ext010-overlap-candidates.json"
OUT = REPO / "reports/extraction/ext010-review-check.json"


def main() -> int:
    failures: list[str] = []
    kus: dict[str, dict] = {}
    for path in BATCHES:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                kus[r["knowledge_unit_id"]] = r

    records = [json.loads(line) for line in
               FILE.read_text(encoding="utf-8").splitlines() if line.strip()]

    # R6 ids
    ids = [r["classification_id"] for r in records]
    if len(ids) != len(set(ids)):
        failures.append("R6: duplicate classification ids")
    for i, cid in enumerate(ids, start=1):
        if not cid.endswith(f"-{i:04d}"):
            failures.append(f"R6: non-sequential id {cid}")

    # R7 duplicate quotes
    all_quotes = [e["quote"] for r in records for e in r["evidence"]]
    if len(all_quotes) != len(set(all_quotes)):
        failures.append("R7: duplicate quotes file-wide")

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)

    participating: set[str] = set()
    source_cache: dict[str, list[str]] = {}
    for rec in records:
        cid = rec["classification_id"]
        # R5 schema
        for err in validator.iter_errors(rec):
            failures.append(f"R5: {cid}: schema: {err.message}")
        # R3
        ev_ids = {e["ku_id"] for e in rec["evidence"]}
        if ev_ids != set(rec["ku_ids"]):
            failures.append(f"R3: {cid}: evidence ku_ids != record ku_ids")
        # R4
        vaults = {kus[k]["source_id"].split(":")[0]
                  for k in rec["ku_ids"] if k in kus}
        if vaults != {"ai-course", "master-ai"}:
            failures.append(f"R4: {cid}: not cross-vault ({vaults})")
        participating.update(rec["ku_ids"])
        for ev in rec["evidence"]:
            ku = kus.get(ev["ku_id"])
            if ku is None:
                failures.append(f"R1: {cid}: unknown KU {ev['ku_id']}")
                continue
            # R1 byte-exact in excerpt
            if ev["quote"] not in ku["excerpt"]:
                failures.append(f"R1: {cid}: quote not in excerpt of {ev['ku_id']}")
            # R2 at stated source lines
            lo, hi = min(ev["lines"]), max(ev["lines"])
            if ku["source_path"] not in source_cache:
                vault = ku["source_id"].split(":", 1)[0]
                sub = "Master AI" if vault == "master-ai" else "AI Course"
                src = REPO / "source-vaults" / "AI " / sub / ku["source_path"]
                source_cache[ku["source_path"]] = src.read_text(encoding="utf-8").splitlines()
            file_lines = source_cache[ku["source_path"]]
            if not (1 <= lo <= hi <= len(file_lines)):
                failures.append(f"R2: {cid}: lines {lo}-{hi} outside file")
                continue
            if not (ku["line_start"] <= lo and hi <= ku["line_end"]):
                failures.append(
                    f"R2: {cid}: stated lines {lo}-{hi} outside KU span "
                    f"{ku['line_start']}-{ku['line_end']} for {ev['ku_id']}")
                continue
            if ev["quote"] not in "\n".join(file_lines[lo - 1:hi]):
                failures.append(
                    f"R2: {cid}: quote NOT at stated lines {lo}-{hi} of "
                    f"{ku['source_path']} [ku {ev['ku_id']}]")

    # R8 committed files vs git HEAD
    for rel in COMMITTED:
        p = REPO / rel
        head = subprocess.run(
            ["git", "-C", str(REPO), "show", f"HEAD:{rel}"],
            capture_output=True).stdout
        if hashlib.sha256(head).hexdigest() != hashlib.sha256(p.read_bytes()).hexdigest():
            failures.append(f"R8: committed file differs from HEAD: {rel}")

    # Coverage section for the reviewer
    by_vault = {"ai-course": 0, "master-ai": 0}
    by_file: dict[str, int] = {}
    for kid in participating:
        v = kus[kid]["source_id"].split(":", 1)[0]
        by_vault[v] += 1
        by_file[kus[kid]["source_path"].split("/")[-1]] = \
            by_file.get(kus[kid]["source_path"].split("/")[-1], 0) + 1

    discovery = json.loads(DISCOVERY.read_text(encoding="utf-8"))
    pairs_path = REPO / "reports/extraction/ext010-overlap-candidates-pairs.jsonl"
    # topics with no classification touching their KUs
    uncovered_topics = []
    disc_topics = discovery.get("topics", [])
    with open(pairs_path, encoding="utf-8") as f:
        pairs = [json.loads(line) for line in f if line.strip()]
    topic_map: dict[str, list] = {}
    for p in pairs:
        topic_map.setdefault(p.get("topic", "?"), []).append(p)
    for topic, plist in sorted(topic_map.items()):
        ku_ids_in_topic = set()
        n_cross = 0
        for p in plist:
            ku_ids_in_topic.add(p["ku_a"]["ku_id"])
            ku_ids_in_topic.add(p["ku_b"]["ku_id"])
            if p["ku_a"]["vault"] != p["ku_b"]["vault"]:
                n_cross += 1
        if not (ku_ids_in_topic & participating):
            uncovered_topics.append({
                "topic": topic,
                "pairs": len(plist),
                "cross_vault_pairs": n_cross,
                "kus": len(ku_ids_in_topic),
            })

    report = {
        "command": "scripts/ext010_review_check.py",
        "file": str(FILE.relative_to(REPO)),
        "records": len(records),
        "quotes": len(all_quotes),
        "participating_kus": len(participating),
        "participating_by_vault": by_vault,
        "participating_by_file": dict(sorted(by_file.items())),
        "uncovered_cross_vault_topics": uncovered_topics,
        "uncovered_topic_count": len(uncovered_topics),
        "discovery_totals": {
            "term_pairs": discovery.get("result", {}).get("counts", {}).get("term_pairs"),
            "topics_cross_vault": discovery.get("result", {}).get("counts", {}).get("topics_cross_vault"),
            "truncated_topics": discovery.get("result", {}).get("truncated_topics"),
        },
        "failures": failures,
        "ok": not failures,
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items()
                      if k != "uncovered_cross_vault_topics"}, indent=2))
    if uncovered_topics:
        print(f"UNCOVERED topics for reviewer adjudication: "
              f"{len(uncovered_topics)} (full list in {OUT.relative_to(REPO)})")
    if failures:
        print("FAILURES:", *failures, sep="\n  ")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
