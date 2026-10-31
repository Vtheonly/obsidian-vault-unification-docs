#!/usr/bin/env python3
"""DISC-002 session 12 (batch 12) semantic-review coverage probe.

Same purpose and FENCE-AWARE design as scripts/disc002_batch11_probe.py:
for each candidate term, search BOTH source vaults for definitional
treatments (real headings containing the term — authoritative mdextract
state machine, so in-fence '#' comments cannot masquerade as headings —
or definition-sentence patterns near it; in-fence def hits are excluded
from def_hits and reported separately).

Repo-relative paths. Batch-12 tranche: 60 highest-signal unreviewed
provisional candidates (post-batch11 state, session-12 twelve-round
replay). Term families mirror the tranche candidates; hyphenation and
spelling variants are included per the session-10/11 lessons (search
variants before claiming absence; check the master-ai glossary Acronyms
Index and A-Z Terms before claiming acronym/term absence).
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

# Concept terms from the batch-12 tranche (excluding pure prose fragments,
# verb phrases, code-comment artifacts, path/variable fragments and
# vault-navigation labels, which are rejected on quote evidence without a
# probe).
TERMS = [
    # --- cifar10 family (gap-watch: named dataset used as exercise proxy) ---
    "cifar-10", "cifar10", "cifar", "60000", "32x32", "60,000 images",
    # --- class label family ---
    "class label", "class labels", "classification problem",
    "classified into", "target label", "ground truth", "integer class",
    # --- logsoftmax family (spelling variant of covered 'log-softmax') ---
    "logsoftmax", "log-softmax", "log softmax", "nllloss",
    "negative log-likelihood", "log-probabilities",
    # --- avg pool family (abbreviation variant of covered 'average pooling') ---
    "avg pool", "avgpool", "average pooling", "adaptiveavgpool",
    "adaptive average pooling", "global average pooling",
    # --- class scores family (logit synonyms) ---
    "class score", "class scores", "logits", "raw logits", "pre-softmax",
    # --- convolutional block family ---
    "convolutional block", "conv block", "convblock", "conv → batchnorm",
    "conv-bn-relu", "standard building block",
    # --- sgd optimizer family ---
    "sgd", "stochastic gradient descent", "mini-batch gradient descent",
    "sgd with momentum", "momentum",
    # --- inside function family (chain-rule vocabulary) ---
    "inside function", "outside function", "composite function",
    "chain rule",
    # --- final relu family (residual block anatomy) ---
    "final relu", "relu after", "after the addition", "residual block",
    "residual connection", "skip connection", "identity shortcut",
    # --- output error family (04.2 backprop teaching) ---
    "output error", "error of the hidden", "delta weight", "error signal",
    # --- sparse signal family (ORM vs PRM) ---
    "sparse signal", "dense signal", "credit assignment",
    "process reward model", "outcome reward model", "prm",
    # --- imagenet weights family ---
    "imagenet weights", "imagenet1k", "pre-trained weights",
    "pretrained", "pre-trained model", "weights='default'",
    # --- input spatial size family ---
    "input spatial size", "spatial size", "fixed-size input",
    "regardless of the input", "adaptive pooling",
    # --- grad-cam heatmap family ---
    "grad-cam", "gradcam", "grad-cam heatmap", "class activation map",
    "activation maps",
    # --- late-interaction retrieval family ---
    "late-interaction", "late interaction", "maxsim", "multi-vector",
    # --- multi-class problems family ---
    "multi-class", "multi-class problems", "one-vs-rest", "macro average",
    "micro average", "macro-averaging", "micro-averaging",
    # --- fully-connected layer family ---
    "fully connected layer", "fully-connected layer", "classification head",
    "flattening", "dense layer",
    # --- pre-trained resnet-50 family ---
    "pre-trained resnet-50", "pretrained resnet-50", "resnet-50",
    "models.resnet50", "resnet50_weights",
    # --- single fixed-length vector family (information bottleneck) ---
    "single fixed-length", "fixed-length vector", "thought vector",
    "information bottleneck", "context vector",
    # --- cot chains family ---
    "cot chains", "chain-of-thought", "reasoning chains",
    "self-consistency", "majority voting",
    # --- models 2023 / reward models 2023 family (PRM paper note) ---
    "process reward models 2023", "let's verify step by step",
    "prm800k",
    # --- uses running stats family (BatchNorm eval mode) ---
    "uses running stats", "running statistics", "running mean",
    "running stats", "evaluation mode", "batch statistics",
    # --- server-side family ---
    "server-side", "server side", "client-side", "mcp server",
    # --- imagenet family (reject-coverage citations) ---
    "imagenet", "ilsvrc", "1000 categories", "1000 imagenet classes",
    # --- 1b-parameter family (reject coverage) ---
    "reverse mode", "reverse-mode", "forward mode", "forward-mode",
    "automatic differentiation", "autodiff",
    # --- networks deeper family (reject coverage) ---
    "deeper networks", "network depth", "degradation problem",
    # --- move images / move labels family (reject coverage) ---
    "to(device)", "device placement", "same device",
    # --- mnistnet family (reject coverage) ---
    "mnistnet", "mnist",
    # --- epoch family (reject coverage) ---
    "epoch is", "one complete pass", "checkpointing",
    # --- speculative decoding family (reject coverage) ---
    "draft model", "target model verifies", "speculative decoding",
    # --- augmentation family (reject coverage) ---
    "randomresizedcrop", "random crop", "data augmentation",
    # --- cot prompt-phrase family (reject coverage) ---
    "let's think step by step", "zero-shot cot",
    # --- colpali family (reject coverage) ---
    "colpali", "paligemma",
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
    out_path = Path("/home/z/my-project/scratch/disc002-batch12-probe.json")
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
