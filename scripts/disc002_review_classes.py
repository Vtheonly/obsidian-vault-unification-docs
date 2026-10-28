#!/usr/bin/env python3
"""DISC-002: mechanical artifact-class classification of provisional candidates.

Deterministic, evidence-based classes for BULK review actions. Classes are
conservative by design — only classes whose membership is mechanically
verifiable are emitted as reject decisions; everything else stays
provisional for semantic review tranches.

Classes:
- R-NUM  numeric-dominant term: at least one numeric token AND every token
         numeric or a unit-like word (channels/tokens/layers/...). A bare
         dimension, count, or size is not a knowledge concept; the source
         KUs are unaffected (disposition assignment is independent).
- R-CODE code identifier: EVERY evidence KU is a code_block unit AND the
         term carries a code marker (import/def/dotted/call syntax) or the
         whole evidence corpus is code. Concepts explained in prose are
         never caught (a prose KU in evidence disqualifies the class).

Output: decisions JSONL (reject with class rationale), class assignment
summary, and a verification sample file for review.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))

from vault_unification.overlap import load_ku_batches  # noqa: E402

CAND = REPO / "state/concept-candidates/002-disc002-full-corpus.jsonl"
DECISIONS = REPO / "state/concept-candidates/002a-disc002-decisions-r1.jsonl"
SAMPLES = REPO / "reports/discovery/disc002-class-samples.json"
SUMMARY = REPO / "reports/discovery/disc002-class-summary.json"
DECIDED_UTC = "2026-10-28T00:45:00Z"
REVIEWER = "orchestrator-glm (class-based, sample-verified)"

_NUM_TOKEN = re.compile(r"^[0-9]+([.,][0-9]+)*[kmb]?$|^[0-9]+x[0-9]+$|^[0-9]+d$")
_UNIT_LIKE = frozenset(
    """channels tokens layers units classes neurons features parameters params
    gb mb kb tb epochs steps dimensions images samples heads blocks filters
    batches values examples rows columns words documents frames pixels
    vector size batch dim dims node nodes item items element elements
    bit bits byte bytes hz ms ns fps tps qps gpu cpu ram""".split()
)
_CODE_MARKER = re.compile(
    r"\bimport\b|\bdef \w|\breturn \w|\bprint\(|\braise \w|\bassert \w|"
    r"^\w+\.\w+|\w\(\)|::|__\w+__|^\w+\(\)$|\w_\w"
)


def main() -> None:
    # ku_id -> unit_type index from all batches
    batches = [str(p) for p in sorted((REPO / "state/knowledge-units").glob("*.jsonl"))]
    schema = str(REPO / "schemas" / "knowledge-unit.schema.json")
    unit_type_by_ku = {}
    for rec in load_ku_batches(batches, schema):
        unit_type_by_ku[rec["knowledge_unit_id"]] = rec["unit_type"]

    records = []
    with open(CAND, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                records.append(json.loads(line))
    prov = [r for r in records if r["status"] == "provisional_candidate"]

    decisions = []
    classes: dict[str, list[dict]] = defaultdict(list)
    unclassified = 0

    for r in prov:
        term = r["term"]
        toks = term.split()
        ev_kus = [e["ku_id"] for e in r["evidence"]]
        ev_types = [unit_type_by_ku.get(k, "?") for k in ev_kus]

        # R-NUM: numeric-dominant
        if any(_NUM_TOKEN.match(t) for t in toks) and all(
            _NUM_TOKEN.match(t) or t in _UNIT_LIKE for t in toks
        ):
            classes["R-NUM"].append(r)
            decisions.append(
                {
                    "candidate_id": r["candidate_id"],
                    "decision_id": f"D002-RNUM-{r['candidate_id']}",
                    "action": "reject",
                    "rationale": (
                        f"mechanical artifact class R-NUM: term {term!r} is a bare "
                        "numeric size/count/dimension (every token numeric or "
                        "unit-like), not a knowledge concept; the underlying KUs "
                        "remain dispositioned independently at synthesis"
                    ),
                    "reviewer": REVIEWER,
                }
            )
            continue

        # R-CODE: code identifier, all evidence in code blocks AND an
        # explicit code marker (keyword/dotted/call/dunder/snake_case);
        # prose phrases that merely occur inside code contexts (comments,
        # docstrings) carry no marker and stay provisional for review
        if (
            ev_types
            and all(t == "code_block" for t in ev_types)
            and _CODE_MARKER.search(term)
            and not any(_NUM_TOKEN.match(t) for t in toks)
        ):
            classes["R-CODE"].append(r)
            decisions.append(
                {
                    "candidate_id": r["candidate_id"],
                    "decision_id": f"D002-RCODE-{r['candidate_id']}",
                    "action": "reject",
                    "rationale": (
                        f"mechanical artifact class R-CODE: term {term!r} is a code "
                        f"identifier mined from code blocks ({len(ev_types)}/{len(ev_types)} "
                        "evidence KUs are code_block units); library symbols are "
                        "synthesis content, not standalone knowledge-concept gaps"
                    ),
                    "reviewer": REVIEWER,
                }
            )
            continue

        unclassified += 1

    # verification samples: 40 per class, stratified by context count
    def sample(rows: list[dict], n: int = 40) -> list[dict]:
        rows_sorted = sorted(rows, key=lambda r: (-r["independent_contexts"], r["term"]))
        step = max(len(rows_sorted) // n, 1)
        picked = rows_sorted[::step][:n]
        return [
            {
                "candidate_id": r["candidate_id"],
                "term": r["term"],
                "contexts": r["independent_contexts"],
                "sample_quotes": [e["quote"][:110] for e in r["evidence"][:2]],
            }
            for r in picked
        ]

    sample_doc = {
        "purpose": "stratified verification samples for the two mechanical classes; reviewer + independent subagent must confirm class assignment before decisions are applied",
        "decided_utc": DECIDED_UTC,
        "R-NUM": sample(classes["R-NUM"]),
        "R-CODE": sample(classes["R-CODE"]),
    }
    SAMPLES.write_text(json.dumps(sample_doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    with open(DECISIONS, "w", encoding="utf-8") as fh:
        for d in decisions:
            fh.write(json.dumps(d, sort_keys=True, ensure_ascii=False) + "\n")

    summary = {
        "provisional_total": len(prov),
        "R-NUM": len(classes["R-NUM"]),
        "R-CODE": len(classes["R-CODE"]),
        "unclassified_remain_provisional": unclassified,
        "decisions_emitted": len(decisions),
        "decisions_path": str(DECISIONS.relative_to(REPO)),
        "decided_utc": DECIDED_UTC,
        "rule_notes": {
            "R-NUM": "any numeric token + all tokens numeric-or-unit-like",
            "R-CODE": "all evidence KUs are code_block AND explicit code marker (import/def/return/raise/assert keywords, dotted paths, calls, dunders, snake_case); prose phrases in code contexts stay provisional; numeric terms excluded (R-NUM takes precedence)",
        },
    }
    SUMMARY.write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
