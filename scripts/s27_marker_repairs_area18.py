#!/usr/bin/env python3
"""S27/SYNTH-001: anchored marker repairs for area 18 (Projects).

Root-caused from reports/synthesis/s25-area18-audit.json (1 finding after the
F-0033/F-0034 framework fixes resolved the two Build-an-MCP-Server extraction
artifacts): the architecture mermaid's bidirectional arrow. The note rendered
the source's `<|-->` (JSON-RPC over stdio, bidirectional) as `<-->`; the
source-verbatim form passes the mermaid grammar check (verified on a fixture).
Restored verbatim (s24 mermaid precedent). Probe-idempotent.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO / "output" / "Unified-Vault"

MCP = "18 - Projects/Capstones/Build an MCP Server.md"

REPAIRS: list[dict] = [
    dict(id="A18-R01", file=MCP,
         why="AF-001 code (src 27 - Projects/Capstones/08 - Build an MCP Server.md L37-45: <|--> is the source's arrow)",
         bad="  Client[MCP Client<br/>Claude Desktop] <-->|JSON-RPC over stdio| Server[Your MCP Server]",
         good="  Client[MCP Client<br/>Claude Desktop] <|-->|JSON-RPC over stdio| Server[Your MCP Server]"),
]


def main() -> int:
    applied = skipped = failed = 0
    for r in REPAIRS:
        path = VAULT / r["file"]
        if not path.is_file():
            print(f"FAILED: missing file {r['file']}"); failed += 1; continue
        text = path.read_text(encoding="utf-8")
        bad, good = r["bad"], r["good"]
        n = text.count(bad)
        if n == 0:
            if good in text:
                print(f"OK (already repaired): {r['id']}"); skipped += 1; continue
            print(f"FAILED: probe not found: {r['id']}"); failed += 1; continue
        if n != 1:
            print(f"FAILED: probe found {n} times (expected 1), refusing: {r['id']}"); failed += 1; continue
        path.write_text(text.replace(bad, good, 1), encoding="utf-8")
        post = path.read_text(encoding="utf-8")
        assert bad not in post and post.count(good) == 1
        print(f"APPLIED: {r['id']} {r['file'].split('/')[-1]} — {r['why'][:70]}")
        applied += 1
    print(f"\nsummary: applied={applied} skipped={skipped} failed={failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
