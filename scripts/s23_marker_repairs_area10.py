#!/usr/bin/env python3
"""S23/SYNTH-001: anchored marker repairs for area 10 (LLMs) — 4 findings -> 0.

Each repair cites its audit finding id, the source locator, and the source
excerpt it restores. Anchored, asserted, idempotent; refuses to guess.

AF-001 'capstones' (LLM Benchmarks.md): source "06 - LLM Benchmarks.md" L226
  "[[27 - Projects/Capstones/13 - Build a RAG Evaluation Harness|RAG Eval
  Harness]] — custom eval implementation." The capstone framing was dropped.

AF-002 'self-critique' (Hallucination.md): source "05 - Hallucination.md" L302
  "[[05 - Reflection]] — agents that self-critique (helps reduce
  hallucination)". The self-critique gloss was dropped with the dead link.

AF-003 'contradicts' (Hallucination.md): source L78 "**Intrinsic**: contradicts
  the source (if RAG is used, contradicts retrieved context)." The note used
  only "contradict"; the exact term was folded away.

AF-004 'todo' (Sampling Strategies.md): source "03 - Sampling Strategies.md"
  L234 "Min-P (Minimum-P) sampling (TODO: cite, 2024) is a newer alternative
  to top-p...". The note dropped the source's literal TODO marker. Restored
  verbatim per the preservation contract (source quirk = knowledge); the
  resulting lint PLACEHOLDER_TEXT warning is documented, not fixed.
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
    # AF-001 capstones
    repair(
        VAULT / "10 - Large Language Models/Evaluation/LLM Benchmarks.md",
        "The same approach extends to custom eval implementations, such as building a RAG evaluation harness.",
        "The same approach extends to custom eval implementations, such as building a RAG evaluation harness — the course treats that build as a capstone project.",
        "AF-001",
    )
    # AF-002 self-critique
    repair(
        VAULT / "10 - Large Language Models/Limitations/Hallucination.md",
        "- [[Constrained Decoding]] — forcing structured output with validatable citation fields.",
        "- [[Constrained Decoding]] — forcing structured output with validatable citation fields.\n- Agent reflection — agents that self-critique their own outputs; this helps reduce hallucination.",
        "AF-002",
    )
    # AF-003 contradicts
    repair(
        VAULT / "10 - Large Language Models/Limitations/Hallucination.md",
        "**Intrinsic** hallucinations contradict the source — in a RAG setting, the retrieved context.",
        "**Intrinsic** hallucinations contradict the source: the output contradicts it — in a RAG setting, the retrieved context.",
        "AF-003",
    )
    # AF-004 todo (verbatim source placeholder)
    repair(
        VAULT / "10 - Large Language Models/Sampling/Sampling Strategies.md",
        "Min-P (Minimum-P) sampling, a newer (2024) alternative to top-p, sets a minimum probability threshold relative to the top token:",
        "Min-P (Minimum-P) sampling (TODO: cite, 2024) is a newer alternative to top-p that sets a minimum probability threshold relative to the top token:",
        "AF-004",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
