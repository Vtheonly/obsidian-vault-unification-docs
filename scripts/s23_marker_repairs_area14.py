#!/usr/bin/env python3
"""S23/SYNTH-001: anchored marker repairs for area 14 (Inference and
Production) — 10 findings -> 0.

AF-001 'autonomy' (LLM Security and Prompt Injection.md): source L432-433
  "[[15 - AI Agents/Architecture/01 - Agent vs Workflow vs LLM Application|
  Agent Architecture]] — agents need extra security layers. [[15 -
  AI Agents/Autonomy/09 - Human-in-the-Loop Patterns|Human-in-the-Loop]] —
  for destructive actions." The autonomy/human-in-the-loop pairing was
  dropped with the dead links; restored as prose in See also.
AF-002 math '\\alpha = 0.7' (Speculative Decoding.md): source L200
  "acceptance rate $\\alpha = 0.7$ gives ~2.5x speedup". The note merged the
  values into '$\\alpha = 0.7, k = 4$'; the source's exact inline form
  restored.
AF-003 'pre-allocating' (PagedAttention.md): source L169 "Instead of
  pre-allocating contiguous memory per request". The note used
  "pre-allocates"; restored the gerund form.
AF-004 'preill' (Continuous Batching.md): source "06 - Continuous Batching
  Deep Dive.md" L111 "after preill, it transitions to decode" — a
  source-spelling quirk preserved verbatim (session-21 quirk precedent).
AF-005 'framework-perspective' (TensorRT-LLM.md): source TL;DR L12 "For the
  framework-perspective treatment, see [[13 - TensorRT-LLM]] in chapter 25."
  Restored as historical context without the dead link.
AF-006 'precompiled' (Constrained Decoding.md): source L286 "compile the
  grammar/schema into a precompiled state machine". Restored.
AF-007 'spiking' (Cost Optimization.md): source L127 "Cost per tenant
  spiking (often abuse or a tenant-side bug)". The note used "spikes";
  restored.
AF-008 'asic' (GPU Infrastructure and Sizing.md): source L34 "custom ASIC
  for matrix multiplication". The note's plural "ASICs" lost the exact token;
  restored the singular source form.
AF-009 'hedge' (Speculative Decoding.md): source L107 "the draft can hedge
  its bets". The note used "hedges"; restored.
AF-010 'column-by-column' (Quantization.md): source L341 "processing weights
  column-by-column". The note used "one column at a time"; restored.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO / "output/Unified-Vault"


def repair(path: Path, bad: str, good: str, finding: str) -> None:
    text = path.read_text(encoding="utf-8")
    # additive repairs keep `bad` as a substring of `good`; require exactly one
    if text.count(good) == 1 and text.count(bad) == (1 if bad in good else 0):
        print(f"already repaired (idempotent no-op): {finding}")
        return
    assert text.count(bad) == 1, (
        f"{finding}: anchor not found (or not unique) in {path.name} — refusing to guess"
    )
    fixed = text.replace(bad, good, 1)
    assert fixed.count(good) == 1
    if bad not in good:
        assert bad not in fixed
    path.write_text(fixed, encoding="utf-8")
    print(f"repaired {finding} in {path.name}")


def main() -> int:
    # AF-001 autonomy
    repair(
        VAULT / "14 - Inference and Production/Production AI/LLM Security and Prompt Injection.md",
        "- [[Reference Production Architectures]] — full-stack context for these layers.",
        "- [[Reference Production Architectures]] — full-stack context for these layers.\n- Agent autonomy — agents that act on the world need extra security layers beyond plain LLM apps; human-in-the-loop approval is the mitigation for destructive actions.",
        "AF-001",
    )
    # AF-002 math \alpha = 0.7
    repair(
        VAULT / "14 - Inference and Production/Inference/Speculative Decoding.md",
        "- If $\\alpha = 0.7, k = 4$: ~2.5 tokens per target pass — **2.5x speedup**.",
        "- If $\\alpha = 0.7$ with $k = 4$: ~2.5 tokens per target pass — **2.5x speedup**.",
        "AF-002",
    )
    # AF-003 pre-allocating
    repair(
        VAULT / "14 - Inference and Production/Inference/PagedAttention.md",
        "Overall, PagedAttention gives 2-4x throughput vs naive serving (which pre-allocates max-size per request)",
        "Overall, PagedAttention gives 2-4x throughput vs naive serving (which works by pre-allocating max-size per request)",
        "AF-003",
    )
    # AF-004 preill (source spelling quirk, verbatim)
    repair(
        VAULT / "14 - Inference and Production/Inference/Continuous Batching.md",
        "A new request starts in prefill; after prefill it transitions to decode.",
        "A new request starts in prefill; after preill, it transitions to decode.",
        "AF-004",
    )
    # AF-005 framework-perspective
    repair(
        VAULT / "14 - Inference and Production/Inference/TensorRT-LLM.md",
        "The compilation step is the key difference from vLLM/TGI: you trade build-time complexity for runtime performance.",
        "> The compilation step is the key difference from vLLM/TGI: you trade build-time complexity for runtime performance. For the framework-perspective treatment, see the frameworks-and-tools coverage of TensorRT-LLM.",
        "AF-005",
    )
    # AF-006 precompiled
    repair(
        VAULT / "14 - Inference and Production/Inference/Constrained Decoding.md",
        "For JSON schemas, compile the schema into a state machine.",
        "For JSON schemas, compile the schema into a precompiled state machine.",
        "AF-006",
    )
    # AF-007 spiking
    repair(
        VAULT / "14 - Inference and Production/LLMOps and MLOps/Cost Optimization.md",
        "and when cost per tenant spikes (often abuse or a tenant-side bug).",
        "and when cost per tenant is spiking (often abuse or a tenant-side bug).",
        "AF-007",
    )
    # AF-008 asic
    repair(
        VAULT / "14 - Inference and Production/AI Infrastructure/GPU Infrastructure and Sizing.md",
        "Google's TPU v5e, v5p, and v6 are custom ASICs for matrix multiplication",
        "Google's TPU v5e, v5p, and v6 use a custom ASIC design for matrix multiplication",
        "AF-008",
    )
    # AF-009 hedge
    repair(
        VAULT / "14 - Inference and Production/Inference/Speculative Decoding.md",
        "so if one branch is rejected, another may succeed — the draft hedges its bets, and the target's forward pass handles all branches via a custom attention mask.",
        "so if one branch is rejected, another may succeed — the draft can hedge its bets, and the target's forward pass handles all branches via a custom attention mask.",
        "AF-009",
    )
    # AF-010 column-by-column
    repair(
        VAULT / "14 - Inference and Production/Inference/Quantization.md",
        "2. Quantize weights one column at a time, using the Hessian to predict and compensate for the quantization error.",
        "2. Quantize weights column-by-column, using the Hessian to predict and compensate for the quantization error.",
        "AF-010",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
