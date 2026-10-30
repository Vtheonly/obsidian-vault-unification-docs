#!/usr/bin/env python3
"""DISC-002 session 5 (batch 5) semantic-review coverage probe.

Same pattern as scripts/disc002_batch4_probe.py: for each candidate term,
search BOTH source vaults for definitional treatments (headings containing
the term, or definition-sentence patterns near it). Output is the
reviewer's coverage evidence for cover/confirm_gap/reject decisions.

Repo-relative paths. Batch-5 tranche: 60 highest-signal unreviewed
provisional candidates (post-batch4 state).
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

# Concept terms from the batch-5 tranche (excluding pure prose fragments,
# code identifiers, and generic English words which are rejected on quote
# evidence without a probe).
TERMS = [
    # batchnorm / normalization family
    "batchnorm normalizes", "batch normalization",
    # augmentation / preprocessing family
    "center crop", "centercrop", "random crop",
    "training transforms", "validation transforms",
    "image patches", "patch representations", "patch embedding",
    # statistics family
    "central limit", "central limit theorem",
    # activation / architecture family
    "common activation", "relu zeros", "spars",
    "randomly drops", "dropout",
    # training / optimization family
    "different initializations", "larger batch size",
    "flat minima", "flat minimum", "sharp minima",
    "jointly learning", "jointly trained",
    "model state", "training mode", "eval mode",
    "omit bias", "redundant bias", "bias term",
    # sequence / VAE family
    "encoder hidden state", "vae decoder", "generative model",
    # evaluation family
    "imbalanced classes", "class imbalance",
    # citations
    "sutskever", "selvaraju", "grad-cam", "medusa",
    # generic-but-checkable (high-context group)
    "deterministic", "downstream", "input image", "tensor dimension",
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
    out_path = Path("/home/z/my-project/scratch/disc002-batch5-probe.json")
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
