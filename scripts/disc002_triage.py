#!/usr/bin/env python3
"""DISC-002: deterministic candidate triage for semantic review planning.

Reads the full-corpus candidates file and produces the review-workload
structure: global stats, tier assignments, n-gram-family grouping, and
per-tier term samples. This is REVIEW PREPARATION (deterministic evidence
collection) — it makes no decisions.
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CAND = REPO / "state/concept-candidates/002-disc002-full-corpus.jsonl"
OUT = REPO / "reports/discovery/disc002-triage.json"


def main() -> None:
    records = []
    with open(CAND, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                records.append(json.loads(line))

    prov = [r for r in records if r["status"] == "provisional_candidate"]
    covered = [r for r in records if r["status"] == "already_covered"]

    # ---- global stats ----
    by_kind = Counter(r["kind"] for r in records)
    conf_buckets = Counter(
        "0.8-1.0" if r["confidence"]["score"] >= 0.8
        else "0.6-0.8" if r["confidence"]["score"] >= 0.6
        else "0.4-0.6" if r["confidence"]["score"] >= 0.4
        else "0.0-0.4"
        for r in prov
    )
    ctx_hist = Counter()
    for r in prov:
        c = r["independent_contexts"]
        ctx_hist["1"] += c == 1
        ctx_hist["2"] += c == 2
        ctx_hist["3-5"] += 3 <= c <= 5
        ctx_hist["6-10"] += 6 <= c <= 10
        ctx_hist["11-50"] += 11 <= c <= 50
        ctx_hist["51+"] += c > 50
    cross_vault = sum(1 for r in prov if r["confidence"]["signals"]["cross_vault"])
    homonym = sum(1 for r in prov if r["homonym_suspect"])
    contra = sum(1 for r in records if r["contradiction_suspect"])
    copied = sum(1 for r in prov if r["copied_passage"])

    # ---- n-gram family grouping (containment within provisional terms) ----
    # term A is a sub-gram of term B if A's token tuple is a contiguous
    # token subsequence of B's token tuple. Families group candidates whose
    # terms share the 1-gram "head anchor" (rarest distinctive token) — a
    # deterministic, review-facing grouping only.
    prov_terms = {r["term"]: r for r in prov}
    all_terms = set(r["term"] for r in records)

    def tokens(term: str) -> list[str]:
        return term.split()

    sub_gram_of: dict[str, list[str]] = defaultdict(list)
    by_unigram = defaultdict(list)
    for t in prov_terms:
        toks = tokens(t)
        for tok in toks:
            by_unigram[tok].append(t)

    for t, r in prov_terms.items():
        toks = tokens(t)
        if len(toks) < 2:
            continue
        # sub-grams of t that are themselves provisional candidate terms
        for n in (1, 2):
            for i in range(len(toks) - n + 1):
                sub = " ".join(toks[i : i + n])
                if sub != t and sub in prov_terms:
                    sub_gram_of[t].append(sub)

    fragment_candidates = set()
    for t, subs in sub_gram_of.items():
        # t's evidence ku_ids vs the union of its sub-grams' evidence:
        # if t's evidence is fully contained in a sub-gram's evidence, t is
        # likely a longer-phrase artifact; if a sub-gram's evidence is fully
        # inside t's, the sub-gram may be the fragment — flagged for review
        for sub in subs:
            t_kus = {e["ku_id"] for e in prov_terms[t]["evidence"]}
            s_kus = {e["ku_id"] for e in prov_terms[sub]["evidence"]}
            if s_kus and s_kus <= t_kus and len(s_kus) < len(t_kus):
                fragment_candidates.add(sub)
            elif t_kus and t_kus <= s_kus and len(t_kus) < len(s_kus):
                fragment_candidates.add(t)

    # ---- tiers ----
    t1 = [r for r in prov if r["kind"] == "fragmented_derivation"]
    t2 = [
        r for r in prov
        if r["kind"] == "unexplained_prerequisite"
        and (r["confidence"]["signals"]["cross_vault"] or r["independent_contexts"] >= 3)
    ]
    t3 = [r for r in prov if r["kind"] == "rare_essential"]
    t4 = [r for r in prov if r not in t1 and r not in t2 and r not in t3]

    def sample(rows: list[dict], n: int = 40) -> list[dict]:
        return [
            {
                "candidate_id": r["candidate_id"],
                "term": r["term"],
                "contexts": r["independent_contexts"],
                "cross_vault": r["confidence"]["signals"]["cross_vault"],
                "score": r["confidence"]["score"],
                "fragment_flag": r["term"] in fragment_candidates,
                "destination": r["destination_recommendation"],
            }
            for r in sorted(
                rows, key=lambda x: (-x["confidence"]["score"], -x["independent_contexts"], x["term"])
            )[:n]
        ]

    report = {
        "command": "disc002-triage (deterministic review preparation)",
        "denominators": {
            "records_total": len(records),
            "provisional": len(prov),
            "already_covered": len(covered),
        },
        "provisional_stats": {
            "by_kind": dict(by_kind),
            "confidence_buckets": dict(conf_buckets),
            "independent_contexts_histogram": dict(ctx_hist),
            "cross_vault": cross_vault,
            "homonym_suspect": homonym,
            "copied_passage_flagged": copied,
            "contradiction_suspect_all_statuses": contra,
            "ngram_fragment_flagged": len(fragment_candidates),
        },
        "tiers": {
            "T1_fragmented_derivation": len(t1),
            "T2_unexplained_prereq_broad": len(t2),
            "T3_rare_essential": len(t3),
            "T4_unexplained_prereq_narrow": len(t4),
            "T4_fragment_flagged_share": round(
                sum(1 for r in t4 if r["term"] in fragment_candidates) / max(len(t4), 1), 3
            ),
        },
        "samples": {
            "T1_top40": sample(t1),
            "T2_top40": sample(t2),
            "T3_top40": sample(t3),
            "T4_top40": sample(t4),
        },
        "note": (
            "fragment_flag is a deterministic containment heuristic over evidence "
            "ku-id sets; it groups likely n-gram artifacts for efficient review and "
            "never decides by itself — every candidate still receives a semantic "
            "decision through discovery-decide"
        ),
    }
    OUT.write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("denominators", "provisional_stats", "tiers")}, indent=1))


if __name__ == "__main__":
    main()
