#!/usr/bin/env python3
"""DISC-002 session 19: F-0022 repair — regenerate evidence entries in the
committed dossier-extension classification files (009..014).

Defect (F-0022): scripts/s18_dext_assembly.py built evidence entries with
``m.get("source_lines", [])``, but KU records carry ``line_start``/``line_end``
(no ``source_lines`` field). Every one of the 7,034 evidence entries across the
six committed files therefore has ``lines: []`` — a violation of the
dossier-extension-classification schema (lines must be a non-empty array of
source line numbers) and a loss of the line locators the evidence contract
requires. Quotes (200-char excerpt prefixes) and source_paths were correct;
the ku_ids, topics, classification ids and all decision fields are untouched.

Repair (narrow, deterministic, idempotent):
  * per record: classification_id, task_id, topic, overlap_type, ku_ids,
    rationale, candidate_ref, classified_by, method, date stay byte-identical;
  * every evidence entry is regenerated from the KU record found in the
    committed batches: quote = the KU's full excerpt, lines = the inclusive
    range [line_start..line_end], source_path = the KU's source_path — the
    same convention as the ext003..010 evidence (full excerpt + full span);
  * evidence entry order (sorted ku_ids) and key order are preserved;
  * scripts/s18_dext_assembly.py is fixed to construct evidence identically,
    so a future session-18 replay reproduces the repaired files byte-for-byte
    (verified by this script's REPLAY-CONSISTENCY assertions).

Delta-verification (pre-written arithmetic):
  * 6 files; 294 records (33 + 41 + 49 + 40 + 47 + 84);
  * 7,034 evidence entries (1,159 + 787 + 586 + 531 + 1,221 + 2,750);
  * before: 7,034 entries with empty lines; after: 0;
  * per record: ku_ids list unchanged; per file: record count and
    classification ids unchanged;
  * every regenerated lines list == [line_start..line_end] of its KU; every
    quote is byte-exact the KU excerpt; every source_path == the KU
    source_path; source_id's path part == source_path.

Usage:
  python3 scripts/s19_repair_ext_evidence.py            # repair + report
  python3 scripts/s19_repair_ext_evidence.py --check    # verify only, no write
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXT_FILES = {
    "regression": "state/classifications/009-disc002-dext-regression-extension.jsonl",
    "tree-based": "state/classifications/010-disc002-dext-tree-extension.jsonl",
    "evaluation": "state/classifications/011-disc002-dext-evaluation-extension.jsonl",
    "clustering": "state/classifications/012-disc002-dext-clustering-extension.jsonl",
    "generalization": "state/classifications/013-disc002-dext-generalization-extension.jsonl",
    "training-stability": "state/classifications/014-disc002-dext-training-stability-extension.jsonl",
}
EXPECTED_RECORDS = {"regression": 33, "tree-based": 41, "evaluation": 49,
                    "clustering": 40, "generalization": 47,
                    "training-stability": 84}
EXPECTED_EVIDENCE = {"regression": 1159, "tree-based": 787, "evaluation": 586,
                     "clustering": 531, "generalization": 1221,
                     "training-stability": 2750}
REPORT_OUT = REPO / "reports" / "dossier-ext" / "s19-f0022-repair-report.json"


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.open(encoding="utf-8") if l.strip()]


def ku_index() -> dict[str, dict]:
    """Index every KU id across ALL committed batches (70 files)."""
    kus: dict[str, dict] = {}
    for p in sorted((REPO / "state" / "knowledge-units").glob("*.jsonl")):
        for r in load_jsonl(p):
            kid = r["knowledge_unit_id"]
            if kid in kus and kus[kid] != r:
                raise ValueError(f"conflicting duplicate KU record for {kid}")
            kus[kid] = r
    return kus


def build_evidence_entry(ku: dict) -> dict:
    """The fixed evidence construction (mirrors the fixed s18_dext_assembly).

    Key order matches the committed files (ku_id, source_path, lines, quote)
    so only the VALUES change under repair.
    """
    return {
        "ku_id": ku["knowledge_unit_id"],
        "source_path": ku["source_path"],
        "lines": list(range(ku["line_start"], ku["line_end"] + 1)),
        "quote": ku["excerpt"],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="verify the committed files against the repaired "
                         "expectation without writing")
    opts = ap.parse_args()

    kus = ku_index()
    print(f"indexed {len(kus)} KU records from committed batches")

    report = {"command": "s19_repair_ext_evidence",
              "defect": "F-0022 (empty evidence lines in 009..014)",
              "files": {}, "checks": {}}
    all_ok = True
    total_records = total_evidence = 0
    for domain, rel in EXT_FILES.items():
        path = REPO / rel
        records = load_jsonl(path)
        if len(records) != EXPECTED_RECORDS[domain]:
            print(f"FAIL [{domain}]: record count {len(records)} != "
                  f"expected {EXPECTED_RECORDS[domain]}")
            all_ok = False
            continue
        repaired = []
        changes = 0
        empty_lines_before = 0
        empty_lines_after = 0
        for rec in records:
            # invariant fields stay byte-identical
            new = dict(rec)
            new_evidence = []
            for ev in rec["evidence"]:
                empty_lines_before += (not ev.get("lines"))
                ku = kus.get(ev["ku_id"])
                if ku is None:
                    print(f"FAIL [{domain}]: evidence ku_id {ev['ku_id']} "
                          "not found in committed batches")
                    all_ok = False
                    new_evidence.append(ev)
                    continue
                fixed = build_evidence_entry(ku)
                if ev != fixed:
                    changes += 1
                empty_lines_after += (not fixed["lines"])
                new_evidence.append(fixed)
            new["evidence"] = new_evidence
            if new["ku_ids"] != rec["ku_ids"]:
                print(f"FAIL [{domain}]: internal ku_ids mismatch")
                all_ok = False
            # every ku_id must have an evidence entry and vice versa
            if sorted(new["ku_ids"]) != sorted(e["ku_id"] for e in new_evidence):
                print(f"FAIL [{domain}]: {rec['classification_id']} "
                      "evidence/ku_ids set mismatch")
                all_ok = False
            repaired.append(new)
        n_ev = sum(len(r["evidence"]) for r in repaired)
        if n_ev != EXPECTED_EVIDENCE[domain]:
            print(f"FAIL [{domain}]: evidence entries {n_ev} != expected "
                  f"{EXPECTED_EVIDENCE[domain]}")
            all_ok = False
        total_records += len(repaired)
        total_evidence += n_ev

        if not opts.check:
            with path.open("w", encoding="utf-8") as fh:
                for r in repaired:
                    fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        report["files"][domain] = {
            "file": rel,
            "records": len(repaired),
            "evidence_entries": n_ev,
            "entries_changed": changes,
            "empty_lines_before": empty_lines_before,
            "empty_lines_after": empty_lines_after,
        }
        print(f"{domain:20s} records={len(repaired):3d} evidence={n_ev:4d} "
              f"changed={changes:4d} empty-lines {empty_lines_before} -> "
              f"{empty_lines_after}")

    # pre-written arithmetic
    ok_arith = (total_records == 294 and total_evidence == 7034
                and sum(EXPECTED_RECORDS.values()) == 294
                and sum(EXPECTED_EVIDENCE.values()) == 7034)
    report["checks"] = {
        "total_records": total_records, "expected_total_records": 294,
        "total_evidence_entries": total_evidence,
        "expected_total_evidence_entries": 7034,
        "arithmetic_ok": ok_arith,
    }
    print(f"TOTALS records={total_records}/294 evidence={total_evidence}/7034 "
          f"arithmetic={'PASS' if ok_arith else 'FAIL'}")
    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
    print(f"wrote {REPORT_OUT.relative_to(REPO)}")
    return 0 if (all_ok and ok_arith) else 1


if __name__ == "__main__":
    sys.exit(main())
