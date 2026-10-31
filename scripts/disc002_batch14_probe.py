#!/usr/bin/env python3
"""DISC-002 session 14 (batch 14) semantic-review coverage probe.

Same purpose and FENCE-AWARE design as scripts/disc002_batch13_probe.py:
for each candidate term, search BOTH source vaults for definitional
treatments (real headings containing the term — authoritative mdextract
state machine, so in-fence '#' comments cannot masquerade as headings —
or definition-sentence patterns near it; in-fence def hits are excluded
from def_hits and reported separately).

Repo-relative paths. Batch-14 tranche: 60 highest-signal unreviewed
provisional candidates (post-batch13 state, session-14 fourteen-round
replay). Term families mirror the tranche candidates; hyphenation and
spelling variants are included per the session-10/11 lessons; the
session-12/13 lessons apply: TERM-SEPARATED definitions (quiz matching
blocks, glossary cross-references) defeat term-only search — probe
property-based phrases too, and inspect description lines near term
occurrences before claiming definitional absence; symbol glosses in
math-notation blocks near the term also count (the 'ŷ is the predicted
label' model at Perceptrons and MLPs.md:63).
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

# Concept terms from the batch-14 tranche (excluding pure prose fragments,
# verb phrases, code-comment artifacts, numeric/LaTeX fragments, path
# fragments and example strings, which are rejected on quote evidence
# without a probe).
TERMS = [
    # --- bounding boxes family (CV detection) ---
    "bounding box", "bounding boxes", "object detection", "iou",
    "detection head", "yolo",
    # --- conditional generation family ---
    "conditional generation", "conditionally", "encoder-decoder",
    "encoder decoder", "seq2seq", "sequence to sequence",
    # --- loss curve family ---
    "loss curve", "loss curves", "training curve", "training curves",
    "learning curve", "learning curves", "convergence plot",
    "seismograph",
    # --- causality family ---
    "causality", "causal", "causation", "correlation and causation",
    "correlation vs", "spurious correlation",
    # --- low-rank approximation family ---
    "low-rank", "low rank", "low-rank approximation", "lora",
    "svd", "singular value", "truncating svd", "rank-k",
    # --- manhattan distance family ---
    "manhattan", "city block", "city-block", "l1 norm", "l_1",
    "chebyshev", "minkowski",
    # --- non-contiguous family (memory layout) ---
    "non-contiguous", "contiguous", "contiguity", "memory layout",
    "stride", "row-major", "column-major",
    # --- parameter update family ---
    "parameter update", "update rule", "weight update",
    "w_{t+1}", "step size",
    # --- input space family (kernel trick) ---
    "input space", "feature space", "kernel trick",
    "higher-dimensional", "higher dimensional",
    # --- lr scheduler family ---
    "lr scheduler", "learning rate schedule", "learning rate schedules",
    "scheduler", "reducelronplateau", "cosine annealing",
    "warmup", "step decay",
    # --- neural network architecture family ---
    "neural network architecture", "architecture and notation",
    "network architecture", "architectures",
    # --- transformer blocks family ---
    "transformer block", "transformer blocks", "encoder block",
    "decoder block", "blocks",
    # --- gradient explosion family ---
    "gradient explosion", "exploding gradient", "exploding gradients",
    "vanishing gradient", "vanishing gradients", "gradient clipping",
    "clip_grad_norm",
    # --- ml engineer family (roles) ---
    "ml engineer", "machine learning engineer", "data scientist",
    "data engineer", "data analyst", "mle",
    # --- scalar loss family ---
    "scalar loss", "scalar loss function", "loss function",
    "scalar value", "single number",
    # --- sora family (gap-watch before reject; OpenHermes precedent) ---
    "sora", "video generation", "dit", "diffusion transformer",
    "runway", "kling",
    # --- different results family (reject-coverage: reproducibility) ---
    "different results", "reproducib", "deterministic", "set_seed",
    "stochastic",
    # --- across runs family (reject-coverage: same as different results) ---
    "across runs", "random seed", "seed",
    # --- correct answers family (reject-coverage: labels/targets) ---
    "correct answers", "ground truth", "ground-truth", "labels",
    "targets", "labeled dataset",
    # --- local structure family (reject-coverage: PCA/t-SNE) ---
    "local structure", "local neighborhood", "local neighborhoods",
    "global variance", "global structure", "t-sne", "umap",
    # --- visual information family (reject-coverage: multi-scale) ---
    "visual information", "multi-scale", "multiple scales",
    "scale", "inception",
    # --- large errors family (reject-coverage: MSE penalty) ---
    "large errors", "squaring", "penalizes large", "outliers",
    "quadratic penalty", "mean squared error",
    # --- image content family (reject-coverage: hallucination) ---
    "image content", "hallucinate", "hallucination",
    "describes objects",
    # --- answer questions family (reject-coverage: QA) ---
    "answer questions", "question answering", "vqa",
    "visual question answering", "chatbot",
    # --- state across family (reject-coverage: RNN hidden state) ---
    "state across", "hidden state", "persistent state",
    "optimizer state", "maintaining a hidden",
    # --- every spatial position family (reject-coverage: weight sharing) ---
    "every spatial position", "spatial position", "parameter sharing",
    "share parameters", "weight sharing", "sliding dot product",
    # --- single hidden family (reject-coverage: hidden layers) ---
    "single hidden", "hidden layer", "hidden layers", "hidden node",
    "hidden units",
    # --- exponential moving family (fragment; EMA concept coverage) ---
    "exponential moving", "exponential moving average", "ema",
    "running average", "running statistics", "momentum",
    # --- small weights family (reject-coverage: vanishing/init) ---
    "small weights", "weight initialization", "xavier", "kaiming",
    "he initialization", "symmetry breaking",
    # --- pure transformers family (reject-coverage: hybrids) ---
    "pure transformers", "pure transformer", "hybrid",
    "hybrid architecture", "hybrid architectures",
    # --- semantically meaningful family (reject-coverage: feature hierarchy) ---
    "semantically meaningful", "semantic", "high-level features",
    "feature hierarchy", "hierarchical features",
    # --- modern models / modern long-context family (reject-coverage) ---
    "modern models", "modern long-context", "long-context",
    "long context", "decoder-only", "128k",
    # --- model families family (reject-coverage: classifier heads) ---
    "model families", "model zoo", "classification head",
    "classifier head", "model.fc", "model.classifier",
    # --- network architectures family (reject-coverage) ---
    "network architectures", "cnn architectures", "alexnet",
    "degradation problem", "skip connections",
    # --- scales better family (reject-coverage: scaling/inductive bias) ---
    "scales better", "scales with data", "scaling", "inductive bias",
    "data-efficient",
    # --- sequence attends family (reject-coverage: self-attention) ---
    "sequence attends", "attends to itself", "self-attention",
    "self attention",
    # --- use linear family (reject-coverage: linear probes/filters) ---
    "use linear", "linear probe", "linear probes", "linear filter",
    "linear filters",
    # --- use relu family (reject-coverage: activations) ---
    "use relu", "relu", "rectified linear", "activation function",
    "activation functions",
    # --- 16 patches family (reject-coverage: ViT patching) ---
    "16 patches", "patch", "patches", "patch size", "patch embedding",
    "196", "14x14", "14×14",
    # --- produces garbage family (reject-coverage: AE latent space) ---
    "produces garbage", "latent space", "unstructured",
    "variational autoencoder", "vae",
    # --- add positional family (reject-coverage) ---
    "add positional", "positional encoding", "positional embedding",
    "positional embeddings", "rope",
    # --- attended family (reject-coverage: attention verb) ---
    "attended", "attend", "attends", "cross-attention",
    # --- frees family (reject-coverage: verb) ---
    "frees", "free the computational graph", "retain_graph",
    # --- gradient points family (reject-coverage: batch-13 covers) ---
    "gradient points", "gradient direction", "steepest ascent",
    "points uphill", "points in the direction",
    # --- learn different family (reject-coverage: symmetry) ---
    "learn different", "symmetry", "identical gradients",
    "same output", "symmetry problem",
    # --- every row family (reject-coverage: code loop) ---
    "every row", "loop through",
    # --- model saved family (reject-coverage: checkpoints) ---
    "model saved", "checkpoint", "checkpoints", "state_dict",
    "save_pretrained",
    # --- across multiple gpus family (reject-coverage: distributed) ---
    "across multiple gpus", "distributed training", "data parallel",
    "model parallel", "shard", "fsdp", "zero",
    # --- times 4096 family (reject-coverage: numeric artifact) ---
    "times 4096", "4096",
    # --- 1000-class family (reject-coverage: artifact) ---
    "1000-class", "imagenet", "num_classes",
    # --- goodfellow et al family (reject-coverage: citation fragments) ---
    "goodfellow et", "goodfellow et al", "et al",
    "deep learning", "adversarial network",
    # --- radford et al family (reject-coverage: citation fragments) ---
    "radford et", "radford et al", "clip", "dcgan", "gpt-2",
    # --- vdots family (reject-coverage: LaTeX artifact) ---
    "vdots", "ddots", "cdots", "vertical dots",
    # --- 51cf66 family (reject-coverage: mermaid color artifact) ---
    "51cf66", "ff6b6b", "c92a2a", "fill:#",
    # --- encoder-decoder models family (same as conditional generation) ---
    "encoder-decoder models", "t5", "bart", "bert",
]


DEF_PAT = re.compile(
    r"(?:is|are)\s+(?:a|an|the)\b|is\s+defined\s+as|refers\s+to|means\b|"
    r"denotes\b|definition\s+of|we\s+define",
    re.IGNORECASE,
)


def fence_spans(struct: dict, total_lines: int) -> list[tuple[int, int]]:
    """Return (start_line, end_line) spans of code fences (1-based, inclusive).

    F-0021 fix: mdextract reports end_line=None with closed=False for an
    UNCLOSSED fence; such a span extends to EOF (total_lines), not to the
    start line. The batch-13 probe used f.get("end_line", start), which
    only defaults when the KEY is absent — an explicit null slipped
    through as None and crashed the span comparison. Same latent bug
    existed in batches 10-13 but never triggered (no probed term matched
    a def pattern inside an unclosed fence).
    """
    out = []
    for f in struct.get("code_fences", []):
        start = f.get("start_line", 0)
        end = f.get("end_line")
        if end is None:
            end = total_lines
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
            spans = fence_spans(struct, len(text.split("\n")))
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
    out_path = Path("/home/z/my-project/scratch/disc002-batch14-probe.json")
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
