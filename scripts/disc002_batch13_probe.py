#!/usr/bin/env python3
"""DISC-002 session 13 (batch 13) semantic-review coverage probe.

Same purpose and FENCE-AWARE design as scripts/disc002_batch12_probe.py:
for each candidate term, search BOTH source vaults for definitional
treatments (real headings containing the term — authoritative mdextract
state machine, so in-fence '#' comments cannot masquerade as headings —
or definition-sentence patterns near it; in-fence def hits are excluded
from def_hits and reported separately).

Repo-relative paths. Batch-13 tranche: 60 highest-signal unreviewed
provisional candidates (post-batch12 state, session-13 thirteen-round
replay). Term families mirror the tranche candidates; hyphenation and
spelling variants are included per the session-10/11 lessons; the
session-12 lesson applies: TERM-SEPARATED definitions (quiz matching
blocks, glossary cross-references) defeat term-only search — probe
property-based phrases too, and inspect description lines near term
occurrences before claiming definitional absence.
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

# Concept terms from the batch-13 tranche (excluding pure prose fragments,
# verb phrases, code-comment artifacts, numeric/LaTeX fragments, path
# fragments and example strings, which are rejected on quote evidence
# without a probe).
TERMS = [
    # --- openhermes family (named instruction dataset; gloss watch) ---
    "openhermes", "hermes", "zephyr", "tulu", "ultrachat", "dolly",
    "synthetic dataset", "synthetic data",
    # --- resnet18 family ---
    "resnet-18", "resnet18", "resnet-34", "models.resnet18",
    "residual block", "resnet",
    # --- scalar bias / per-filter bias family ---
    "scalar bias", "bias parameter", "one bias per filter",
    "exactly one", "bias per filter", "learnable scalar",
    # --- single artificial neuron family ---
    "single artificial neuron", "artificial neuron", "formal neuron",
    "perceptron", "weighted sum plus",
    # --- true negatives family (confusion matrix) ---
    "true negative", "true positives", "confusion matrix",
    "cm.ravel", "tn, fp, fn, tp", "specificity",
    # --- def keyword family (Python functions) ---
    "def keyword", "function definition", "def statement",
    "lambda", "docstring",
    # --- super family (Python OOP) ---
    "super()", "super().__init__", "parent class", "inheritance",
    "subclass",
    # --- tree shape family (speculative decoding draft trees) ---
    "tree shape", "tree attention", "draft tree", "tree topology",
    "speculative decoding", "draft model", "verify",
    # --- normalization layers family ---
    "normalization layer", "batch normalization", "layer normalization",
    "batchnorm", "layernorm", "running statistics",
    # --- odot family (Hadamard product) ---
    "hadamard", "element-wise multiplication", "elementwise",
    "odot",
    # --- low frequencies family ---
    "low frequency", "low frequencies", "high frequency",
    "high frequencies", "frequency domain", "smooth, large-scale",
    # --- feed-forward network family ---
    "feed-forward network", "feedforward network", "feed-forward",
    "ffn", "mlp", "position-wise",
    # --- goodfellow family (historical entity) ---
    "goodfellow", "invented gans", "created gans", "2014",
    "generative adversarial",
    # --- high bias family (bias-variance) ---
    "high bias", "bias-variance", "underfitting", "overfitting",
    "variance",
    # --- single attention family ---
    "single attention head", "attention head", "single head",
    "one attention distribution", "multi-head",
    # --- dynamic range family ---
    "dynamic range", "bit depth", "contrast stretching",
    "wider dynamic range",
    # --- latent vector family ---
    "latent vector", "latent space", "latent representation",
    "latent code", "bottleneck vector",
    # --- projection layer family ---
    "projection layer", "linear projection", "project the",
    "projects into", "classifier[6]",
    # --- learning rate schedules family ---
    "learning rate schedule", "learning rate schedules",
    "lr schedule", "rate schedules", "warmup", "cosine decay",
    "step decay", "schedule",
    # --- gradient direction / steepest ascent family ---
    "gradient direction", "steepest ascent", "gradient ascent",
    "points in the direction", "uphill", "sensitivity vector",
    # --- squared gradients family (Adam second moment) ---
    "squared gradients", "second moment", "rmsprop", "v_t",
    "first moment", "adam",
    # --- tensor shape family ---
    "tensor shape", "shape mismatch", "nchw", "nhwc",
    "shape manipulation", "torch.size",
    # --- image features family ---
    "image features", "feature extraction", "learned features",
    "feature map", "hierarchical features",
    # --- still sota family (gap-watch before reject) ---
    "sota", "state of the art", "state-of-the-art",
    # --- runtimeerror family (gap-watch before reject) ---
    "runtimeerror", "exception", "try/except", "error handling",
    "raise", "catch",
    # --- cos/sin family (gap-watch before reject) ---
    "cosine", "sine", "sinusoidal", "trigonometric",
    # --- lfloor/rfloor family (gap-watch before reject) ---
    "floor function", "floor of", "rounds down", "integer part",
    # --- input tokens family (reject-coverage) ---
    "token", "tokenization", "input token",
    # --- reward model family (reject-coverage) ---
    "reward model", "rlhf", "preference model",
    # --- active per family (reject-coverage: MoE) ---
    "mixture of experts", "moe", "active parameters",
    "experts", "fraction of parameters",
    # --- outside function family (reject-coverage: chain rule) ---
    "chain rule", "composite function", "inside function",
    # --- small learning rate family (reject-coverage) ---
    "learning rate", "small learning rate", "range test",
    # --- loss decreases family (reject-coverage) ---
    "training loss", "validation loss", "converge",
    # --- across positions family (reject-coverage) ---
    "parameter sharing", "share parameters", "weight sharing",
    # --- use hybrid family (reject-coverage) ---
    "hybrid", "hybrid architecture", "hybrid attention",
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
    out_path = Path("/home/z/my-project/scratch/disc002-batch13-probe.json")
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
