#!/usr/bin/env python3
"""DISC-002: differential verification of _match_relationship_fast.

Part of the F-0015 performance fix evidence. Verifies that the inverted
position-set classifier is equivalent to the per-term regex reference on:

1. EVERY (term, KU) pair mined from a real sample of batches — both
   classifiers run directly on the same normalized text and every mismatch
   is reported with the exact text and term (differential testing).
2. The full discover_candidates() pipeline over the same sample — run once
   with the fast path, once with the reference path monkeypatched in; the
   candidate lists must be byte-identical.

Read-only; writes a JSON report to reports/discovery/.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from vault_unification import discovery as disc  # noqa: E402

SAMPLE = [
    "001-ext001-ai-course-03.1-regression.jsonl",
    "002-ext002-master-ai-supervised-learning.jsonl",
    "003-ext004-ai-course-03.7-tree-based-models.jsonl",
    "012-regen001-ai-course-01-foundations-and-overview.jsonl",
    "026-regen001-ai-course-08-attention-and-transformers.jsonl",
    "040-regen001-master-ai-08-llms.jsonl",
]
BATCH_PATHS = [f"state/knowledge-units/{name}" for name in SAMPLE]
MANIFESTS = {
    "master-ai": "state/manifests/master-ai.jsonl",
    "ai-course": "state/manifests/ai-course.jsonl",
}
KUS_SCHEMA = "schemas/knowledge-unit.schema.json"


def differential_pairs() -> dict:
    """Compare both classifiers on every mined (term, KU) pair."""
    records = disc.load_ku_batches(BATCH_PATHS, KUS_SCHEMA)
    mined: dict[str, dict[str, list[dict]]] = {}
    for rec in records:
        if rec["unit_type"] not in disc._MINEABLE_UNIT_TYPES:
            continue
        grams = set(disc._mine_ngrams(rec["excerpt"]))
        for heading in rec.get("heading_path", []):
            for g in disc._mine_ngrams(heading):
                grams.add(g)
        for g in grams:
            mined.setdefault(disc._term_text(g), {})[
                rec["knowledge_unit_id"]
            ] = [rec]

    pairs = 0
    mismatches: list[dict] = []
    started = time.monotonic()
    norm_cache: dict[str, str] = {}
    for term in mined:
        for ku_id in sorted(mined[term]):
            ku = mined[term][ku_id][0]
            norm = norm_cache.get(ku_id)
            if norm is None:
                norm = disc._normalize(ku["excerpt"])
                norm_cache[ku_id] = norm
            # heading_declared False isolates the text classifier comparison
            ref = disc._match_relationship(term, norm, False)
            fast = disc._match_relationship_fast(term, ku, norm, False)
            pairs += 1
            if ref != fast:
                mismatches.append(
                    {
                        "term": term,
                        "ku_id": ku_id,
                        "reference": ref,
                        "fast": fast,
                        "norm_text_head": norm[:200],
                    }
                )
                if len(mismatches) >= 25:
                    break
        if len(mismatches) >= 25:
            break
    return {
        "batches": SAMPLE,
        "pairs_compared": pairs,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches[:25],
        "seconds": round(time.monotonic() - started, 1),
    }


def pipeline_ab() -> dict:
    """Run discover_candidates with fast vs reference; compare hashes."""
    manifests = dict(MANIFESTS)

    t0 = time.monotonic()
    fast_res = disc.discover_candidates(BATCH_PATHS, KUS_SCHEMA, manifests)
    fast_sec = time.monotonic() - t0

    original_fast = disc._match_relationship_fast

    def reference_via_fast(term, ku, ku_text_norm, heading_declared):
        return disc._match_relationship(term, ku_text_norm, heading_declared)

    disc._match_relationship_fast = reference_via_fast
    try:
        t0 = time.monotonic()
        ref_res = disc.discover_candidates(BATCH_PATHS, KUS_SCHEMA, manifests)
        ref_sec = time.monotonic() - t0
    finally:
        disc._match_relationship_fast = original_fast

    fast_blob = json.dumps(fast_res["candidates"], sort_keys=True).encode()
    ref_blob = json.dumps(ref_res["candidates"], sort_keys=True).encode()
    return {
        "fast_seconds": round(fast_sec, 1),
        "reference_seconds": round(ref_sec, 1),
        "fast_candidates": len(fast_res["candidates"]),
        "reference_candidates": len(ref_res["candidates"]),
        "fast_sha256": hashlib.sha256(fast_blob).hexdigest(),
        "reference_sha256": hashlib.sha256(ref_blob).hexdigest(),
        "byte_identical": fast_blob == ref_blob,
    }


def main() -> int:
    pair_report = differential_pairs()
    print("pair differential:", json.dumps({k: pair_report[k] for k in ("pairs_compared", "mismatch_count", "seconds")}))
    ab = pipeline_ab()
    print("pipeline A/B:", json.dumps(ab))

    report = {
        "task": "DISC-002 F-0015 equivalence evidence",
        "pair_differential": pair_report,
        "pipeline_ab": ab,
        "verdict": (
            "PASS"
            if pair_report["mismatch_count"] == 0 and ab["byte_identical"]
            else "FAIL"
        ),
    }
    out = REPO / "reports" / "discovery" / "disc002-f0015-equivalence.json"
    out.write_text(json.dumps(report, indent=1) + "\n", encoding="utf-8")
    print(f"report -> {out}")
    print("verdict:", report["verdict"])
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
