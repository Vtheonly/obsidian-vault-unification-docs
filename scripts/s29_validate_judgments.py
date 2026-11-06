#!/usr/bin/env python3
"""VERIF-001 mechanical validation of subagent judgments.

Validates all 18 group judgment files:
  1. Schema: required fields, allowed verdicts, quote count 1-3, quote length <= 200.
  2. Coverage: exactly one judgment per sampled KU (246), no extras, no missing.
  3. Evidence integrity: every evidence_quote is a substring of the cited
     destination_note file after whitespace normalization (collapse runs of
     whitespace to single spaces). Also checks the cited note is one of the
     KU's declared destinations.
  4. Order: judgments appear in the same order as the group's KU list.

Exit code 0 = all valid. Any violation prints details and exits 1.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path("/home/z/my-project/repo")
JUDG_DIR = REPO / "scratch/s29-verify/judgments"
VAULT = REPO / "output/Unified-Vault"
ALLOWED_VERDICTS = {"present", "partial", "absent", "superseded-info-retained"}

def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()

def main() -> int:
    sample = {}
    for line in (REPO / "state/synthesis/s29-semantic-sample.jsonl").open(encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            sample[r["ku_id"]] = r

    manifest = json.loads((REPO / "reports/synthesis/s29-semantic-groups.json").read_text())
    problems = []
    judged = {}
    note_cache: dict[str, str] = {}

    for g in manifest["groups"]:
        gid = g["group_id"]
        spec = json.loads((REPO / f"scratch/s29-verify/groups/group-{gid:02d}.json").read_text())
        expected_ids = [k["ku_id"] for k in spec["kus"]]
        jpath = JUDG_DIR / f"group-{gid:02d}.jsonl"
        if not jpath.exists():
            problems.append(f"group {gid}: output file missing: {jpath}")
            continue
        recs = [json.loads(l) for l in jpath.open(encoding="utf-8") if l.strip()]

        if [r.get("ku_id") for r in recs] != expected_ids:
            problems.append(f"group {gid}: judgment order/ids do not match KU list")

        for r in recs:
            kid = r.get("ku_id")
            if kid not in sample:
                problems.append(f"group {gid}: unknown ku_id {kid}")
                continue
            if kid in judged:
                problems.append(f"group {gid}: duplicate judgment for {kid}")
            judged[kid] = r
            ku = sample[kid]

            if r.get("verdict") not in ALLOWED_VERDICTS:
                problems.append(f"{kid}: invalid verdict {r.get('verdict')!r}")
            if ku["disposition"] != "Superseded" and r.get("verdict") == "superseded-info-retained":
                problems.append(f"{kid}: superseded-info-retained used for non-Superseded KU")
            if ku["disposition"] == "Superseded" and r.get("verdict") not in ("superseded-info-retained", "partial", "absent"):
                problems.append(f"{kid}: Superseded KU got verdict {r.get('verdict')!r}")

            quotes = r.get("evidence_quotes")
            if not isinstance(quotes, list) or not (1 <= len(quotes) <= 3):
                problems.append(f"{kid}: evidence_quotes must be 1-3 strings")
                continue
            for q in quotes:
                if not isinstance(q, str) or not q:
                    problems.append(f"{kid}: empty/non-string quote")
                    continue
                if len(q) > 200:
                    problems.append(f"{kid}: quote exceeds 200 chars ({len(q)})")
            if not isinstance(r.get("justification"), str) or len(r.get("justification", "")) < 10:
                problems.append(f"{kid}: justification missing/too short")
            if not isinstance(r.get("quality_flags"), list):
                problems.append(f"{kid}: quality_flags must be a list")

            dest = r.get("destination_note")
            dests = {d["path"] for d in ku["destinations"]}
            if dest not in dests:
                problems.append(f"{kid}: destination_note {dest!r} not among declared {sorted(dests)}")
                continue

            np = VAULT / dest
            if dest not in note_cache:
                note_cache[dest] = np.read_text(encoding="utf-8")
            note_norm = norm(note_cache[dest])
            for i, q in enumerate(quotes):
                if isinstance(q, str) and q and norm(q) not in note_norm:
                    problems.append(f"{kid}: quote[{i}] NOT FOUND in {dest}: {q[:80]!r}")

    missing = set(sample) - set(judged)
    if missing:
        problems.append(f"{len(missing)} sampled KUs lack judgments: {sorted(missing)[:5]}")

    if problems:
        print(f"VALIDATION FAILED — {len(problems)} problems")
        for p in problems:
            print(" -", p)
        return 1

    from collections import Counter
    verdicts = Counter(r["verdict"] for r in judged.values())
    print(f"VALIDATION PASSED: {len(judged)}/{len(sample)} KUs judged, all quotes verbatim-verified")
    print("verdicts:", dict(verdicts))
    flags = [(kid, r["quality_flags"]) for kid, r in sorted(judged.items()) if r["quality_flags"]]
    print(f"quality flags on {len(flags)} KUs:")
    for kid, fl in flags:
        for f in fl:
            print(f"  {kid}: {f[:150]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
