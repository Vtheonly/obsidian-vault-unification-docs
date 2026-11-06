#!/usr/bin/env python3
"""s29 startup verification: rebuild the knowledge registry from committed
batches + dispositions ledger, then validate — replicating the s28 sequence
(reports/synthesis/s28-kureg-*.json) to independently confirm the
accounting claims (applied 27,536 / Unaccounted 0 / needs_review 0)."""
import json
import subprocess
import sys
from pathlib import Path

REPO = Path("/home/z/my-project/repo")
DB = "state/registries/kuregistry.db"


def run(args):
    proc = subprocess.run(
        ["vu", *args], capture_output=True, text=True, cwd=REPO
    )
    if proc.returncode != 0:
        print("FAILED:", " ".join(args))
        print(proc.stdout[-2000:])
        print(proc.stderr[-2000:])
        sys.exit(1)
    return proc


# 1. init (force: fresh rebuild)
run(["kureg-init", "--db", DB, "--force", "--report", "/tmp/vk29-init.json"])

# 2. load all committed KU batches (sorted for determinism)
batches = sorted((REPO / "state/knowledge-units").glob("*.jsonl"))
print(f"batches found: {len(batches)}")
total_loaded = 0
for b in batches:
    run(["kureg-load", "--db", DB, "--kus", str(b.relative_to(REPO)),
         "--report", "/tmp/vk29-load.json"])
    d = json.load(open("/tmp/vk29-load.json"))
    r = d.get("result", d)
    total_loaded += int(r.get("records_inserted", r.get("inserted", 0)) or 0)
print(f"total records inserted: {total_loaded}")

# 3. apply dispositions ledger
run(["kureg-apply-dispositions", "--db", DB,
     "--dispositions", "state/dispositions/001-disp001-rule-driven.jsonl",
     "--report", "/tmp/vk29-apply.json"])
apply_r = json.load(open("/tmp/vk29-apply.json")).get("result", {})
print("apply:", {k: apply_r.get(k) for k in
                 ("records_in_file", "applied", "revised", "idempotent_skipped")})

# 4. validate
run(["kureg-validate", "--db", DB, "--report", "/tmp/vk29-validate.json"])
val = json.load(open("/tmp/vk29-validate.json")).get("result", {})
print("validate:", {k: val.get(k) for k in
                    ("valid", "kus_total", "unaccounted_count", "unaccounted_after",
                     "needs_review_count")})
