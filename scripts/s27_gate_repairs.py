#!/usr/bin/env python3
"""S27/SYNTH-001: anchored gate repair for the areas 15-19 gate run.

Finding (s21-area16/17/18/19 assess-all, gate chain): ONE vault note measured
below band — '18 - Projects/Capstones/Build a Knowledge-Graph Construction
Pipeline.md' (type tutorial), examples dimension 0.4 vs floor 0.5 (score = 0.4
for labeled code blocks only; no example-discourse marker present).

Root cause (measured): the SOURCE (master-ai '27 - Projects/Capstones/
21 - Build a Knowledge-Graph Construction Pipeline.md') itself carries 0
example-discourse markers and 8 labeled fences — the note reproduces the
source's discourse profile exactly. The s24 area-03 precedent applies (repair,
not waiver): the dimension measures discourse style, not content, and the
source's concrete material supports grounded example discourse.

Repair: the entity-extraction intro sentence currently says the prompt "lists
the common relation types to look for". The source's extraction prompt carries
those types verbatim (WORKS_FOR, FOUNDED_BY, LOCATED_IN, ... — twelve, source
lines 96-97). The repair names three of them with a "for instance" marker,
referencing only source-verbatim tokens; nothing is invented.

Probe-based idempotency: probes the defective sentence, replaces once, asserts
the post-condition; a second run is a complete no-op.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO / "output" / "Unified-Vault"

REPAIR = {
    "id": "S27-GATE-R1",
    "file": "18 - Projects/Capstones/Build a Knowledge-Graph Construction Pipeline.md",
    "finding": "examples dimension 0.4 < tutorial floor 0.5 (0 example-discourse markers; 8 labeled code fences)",
    "source_ku_note": (
        "master-ai '27 - Projects/Capstones/21 - Build a Knowledge-Graph Construction "
        "Pipeline.md' extraction prompt (WORKS_FOR, FOUNDED_BY, LOCATED_IN, ... verbatim)"
    ),
    "probe": (
        "lists the common relation types to look for, and instructs the model to be "
        "conservative"
    ),
    "replacement": (
        "lists the common relation types to look for — WORKS_FOR, FOUNDED_BY, and "
        "LOCATED_IN, for instance — and instructs the model to be conservative"
    ),
    "note": "s24 gate-repair precedent: grounded discourse marker naming source-verbatim relation types",
}


def main() -> int:
    path = VAULT / REPAIR["file"]
    if not path.is_file():
        print(f"FAILED: missing file {REPAIR['file']}")
        return 1
    text = path.read_text(encoding="utf-8")
    probe, repl = REPAIR["probe"], REPAIR["replacement"]
    n = text.count(probe)
    if n == 0:
        if repl in text:
            print(f"OK (already repaired): {REPAIR['id']} {REPAIR['file']}")
            return 0
        print(f"FAILED: probe not found and repair not present: {REPAIR['id']}")
        return 1
    if n != 1:
        print(f"FAILED: probe found {n} times (expected 1), refusing: {REPAIR['id']}")
        return 1
    new_text = text.replace(probe, repl, 1)
    path.write_text(new_text, encoding="utf-8")
    post = path.read_text(encoding="utf-8")
    assert probe not in post, f"{REPAIR['id']}: probe still present after repair"
    assert post.count(repl) == 1, f"{REPAIR['id']}: repaired form missing"
    # the named types must be the source-verbatim tokens
    for t in ("WORKS_FOR", "FOUNDED_BY", "LOCATED_IN"):
        assert t in post, f"{REPAIR['id']}: {t} missing from repaired note"
    print(f"APPLIED: {REPAIR['id']} {REPAIR['file']}")
    print(f"  {REPAIR['finding']}")
    print(f"  {REPAIR['note']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
