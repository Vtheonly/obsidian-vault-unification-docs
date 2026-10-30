#!/usr/bin/env python3
"""DISC-002 session 6 (batch 6) semantic-review coverage probe.

Same pattern as scripts/disc002_batch5_probe.py: for each candidate term,
search BOTH source vaults for definitional treatments (headings containing
the term, or definition-sentence patterns near it). Output is the
reviewer's coverage evidence for cover/confirm_gap/reject decisions.

Repo-relative paths. Batch-6 tranche: 60 highest-signal unreviewed
provisional candidates (post-batch5 state).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))
from vault_unification.search import boundary_pattern  # noqa: E402

VAULTS = {
    "master-ai": REPO / "source-vaults/AI /Master AI",
    "ai-course": REPO / "source-vaults/AI /AI Course",
}

# Concept terms from the batch-6 tranche (excluding pure prose fragments,
# code identifiers, and generic English words which are rejected on quote
# evidence without a probe).
TERMS = [
    # random-number / initialization family
    "randn", "standard normal", "normal_(", "random initialization",
    # evaluation family
    "eval set", "evaluation set", "golden", "held-out", "held out",
    "test set", "validation set",
    # tooling family
    "sklearn", "scikit-learn", "scikit",
    # probability family
    "probability distribution", "random variable",
    # linear algebra family
    "diagonal matrix", "diagonal", "square matrix", "square root",
    "sum of diagonal",
    # caching family
    "kv cache", "k/v cache", "cache directory", "weights cached",
    # voting family
    "majority vote", "majority label", "majority class",
    # misc checkable
    "compressed representation", "spatially adjacent",
    "10x faster", "named_parameters",
]

DEF_PAT = re.compile(
    r"(?:is|are)\s+(?:a|an|the)\b|is\s+defined\s+as|refers\s+to|means\b|"
    r"denotes\b|definition\s+of|we\s+define",
    re.IGNORECASE,
)


def probe(term: str) -> dict:
    pat = boundary_pattern(term)
    heading_hits: list[str] = []
    def_hits: list[str] = []
    total = 0
    for vault, root in VAULTS.items():
        for md in sorted(root.rglob("*.md")):
            try:
                text = md.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if not pat.search(text):
                continue
            total += 1
            rel = f"{vault}:{md.relative_to(root)}"
            in_heading = False
            for line in text.splitlines():
                if line.lstrip().startswith("#") and pat.search(line):
                    heading_hits.append(f"{rel} :: {line.strip()[:100]}")
                    in_heading = True
                    break
            if not in_heading:
                for m in pat.finditer(text):
                    window = text[max(0, m.start() - 120) : m.end() + 160]
                    if DEF_PAT.search(window):
                        first_line = text[: m.start()].count("\n") + 1
                        snippet = " ".join(window.split())[:200]
                        def_hits.append(f"{rel}:{first_line} :: {snippet}")
                        break
    return {
        "term": term,
        "files_with_term": total,
        "heading_hits": heading_hits[:8],
        "def_hits": def_hits[:8],
    }


def main() -> int:
    out_path = Path("/home/z/my-project/scratch/disc002-batch6-probe.json")
    results = []
    for term in TERMS:
        r = probe(term)
        results.append(r)
        print(f"== {r['term']!r}: files={r['files_with_term']}")
        for h in r["heading_hits"][:4]:
            print(f"   HEADING {h}")
        for d in r["def_hits"][:3]:
            print(f"   DEF    {d}")
        if not r["heading_hits"] and not r["def_hits"]:
            print("   (no heading or definitional treatment found)")
    out_path.write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")
    print(f"\nprobe results saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
