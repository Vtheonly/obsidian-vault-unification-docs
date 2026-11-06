#!/usr/bin/env python3
"""S21/SYNTH-001: marker-retention repair pass for the area-05 batch.

Applies the bounded, evidence-targeted repairs for the 40 audit-output
findings (equation-omission / code-omission / unique-detail-omission) over
scratch/synth/area05/audit-kus.jsonl (report:
reports/synthesis/s21-area05-audit.json). Every edit is anchored to unique
context and asserted; the script is idempotent (re-running finds
already-applied edits and skips them).

Repair classes (root-caused like session 20):
  R1 verbatim-form equation gaps (content present in equivalent notation;
     the source's exact LaTeX form added at the matching spot);
  R2 verbatim-form code gaps (README directory tree restored as a `text`
     fence; mermaid label restored to the source's unquoted form; one
     diagram character typo fixed Var = 1 -> Var ≈ 1);
  R3 rare-term/wording gaps (the source's exact wording restored, including
     two source-spelling quirks preserved verbatim per the preservation
     contract: "breakthroughths", "Presving");
  R4 underscore-emphasis formatting variants (the source's _word_ italic
     forms restored where the note had rewritten them as plain/asterisk);
  R5 source section cross-references (Section 13.5.3 / 13.9.1 / 14.4)
     restored verbatim where the source had them (historical context of the
     original curriculum, per the session-20 "historical notes" precedent);
  R6 the label-smoothing source self-correction: both the formula value
     (0.91) and the source's recalculated arithmetic (0.9 + the target
     vector) preserved together, with the difference contextualized.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BASE = REPO / "output/Unified-Vault/05 - Neural Network Foundations"

# (relative file path, unique old text, exact new text)
REPAIRS: list[tuple[str, str, str]] = [
    # ------------------------------------------------ Weight Initialization
    # R1a: master-ai Xavier compromise display form (Var(W_ij) element notation)
    (
        "Training Dynamics and Stability/Weight Initialization.md",
        "$$\\boxed{\\text{Var}(w) = \\frac{2}{n_{\\text{in}} + n_{\\text{out}}}}$$",
        "$$\\boxed{\\text{Var}(w) = \\frac{2}{n_{\\text{in}} + n_{\\text{out}}}}$$\n\n"
        "In element notation, the same compromise reads:\n\n"
        "$$\n\\text{Var}(W_{ij}) = \\frac{2}{n_{\\text{in}} + n_{\\text{out}}}\n$$",
    ),
    # R1b: master-ai Xavier sample-form sentence (N/U with \left forms)
    (
        "Training Dynamics and Stability/Weight Initialization.md",
        "Or using a uniform distribution:\n\n$$ W \\sim \\mathcal{U}\\left(-\\sqrt{\\frac{6}{n_{in} + n_{out}}}, +\\sqrt{\\frac{6}{n_{in} + n_{out}}}\\right) $$",
        "Or using a uniform distribution:\n\n$$ W \\sim \\mathcal{U}\\left(-\\sqrt{\\frac{6}{n_{in} + n_{out}}}, +\\sqrt{\\frac{6}{n_{in} + n_{out}}}\\right) $$\n\n"
        "In the concise sampling form: sample from $\\mathcal{N}\\left(0, \\frac{2}{n_{\\text{in}} + n_{\\text{out}}}\\right)$ "
        "or $\\mathcal{U}\\left(-\\sqrt{\\frac{6}{n_{\\text{in}} + n_{\\text{out}}}}, \\sqrt{\\frac{6}{n_{\\text{in}} + n_{\\text{out}}}}\\right)$.",
    ),
    # R1c: master-ai He sample-form sentence
    (
        "Training Dynamics and Stability/Weight Initialization.md",
        "$$ W \\sim \\mathcal{N}\\left(0, \\sqrt{\\frac{2}{n_{in}}}\\right) $$",
        "$$ W \\sim \\mathcal{N}\\left(0, \\sqrt{\\frac{2}{n_{in}}}\\right) $$\n\n"
        "In the concise sampling form: sample from $\\mathcal{N}\\left(0, \\frac{2}{n_{\\text{in}}}\\right)$ "
        "or $\\mathcal{U}\\left(-\\sqrt{\\frac{6}{n_{\\text{in}}}}, \\sqrt{\\frac{6}{n_{\\text{in}}}}\\right)$.",
    ),
    # R1d: master-ai ReLU-halving sentence with its equation
    (
        "Training Dynamics and Stability/Weight Initialization.md",
        "An introductory form of He initialization for ReLU and its variants states the same principle directly: since ReLU zeros out half of the inputs (negative ones), the variance of the output is effectively halved compared to the input, so the initialization compensates by doubling the variance:",
        "An introductory form of He initialization for ReLU and its variants states the same principle directly. He et al. (2015) observed that ReLU zeros out ~half the inputs: $y_j = \\text{ReLU}(\\sum_i W_{ji} x_i)$; the variance of the active (non-zero) outputs is halved. To compensate, the initialization doubles the variance:",
    ),
    # R1e: source's PyTorch Kaiming-uniform default formula (with a^2 inline)
    (
        "Training Dynamics and Stability/Weight Initialization.md",
        "In other words, the weights are drawn from a uniform distribution $U(-a, a)$ whose bound is computed from the effective fan-in, and the bias is initialized from a uniform distribution $U(-1/\\sqrt{fan_{in}}, 1/\\sqrt{fan_{in}})$.",
        "In other words, the weights are initialized from a uniform distribution $U(-a, a)$ "
        "where $a = \\sqrt{6 / ((1 + a^2) \\times fan_{in})}$ and $a^2$ is the negative slope of "
        "the ReLU (default 0 for standard ReLU), and the bias is initialized from a uniform "
        "distribution $U(-1/\\sqrt{fan_{in}}, 1/\\sqrt{fan_{in}})$.",
    ),
    # R3: source spelling preserved verbatim ("breakthroughths")
    (
        "Training Dynamics and Stability/Weight Initialization.md",
        "> Xavier initialization was one of the key breakthroughs that enabled training of deep feedforward networks.",
        "> Xavier initialization was one of the key breakthroughths that enabled training of deep feedforward networks.",
    ),
    # R3: "well-chosen" (source hyphenation)
    (
        "Training Dynamics and Stability/Weight Initialization.md",
        "they are well chosen for the standard architectures — in production, use the default inits from PyTorch/HuggingFace",
        "they're well-chosen for the standard architectures — in production, use the default inits from PyTorch/HuggingFace",
    ),
    # R5: source cross-reference (Section 14.4)
    (
        "Training Dynamics and Stability/Weight Initialization.md",
        "While this does break symmetry, it suffers from the same vanishing problem described above.",
        "While this does break symmetry, it suffers from the same vanishing problem described in Section 14.4.",
    ),
    # R2: diagram character restored (Var ≈ 1, not Var = 1)
    (
        "Training Dynamics and Stability/Weight Initialization.md",
        '        E3 --> F3["Var = 1"]',
        '        E3 --> F3["Var ≈ 1"]',
    ),
    # ------------------------------------------------------------ Backpropagation
    # R2: README directory tree restored as a historical note (text fence)
    (
        "Backpropagation/Backpropagation.md",
        "Each stage builds on the concepts introduced in the previous ones, so reading out of order tends to produce confusion rather than saved time.",
        "Each stage builds on the concepts introduced in the previous ones, so reading out of order tends to produce confusion rather than saved time. "
        "As a historical note, the module that consolidated this treatment was organized as the following directory structure:\n\n"
        "```text\n"
        "01 - Prerequisites/\n"
        "    1. Derivatives, Power Rule, and the Chain Rule\n"
        "    2. Gradients and Gradient Descent\n"
        "\n"
        "02 - Foundations/\n"
        "    3. Neural Network Architecture and Notation\n"
        "    4. Forward Propagation and Activation Functions\n"
        "\n"
        "03 - Error and Optimization/\n"
        "    5. Loss Functions and Error Calculation\n"
        "    6. Gradient Descent \u2014 The Update Rule and Convergence\n"
        "\n"
        "04 - Backpropagation/\n"
        "    7. Backpropagating to the Output Layer\n"
        "    8. Backpropagating to the Hidden Layer\n"
        "    9. Matrix Implementation and the Delta Weight Formula\n"
        "```\n\n"
        "The same module consolidated a family of lesson files, each contributing a distinct slice of the treatment:\n\n"
        "| Lesson file | Key content |\n"
        "| --- | --- |\n"
        "| Backpropagation 1 Coding Training | Intuitive proportional blame, feedforward |\n"
        "| Backpropagation 2 Coding Training | JS matrix code, transposition, error backprop |\n"
        "| Backpropagation 3 Coding Training | Architecture, gradient descent, delta weight |\n"
        "| Backpropagation | Rigorous calculus derivations, delta notation |\n"
        "| Chatgpt Gradients | Gradient definition, geometric meaning |\n"
        "| Stat quest Backpropagation 1 | Drug dosage, SSR, chain rule for b3 |\n"
        "| Stat quest Backpropagation 2 | Multiple parameters, fancy notation, BFEs |\n"
        "| Stat quest Backpropagation 3 | Hidden layer BFEs, Softplus derivative |\n"
        "| Stat quest Chain-rule | Derivatives, power rule, chain rule, RSS |",
    ),
    # R1: hidden node 2 inline label form ($e_{h2}$)
    (
        "Backpropagation/Backpropagation.md",
        "and symmetrically for **Hidden Node 2**:",
        "and symmetrically, the **total error for Hidden Node 2 ($e_{h2}$)** is:",
    ),
    # R3: "5-term multiplication" (source phrasing)
    (
        "Backpropagation/Backpropagation.md",
        "The chain rule multiplies all five effects:",
        "Using the Chain Rule, we get a 5-term multiplication:",
    ),
    # R3: "at the micro-level" (source phrasing)
    (
        "Backpropagation/Backpropagation.md",
        "In detailed algebraic steps (StatQuest style): first the **power rule** brings",
        "In detailed algebraic steps (StatQuest style) — using the **power rule** and the **chain rule** (at the micro-level): first the **power rule** brings",
    ),
    # R3: "parallelizing backprop" (source phrasing)
    (
        "Backpropagation/Backpropagation.md",
        "For models too large for one GPU, backprop must be parallelized, with four main strategies.",
        "For models too large for one GPU, parallelizing backprop becomes its own discipline, with four main strategies.",
    ),
    # ------------------------------------------- Perceptrons and Multi-Layer Perceptrons
    # R4: source underscore-italic form restored (superseded by FIXUPS (a)
    # after the old idempotency bug tripled the underscores)
    # ------------------------------------------------------------ Backpropagation
    # R2: README directory tree + lesson-file table restored as a historical
    # note (the tree body must be the SOURCE's exact directory structure;
    # see FIXUPS (b) which corrected the first, reconstructed version)
    (
        "Neural Network Basics/Perceptrons and Multi-Layer Perceptrons.md",
        "starting from the output and moving backward to the input using the **chain rule of calculus**. This is the computationally brilliant part",
        "starting from the output and moving backward to the input using the _chain rule of calculus_. It reuses the same rule to calculate the gradient (partial derivative) of the loss function with respect to _every single weight and bias_ in the network. This is the computationally brilliant part",
    ),
    (
        "Neural Network Basics/Perceptrons and Multi-Layer Perceptrons.md",
        "the chain rule must multiply backward through the *entire* network",
        "the chain rule must multiply backward through the _entire_ network",
    ),
    # ------------------------------------------------------------- Data Augmentation
    # R3: source sentence (well-lit / dimly lit cats)
    (
        "Training Dynamics and Stability/Data Augmentation.md",
        "it does not know that a cat is still a cat when viewed from a slightly different angle, when the lighting changes, or when part of it is occluded. By presenting transformed versions",
        "it does not know that a cat is still a cat when viewed from a slightly different angle, when the lighting changes, or when part of it is occluded. "
        "If the network has only ever seen upright, well-lit, fully visible cats during training, it will fail to recognize a tilted, dimly lit, or partially hidden cat at test time. "
        "By presenting transformed versions",
    ),
    # R3: "deferred" (source phrasing)
    (
        "Training Dynamics and Stability/Data Augmentation.md",
        "The introductions here are kept brief for awareness; detailed implementations and analysis are a more advanced topic in training technique design.",
        "We provide brief introductions here for awareness; detailed implementations and analysis are deferred to the advanced training techniques chapter.",
    ),
    # R2: mermaid label restored to the source's unquoted form
    (
        "Training Dynamics and Stability/Data Augmentation.md",
        '    A["PIL Image<br/>HWC, uint8<br/>[0, 255]"] --> B["RandomResizedCrop<br/>(PIL → PIL)"]',
        '    A[PIL Image<br/>HWC, uint8<br/>[0, 255]] --> B["RandomResizedCrop<br/>(PIL → PIL)"]',
    ),
    # --------------------------------- Hyperparameters and Network Configuration
    # R3: "exhaustively" + "equip" (source phrasing)
    (
        "Training Dynamics and Stability/Hyperparameters and Network Configuration.md",
        "This note covers every major hyperparameter, derives the intuitions behind them from first principles, provides practical guidance grounded in empirical research, and equips you with systematic strategies for hyperparameter tuning.",
        "This note exhaustively covers every major hyperparameter, derives the intuitions behind them from first principles, provides practical guidance grounded in empirical research, and aims to equip you with systematic strategies for hyperparameter tuning.",
    ),
    # R3: "too-low" (source hyphenation)
    (
        "Training Dynamics and Stability/Hyperparameters and Network Configuration.md",
        "and a tiny learning rate causes the optimizer to crawl through these flat regions. The typical symptoms are:",
        "and a tiny learning rate causes the optimizer to crawl through these flat regions. The typical symptoms of too-low learning rate are:",
    ),
    # R3: source spelling preserved verbatim ("Presving")
    (
        "Training Dynamics and Stability/Hyperparameters and Network Configuration.md",
        "2. **Preserving border information**: Without padding,",
        "2. **Presving border information**: Without padding,",
    ),
    # ------------------------------------------------------ Dropout and Regularization
    # R3: "moderately-sized" (source hyphenation)
    (
        "Training Dynamics and Stability/Dropout and Regularization.md",
        "Even a moderately sized model will overfit",
        "Even a moderately-sized model will overfit",
    ),
    # R6: label smoothing — preserve the source's self-correction (both values)
    (
        "Training Dynamics and Stability/Dropout and Regularization.md",
        "where $\\alpha$ is the smoothing parameter (typically 0.1). For a 10-class problem with $\\alpha = 0.1$, the correct class target becomes $0.9 + 0.01 = 0.91$ and each incorrect class target is $0.1 / 10 = 0.01$, so the smoothed label is $[0.01, 0.01, 0.91, 0.01, \\ldots, 0.01]$ instead of $[0, 0, 1, 0, \\ldots, 0]$.",
        "where $\\alpha$ is the smoothing parameter (typically 0.1). For a 10-class problem with $\\alpha = 0.1$, the correct class target becomes $0.9 + 0.01 = 0.91$ by the formula. The worked arithmetic is often walked through as: the correct class target is $1 - 0.1 = 0.9$, and each incorrect class target is $0.1 / 10 = 0.01$, so the smoothed label is $[0.01, 0.01, 0.9, 0.01, \\ldots, 0.01]$ instead of $[0, 0, 1, 0, \\ldots, 0]$. The two readings differ by the $\\alpha/K$ mass that the formula adds back to the correct class; an implementation of $\\text{label smoothing} = 0.1$ produces the $0.91$ value.",
    ),
    # -------------------------------------------- Data Preparation for Neural Networks
    # R4: source underscore-italic form restored
    (
        "Neural Network Basics/Data Preparation for Neural Networks.md",
        "> [!WARNING] Never initialize weights to zero",
        "> [!WARNING] _Never initialize weights to zero_",
    ),
    # ---------------------------------- Backpropagation and Gradient Flow in CNNs
    # R5: source cross-references restored
    (
        "Backpropagation/Backpropagation and Gradient Flow in CNNs.md",
        "**What it does internally**: This single method call triggers the entire reverse-mode automatic differentiation process described above. Here is what happens step by step:",
        "**What it does internally**: This single method call triggers the entire reverse-mode automatic differentiation process described in Section 13.5.3. Here is what happens step by step:",
    ),
    (
        "Backpropagation/Backpropagation and Gradient Flow in CNNs.md",
        "| Conv2d | Computes the gradient via convolution as described above |",
        "| Conv2d | Computes the gradient via convolution as described in Section 13.9.1 |",
    ),
    # -------------------------------------------- Artificial Neural Networks
    # R1: the source's compact step-C result form ($Input$)
    (
        "Neural Network Basics/Artificial Neural Networks.md",
        "$$ \\frac{\\partial n}{\\partial W} = P \\text{ (the input to that connection)} $$",
        "$$ \\frac{\\partial n}{\\partial W} = P $$\n\nResult: $Input$ (the signal coming into that connection).",
    ),
    # ------------------------------------------------------ Activation Functions
    # R3: "facilitates" (source phrasing)
    (
        "Neural Network Basics/Activation Functions.md",
        "the gradients for weights can be both positive and negative, leading to more efficient optimization paths and faster convergence, which is why tanh was historically preferred",
        "the gradients for weights can be both positive and negative, which facilitates faster convergence and more efficient optimization paths — which is why tanh was historically preferred",
    ),
    # -------------------------------------- Vanishing and Exploding Gradients
    # R3: "early-layer" (source phrasing)
    (
        "Training Dynamics and Stability/Vanishing and Exploding Gradients.md",
        "This product of Jacobians is the source of both the vanishing and exploding gradient problems.",
        "This product of Jacobians — the gradient of the loss w.r.t. early-layer weights — is the source of both the vanishing and exploding gradient problems.",
    ),
]


_R1A_BLOCK = (
    "In element notation, the same compromise reads:\n\n$$\n\\text{Var}(W_{ij}) = \\frac{2}{n_{\\text{in}} + n_{\\text{out}}}\n$$"
)
_R1B_LINE = (
    "In the concise sampling form: sample from $\\mathcal{N}\\left(0, \\frac{2}{n_{\\text{in}} + n_{\\text{out}}}\\right)$ "
    "or $\\mathcal{U}\\left(-\\sqrt{\\frac{6}{n_{\\text{in}} + n_{\\text{out}}}}, \\sqrt{\\frac{6}{n_{\\text{in}} + n_{\\text{out}}}}\\right)$."
)
_R1C_LINE = (
    "In the concise sampling form: sample from $\\mathcal{N}\\left(0, \\frac{2}{n_{\\text{in}}}\\right)$ "
    "or $\\mathcal{U}\\left(-\\sqrt{\\frac{6}{n_{\\text{in}}}}, \\sqrt{\\frac{6}{n_{\\text{in}}}}\\right)$."
)

# (file, insertion that must appear exactly once after dedup)
DEDUP: list[tuple[str, str]] = [
    ("Training Dynamics and Stability/Weight Initialization.md", _R1A_BLOCK),
    ("Training Dynamics and Stability/Weight Initialization.md", _R1B_LINE),
    ("Training Dynamics and Stability/Weight Initialization.md", _R1C_LINE),
]


def _dedup_tree() -> None:
    """Collapse the tripled README-tree insertion in Backpropagation.md.

    The insertion INS (= new[len(anchor):] of the tree repair, a leading
    space + the historical-note block ending in 'chain rule, RSS |') was
    applied three times, so the file reads anchor + INS*3. Keep one.
    """
    relpath, anchor, new = next(
        r for r in REPAIRS if r[0] == "Backpropagation/Backpropagation.md" and "As a historical note" in r[2]
    )
    ins = new[len(anchor):]
    path = BASE / relpath
    text = path.read_text(encoding="utf-8")
    for n in (3, 2):
        repeated = ins * n
        if repeated in text:
            path.write_text(text.replace(repeated, ins, 1), encoding="utf-8")
            print(f"dedup (x{n}->x1): {relpath} README-tree insertion")
            return
    if text.count("As a historical note, the module that consolidated") != 1:
        raise SystemExit("tree dedup failed: unexpected occurrence count")


FIXUPS: list[tuple[str, str, str]] = [
    # (a) the Perceptrons underscore repair applied 3x under the old buggy
    #     idempotency check (old is a substring of new): collapse to the
    #     source-exact single-underscore form (capital **Epochs** as in source)
    (
        "Neural Network Basics/Perceptrons and Multi-Layer Perceptrons.md",
        "___This process is repeated for thousands of **epochs** until the loss is minimized.___",
        "_This process is repeated for thousands of **Epochs** until the loss is minimized._",
    ),
    # (b) the first tree insertion reconstructed the directory structure from
    #     the study-path prose instead of copying the source verbatim; replace
    #     with the source's exact tree (00. README lines 8-23)
    (
        "Backpropagation/Backpropagation.md",
        "```text\n01 - Prerequisites/\n    1. Derivatives, Power Rule, and the Chain Rule\n    2. Gradients and Gradient Descent\n\n02 - Foundations/\n    3. Neural Network Architecture and Notation\n    4. Forward Propagation and Activation Functions\n    5. Loss Functions and Error Calculation\n\n03 - Core Backpropagation/\n    6. Backpropagating to the Output Layer\n    7. Backpropagating to the Hidden Layer\n    8. Matrix Implementation and the Delta Weight Formula\n\n04 - Advanced Topics/\n    9. Backpropagation and Gradient Flow in CNNs\n```",
        "```text\n01 - Prerequisites/\n    1. Derivatives, Power Rule, and the Chain Rule\n    2. Gradients and Gradient Descent\n\n02 - Foundations/\n    3. Neural Network Architecture and Notation\n    4. Forward Propagation and Activation Functions\n\n03 - Error and Optimization/\n    5. Loss Functions and Error Calculation\n    6. Gradient Descent \u2014 The Update Rule and Convergence\n\n04 - Backpropagation/\n    7. Backpropagating to the Output Layer\n    8. Backpropagating to the Hidden Layer\n    9. Matrix Implementation and the Delta Weight Formula\n```",
    ),
    # (c) restore the paragraph break after the lesson-file table (the tree
    #     insertion left the following sentence glued to the last table row)
    (
        "Backpropagation/Backpropagation.md",
        "| Stat quest Chain-rule | Derivatives, power rule, chain rule, RSS | The forward pass is treated in",
        "| Stat quest Chain-rule | Derivatives, power rule, chain rule, RSS |\n\nThe forward pass is treated in",
    ),
]


def main() -> int:
    applied = 0
    skipped = 0
    failed: list[str] = []
    # one-time dedup: the first version of this script had an idempotency bug
    # (append-style repairs whose `new` contains `old` re-applied on re-run,
    # tripling four insertions); collapse them back to a single copy.
    for relpath, single in DEDUP:
        path = BASE / relpath
        text = path.read_text(encoding="utf-8")
        tripled = single + "\n\n" + single + "\n\n" + single
        doubled = single + "\n\n" + single
        if tripled in text:
            path.write_text(text.replace(tripled, single, 1), encoding="utf-8")
            print(f"dedup (x3->x1): {relpath}")
        elif doubled in text:
            path.write_text(text.replace(doubled, single, 1), encoding="utf-8")
            print(f"dedup (x2->x1): {relpath}")
    _dedup_tree()
    for relpath, old, new in FIXUPS + REPAIRS:
        path = BASE / relpath
        if not path.is_file():
            failed.append(f"file not found: {relpath}")
            continue
        text = path.read_text(encoding="utf-8")
        if new in text:  # already applied (idempotent, incl. append-style)
            skipped += 1
            continue
        hits = text.count(old)
        if hits != 1:
            failed.append(f"anchor not unique ({hits} hits): {relpath}: {old[:60]!r}")
            continue
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        applied += 1
    summary = {
        "script": "scripts/s21_marker_repairs.py",
        "repairs_declared": len(REPAIRS) + len(FIXUPS),
        "applied": applied,
        "already_applied": skipped,
        "failed": failed,
        "idempotent": True,
    }
    print(json.dumps(summary, indent=1))
    if failed:
        print("FAILED REPAIRS:", file=sys.stderr)
        for f in failed:
            print("  " + f, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
