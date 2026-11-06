#!/usr/bin/env python3
"""s29 startup verification: independently reproduce the s28 full-corpus audit.

Replicates the ledger overlay documented in scripts/s20_build_synthesis_inputs.py
(raw committed KU batches + dispositions ledger -> effective audit records),
then re-runs `vu audit-output` over the entire 544-note vault and compares
against the committed s28 report (reports/synthesis/s28-final-full-corpus-audit.json):
expected valid=true, 0 findings, 27,536 KUs, markers 26,308 term / 14,119 math /
1,729 code, 0 missing.
"""
import json
import subprocess
import sys
from pathlib import Path

REPO = Path("/home/z/my-project/repo")
LEDGER = REPO / "state/dispositions/001-disp001-rule-driven.jsonl"
BATCH_DIR = REPO / "state/knowledge-units"
OUT_BATCH = REPO / "scratch/s29-verify/full-corpus-audit-kus.jsonl"
REPORT = "reports/synthesis/s29-verify-full-corpus-audit.json"


def load_jsonl(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


# 1. load raw KU batches -> ku_by_id
ku_by_id = {}
for batch in sorted(BATCH_DIR.glob("*.jsonl")):
    for rec in load_jsonl(batch):
        kid = rec["knowledge_unit_id"]
        assert kid not in ku_by_id, f"duplicate KU id {kid} across batches"
        ku_by_id[kid] = rec
print(f"raw KU records: {len(ku_by_id)}")

# 2. load ledger
ledger = load_jsonl(LEDGER)
print(f"ledger records: {len(ledger)}")

# 3. 1:1 coverage assertions (fail loudly)
ledger_ids = {r["ku_id"] for r in ledger}
missing_in_ledger = set(ku_by_id) - ledger_ids
missing_in_kus = ledger_ids - set(ku_by_id)
assert not missing_in_ledger, f"{len(missing_in_ledger)} KUs lack ledger disposition"
assert not missing_in_kus, f"{len(missing_in_kus)} ledger KUs lack extraction record"

# 4. overlay (exact s20 semantics: disposition + destinations + superseded rationale)
audit_records = []
for r in ledger:
    base = dict(ku_by_id[r["ku_id"]])
    base["disposition"] = r["disposition"]
    base["destinations"] = r["destinations"]
    if r["disposition"] == "Superseded":
        base["superseded_rationale"] = r["rationale"]
    audit_records.append(base)

OUT_BATCH.parent.mkdir(parents=True, exist_ok=True)
with OUT_BATCH.open("w", encoding="utf-8") as fh:
    for rec in sorted(audit_records, key=lambda x: x["knowledge_unit_id"]):
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
print(f"overlaid audit batch written: {len(audit_records)} records -> {OUT_BATCH}")

# 5. re-run the full-corpus audit (same args shape as s28)
proc = subprocess.run(
    ["vu", "audit-output",
     "--source-root", "source-vaults/AI ",
     "--output-root", "output/Unified-Vault",
     "--ku-batch", str(OUT_BATCH.relative_to(REPO)),
     "--report", REPORT],
    capture_output=True, text=True, cwd=REPO,
)
print("audit exit code:", proc.returncode)
if proc.returncode != 0:
    print(proc.stderr[-3000:])
    sys.exit(1)

# 6. compare against the committed s28 report
new = json.load(open(REPO / REPORT))["result"]
old = json.load(open(REPO / "reports/synthesis/s28-final-full-corpus-audit.json"))["result"]

def summarize(r):
    s = r["stats"]
    return {
        "valid": r["valid"],
        "kus_total": s["kus_total"],
        "output_files_total": s["output_files_total"],
        "findings_total": s["findings_total"],
        "findings_by_severity": s["findings_by_severity"],
        "markers": {k: s["markers"][k] for k in
                    ("terms", "math", "code", "missing_terms", "missing_math", "missing_code")},
    }

ns, os_ = summarize(new), summarize(old)
print("\nNEW (s29 re-run):", json.dumps(ns, indent=1))
print("OLD (s28 committed):", json.dumps(os_, indent=1))
if ns == os_:
    print("\nMATCH: s29 independent re-run reproduces the s28 full-corpus audit exactly.")
else:
    print("\nMISMATCH — investigate before proceeding")
    sys.exit(2)
