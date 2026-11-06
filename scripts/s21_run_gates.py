#!/usr/bin/env python3
"""S21/SYNTH-001: run the per-area quality gate chain (assess -> filter -> drift -> gate).

Reusable for every remaining synthesis area (sessions 22+). Deterministic,
idempotent. Chain per area slug:

  1. vu assess-quality over the WHOLE output vault (so the shared link
     context resolves links across already-generated areas) with the area's
     provenance mapping -> scratch/synth/<slug>/gates/assessments-all.jsonl
  2. deterministic filter to the area's expected notes ->
     scratch/synth/<slug>/gates/assessments.jsonl (order preserved)
  3. vu quality-drift over the filtered assessments
  4. vu quality-gate with the area's expected-notes (waivers passed through)

Exit 0 only when the gate verdict is "pass". Reports land in
reports/synthesis/s21-<slug>-{assess,drift,gate}.json (committed evidence).

Usage: python3 scripts/s21_run_gates.py <slug> [--waiver drift::<type>=<reason>]...
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def run(cmd: list[str]) -> dict:
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO))
    if p.returncode != 0:
        print(f"FAILED ({p.returncode}): {' '.join(cmd)}\n{p.stdout}\n{p.stderr}", file=sys.stderr)
        raise SystemExit(p.returncode)
    try:
        return json.loads(p.stdout)
    except json.JSONDecodeError:
        return {"raw": (p.stdout + p.stderr)[:400]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("slug", help="area scratch slug, e.g. area05")
    ap.add_argument("--waiver", action="append", default=[], help="quality-gate waiver, e.g. drift::reference=reason")
    ap.add_argument("--skip-assess", action="store_true", help="reuse existing assessments-all.jsonl")
    args = ap.parse_args()

    slug = args.slug
    gates = REPO / "scratch/synth" / slug / "gates"
    gates.mkdir(parents=True, exist_ok=True)
    all_jsonl = gates / "assessments-all.jsonl"
    area_jsonl = gates / "assessments.jsonl"
    expected = REPO / "scratch/synth" / slug / "expected-notes.txt"
    provenance = REPO / "scratch/synth" / slug / "provenance.jsonl"
    for req in (expected, provenance):
        if not req.is_file():
            print(f"missing input: {req}", file=sys.stderr)
            return 2
    expected_notes = {l.strip() for l in expected.read_text(encoding="utf-8").splitlines() if l.strip()}

    # ---- 1. assess (whole vault root: cross-area links resolve) ----
    if not args.skip_assess or not all_jsonl.is_file():
        cmd = [
            "vu", "assess-quality", "output/Unified-Vault",
            "--provenance", str(provenance),
            "--out", str(all_jsonl),
            "--report", f"reports/synthesis/s21-{slug}-assess.json",
        ]
        for batch in sorted((REPO / "state/knowledge-units").glob("*.jsonl")):
            cmd += ["--ku-batch", str(batch)]
        assess = run(cmd)
        print("assess:", json.dumps({k: v for k, v in assess.items() if not isinstance(v, (list, dict))}))

    # ---- 2. filter to the area's notes (order preserved) ----
    kept, dropped = [], 0
    with all_jsonl.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("note") in expected_notes:
                kept.append(line)
            else:
                dropped += 1
    area_jsonl.write_text("\n".join(kept) + "\n", encoding="utf-8")
    print(f"filtered: {len(kept)} area notes kept, {dropped} other-area notes excluded")
    if len(kept) != len(expected_notes):
        print(
            f"ERROR: expected {len(expected_notes)} notes, kept {len(kept)} "
            "(missing: " + ", ".join(sorted(expected_notes - {json.loads(l)['note'] for l in kept})) + ")",
            file=sys.stderr,
        )
        return 1

    # ---- 3. drift ----
    drift = run([
        "vu", "quality-drift",
        "--assessments", str(area_jsonl),
        "--report", f"reports/synthesis/s21-{slug}-drift.json",
    ])
    drifted = [
        t
        for t in drift.get("drifted_types", [])
        if (t.get("verdict") == "drift_detected" if isinstance(t, dict) else True)
    ]
    print("drift: drifted types:", [t["type"] if isinstance(t, dict) else t for t in drifted] or "none")

    # ---- 4. gate ----
    cmd = [
        "vu", "quality-gate",
        "--assessments", str(area_jsonl),
        "--expected", str(expected),
        "--drift-report", f"reports/synthesis/s21-{slug}-drift.json",
        "--report", f"reports/synthesis/s21-{slug}-gate.json",
    ]
    for w in args.waiver:
        cmd += ["--waiver", w]
    gate = run(cmd)
    verdict = gate.get("verdict")
    print("gate:", json.dumps({k: v for k, v in gate.items() if not isinstance(v, (list, dict))}))
    if verdict != "pass":
        print("GATE FAILED:", json.dumps(gate.get("failures", []), indent=1)[:2000], file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
