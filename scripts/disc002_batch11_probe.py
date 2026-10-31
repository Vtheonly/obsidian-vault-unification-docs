#!/usr/bin/env python3
"""DISC-002 session 11 (batch 11) semantic-review coverage probe.

Same purpose and FENCE-AWARE design as scripts/disc002_batch10_probe.py:
for each candidate term, search BOTH source vaults for definitional
treatments (real headings containing the term — authoritative mdextract
state machine, so in-fence '#' comments cannot masquerade as headings —
or definition-sentence patterns near it; in-fence def hits are excluded
from def_hits and reported separately).

Repo-relative paths. Batch-11 tranche: 60 highest-signal unreviewed
provisional candidates (post-batch10 state, session-11 eleven-round
replay). Term families mirror the tranche candidates; hyphenation and
spelling variants are included per the session-10 'unembedding/un-embedding'
lesson (search variants before claiming absence).
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

# Concept terms from the batch-11 tranche (excluding pure prose fragments,
# gerunds, adverbs, generic English words, vault-management labels and
# numeric ranges, which are rejected on quote evidence without a probe).
TERMS = [
    # --- ddpm family (gap-shaped candidate: cross-vault, homonym) ---
    "ddpm", "improved ddpm", "denoising diffusion probabilistic",
    "diffusion model", "diffusion models", "ho et al",
    # --- rejection sampling family (gap-shaped: DeepSeek-R1 + Medusa/EAGLE) ---
    "rejection sampling", "rejection-sampling", "rejection",
    "speculative sampling", "accept the",
    # --- watermark family (dataset-bias context) ---
    "watermark", "watermarks", "watermarking", "shortcut learning",
    "dataset bias", "spurious correlation",
    # --- closed-source models family ---
    "closed-source", "closed source", "open-source", "open-weight",
    "frontier model", "frontier models",
    # --- lr schedules family ---
    "lr schedule", "lr schedules", "learning rate schedule",
    "learning rate schedules", "warmup", "cosine decay", "cosine schedule",
    # --- vidore family ---
    "vidore", "visual document retrieval",
    # --- periodic noise family ---
    "periodic noise", "notch filter", "notch filters",
    "interference pattern",
    # --- break symmetry family ---
    "symmetry breaking", "break symmetry", "symmetry",
    "identical weights",
    # --- hyperbolic tangent family ---
    "tanh", "hyperbolic tangent", "zero-centered",
    # --- io-aware family ---
    "io-aware", "io aware", "sram", "hbm",
    # --- objective function family ---
    "objective function", "cost function", "loss function",
    # --- learning curve family ---
    "learning curve", "learning curves", "error curve", "error surface",
    "loss landscape",
    # --- top-k experts family ---
    "top-k", "top-k experts", "mixture of experts", "moe", "router",
    "gating function", "load balancing", "load-balancing",
    # --- frozen parameters family ---
    "freeze", "freezing", "frozen", "frozen layers", "requires_grad",
    # --- fully-connected family ---
    "fully connected layer", "fully-connected", "fully connected",
    "flattening", "fc layer",
    # --- contextual embeddings family ---
    "contextual embedding", "contextual embeddings", "elmo",
    # --- resnet50 family ---
    "resnet50", "resnet-50", "resnet 50", "bottleneck block",
    # --- vgg16-bn family ---
    "vgg16-bn", "vgg16_bn", "batch normalization", "batch norm",
    # --- stride family ---
    "stride", "stride-1", "strided", "downsampling",
    # --- spatial features family ---
    "spatial feature", "spatial features", "hierarchical feature",
    "feature extraction",
    # --- independence family (homonym probe: 9 clusters) ---
    "independence", "linear independence", "i.i.d", "iid",
    "naive bayes", "batch independence",
    # --- single-vector family ---
    "single-vector", "single vector", "late interaction", "multi-vector",
    # --- json schemas family ---
    "json schema", "json schemas", "constrained decoding", "grammar",
    # --- crawl family (homonym probe: 6 clusters) ---
    "common crawl", "web crawl", "crawling", "crawl",
    # --- rare terms family ---
    "rare terms", "rare term", "inverse document frequency", "idf",
    # --- eval-mode family (disables dropout / set model) ---
    "evaluation mode", "model.eval", "model.train", "inference mode",
    "train mode",
    # --- decoding step family ---
    "decoding step", "teacher forcing", "autoregressive decoding",
    # --- gradient product / computed gradients family ---
    "gradient product", "vanishing gradient", "exploding gradient",
    # --- ddpm/u-net context check ---
    "u-net", "unet", "noise schedule", "noise prediction",
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
            # AUTHORITATIVE fence-aware structure:
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
    out_path = Path("/home/z/my-project/scratch/disc002-batch11-probe.json")
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
