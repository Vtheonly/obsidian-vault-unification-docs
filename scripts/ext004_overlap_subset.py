"""EXT-004: derive the master-ai tree-based sub-batch for overlap discovery.

Filters batch 002 (state/knowledge-units/002-ext002-master-ai-supervised-
learning.jsonl, 65 KUs) down to the KUs whose source file is
'03 - Machine Learning/Supervised Learning/03 - Decision Trees and
Gradient Boosting.md' (30 KUs — the master-ai side of the EXT-004 tree
domain), writing them BYTE-EXACT (line-for-line, original order) to
reports/extraction/ext004-master-ai-tree-subset.jsonl.

This is a derived intermediate (regenerable deterministically from the
committed canonical batch 002); canonical stores are never edited
(ADR-0007 append-only). The subset exists because CAP-013's
overlap-candidates CLI takes batch files, and the EXT-004 task record
scopes discovery to "batch 003 + the tree-based KUs of batch 002".

Exits non-zero unless exactly 30 records are selected. Read-only with
respect to source vaults.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BATCH_002 = REPO_ROOT / "state" / "knowledge-units" / "002-ext002-master-ai-supervised-learning.jsonl"
OUT = REPO_ROOT / "reports" / "extraction" / "ext004-master-ai-tree-subset.jsonl"
MASTER_TREE_RELPATH = "03 - Machine Learning/Supervised Learning/03 - Decision Trees and Gradient Boosting.md"
EXPECTED_COUNT = 30


def main() -> int:
    lines = [ln for ln in BATCH_002.read_text(encoding="utf-8").splitlines() if ln.strip()]
    selected: list[str] = []
    for ln in lines:
        record = json.loads(ln)
        if record["source_path"] == MASTER_TREE_RELPATH:
            selected.append(ln)
    if len(selected) != EXPECTED_COUNT:
        print(f"error: expected {EXPECTED_COUNT} master-ai tree KUs, got {len(selected)}", file=sys.stderr)
        return 1
    OUT.write_text("\n".join(selected) + "\n", encoding="utf-8")
    # byte-exactness check: every selected line must appear verbatim in batch 002
    batch_text = BATCH_002.read_text(encoding="utf-8")
    if not all(ln in batch_text.splitlines() for ln in selected):
        print("error: subset lines are not byte-exact slices of batch 002", file=sys.stderr)
        return 1
    print(json.dumps({
        "ok": True,
        "source_batch": str(BATCH_002.relative_to(REPO_ROOT)),
        "filter": f"source_path == {MASTER_TREE_RELPATH!r}",
        "records_selected": len(selected),
        "out": str(OUT.relative_to(REPO_ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
