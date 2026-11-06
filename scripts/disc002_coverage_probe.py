#!/usr/bin/env python3
"""DISC-002 semantic-review coverage probe.

For each judgment-call concept term, search BOTH source vaults for
definitional treatments (headings containing the term, or definition-sentence
patterns near it). This is the reviewer's coverage evidence for
cover/confirm_gap/defer decisions: a concept with a dedicated source
treatment is `already_covered` for discovery purposes (synthesis will carry
it into the unified vault); a concept used only in passing with no
treatment anywhere is a genuine gap candidate.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, "src")
from vault_unification.search import boundary_pattern  # noqa: E402

VAULTS = {
    "master-ai": Path("source-vaults/AI /Master AI"),
    "ai-course": Path("source-vaults/AI /AI Course"),
}

TERMS = [
    "bradley-terry", "bradley terry",
    "decoupled weight decay", "adamw",
    "second moment",
    "hessian eigenvalues", "hessian",
    "log-softmax", "log softmax",
    "residual connection", "skip connection",
    "irreducible error",
    "reference policy",
    "information theory",
    "relu",
    "true convolution",
    "spatial position",
    "upstream gradient",
    "jacobian",
    "importance weight", "importance sampling",
    "l2 norm",
    "element-wise multiplication", "hadamard",
    "curvature",
    "human preferences",
    "imagenet",
    "majority class",
    "class imbalance",
    "3d tensor", "tensor shape",
    "encoder hidden states",
    "initialization",
    "detached", "detach",
    "false negatives",
    "precision and recall",
    "validation",
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
                        snippet = " ".join(window.split())[:220]
                        def_hits.append(f"{rel}:{first_line} :: {snippet}")
                        break
    return {
        "term": term,
        "files_with_term": total,
        "heading_hits": heading_hits[:6],
        "def_hits": def_hits[:6],
    }


def main() -> int:
    for term in TERMS:
        r = probe(term)
        print(f"== {r['term']!r}: files={r['files_with_term']}")
        for h in r["heading_hits"]:
            print(f"   HEADING {h}")
        for d in r["def_hits"]:
            print(f"   DEF    {d}")
        if not r["heading_hits"] and not r["def_hits"]:
            print("   (no heading or definitional treatment found)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
