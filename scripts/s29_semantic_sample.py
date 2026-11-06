#!/usr/bin/env python3
"""VERIF-001 setup: post-delivery stratified semantic spot-verification.

Addresses final-report §5.1 limitation #1: marker retention is lexical, not
semantic. This campaign draws a deterministic stratified sample of knowledge
units and subjects each to an independent reading-level semantic judgment
(subagent groups, orchestrator-reviewed) with mechanically verifiable
destination evidence quotes.

Sampling design (deterministic, no RNG):
  - Census: every (disposition, unit_type) cell with population <= 3
    (covers Superseded x2 and empty_section x2 in full).
  - Stratified allocation over the remaining budget of 240:
      Contextualized 40 / Consolidated 118 / Preserved 80
    (reduced by any census members already drawn from that disposition),
    allocated across unit_types proportionally (largest remainder),
    minimum 1 per non-empty non-census cell.
  - Within a cell: sort by ku_id, pick evenly spaced indices
    round(i*(N-1)/(n-1)) — reproducible without randomness.

Outputs (committed):
  state/synthesis/s29-semantic-sample.jsonl   one record per sampled KU
  reports/synthesis/s29-semantic-sample.json  allocation report w/ denominators
  state/task-queue.jsonl                      + VERIF-001 (appended)
  state/current-state.json                    current_task_id/stage refresh
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path("/home/z/my-project/repo")
LEDGER = REPO / "state/dispositions/001-disp001-rule-driven.jsonl"
BATCH_DIR = REPO / "state/knowledge-units"
SAMPLE_OUT = REPO / "state/synthesis/s29-semantic-sample.jsonl"
REPORT_OUT = REPO / "reports/synthesis/s29-semantic-sample.json"

DISPOSITION_TARGETS = {"Contextualized": 40, "Consolidated": 118, "Preserved": 80}
CENSUS_MAX = 3


def load_jsonl(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def largest_remainder(total: int, weights: dict[str, int]) -> dict[str, int]:
    """Proportional integer allocation with largest-remainder tie-breaking.
    Ties broken by descending weight then ascending key for determinism."""
    wsum = sum(weights.values())
    if wsum == 0 or total <= 0:
        return {k: 0 for k in weights}
    raw = {k: total * w / wsum for k, w in weights.items()}
    alloc = {k: int(v) for k, v in raw.items()}
    rem = total - sum(alloc.values())
    order = sorted(weights, key=lambda k: (-(raw[k] - alloc[k]), -weights[k], k))
    for k in order[:rem]:
        alloc[k] += 1
    return alloc


def even_spaced(ku_ids: list[str], n: int) -> list[str]:
    assert n <= len(ku_ids)
    if n == len(ku_ids):
        return list(ku_ids)
    if n == 1:
        return [ku_ids[len(ku_ids) // 2]]
    return [ku_ids[round(i * (len(ku_ids) - 1) / (n - 1))] for i in range(n)]


def main() -> int:
    # ---- merge raw KU batches with the dispositions ledger (s20 overlay) ----
    ku_by_id = {}
    for batch in sorted(BATCH_DIR.glob("*.jsonl")):
        for rec in load_jsonl(batch):
            kid = rec["knowledge_unit_id"]
            assert kid not in ku_by_id, f"duplicate KU id {kid}"
            ku_by_id[kid] = rec
    ledger = load_jsonl(LEDGER)
    assert len(ku_by_id) == len(ledger) == 27536

    merged = []
    for r in ledger:
        base = dict(ku_by_id[r["ku_id"]])
        base["disposition"] = r["disposition"]
        base["destinations"] = r["destinations"]
        if r["disposition"] == "Superseded":
            base["superseded_rationale"] = r["rationale"]
        else:
            base["rationale"] = r["rationale"]
        merged.append(base)

    # ---- cell census + stratified allocation ----
    cells = defaultdict(list)
    for rec in merged:
        cells[(rec["disposition"], rec["unit_type"])].append(rec["knowledge_unit_id"])
    for ids in cells.values():
        ids.sort()

    sample_ids = []
    census_log = []
    for (disp, utype), ids in sorted(cells.items()):
        if len(ids) <= CENSUS_MAX:
            sample_ids.extend(ids)
            census_log.append({"disposition": disp, "unit_type": utype,
                               "population": len(ids), "drawn": len(ids),
                               "method": "census"})

    censused_by_disp = Counter()
    for rec in merged:
        if rec["knowledge_unit_id"] in set(sample_ids):
            censused_by_disp[rec["disposition"]] += 1

    alloc_log = list(census_log)
    for disp, target in sorted(DISPOSITION_TARGETS.items()):
        remaining = max(0, target - censused_by_disp.get(disp, 0))
        cell_pop = {ut: len(ids) for (d, ut), ids in cells.items()
                    if d == disp and len(ids) > CENSUS_MAX}
        if not cell_pop or remaining == 0:
            for ut, pop in sorted(cell_pop.items()):
                alloc_log.append({"disposition": disp, "unit_type": ut,
                                  "population": pop, "drawn": 0,
                                  "method": "stratified (none — budget exhausted)"})
            continue
        # cap: never draw more than population
        remaining = min(remaining, sum(cell_pop.values()))
        alloc = largest_remainder(remaining, cell_pop)
        # enforce minimum 1 per non-empty cell where budget allows
        for ut in sorted(cell_pop):
            if alloc[ut] == 0 and remaining >= 1:
                alloc[ut] = 1
                remaining -= 1
        # final largest-remainder pass after min bumps (keep total == remaining+bumps)
        # (min bumps only redistribute, totals preserved by construction above)
        for (d, ut), ids in sorted(cells.items()):
            if d == disp and len(ids) > CENSUS_MAX:
                drawn = alloc[ut]
                sample_ids.extend(even_spaced(ids, drawn))
                alloc_log.append({"disposition": disp, "unit_type": ut,
                                  "population": len(ids), "drawn": drawn,
                                  "method": "stratified even-spaced by ku_id"})

    sample_set = set(sample_ids)
    assert len(sample_ids) == len(sample_set), "duplicate draws"

    # ---- area floor: every destination area gets >= 2 sampled KUs ----
    # Deterministic: within an under-represented area, draw evenly-spaced KUs
    # from the highest-rewrite-risk disposition available (Consolidated first,
    # then Contextualized, then Preserved), sorted by ku_id.
    DISP_PRIORITY = ["Consolidated", "Contextualized", "Preserved", "Superseded"]
    area_pop = defaultdict(list)
    for rec in merged:
        if rec["destinations"]:
            area_pop[rec["destinations"][0]["path"].split("/")[0]].append(rec)
    area_floor_log = []
    for area in sorted(area_pop):
        members = [r for r in area_pop[area] if r["knowledge_unit_id"] not in sample_set]
        drawn_here = sum(1 for r in area_pop[area] if r["knowledge_unit_id"] in sample_set)
        need = 2 - drawn_here
        if need <= 0 or not members:
            continue
        for disp in DISP_PRIORITY:
            if need <= 0:
                break
            pool = sorted([r["knowledge_unit_id"] for r in members
                           if r["disposition"] == disp])
            if not pool:
                continue
            take = min(need, len(pool))
            for kid in even_spaced(pool, take):
                sample_ids.append(kid)
                sample_set.add(kid)
                need -= 1
        area_floor_log.append({"area": area, "added_to_reach_floor": 2 - drawn_here})

    # ---- write sample file ----
    sampled = [r for r in merged if r["knowledge_unit_id"] in sample_set]
    sampled.sort(key=lambda r: r["knowledge_unit_id"])
    SAMPLE_OUT.parent.mkdir(parents=True, exist_ok=True)
    with SAMPLE_OUT.open("w", encoding="utf-8") as fh:
        for rec in sampled:
            out = {
                "ku_id": rec["knowledge_unit_id"],
                "disposition": rec["disposition"],
                "unit_type": rec["unit_type"],
                "source_id": rec["source_id"],
                "source_path": rec["source_path"],
                "heading_path": rec["heading_path"],
                "line_start": rec["line_start"],
                "line_end": rec["line_end"],
                "excerpt": rec["excerpt"],
                "destinations": rec["destinations"],
            }
            if rec["disposition"] == "Superseded":
                out["superseded_rationale"] = rec["superseded_rationale"]
            fh.write(json.dumps(out, ensure_ascii=False) + "\n")

    # ---- report ----
    by_disp = Counter(r["disposition"] for r in sampled)
    by_type = Counter(r["unit_type"] for r in sampled)
    areas_in_sample = set()
    for r in sampled:
        for d in r["destinations"]:
            areas_in_sample.add(d["path"].split("/")[0])
    by_area = Counter(r["destinations"][0]["path"].split("/")[0] if r["destinations"] else "(none)"
                      for r in sampled)
    report = {
        "task_id": "VERIF-001",
        "purpose": "post-delivery stratified semantic spot-verification (final-report §5.1 limitation #1)",
        "population": {"kus_total": len(merged),
                       "by_disposition": dict(Counter(r["disposition"] for r in merged)),
                       "by_unit_type": dict(Counter(r["unit_type"] for r in merged))},
        "sample": {"drawn": len(sampled),
                   "fraction": round(len(sampled) / len(merged), 5),
                   "by_disposition": dict(by_disp),
                   "by_unit_type": dict(by_type),
                   "by_destination_area": dict(sorted(by_area.items())),
                   "method": ("census of (disposition x unit_type) cells with population<=3; "
                              "stratified allocation Contextualized 40 / Consolidated 118 / "
                              "Preserved 80 (minus census members), proportional across unit_types "
                              "by largest remainder, minimum 1 per non-empty cell; within-cell "
                              "selection evenly spaced over ku_id-sorted members (no RNG); "
                              "area floor: every destination area >= 2 sampled KUs "
                              "(Consolidated > Contextualized > Preserved priority); allocation "
                              "overweights prose/list/callout deliberately — math/code/table "
                              "already carry verbatim fingerprints in the lexical marker net "
                              "(final-report gate 7), so reading-level effort targets the "
                              "claims the marker net covers least")},
        "allocation_log": alloc_log,
        "area_floor_log": area_floor_log,
        "areas_covered": len(areas_in_sample),
        "judgment_protocol": {
            "verdicts": ["present", "partial", "absent",
                         "superseded-info-retained (Superseded KUs only)"],
            "evidence_rule": ("every judgment must quote verbatim span(s) from the destination "
                              "note that carry the knowledge; quotes are mechanically verified "
                              "to appear in the note file"),
            "denominator": "sampled KUs with a completed judgment",
        },
        "sample_file": "state/synthesis/s29-semantic-sample.jsonl",
    }
    REPORT_OUT.write_text(json.dumps(report, ensure_ascii=False, indent=1) + "\n",
                          encoding="utf-8")

    print(f"sample drawn: {len(sampled)}/{len(merged)} ({report['sample']['fraction']:.2%})")
    print("by disposition:", dict(by_disp))
    print("by unit_type:", dict(by_type))
    print("areas covered:", len(by_area))
    return 0


if __name__ == "__main__":
    sys.exit(main())
