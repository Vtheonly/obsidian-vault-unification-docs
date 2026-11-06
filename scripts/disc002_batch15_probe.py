#!/usr/bin/env python3
"""DISC-002 session 15 (batch 15) semantic-review coverage probe.

Same purpose and FENCE-AWARE design as scripts/disc002_batch14_probe.py:
for each candidate term, search BOTH source vaults for definitional
treatments (real headings containing the term — authoritative mdextract
state machine, so in-fence '#' comments cannot masquerade as headings —
or definition-sentence patterns near it; in-fence def hits are excluded
from def_hits and reported separately).

F-0021-FIXED fence_spans (signature fence_spans(struct, total_lines)):
mdextract reports end_line=null with closed=false for an UNCLOSed fence;
such a span extends to EOF (total_lines), never None. Copied verbatim
from scripts/disc002_batch14_probe.py per the session-14 handoff — do
NOT copy the batch-13 probe's fence_spans.

Repo-relative paths. Batch-15 tranche: 60 highest-signal unreviewed
provisional candidates (post-batch14 state, session-15 fifteen-round
replay). Term families mirror the tranche candidates; hyphenation and
spelling variants are included per the session-10/11 lessons; the
session-12/13/14 lessons apply: TERM-SEPARATED definitions (quiz
matching blocks, glossary cross-references) defeat term-only search —
probe property-based phrases too, and inspect description lines near
term occurrences before claiming definitional absence; symbol glosses in
math-notation blocks near the term also count (the 'ŷ is the predicted
label' model at Perceptrons and MLPs.md:63), and so do operational
definitions (the 'loss curve' LR-range-test and BatchNorm-EMA models
from session 14).
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

# Concept terms from the batch-15 tranche (excluding pure prose fragments,
# verb phrases, code-comment artifacts, numeric/LaTeX fragments, path
# fragments and example strings, which are rejected on quote evidence
# without a probe).
TERMS = [
    # --- backpropagation computes family (reject-coverage #1) ---
    "backpropagation", "backprop", "chain rule",
    # --- speculative decoding / cheap draft family (#3, #35, #37, #40) ---
    "speculative decoding", "draft model", "draft models", "cheap draft",
    "n-gram", "n-gram model", "verification", "verify the draft",
    "medusa", "eagle", "acceptance rate", "hidden features",
    "predicts hidden", "prompt-derived", "repetitive content",
    # --- class index family (#4) ---
    "class index", "correct class", "target class", "cross-entropy",
    "softmax", "logits", "argmax",
    # --- classification networks family (#5) ---
    "classification network", "classification networks",
    "classification", "classifier", "classification head",
    # --- clear/previous gradients family (#6, #7, #8, #36) ---
    "clear gradients", "zero_grad", "zero the gradients",
    "previous gradients", "gradient accumulation", "accumulate gradients",
    "zero the gradient",
    # --- vault-management meta-prose family (#2, #9, #18, #19, #22, #25, #29) ---
    "candidate note", "concrete gaps", "identify concrete",
    "missing sections", "never remove", "note substantially",
    "architecture decisions", "wc -l", "iteration",
    # --- convert pil family (#10) ---
    "convert pil", "pil", "pillow", "totensor", "transforms",
    "image preprocessing",
    # --- early stopping family (#11, #43) ---
    "early stopping", "patience", "patience_counter",
    "stopping triggered", "best val",
    # --- f-string artifact family (#12) ---
    "f'epoch", "epoch {", "print(f",
    # --- fine-tuning / pre-trained family (#13, #20, #26, #27, #53) ---
    "fine-tuning", "fine tuning", "fine-tune", "pre-trained",
    "pretrained", "pre-trained model", "pre-trained models",
    "pre-trained weights", "transfer learning", "resnet-50", "resnet 50",
    "load pre-trained", "new fc", "fc layer", "fully connected",
    "replace the final", "num_classes", "frozen", "freeze",
    # --- global avg pool family (#14, #15) ---
    "global average pooling", "global avg pool", "global avg",
    "gap", "adaptiveavgpool", "average pooling", "pooling",
    # --- gpu transfer family (#16) ---
    "gpu transfer", "to(device)", "device", "cuda", "gpu",
    # --- hessian / newton family (#17, #21, #28) ---
    "hessian", "hessian information", "newton's method", "newton",
    "second-order", "second-order methods", "curvature",
    "method uses",
    # --- need paired / preference data family (#23, #54) ---
    "preference data", "paired preferences", "preference pairs",
    "preference", "dpo", "kto", "rlhf", "chosen", "reward model",
    "need paired", "binary good/bad",
    # --- negative error family (#24) ---
    "negative error", "squared error", "target - output",
    "error signal", "derivative of the error",
    # --- output spatial size / padding family (#30, #41, #50) ---
    "output spatial size", "output size", "spatial size", "same padding",
    "valid padding", "zero-padding", "zero padding", "padding",
    "sliding window", "right edge", "edge effects", "formula",
    # --- overall accuracy family (#31) ---
    "overall accuracy", "accuracy", "evaluation metrics", "metrics",
    # --- per-channel means family (#32) ---
    "per-channel", "per-channel means", "normalization", "normalize",
    "mean=[0.485", "standardization", "channel means", "0.229",
    # --- pool gradients family (#33) ---
    "pool gradients", "conv gradients", "backward through pooling",
    "gradient of pooling", "upsample", "max pool backward", "route",
    # --- positive contributions / grad-cam family (#34) ---
    "positive contributions", "grad-cam", "gradcam", "cam",
    "class activation map", "class activation mapping",
    # --- total samples family (#44) ---
    "total samples", "dataset size", "sample size", "n =",
    # --- tulu / open-source chat model family (gap-watch #45) ---
    "tulu", "zephyr", "openchat", "instruction-tuned",
    "instruction tuning", "open-source chat", "open source chat",
    "aligned model", "chat model",
    # --- update learning rate family (#46, #47) ---
    "update learning rate", "update the learning rate",
    "learning rate", "scheduler", "lr", "lr_scheduler",
    # --- update step family (#48) ---
    "update step", "update rule", "parameter update",
    "gradient descent step", "sequential", "simultaneous update",
    # --- vlm backbone family (#49) ---
    "vlm", "vlm backbone", "vision-language", "vision-language model",
    "backbone", "multimodal model", "feature extractor", "colpali",
    # --- memories / key-value memories family (#51) ---
    "memories", "key-value memories", "key value memories", "memory",
    "ffn", "feed-forward", "memory systems", "associative memory",
    # --- total number family (#52) ---
    "total number", "notation", "n denotes", "number of items",
    "mathematical notation",
    # --- mamba-2 / ssd family (gap-watch #55) ---
    "mamba-2", "mamba", "ssd", "state space duality",
    "state-space duality", "ssm", "state space model",
    "selective scan", "kernel efficiency",
    # --- rule-based family (gap-watch #56) ---
    "rule-based", "rule based", "symbolic", "expert system",
    "if-then rules", "hand-coded", "rules",
    # --- web search family (gap-watch #57) ---
    "web search", "search tool", "tool use", "tool calling",
    "search engine", "retrieval tool", "google-proof", "tools",
    # --- output node family (#58) ---
    "output node", "output layer", "output neuron", "output units",
    "prediction", "output layer node",
    # --- chat template family (gap-watch #59) ---
    "chat template", "chat templates", "chatml", "im_start",
    "special tokens", "im_end", "instruction template", "template",
    # --- paging / paged attention family (#60) ---
    "paging", "paged", "pagedattention", "vllm", "page table",
    "block table", "kv cache", "contiguous block",
    # --- randomly flip / augmentation family (#38) ---
    "randomly flip", "random horizontal flip", "augmentation",
    "data augmentation", "randomhorizontalflip", "random crop",
    "randomly crop",
    # --- releasing / graph family (#39) ---
    "releasing", "computational graph", "retain_graph", "detach",
    "memory leak", "backward pass",
    # --- second conv family (#42) ---
    "second conv", "conv layer", "convolutional layer", "conv2d",
    # --- load pre-trained / checkpoints family (#20) ---
    "state_dict", "load_state_dict", "torchvision.models", "weights=",
    "checkpoint", "load",
]


DEF_PAT = re.compile(
    r"(?:is|are)\s+(?:a|an|the)\b|is\s+defined\s+as|refers\s+to|means\b|"
    r"denotes\b|definition\s+of|we\s+define",
    re.IGNORECASE,
)


def fence_spans(struct: dict, total_lines: int) -> list[tuple[int, int]]:
    """Return (start_line, end_line) spans of code fences (1-based, inclusive).

    F-0021 fix (copied from scripts/disc002_batch14_probe.py): mdextract
    reports end_line=None with closed=False for an UNCLOSSED fence; such a
    span extends to EOF (total_lines), not to the start line. The
    batch-13 probe used f.get("end_line", start), which only defaults
    when the KEY is absent — an explicit null slipped through as None and
    crashed the span comparison. Same latent bug existed in batches 10-13
    but never triggered (no probed term matched a def pattern inside an
    unclosed fence).
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
    out_path = Path("/home/z/my-project/scratch/disc002-batch15-probe.json")
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
