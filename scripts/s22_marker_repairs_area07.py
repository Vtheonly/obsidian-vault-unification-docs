#!/usr/bin/env python3
"""S22/SYNTH-001: anchored marker-retention repairs for area 07 (4 findings).

Findings AF-001..AF-004 (reports/synthesis/s22-area07-audit.json): rare source
terms dropped when the subagent paraphrased the sources' transitional
sentences. Each repair below restores the source-voice wording (verbatim-form
term retained) while keeping the canonical wikilink targets. Anchored,
asserted, idempotent.

Sources:
- AF-001 'formalizes': ai-course 07.1/01. Why Sequence Models..., line 94
  "The next note formalizes \"share weights across time\" and shows the
   diagram that every RNN explanation in the world eventually draws — the
   **unrolled computational graph**."
- AF-002 '07.2': ai-course 07.4/03. From RNNs to Attention..., lines 88-92
  checklist "You understand how RNNs work and why they fail (07.1, 07.2)."
  (source section cross-references kept as historical context, per the
  session-21 standing precedent for section-number references)
- AF-003 'confront': ai-course 07.1/02. The Recurrent Neuron..., line 131
  "which forces us to confront a subtle and dangerous fact: ..."
- AF-004 'flesh': ai-course 07.3/01. The Encoder-Decoder Pattern..., line 105
  "The next two notes flesh out the practical details of training (teacher
   forcing) and decoding (beam search), and then the final note in this
   chapter makes the bottleneck argument precise ..."
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO / "output/Unified-Vault"

REPAIRS: list[dict] = [
    {
        "id": "AF-001",
        "file": "07 - Sequence Models/Motivation and Recurrence/Why Sequence Models.md",
        "bad": (
            'The formalization of "share weights across time" — together with the '
            "unrolled computational graph that every RNN explanation eventually "
            "draws — is developed in [[The Recurrent Neuron]]."
        ),
        "good": (
            'The next note, [[The Recurrent Neuron]], formalizes "share weights '
            "across time\" and shows the diagram that every RNN explanation in the "
            "world eventually draws — the **unrolled computational graph**."
        ),
    },
    {
        "id": "AF-002",
        "file": "07 - Sequence Models/Pitfalls and Limits/From RNNs to Attention.md",
        "bad": (
            "You know why sequence models exist ([[Why Sequence Models]]), how RNNs "
            "work and why they fail ([[The Recurrent Neuron]], [[LSTM]], "
            "[[Backpropagation Through Time]], [[07 - Sequence Models/Motivation "
            "and Recurrence/Vanishing and Exploding Gradients|Vanishing and "
            "Exploding Gradients]]), the Encoder-Decoder pattern and its bottleneck "
            "([[The Encoder-Decoder Pattern]], [[The Bottleneck Problem]]),"
        ),
        "good": (
            "You know why sequence models exist (07.1; [[Why Sequence Models]]), "
            "how RNNs work and why they fail (07.1, 07.2; [[The Recurrent "
            "Neuron]], [[LSTM]], [[Backpropagation Through Time]], "
            "[[07 - Sequence Models/Motivation and Recurrence/Vanishing and "
            "Exploding Gradients|Vanishing and Exploding Gradients]]), the "
            "Encoder-Decoder pattern and its bottleneck (07.3, 07.4; "
            "[[The Encoder-Decoder Pattern]], [[The Bottleneck Problem]]),"
        ),
    },
    {
        "id": "AF-003",
        "file": "07 - Sequence Models/Motivation and Recurrence/The Recurrent Neuron.md",
        "bad": (
            "Training the cell forces a subtle and dangerous fact into the open: "
            "training an RNN is just backpropagation on the unrolled graph, but the "
            "unrolled graph can be very deep — as deep as the sequence is long — "
            "and that depth is what causes the [[07 - Sequence Models/Motivation "
            "and Recurrence/Vanishing and Exploding Gradients|Vanishing and "
            "Exploding Gradients]] problem."
        ),
        "good": (
            "Training the cell forces us to confront a subtle and dangerous fact: "
            "training an RNN is just backpropagation on the unrolled graph, but the "
            "unrolled graph can be **very deep** — as deep as the sequence is "
            "long — and that depth is what causes the [[07 - Sequence Models/"
            "Motivation and Recurrence/Vanishing and Exploding Gradients|"
            "Vanishing and Exploding Gradients]] problem."
        ),
    },
    {
        "id": "AF-004",
        "file": "07 - Sequence Models/Sequence to Sequence/The Encoder-Decoder Pattern.md",
        "bad": (
            "The practical details around this architecture complete the picture: "
            "[[Teacher Forcing and Exposure Bias]] covers how the decoder is "
            "trained, [[Beam Search and Decoding Strategies]] covers how it "
            "generates at inference, and [[The Bottleneck Problem]] makes the "
            "bottleneck argument precise before handing off to attention."
        ),
        "good": (
            "The next two notes flesh out the practical details of training "
            "(teacher forcing) and decoding (beam search): [[Teacher Forcing and "
            "Exposure Bias]] covers how the decoder is trained and "
            "[[Beam Search and Decoding Strategies]] covers how it generates at "
            "inference; then [[The Bottleneck Problem]] makes the bottleneck "
            "argument precise and hands off to attention."
        ),
    },
]


def main() -> int:
    applied, skipped = 0, 0
    for r in REPAIRS:
        target = VAULT / r["file"]
        text = target.read_text(encoding="utf-8")
        if r["good"] in text:
            print(f"{r['id']}: already repaired (no-op)")
            skipped += 1
            continue
        assert r["bad"] in text, (
            f"{r['id']}: anchor not found in {r['file']} — refusing to guess"
        )
        fixed = text.replace(r["bad"], r["good"], 1)
        assert fixed.count(r["good"]) == 1
        target.write_text(fixed, encoding="utf-8")
        print(f"{r['id']}: repaired {r['file']}")
        applied += 1
    print(f"applied={applied} skipped(already-done)={skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
