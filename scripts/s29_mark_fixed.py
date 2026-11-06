#!/usr/bin/env python3
"""Mark F-0035..F-0039 as fixed with verification evidence from the
post-repair battery (lint 0 errors / links 12,002 0 problems / full-corpus
audit valid=true 0 findings 42,156 markers / 752/752 tests / sources
276+333 byte-identical)."""
import json
from pathlib import Path

REPO = Path("/home/z/my-project/repo")
FINDINGS = REPO / "state/findings.jsonl"

records = [json.loads(l) for l in FINDINGS.open(encoding="utf-8") if l.strip()]
verify = {
    "F-0035": "s29_semantic_repairs.py repair 2 applied (idempotent no-op on re-run); check-links 12,002 links 0 problems (both new path-form links resolve); lint 0 errors; full-corpus audit valid=true 0 findings; 752/752 tests; sources 276/276+333/333 immutable",
    "F-0036": "s29_semantic_repairs.py repair 1 applied (idempotent); [[Quantization|quantization]] restored between spec-decoding and DPO-variants; check-links 0 problems; lint 0 errors; full-corpus audit valid=true 0 findings; 752/752 tests",
    "F-0037": "s29_semantic_repairs.py repair 3 applied (idempotent); tripled phrase collapsed to one; lint 0 errors; full-corpus audit valid=true 0 findings; 752/752 tests",
    "F-0038": "s29_semantic_repairs.py repair 4 applied (idempotent); duplicate blocks removed, first block + formula retained verbatim (math markers intact: 14,119 present 0 missing); lint 0 errors; 752/752 tests",
    "F-0039": "s29_semantic_repairs.py repair 5 applied (idempotent); heading merged to '### Large K: underfitting and high bias' (parallel to Small K form), stray line removed; lint 0 errors; 752/752 tests",
}
for r in records:
    if r["finding_id"] in verify:
        assert r["status"] == "open", f"{r['finding_id']} unexpected status {r['status']}"
        r["status"] = "fixed"
        r["verification"] = verify[r["finding_id"]]

with FINDINGS.open("w", encoding="utf-8") as fh:
    for r in records:
        fh.write(json.dumps(r, ensure_ascii=False) + "\n")

from collections import Counter
print("findings status:", dict(Counter(r["status"] for r in records)))
print("total records:", len(records))
