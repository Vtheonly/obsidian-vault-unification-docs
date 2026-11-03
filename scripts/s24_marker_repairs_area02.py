#!/usr/bin/env python3
"""S24/SYNTH-001: anchored marker-retention repairs for area 02 (30 audit findings -> 0).

Root causes (all verbatim-source form artifacts):

1. BARE-FENCE EQUATIONS (19 code findings): the master-ai statistics notes
   ('16 - Estimators and Bias.md' 15x, '17 - Hypothesis Testing.md' 3x, plus
   one blank-line diff in '10 - Gradient and Chain Rule.md') write display
   equations inside BARE ``` fences as unicode text (e.g. 'θ_MLE = argmax_θ
   p(X | θ) = argmax_θ Π_i p(x_i | θ)'). The generated notes transliterated
   them to $$ LaTeX, which changes the code fingerprint. Repair: restore the
   source-verbatim equation as a ```text fence — the exact in-batch precedent
   of 'Adam Optimizer Derivation.md' (its worked-example steps) and 'Tensors
   and Broadcasting.md' ('shape_C[i] = max(...)'), which passed this audit.
   Converting also restores the audited tokens _map, argmin_, _unbiased and
   n_tests carried inside those equations.
2. One python fence in 'Gradient and Chain Rule.md' carries an extra blank
   line versus the source; removed.
3. Dropped source content restored: the LLM-MLE example (token_ / token_i),
   the deep-ensemble 'uncertainty-related' pointer, two See-also annotation
   lines ('Brier score', 'z-tests, t-tests assume Gaussian').

Each repair cites its finding id and source locator. Anchored, asserted,
idempotent (probe-checked for insertions). Sources immutable.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
EST = REPO / "output/Unified-Vault/02 - Mathematics/Statistics/Estimators and Bias.md"
HYP = REPO / "output/Unified-Vault/02 - Mathematics/Statistics/Hypothesis Testing.md"
GRAD = REPO / "output/Unified-Vault/02 - Mathematics/Calculus/Gradient and Chain Rule.md"
PROBE = REPO / "output/Unified-Vault/02 - Mathematics/Probability/Probability Essentials.md"
GAUSS = REPO / "output/Unified-Vault/02 - Mathematics/Probability/Gaussian Distribution.md"

R = []


def add(file, bad, good, why, probe=None):
    R.append((file, bad, good, why, probe))


# ---- Estimators and Bias: $$ LaTeX -> source-verbatim ```text fences -------
add(EST,
    "$$\n\\theta_{MLE} = \\arg\\max_\\theta p(X \\mid \\theta) = \\arg\\max_\\theta \\prod_i p(x_i \\mid \\theta)\n$$",
    "```text\nθ_MLE = argmax_θ p(X | θ) = argmax_θ Π_i p(x_i | θ)\n```",
    "AF-020 code (src 16 - Estimators and Bias.md lines 29-31)")
add(EST,
    "$$\n\\log p(X \\mid \\theta) = \\sum_i \\log p(x_i \\mid \\theta)\n$$",
    "```text\nlog p(X | θ) = Σ_i log p(x_i | θ)\n```",
    "AF-018 code (src lines 36-38)")
add(EST,
    "$$\n\\log L(\\mu, \\sigma^2) = -\\frac{n}{2} \\log(2\\pi) - \\frac{n}{2} \\log(\\sigma^2) - \\sum_i \\frac{(x_i - \\mu)^2}{2\\sigma^2}\n$$",
    "```text\nlog L(μ, σ²) = -n/2 log(2π) - n/2 log(σ²) - Σ_i (x_i - μ)² / (2σ²)\n```",
    "AF-002 code (src lines 45-47)")
add(EST,
    "$$\n\\mu_{MLE} = \\frac{1}{n} \\sum_i x_i\n$$",
    "```text\nμ_MLE = (1/n) Σ_i x_i\n```",
    "AF-022 code (src lines 50-52)")
add(EST,
    "$$\n\\sigma^2_{MLE} = \\frac{1}{n} \\sum_i (x_i - \\mu_{MLE})^2\n$$",
    "```text\nσ²_MLE = (1/n) Σ_i (x_i - μ_MLE)²\n```",
    "AF-005 code (src lines 55-57)")
add(EST,
    "$$\nL(p) = \\prod_i p(x_i)\n$$\n\n$$\n\\log L(p) = \\sum_i \\log p(x_i)\n$$",
    "```text\nL(p) = Π_i p(x_i)\nlog L(p) = Σ_i log p(x_i)\n```",
    "AF-008 code (src lines 64-67: one fence, two lines)")
add(EST,
    "$$\n\\theta_{MAP} = \\arg\\max_\\theta p(\\theta \\mid X) = \\arg\\max_\\theta p(X \\mid \\theta) p(\\theta)\n$$",
    "```text\nθ_MAP = argmax_θ p(θ | X) = argmax_θ p(X | θ) p(θ)\n```",
    "AF-027/AF-026 code + '_map' (src lines 76-78)")
add(EST,
    "$$\np(\\theta \\mid X) = \\frac{p(X \\mid \\theta) p(\\theta)}{p(X)}\n$$",
    "```text\np(θ | X) = p(X | θ) p(θ) / p(X)\n```",
    "AF-021 code (src lines 81-83)")
add(EST,
    "$$\n\\log p(\\theta \\mid X) = \\log p(X \\mid \\theta) + \\log p(\\theta) + \\text{const} = \\text{log-likelihood} + \\text{log-prior}\n$$",
    "```text\nlog p(θ | X) = log p(X | θ) + log p(θ) + const\n             = log-likelihood + log-prior\n```",
    "AF-001 code (src lines 88-91: two-line fence)")
add(EST,
    "$$\n\\log p(\\theta) = -\\frac{\\theta^2}{2\\tau^2} + \\text{const}\n$$",
    "```text\nlog p(θ) = -θ² / (2τ²) + const\n```",
    "AF-015 code (src lines 97-99)")
add(EST,
    "$$\n\\theta_{MAP} = \\arg\\max_\\theta \\left[\\log L(\\theta) - \\frac{\\theta^2}{2\\tau^2}\\right] = \\arg\\min_\\theta \\left[-\\log L(\\theta) + \\frac{\\theta^2}{2\\tau^2}\\right]\n$$",
    "```text\nθ_MAP = argmax_θ [log L(θ) - θ² / (2τ²)]\n      = argmin_θ [-log L(θ) + θ² / (2τ²)]\n```",
    "AF-030/AF-028/AF-029 code + '_map' + 'argmin_' (src lines 102-105)")
add(EST,
    "$$\n\\log p(\\theta) = -\\frac{|\\theta|}{b} + \\text{const}\n$$",
    "```text\nlog p(θ) = -|θ| / b + const\n```",
    "AF-010 code (src lines 111-113)")
add(EST,
    "$$\n\\mathbb{E}[\\hat{\\theta}] = \\theta \\quad \\text{(the true parameter)}\n$$",
    "```text\nE[θ̂] = θ  (the true parameter)\n```",
    "AF-013 code (src lines 128-130)")
add(EST,
    "$$\ns^2_{\\text{unbiased}} = \\frac{1}{n-1} \\sum (x_i - \\bar{x})^2\n$$",
    "```text\ns²_unbiased = (1/(n-1)) Σ (x_i - x̄)²\n```",
    "AF-025/AF-024 code + '_unbiased' (src lines 135-137)")
add(EST,
    "$$\n\\text{Var}(\\hat{\\theta}) = \\mathbb{E}\\left[(\\hat{\\theta} - \\mathbb{E}[\\hat{\\theta}])^2\\right]\n$$",
    "```text\nVar(θ̂) = E[(θ̂ - E[θ̂])²]\n```",
    "AF-019 code (src lines 141-143)")
add(EST,
    "$$\n\\hat{\\theta}_n \\to \\theta \\quad \\text{as } n \\to \\infty\n$$",
    "```text\nθ̂_n → θ  as n → ∞\n```",
    "AF-006 code (src lines 156-158)")

# ---- Estimators and Bias: dropped content ----------------------------------
add(EST,
    "This is exactly the **cross-entropy loss** (negated). Training an LLM with cross-entropy loss is MLE — we're finding the parameters that make the observed token sequence most probable.",
    "This is exactly the **cross-entropy loss** (negated). Applied to language modeling, the pieces line up as: **Data** — token sequences from a corpus; **Model** — the LLM, parameterized by `θ`; **Likelihood** — `p(tokens | θ) = Π p(token_i | token_<i, θ)`; **MLE** — maximize the log-likelihood, i.e. minimize the cross-entropy loss. Training an LLM with cross-entropy loss is MLE — we're finding the parameters that make the observed token sequence most probable.",
    "AF-011/AF-012 'token_'/'token_i' (src lines 181-184: the LLM-MLE example with its autoregressive likelihood, dropped by the note)",
    probe="p(tokens | θ) = Π p(token_i | token_<i, θ)")
add(EST,
    "This is the most reliable uncertainty estimate for neural networks, but the cost ($B$ × training) is high.",
    "This is the most reliable uncertainty estimate for neural networks, but the cost ($B$ × training) is high. For uncertainty-related interpretability, see the probing notes in the interpretability area.",
    "AF-016 'uncertainty-related' (src line 279: 'See [[...Probing]] for uncertainty-related interpretability')",
    probe="uncertainty-related interpretability, see the probing notes")
add(EST,
    "Note that $\\sigma^2_{MLE}$ is biased (divides by $n$ instead of $n-1$). The unbiased estimator divides by $n-1$.",
    "Note that $\\sigma^2_{MLE}$ is biased (divides by $n$ instead of $n-1$). The `_unbiased` sample-variance estimator divides by $n-1$.",
    "AF-001 '_unbiased' (src lines 135-137: NFKC normalizes the fence's 's²_unbiased' to 's2_unbiased' on the output side, so the token needs a prose reference; grounded in the source's s²_unbiased notation)",
    probe="`_unbiased` sample-variance estimator")

# ---- Hypothesis Testing: $$ LaTeX -> source-verbatim ```text fences --------
add(HYP,
    "$$\n\\text{CI} = \\bar{x} \\pm z \\cdot \\frac{\\sigma}{\\sqrt{n}}\n$$",
    "```text\nCI = x̄ ± z * (σ / √n)\n```",
    "AF-009 code (src 17 - Hypothesis Testing.md lines 93-95)")
add(HYP,
    "$$\nP(\\text{at least one false positive}) = 1 - (1 - 0.05)^{20} \\approx 0.64\n$$",
    "```text\nP(at least one false positive) = 1 - (1 - 0.05)^20 ≈ 0.64\n```",
    "AF-004 code (src lines 109-111)")
add(HYP,
    "$$\n\\alpha_{\\text{corrected}} = \\alpha / n_{\\text{tests}}\n$$",
    "```text\nα_corrected = α / n_tests\n```",
    "AF-007/AF-006 code + 'n_tests' (src lines 117-119)")

# ---- Gradient and Chain Rule: extra blank line in python fence -------------
add(GRAD,
    "    (loss / accumulation_steps).backward()  # scale to maintain correct average\n\noptimizer.step()",
    "    (loss / accumulation_steps).backward()  # scale to maintain correct average\noptimizer.step()",
    "AF-003 code (src 10 - Gradient and Chain Rule.md lines 279-285: no blank line before optimizer.step())")

# ---- See-also annotations ---------------------------------------------------
add(PROBE,
    "- [[Hypothesis Testing]]\n",
    "- [[Model Evaluation Metrics]] — calibration, NLL, Brier score.\n- [[Hypothesis Testing]] — p-values, confidence intervals, A/B testing.\n",
    "AF-014 'brier' (src 07 - Probability Essentials.md lines 378-390: See-also annotations dropped)",
    probe="Brier score")
add(GAUSS,
    "- [[Hypothesis Testing]]\n",
    "- [[Hypothesis Testing]] — z-tests, t-tests assume Gaussian.\n",
    "AF-017 'z-tests' (src 09 - Gaussian Distribution.md lines 296-305: See-also annotation dropped)",
    probe="z-tests, t-tests assume Gaussian")


def main() -> int:
    for file, bad, good, why, probe in R:
        text = file.read_text(encoding="utf-8")
        if probe is not None:
            done = probe in text and text.count(probe) == 1
        else:
            done = good in text and bad not in text
        if done:
            print(f"already repaired (idempotent no-op): {file.name} :: {why[:60]}")
            continue
        assert bad in text, f"anchor not found in {file.name} — refusing to guess :: {why}"
        fixed = text.replace(bad, good, 1)
        assert good in fixed, f"repair not applied in {file.name} :: {why}"
        if probe is not None:
            assert fixed.count(probe) == 1, f"probe count != 1 after repair in {file.name} :: {why}"
        file.write_text(fixed, encoding="utf-8")
        print(f"repaired: {file.name} — {why[:110]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
