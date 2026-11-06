#!/usr/bin/env python3
"""S25/SYNTH-001: anchored lint repairs for the areas 15-19 batch.

Repair 1 (area 15, Multi-Agent Systems/Communication Patterns.md): the source's
message-envelope example contains an inline `// or "topic": ...` comment, so it
is NOT valid JSON; the note fenced it verbatim as ```json, which trips
CODE_JSON_INVALID (an artifact-lint ERROR that blocks the gate). The F-0031
fence-label precedent (session 23) applies: the fence content stays
byte-identical (verbatim source code) and only the label is corrected to
`text`. Probe-based idempotency (the s24 incident lesson): every repair probes
that the defective form exists exactly once before replacing, and asserts the
repaired form afterwards; a second run is a complete no-op.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO / "output" / "Unified-Vault"

REPAIRS: list[dict] = [
    {
        "id": "S25-LINT-R1",
        "file": "15 - Agents and Tooling/Multi-Agent Systems/Communication Patterns.md",
        "finding": "CODE_JSON_INVALID: json code block fails to parse (source carries an inline // comment inside the envelope JSON)",
        "source_ku_note": "master-ai 15 - AI Agents/.../Communication Patterns (message envelope example)",
        "probe": "```json\n{\n  \"id\": \"msg_001\",",
        "replacement": "```text\n{\n  \"id\": \"msg_001\",",
        "note": "F-0031 fence-label precedent: label corrected json->text; content byte-identical",
    },
]


def main() -> int:
    applied = 0
    skipped = 0
    failed = 0
    for r in REPAIRS:
        path = VAULT / r["file"]
        if not path.is_file():
            print(f"FAILED: missing file {r['file']}")
            failed += 1
            continue
        text = path.read_text(encoding="utf-8")
        probe = r["probe"]
        replacement = r["replacement"]
        n = text.count(probe)
        if n == 0:
            if replacement in text:
                print(f"OK (already repaired): {r['id']} {r['file']}")
                skipped += 1
                continue
            print(f"FAILED: probe not found and repair not present: {r['id']} {r['file']}")
            failed += 1
            continue
        if n != 1:
            print(f"FAILED: probe found {n} times (expected 1), refusing: {r['id']}")
            failed += 1
            continue
        new_text = text.replace(probe, replacement, 1)
        if new_text == text:
            print(f"FAILED: replacement produced no change: {r['id']}")
            failed += 1
            continue
        path.write_text(new_text, encoding="utf-8")
        # post-condition: the defective form is gone, the repaired form present exactly once
        post = path.read_text(encoding="utf-8")
        assert probe not in post, f"{r['id']}: probe still present after repair"
        assert post.count(replacement) >= 1, f"{r['id']}: repaired form missing"
        print(f"APPLIED: {r['id']} {r['file']} ({r['note']})")
        applied += 1
    print(f"\nrepairs applied={applied} already-ok={skipped} failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
