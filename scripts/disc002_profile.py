#!/usr/bin/env python3
"""DISC-002: profile the optimized discovery pass on a real subset."""
from __future__ import annotations

import cProfile
import io
import pstats
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from vault_unification.discovery import discover_candidates  # noqa: E402

SCHEMA = REPO / "schemas" / "knowledge-unit.schema.json"
BATCH_DIR = REPO / "state" / "knowledge-units"
MANIFESTS = {
    "master-ai": REPO / "state" / "manifests" / "master-ai.jsonl",
    "ai-course": REPO / "state" / "manifests" / "ai-course.jsonl",
}


def main() -> None:
    names = sorted(p.name for p in BATCH_DIR.glob("*.jsonl"))[:7]
    profiler = cProfile.Profile()
    profiler.enable()
    result = discover_candidates(
        [str(BATCH_DIR / n) for n in names], str(SCHEMA), MANIFESTS
    )
    profiler.disable()
    out = io.StringIO()
    stats = pstats.Stats(profiler, stream=out)
    stats.sort_stats("cumulative").print_stats(28)
    print("candidates:", len(result["candidates"]))
    print(out.getvalue())


if __name__ == "__main__":
    main()
