#!/usr/bin/env python3
"""DISC-002 session 10 (batch 10) semantic-review coverage probe.

Same purpose as scripts/disc002_batch9_probe.py: for each candidate term,
search BOTH source vaults for definitional treatments (headings containing
the term, or definition-sentence patterns near it). Output is the
reviewer's coverage evidence for cover/confirm_gap/reject decisions.

FENCE-AWARE (batch-10 improvement over batches 3-9): heading detection now
uses the authoritative mdextract structure state machine instead of a
naive `line.startswith('#')` scan, so Python comments like
`# 1x1 convolution` inside code fences can no longer masquerade as
headings (recurring defect class flagged three sessions in a row; see the
session-9 handoff). Definition-window hits are also tagged with their
in-fence status, and in-fence def hits are excluded from `def_hits`
(kept in `fence_def_hits` for review). Line numbers for real headings come
from the authoritative extraction.

Repo-relative paths. Batch-10 tranche: 60 highest-signal unreviewed
provisional candidates (post-batch9 state, session-10 replay).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "src"))
from vault_unification.mdextract import extract_structure_text  # noqa: E402
from vault_unification.search import boundary_pattern  # noqa: E402

VAULTS = {
    "master-ai": REPO / "source-vaults/AI /Master AI",
    "ai-course": REPO / "source-vaults/AI /AI Course",
}

# Concept terms from the batch-10 tranche (excluding pure prose fragments,
# gerunds, adverbs and generic English words which are rejected on quote
# evidence without a probe).
TERMS = [
    # --- potential GAP candidate (absence probes, highest priority) ---
    "unembedding", "lm_head", "output projection", "output embedding",
    "unembed",
    # --- dpo 2023 family ---
    "dpo", "direct preference optimization",
    # --- final classification family ---
    "classification head", "classifier head",
    # --- fpr family ---
    "false positive rate", "fpr",
    # --- hybrid models family (Mamba-Transformer hybrids) ---
    "hybrid", "hybrid architecture", "mamba",
    # --- imagenet normalization family ---
    "imagenet normalization", "normalization constants",
    # --- long-running agents family ---
    "autonomous agent", "long-running agent",
    # --- pure vector search family ---
    "vector search", "hybrid search", "bm25",
    # --- running mean family ---
    "running mean", "running variance", "running statistics",
    # --- unlabeled family ---
    "unlabeled", "labeled data",
    # --- 20 tokens per family ---
    "tokens per parameter", "compute-optimal",
    # --- adaptiveavgpool2d family ---
    "adaptiveavgpool2d", "adaptive average pooling", "global average pooling",
    # --- base models / chat models family ---
    "base model", "base models", "chat model", "chat models",
    "instruction-tuned", "instruction tuning",
    # --- channel dimensions family ---
    "channel", "channels", "color channels", "input channels",
    # --- cpu' artifact family (dedicated-section check) ---
    "cpu", "device",
    # --- final convolutional family ---
    "final convolutional layer", "last convolutional",
    # --- non-verifiable family ---
    "verifiable rewards", "rlvr", "non-verifiable",
    # --- paligemma family (dedicated-note check) ---
    "paligemma",
    # --- spatial feature family ---
    "spatial feature", "spatial features",
    # --- 56-layer / higher training error family ---
    "degradation problem", "degradation", "underfitting",
    # --- best validation family ---
    "early stopping", "best validation loss", "checkpoint",
    # --- conv3 family ---
    "bottleneck", "conv3",
    # --- mini moe family (dedicated-note check) ---
    "mini moe", "mixture of experts",
    # --- one bias family ---
    "bias per filter", "one bias",
    # --- snell family ---
    "snell", "test-time compute",
    # --- triangle family ---
    "triangle inequality",
    # --- 0-1 family ---
    "0-1 loss", "zero-one loss",
    # --- alignment method family ---
    "alignment method", "alignment",
    # --- 3e-4 artifact family (dedicated-section check) ---
    "3e-4", "learning rate",
]


DEF_PAT = re.compile(
    r"(?:is|are)\s+(?:a|an|the)\b|is\s+defined\s+as|refers\s+to|means\b|"
    r"denotes\b|definition\s+of|we\s+define",
    re.IGNORECASE,
)


def fence_spans(struct: dict) -> list[tuple[int, int]]:
    """Return (start_line, end_line) spans of code fences (1-based, inclusive)."""
    out = []
    for f in struct.get("code_fences", []):
        start = f.get("start_line", 0)
        end = f.get("end_line", start)
        # end_line is the closing fence line when closed; when unclosed the
        # span extends to EOF (mdextract reports end_line as the last line).
        out.append((start, end))
    return out


def in_any_span(line: int, spans: list[tuple[int, int]]) -> bool:
    return any(s <= line <= e for s, e in spans)


def probe(term: str) -> dict:
    pat = boundary_pattern(term)
    heading_hits: list[str] = []
    def_hits: list[str] = []
    fence_def_hits: list[str] = []
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
            # AUTHORITATIVE fence-aware structure (batch-10 improvement):
            # real headings only — Python comments inside fences excluded.
            struct = extract_structure_text(text)
            spans = fence_spans(struct)
            matched_heading = False
            for h in struct.get("headings", []):
                if pat.search(h["text"]):
                    heading_hits.append(f"{rel}:{h['line']} :: {h['text'][:100]}")
                    matched_heading = True
                    break  # one heading hit per file is enough for coverage
            if not matched_heading:
                for m in pat.finditer(text):
                    window = text[max(0, m.start() - 120) : m.end() + 160]
                    if DEF_PAT.search(window):
                        first_line = text[: m.start()].count("\n") + 1
                        snippet = " ".join(window.split())[:200]
                        if in_any_span(first_line, spans):
                            fence_def_hits.append(
                                f"{rel}:{first_line} :: (IN FENCE) {snippet}"
                            )
                        else:
                            def_hits.append(f"{rel}:{first_line} :: {snippet}")
                        break
    return {
        "term": term,
        "files_with_term": total,
        "heading_hits": heading_hits[:8],
        "def_hits": def_hits[:8],
        "fence_def_hits_excluded": fence_def_hits[:4],
    }


def main() -> int:
    out_path = Path("/home/z/my-project/scratch/disc002-batch10-probe.json")
    results = []
    for term in TERMS:
        r = probe(term)
        results.append(r)
        print(f"== {r['term']!r}: files={r['files_with_term']}")
        for h in r["heading_hits"][:4]:
            print(f"   HEADING {h}")
        for d in r["def_hits"][:3]:
            print(f"   DEF    {d}")
        if r["fence_def_hits_excluded"]:
            print(f"   ({len(r['fence_def_hits_excluded'])} in-fence def hits excluded)")
        if not r["heading_hits"] and not r["def_hits"]:
            print("   (no heading or definitional treatment found)")
    out_path.write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")
    print(f"\nprobe results saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
