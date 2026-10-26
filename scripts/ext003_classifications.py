#!/usr/bin/env python3
"""Generate EXT-003 overlap classification records (EXT-003).

Builds state/classifications/001-ext003-regression-overlap.jsonl from the
orchestrator's evidence review of CAP-013 candidates over batches 001+002.

Safety properties:
- every ku_id is resolved against the committed batches (full-id match);
- every evidence quote is verified BYTE-EXACT inside the referenced KU
  excerpt (no transcription);
- evidence lines are computed from the excerpt line positions;
- the output is validated against the classification schema + file-level
  cross-checks before the script exits 0.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from vault_unification import registry  # noqa: E402

BATCHES = [
    REPO / "state/knowledge-units/001-ext001-ai-course-03.1-regression.jsonl",
    REPO / "state/knowledge-units/002-ext002-master-ai-supervised-learning.jsonl",
]
OUT = REPO / "state/classifications/001-ext003-regression-overlap.jsonl"
CLS_SCHEMA = REPO / "schemas/overlap-classification.schema.json"

CANDIDATE_REF = (
    "reports/extraction/ext003-overlap-candidates.json (+ pairs JSONL; "
    "CAP-013 run 2026-10-26 over batches 001+002 with "
    "state/term-maps/regression-domain-v1.json)"
)
CLASSIFIED_BY = "EXT-003 orchestrator (Z AI / GLM 5.3 session, 2026-10-26)"
METHOD = (
    "CAP-013 word-boundary candidate discovery + orchestrator excerpt review: "
    "both sides' KU excerpts read in full from the committed batches; "
    "evidence quotes are byte-exact fragments; overlap_type assigned per "
    "docs/KNOWLEDGE_AND_PROVENANCE.md section 7 (pair-level, separate from "
    "disposition)"
)
DATE = "2026-10-26"

# ---------------------------------------------------------------------------
# load KUs, index by full id and unique suffix


def load_kus():
    kus = {}
    for batch in BATCHES:
        for line in batch.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                kus[rec["knowledge_unit_id"]] = rec
    return kus


def resolve(kus, suffix: str) -> str:
    matches = [k for k in kus if k.endswith(suffix)]
    if len(matches) != 1:
        raise SystemExit(f"suffix {suffix!r} matches {len(matches)} KU ids: {matches}")
    return matches[0]


def quote_evidence(kus, ku_id: str, fragment: str):
    """Verify *fragment* is a byte-exact substring of the KU excerpt and
    return the evidence dict with the exact quote and its source lines."""
    rec = kus[ku_id]
    excerpt = rec.get("excerpt") or ""
    if fragment not in excerpt:
        raise SystemExit(
            f"quote not found byte-exact in {ku_id}:\n  {fragment[:120]!r}\n"
            f"excerpt starts: {excerpt[:120]!r}"
        )
    lines = excerpt.splitlines()
    start_idx = None
    for i, line in enumerate(lines):
        # fragment may span lines; locate its first line
        if fragment.split("\n")[0] in line:
            start_idx = i
            break
    if start_idx is None:
        # multi-line fragment: find via join
        joined = "\n".join(lines)
        pos = joined.find(fragment)
        start_idx = joined[:pos].count("\n")
    n_span = fragment.count("\n") + 1
    src_lines = [
        rec["line_start"] + start_idx + k for k in range(n_span)
    ]
    return {
        "ku_id": ku_id,
        "quote": fragment,
        "source_path": rec["source_path"],
        "lines": src_lines,
    }


def main() -> int:
    kus = load_kus()

    def R(ku_suffix, fragment):
        return (resolve(kus, ku_suffix), fragment)

    classifications = []

    def add(cid, topic, overlap_type, rationale, evidence_pairs):
        ev = [quote_evidence(kus, kid, frag) for kid, frag in evidence_pairs]
        ku_ids = sorted({e["ku_id"] for e in ev})
        vaults = {kus[k]["source_id"].split(":")[0] for k in ku_ids}
        assert len(vaults) >= 2, f"{cid}: single-vault group {vaults}"
        classifications.append(
            {
                "classification_id": cid,
                "task_id": "EXT-003",
                "topic": topic,
                "overlap_type": overlap_type,
                "ku_ids": ku_ids,
                "rationale": rationale,
                "evidence": ev,
                "candidate_ref": CANDIDATE_REF,
                "classified_by": CLASSIFIED_BY,
                "method": METHOD,
                "date": DATE,
            }
        )

    # ---- 0001 linear model form ----
    add(
        "OC-ext003-0001",
        "Linear regression model form (hypothesis function)",
        "Semantic Duplicate",
        "Both vaults define linear regression as predicting a continuous target "
        "with a linear function of the features and write the same model form: "
        "master-ai uses vector notation (y-hat = w·x + b), the course uses "
        "theta-notation (h(x) = theta0 + theta1*x1 + ... + theta_n*x_n) and "
        "Y = wX + b. The claim (linear model form with intercept/bias) is "
        "identical; only notation differs. Course-unique material (simple vs "
        "multiple regression split, endogenous/exogenous terminology, parameter "
        "walkthroughs) is elaboration around the duplicated core, not a "
        "different claim.",
        [
            R("16d1de23", "Predict a continuous target as a linear function of features:"),
            R("797cabc8", "\\hat{y} = \\mathbf{w} \\cdot \\mathbf{x} + b"),
            R("f0cb1d305a4581e8", "Linear regression tries to fit a straight line through a cloud of data"),
            R("9f3cdbe76a29f6b0", "**Simple Linear Regression:** 1 independent variable. $Y = wX + b$"),
            R("44a5244e44dcdc72", "h(x) = \\theta_0 + \\theta_1 x_1 + \\theta_2 x_2 ... \\theta_n x_n"),
        ],
    )

    # ---- 0002 MSE ----
    add(
        "OC-ext003-0002",
        "Mean squared error as the regression cost function",
        "Semantic Duplicate",
        "Both vaults define the regression loss as the mean of squared "
        "prediction errors and present the same formula up to notation and a "
        "normalization convention: master-ai L(w,b) = (1/N) sum (y_i - "
        "y-hat_i)^2; the course J(theta) = (1/2m) sum (h(x) - y)^2 and "
        "E = (1/n) sum (y_i - (m x_i + b))^2, with an explicit callout "
        "explaining its 1/2m convention. The claim (MSE is the standard "
        "regression cost) is duplicated; the course additionally motivates "
        "why squaring (positivity, penalizing large errors).",
        [
            R("77f78038", "L(\\mathbf{w}, b) = \\frac{1}{N} \\sum_{i=1}^{N} (y_i - \\hat{y}_i)^2"),
            R("a952b410c46f7d4b", "We use the Method of Least Squares, formulated as the Mean Squared Err"),
            R("2f6b01e0cad03c87", "J(\\theta_0, \\theta_1) = \\frac{1}{2m} \\sum_{i=1}^{m} (h_\\theta(x^{("),
            R("da614e48a2dd60b6", "Notice the $\\frac{1}{2m}$ instead of jus"),
            R("d34b1ad0162dc662", "**Mean Squared Error (MSE)**"),
            R("0e140ed623033fc0", "E = \\frac{1}{n} \\sum_{i=0}^{n} (y_i - (mx_i + b))^2"),
        ],
    )

    # ---- 0003 normal equations ----
    add(
        "OC-ext003-0003",
        "Normal equations / OLS closed-form solution",
        "Semantic Duplicate",
        "Both vaults give the closed-form OLS solution as the identical "
        "formula (X^T X)^{-1} X^T y (master-ai bold-hat-w notation; course "
        "W = (X^T X)^{-1} X^T Y) and present it as the exact/analytical "
        "solution; only the course describes the derivation (setting the "
        "derivative of the MSE loss to zero and solving algebraically) — "
        "master-ai states the formula and the 'closed-form' concept without "
        "derivation prose. "
        "Term-evidence note: the master-ai excerpt carries the formula and the "
        "'closed-form' concept while the literal words 'Normal Equation' "
        "appear only in its heading (not part of the excerpt), so term "
        "matching alone under-reports this pair; classification is justified "
        "by the formula evidence.",
        [
            R("28a9111a", "\\hat{\\mathbf{w}} = (\\mathbf{X}^T \\mathbf{X})^{-1} \\mathbf{X}^T \\mathbf{y}"),
            R("a6b13aed75257e72", "We set the derivative of the MSE loss to zero and solve for $W$ algebr"),
            R("64d87f0278acada9", "W = (X^T X)^{-1} X^T Y"),
            R("afad28616fcebe08", "This is the **Normal Equation**. It gives the exact, optimal solution"),
        ],
    )

    # ---- 0004 cubic inverse cost ----
    add(
        "OC-ext003-0004",
        "Cubic cost of the matrix inverse (O(d^3) / O(m^3) caveat)",
        "Semantic Duplicate",
        "Both vaults state that inverting X^T X costs cubic time in the number "
        "of features, as the reason the closed form becomes impractical at "
        "scale: master-ai says 'the matrix inverse is $O(d^3)$' (d features); "
        "the course says 'Computing the inverse of $X^T X$ has $O(m^3)$ "
        "complexity (where $m$ is the number of features)' and quantifies it "
        "(10,000 features, roughly 10^12 operations). This corrects "
        "EXT-002-REVIEW Check 5, which listed the O(d^3) caveat as "
        "Master-AI-only: the review's literal term search missed the course's "
        "O(m^3) phrasing (d vs m notation).",
        [
            R("31fa3fbe", "the matrix inverse is $O(d^3)$"),
            R("b3fe573dcfc4675f", "Computing the inverse of $X^T X$ has $O(m^3)$ complexity (where $m$ is the number of features). For a model with 10,000 features, this means roughly $10^{12}$ operations — prohibitively expensive."),
        ],
    )

    # ---- 0005 exact vs iterative tradeoff ----
    add(
        "OC-ext003-0005",
        "When to use the closed form vs gradient descent (scale trade-off)",
        "Semantic Duplicate",
        "Both vaults state the same decision rule: the closed form gives the "
        "exact answer and suits small problems, while gradient descent is the "
        "choice for large problems/datasets. Master-ai: 'For small problems, "
        "this is the exact solution — no iteration needed. For large problems, "
        "use gradient descent (or SGD) instead'. Course trade-off prose and "
        "when-to-use tip callout mirror it ('Small dataset, few features: OLS "
        "is faster and gives the exact answer. Large dataset or many features: "
        "Gradient Descent...'). Same claim, near-verbatim agreement.",
        [
            R("31fa3fbe", "For small problems, this is the exact solution — no iteration needed. For large problems, use gradient descent (or SGD) instead"),
            R("947bf1c807feead8", "There are two fundamentally different approaches to finding the optima"),
            R("3ebb5b50173d194d", "**The trade-off:** OLS gives the exact answer immediately (when feasible"),
            R("fcddebecb4c8121c", "**Small dataset, few features:** OLS is faster and gives the exact answer."),
        ],
    )

    # ---- 0006 GD as scalable iterative method ----
    add(
        "OC-ext003-0006",
        "Gradient descent as the scalable iterative optimization method",
        "Partial Overlap",
        "The shared content is the role of gradient descent as the iterative "
        "alternative that scales (course: 'scales beautifully to arbitrarily "
        "large datasets... mini-batches'; master-ai: one line prescribing "
        "GD/SGD for large problems). Beyond that shared core the sides "
        "diverge: the course develops GD mechanics in depth — update rules "
        "(W = W - eta * grad MSE), learning-rate choice and failure modes "
        "(too small/too large), epochs, and a from-scratch implementation — "
        "while master-ai contributes only the concise prescription. The "
        "mechanics are course-unique depth, not duplicated claims.",
        [
            R("31fa3fbe", "use gradient descent (or SGD) instead"),
            R("59e91d3f0050ae74", "We use the update rule $W = W - \\eta \\cdot \\nabla MSE$ to iteratively"),
            R("b2293a6698747777", "It scales beautifully to arbitrarily large datasets — you never need"),
            R("c1484237", "We use a **Learning Rate ($L$)** to"),
            R("4f1c9fce", "**If $L$ is too small:** The model will learn very slowly. It might take millions of epochs to reach the minimum error."),
            R("e22bf2f0", "def gradient_descent(m_now, b_now, points, L):"),
        ],
    )

    # ---- 0007 sigmoid model form ----
    add(
        "OC-ext003-0007",
        "Logistic sigmoid model form",
        "Semantic Duplicate",
        "Both vaults define logistic regression as the sigmoid applied to the "
        "linear score: master-ai p(y=1|x) = sigma(w·x + b) = 1/(1+e^-(w·x+b)); "
        "course g(z) = 1/(1+e^-z) with h(x) = g(theta^T x), plus the same "
        "purpose statement (squash any linear output into a probability in "
        "(0,1)). Term-evidence note: the master-ai excerpt expresses the "
        "sigmoid as the sigma symbol without the word 'sigmoid', so term "
        "matching alone missed this pair; the classification rests on the "
        "formula evidence. Course-unique elaborations (limit properties as "
        "z -> +/-infinity, 'squashes' intuition prose) are not part of the "
        "duplicated core claim.",
        [
            R("3cf40509", "Binary classification with a probabilistic output:"),
            R("30690f3f", "p(y = 1 \\mid \\mathbf{x}) = \\sigma(\\mathbf{w} \\cdot \\mathbf{x} + b) = \\frac{1}{1 + e^{-(\\mathbf{w} \\cdot \\"),
            R("37365ca5a1071a9b", "We need our hypothesis to output a value between 0 and 1 (a probability). We do this by passing our"),
            R("990a4212d39fcc83", "g(z) = \\frac{1}{1 + e^{-z}}"),
            R("d21e1cb7f027b909", "h(x) = g(\\theta^T x) = \\frac{1}{1 + e^{-\\theta^T x}}"),
        ],
    )

    # ---- 0008 BCE ----
    add(
        "OC-ext003-0008",
        "Binary cross-entropy / log loss definition",
        "Semantic Duplicate",
        "Both vaults define the logistic loss as binary cross-entropy with the "
        "same single-example formula L = -[y log(p-hat) + (1-y) log(1-p-hat)] "
        "and the same batch average (master-ai: -(1/N) sum_i [...]; course: "
        "J(theta) = -(1/m) sum [y log h + (1-y) log(1-h)]), and both build "
        "the full formula stepwise (master-ai 'For one example' then 'For a "
        "batch'; course piecewise 'Cost if y=1 / Cost if y=0' then the "
        "combined equation). The definition is semantically duplicated; the "
        "course additionally derives why (non-convexity of MSE under sigmoid) "
        "in separate course-unique units.",
        [
            R("2f36cf98", "For one example:"),
            R("729f705a", "L = -[y \\log \\hat{p} + (1-y) \\log(1 - \\hat{p})]"),
            R("3c5e48b4", "For a batch:"),
            R("448131a4", "L = -\\frac{1}{N} \\sum_i [y_i \\log \\hat{p}_i + (1-y_i) \\log(1 - \\hat{p}_i)]"),
            R("b31d134d133a3b32", "- Cost if $y=1$: $-\\log(h(x))$"),
            R("2327ca515b6bccb3", "\\text{Loss} = -[y \\log(\\hat{y}) + (1-y) \\log(1-\\hat{y})]"),
            R("71a2a0040ce29e58", "J(\\theta) = -\\frac{1}{m} \\sum_{i=1}^{m} [y^{(i)} \\log(h_\\theta(x^{("),
            R("deeee89749d932bf", "**Binary Cross-Entropy (Log Loss)**"),
            R("d12bca6dab0606d9", "Averaging over $n$ samples gives the full Binary Cross-Entropy formula"),
        ],
    )

    # ---- 0009 softmax ----
    add(
        "OC-ext003-0009",
        "Softmax as the multiclass output layer",
        "Partial Overlap",
        "The shared content is the role of softmax as the multiclass output "
        "mechanism: master-ai defines softmax regression mathematically "
        "(p(y=k|x) = exp(w_k·x) / sum_j exp(w_j·x)) and states 'softmax "
        "regression is exactly the output layer of every modern LLM'; the "
        "course demonstrates the same output-layer role in practice in its "
        "French MNIST lab (keras Dense(10, activation='softmax') for 10-class "
        "output, with the architecture explained in French). The course never "
        "states the softmax formula and master-ai shows no implementation, so "
        "each side contributes a different facet (theory vs applied usage) of "
        "the same claim rather than duplicating content.",
        [
            R("8ea55a48", "For $K$ classes:"),
            R("d567d124", "p(y = k \\mid \\mathbf{x}) = \\frac{\\exp(\\mathbf{w}_k \\cdot \\mathbf{x})}{\\sum_j \\exp(\\mathbf{w}_j \\cdot \\mathbf{x})}"),
            R("2fefe5f8", "softmax regression is exactly the output layer of every modern LLM"),
            R("d758cb4d3ebb7e4d", "activation='softmax'"),
            R("942d3848", "`Sequential()` : Indique que le modèle est une pile linéaire de couches."),
        ],
    )

    # ---- 0010 NN building blocks ----
    add(
        "OC-ext003-0010",
        "Linear/logistic regression as neural-network building blocks",
        "Partial Overlap",
        "The shared framing is that the classical models are the primitives "
        "of neural networks: master-ai makes the specific claim ('A dense "
        "layer is a linear regression + activation. A classification head is "
        "softmax regression. Every Transformer is built from these "
        "primitives.'), while the course opens its DL-perspective note with "
        "the general version ('Before building neural networks, we must "
        "understand the fundamental statistical models they are built upon') "
        "and then demonstrates the claim by building an actual keras network "
        "from Dense layers in the MNIST lab. Master-ai's specific "
        "layer-equations claim and the course's implementation are "
        "complementary facets of the same framing, not duplicated statements.",
        [
            R("99aa02fb", "A dense layer is a linear regression + activation. A classification head is softmax regression. Every Transfor"),
            R("f97d032588b7d830", "Before building neural networks, we must understand the fundamental statistical models they are built upon."),
            R("d758cb4d3ebb7e4d", "from tensorflow.keras import models, layers"),
        ],
    )

    # ---- 0011 sklearn workflow ----
    add(
        "OC-ext003-0011",
        "sklearn linear-model usage workflow",
        "Partial Overlap",
        "Both vaults demonstrate the sklearn linear-model workflow "
        "(import -> instantiate -> fit -> predict -> evaluate): master-ai's "
        "worked example uses LinearRegression, LogisticRegression and Ridge "
        "with the C = 1/lambda mapping; the course's French lab walks through "
        "LinearRegression on synthetic data with mean_squared_error and "
        "model.score evaluation, explained line-by-line in French. The shared "
        "content is the usage pattern; the specific models, the Ridge/C "
        "inverse-regularization mapping (master-ai-only) and the French "
        "pedagogy (course-only) are unique to each side.",
        [
            R("095bdcf5", "from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge"),
            R("095bdcf5", "# C = 1/lambda"),
            R("bca783756b65c8f9", "from sklearn.linear_model import LinearRe"),
            R("d633a7f7db26734a", "model = LinearRegression()"),
            R("22c1d3c61a0ed141", "preds = model.predict(x)"),
            R("78aa89cfcb3a1f19", "mse = mean_squared_error(y, preds)"),
        ],
    )

    # ---- 0012 multicollinearity ----
    add(
        "OC-ext003-0012",
        "Multicollinearity / singular X^T X",
        "Partial Overlap",
        "The shared claim is that correlated features make the unregularized "
        "linear model ill-conditioned: the course states it as an OLS "
        "limitation ('The matrix $X^T X$ may be singular (non-invertible) "
        "when features are highly correlated (multicollinearity), causing "
        "numerical instability'); master-ai states it as a pitfall with a "
        "remedy ('Multicollinearity — correlated features produce unstable "
        "coefficients in unregularized regression. Use ridge.') and, in the "
        "ridge section, the fix ('The $\\lambda \\mathbf{I}$ term makes the "
        "inverse always well-defined (no singularity)'). Shared core concept; "
        "master-ai uniquely contributes the ridge remedy connection.",
        [
            R("b3fe573dcfc4675f", "The matrix $X^T X$ may be singular (non-invertible) when features are highly correlated (multicollinearity), causing numerical instability."),
            R("5fea1a73", "**Multicollinearity** — correlated features produce unstable coefficients in unregularized regression. Use ridge."),
            R("32e307c8", "The $\\lambda \\mathbf{I}$ term makes the"),
        ],
    )

    # ---- 0013 decision boundary ----
    add(
        "OC-ext003-0013",
        "Linearity of the logistic decision boundary",
        "Partial Overlap",
        "The shared claim is that the logistic decision boundary is linear in "
        "the features: the course derives it ('the decision boundary is the "
        "line where $\\theta^T x = 0$' from g(z) >= 0.5 iff z >= 0) and "
        "extends it (polynomial features give curved boundaries); master-ai "
        "states it as a pitfall ('the decision boundary is a hyperplane. If "
        "classes aren't linearly separable (even in feature space), it won't "
        "work well'). Shared core claim; course-unique: the derivation and "
        "the polynomial extension; master-ai-unique: the failure-mode "
        "framing.",
        [
            R("e0cf9e25", "Therefore, the decision boundary is the line where **$\\theta^T x = 0$**."),
            R("fedad87c", "The decision boundary can be linear, or if we use polynomial features"),
            R("810a0f7123ae76d0", "Logistic Regression is actually modeling the **linear relationship between the features a"),
            R("5fea1a73", "the decision boundary is a hyperplane. If classes aren't linearly separable (even in feature space), it won't work well."),
        ],
    )

    # ---- 0014 feature scaling ----
    add(
        "OC-ext003-0014",
        "Feature scaling / standardization practice",
        "Partial Overlap",
        "The shared content is the practice of bringing features to a "
        "comparable scale: the course presents it as an optimization aid "
        "('Gradient Descent works best when input features are on a similar "
        "scale'), details Min-Max normalization and Z-score "
        "standardization, and applies it in the MNIST lab (pixel values "
        "divided by 255 into [0,1]); master-ai prescribes it for regularized "
        "models ('Feature scaling matters for regularized linear models. "
        "Standardize features before applying L1/L2.') without stating a "
        "motivation. Shared practice recommendation; the course's GD-"
        "conditioning motivation is course-unique, and the technique "
        "details are split across sides.",
        [
            R("fa3e4f35", "Gradient Descent works best when input features are on a similar scale"),
            R("cade2cf1", "**Min-Max Normalization:** Scales data strictly between 0 and 1."),
            R("5e3ac3f2", "**Standardization (Z-score):** Centers data around a mean of 0 with a standard deviation of 1."),
            R("169259731978f5ae", "On divise par 255 pour ramener toutes les valeurs dans l'intervalle [0, 1]."),
            R("5c4493b4", "**Feature scaling** matters for regularized linear models. Standardize features before applying L1/L2."),
        ],
    )

    # ------------------------------------------------------------------
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        for rec in classifications:
            fh.write(json.dumps(rec, ensure_ascii=False, sort_keys=True) + "\n")

    # file-level validation (schema + cross-checks) before exit 0
    report = registry.validate_classification_file(OUT, CLS_SCHEMA)
    if not report["valid"]:
        print("VALIDATION FAILED:")
        for err in report["errors"]:
            print(" ", err)
        return 1
    print(f"wrote {OUT} with {len(classifications)} classifications; valid")
    for rec in classifications:
        print(
            f"  {rec['classification_id']} {rec['overlap_type']:30s} "
            f"ku_ids={len(rec['ku_ids'])} evidence={len(rec['evidence'])} "
            f"| {rec['topic']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
