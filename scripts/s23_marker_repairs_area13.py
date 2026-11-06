#!/usr/bin/env python3
"""S23/SYNTH-001: anchored marker repairs for area 13 (Training and
Adaptation) — 8 findings -> 0.

AF-001 '2-10x' (Loss Spikes and Stability.md): source "05 - Loss Spikes and
  Stability.md" L268 "(3) reduce LR by 2-10x". The note used the typographic
  '2-10×'; the source's ASCII form restored.
AF-002 'english-training' (Data Pipelines and Deduplication.md): source
  "03 - Data Pipelines and Deduplication.md" L85 "you don't want
  English-training to be polluted" — hyphenated form restored.
AF-003 'prep' (DPO Derivation.md): source "04 - DPO Derivation.md" L246
  "[[29 - Interview Prep/Coding/04 - Coding Interview Questions 2|Coding
  Interview Q2]] — GRPO loss implementation." The interview-prep framing was
  dropped.
AF-004 'capstones' (Loss Spikes and Stability.md): source L289 "[[27 -
  Projects/Capstones/11 - Build a Distributed Training Pipeline|Distributed
  Training Pipeline]] — checkpointing and recovery." Capstone framing added
  to See also.
AF-005 math (QLoRA.md): source "02 - QLoRA.md" L118 "…(~$30k/month on
  cloud). After QLoRA, it requires a single 48GB GPU (~$2k/month…)". The
  note's '; after' broke the source's byte-run that the math fingerprint
  spans; restored to '. After'.
AF-006 'inspires' (LoRA.md): source "01 - LoRA.md" L471 "[[05 - Matrix
  Decomposition]] — SVD, which inspires PiSSA". Restored.
AF-007 'capstones' (Distributed Training.md): source "02 - Distributed
  Training.md" L175 "[[27 - Projects/Capstones/11 - Build a Distributed
  Training Pipeline|Build a Distributed Training Pipeline]] — hands-on FSDP
  implementation." Capstone framing added to See also.
AF-008 'capstones' (QLoRA.md): source L178 "[[27 - Projects/Capstones/07 -
  Build a Reasoning Model Fine-Tune|Reasoning Model Fine-Tune]] — uses
  QLoRA." Capstone framing restored in the production-implications prose.
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
    # AF-001 2-10x
    repair(
        VAULT / "13 - Training and Adaptation/Optimization/Loss Spikes and Stability.md",
        "If spikes recur, reduce the learning rate by 2-10×.",
        "If spikes recur, reduce the learning rate by 2-10x.",
        "AF-001",
    )
    # AF-002 english-training
    repair(
        VAULT / "13 - Training and Adaptation/Training Data/Data Pipelines and Deduplication.md",
        "you don't want English training to be polluted by misclassified non-English text.",
        "you don't want English-training to be polluted by misclassified non-English text.",
        "AF-002",
    )
    # AF-003 prep
    repair(
        VAULT / "13 - Training and Adaptation/Fine-Tuning/DPO Derivation.md",
        "A related coding exercise is implementing the GRPO loss.",
        "A related coding exercise from the interview-prep track is implementing the GRPO loss.",
        "AF-003",
    )
    # AF-004 capstones (Loss Spikes See also)
    repair(
        VAULT / "13 - Training and Adaptation/Optimization/Loss Spikes and Stability.md",
        "- [[05 - Neural Network Foundations/Training Dynamics and Stability/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]] — the underlying gradient pathologies.",
        "- [[05 - Neural Network Foundations/Training Dynamics and Stability/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]] — the underlying gradient pathologies.\n- Building a distributed-training pipeline (a capstone project) — the hands-on treatment of checkpointing and recovery.",
        "AF-004",
    )
    # AF-005 math (source byte-run '. After QLoRA')
    repair(
        VAULT / "13 - Training and Adaptation/Fine-Tuning/QLoRA.md",
        "Before QLoRA, fine-tuning a 65B model required 8x A100 80GB (~$30k/month on cloud); after QLoRA, it requires a single 48GB GPU (~$2k/month or even a workstation).",
        "Before QLoRA, fine-tuning a 65B model required 8x A100 80GB (~$30k/month on cloud). After QLoRA, it requires a single 48GB GPU (~$2k/month or even a workstation).",
        "AF-005",
    )
    # AF-006 inspires
    repair(
        VAULT / "13 - Training and Adaptation/Fine-Tuning/LoRA.md",
        "Initializes $\\mathbf{A}, \\mathbf{B}$ from the SVD of $\\mathbf{W}$ rather than randomly.",
        "Initializes $\\mathbf{A}, \\mathbf{B}$ from the SVD of $\\mathbf{W}$ — the matrix decomposition that inspires PiSSA — rather than randomly.",
        "AF-006",
    )
    # AF-007 capstones (Distributed Training See also)
    repair(
        VAULT / "13 - Training and Adaptation/Distributed Training/Distributed Training.md",
        "- [[14 - Inference and Production/Inference/vLLM|vLLM]] — tensor parallelism at inference; distributed inference uses similar techniques",
        "- [[14 - Inference and Production/Inference/vLLM|vLLM]] — tensor parallelism at inference; distributed inference uses similar techniques\n- Building a distributed training pipeline (a capstone project) — hands-on FSDP implementation with checkpointing",
        "AF-007",
    )
    # AF-008 capstones (QLoRA prose)
    repair(
        VAULT / "13 - Training and Adaptation/Fine-Tuning/QLoRA.md",
        "including hands-on projects such as building a reasoning-model fine-tune.",
        "including hands-on projects such as building a reasoning-model fine-tune — one of the course's capstones that uses QLoRA.",
        "AF-008",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
