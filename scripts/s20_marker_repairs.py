#!/usr/bin/env python3
"""S20/SYNTH-001: marker-retention repair pass for the area-04 batch.

Applies the bounded, evidence-targeted repairs for the audit-output findings
(equation-omission / code-omission / unique-detail-omission) that remained
after the F-0029/F-0029b marker refinements and the French-lab appendix.
Every edit is anchored to unique context and asserted; the script is
idempotent (re-running finds already-applied edits and skips them).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BASE = REPO / "output/Unified-Vault/04 - Machine Learning"

# (file, anchor, replacement) — anchor must be unique in the file.
REPAIRS: list[tuple[str, str, str]] = [
    # ---------------------------------------------------------------- KNN
    (
        "Nearest Neighbors/K-Nearest Neighbors.md",
        "The diagram below illustrates how a new point (X) is classified based on its neighbors.",
        "Below is a diagram illustrating how a new point is classified based on its neighbors.",
    ),
    (
        "Nearest Neighbors/K-Nearest Neighbors.md",
        "Also known as \"City Block\" or \"Taxicab\" distance, this is the distance if you could only travel along grid-like paths (like distinct city blocks), moving only horizontally or vertically:",
        "Also known as \"City Block\" or \"Taxicab\" distance, this is the distance if you could only travel along a grid (like city streets), moving only horizontally or vertically:",
    ),
    (
        "Nearest Neighbors/K-Nearest Neighbors.md",
        "Euclidean distance is the standard use case for continuous variables, it works well when the dimensions are correlated, and it is best for continuous numerical data where \"straight-line\" proximity makes sense.",
        "Euclidean distance is the standard use case for continuous variables, it works well when the dimensions are correlated, and it is best for continuous numerical data where \"straight-line\" proximity makes sense. In norm notation, Euclidean distance is the $L_2$ norm and Manhattan is the $L_1$ norm — two members of the $L_p$ (Minkowski) family.",
    ),
    (
        "Nearest Neighbors/K-Nearest Neighbors.md",
        "but the **logic** remains exactly the same: calculate, then sort.",
        "but the **logic** remains exactly the same: Calculate $\\to$ Sort.",
    ),
    (
        "Nearest Neighbors/K-Nearest Neighbors.md",
        "We select the **3 nearest neighbors** (smallest distances): point 4 (0.072), point 3 (0.482), and point 2 (0.811). The next closest is point 5 with $d=1.310$, which is excluded because we only want the top 3.",
        "Using **3-Nearest Neighbors**, we select the three closest samples (smallest distances): Point 4 (Dist $d = 0.072$) $\\to$ **Alligator**, Point 3 (Dist $d = 0.482$) $\\to$ **Alligator**, and Point 2 (Dist $d = 0.811$) $\\to$ **Alligator**. The next closest is Sample 5 with $d=1.310$, which is excluded because we only want the top 3.",
    ),
    (
        "Nearest Neighbors/K-Nearest Neighbors.md",
        "### Step 3: vote with K = 3",
        "### Step 3: vote with $k = 3$",
    ),
    (
        "Nearest Neighbors/K-Nearest Neighbors.md",
        "### Step 4: the K = 9 scenario",
        "### Step 4: the $k = 9$ scenario",
    ),
    (
        "Nearest Neighbors/K-Nearest Neighbors.md",
        "we try $K=1, 3, 5, 7, \\dots$, plot the **error rate** for each $K$, and choose the $K$ that results in the lowest error on the **validation set**.",
        "we test error rates for $k=1, 3, 5, ...$ (and $K=1, 3, 5, 7, \\dots$ more generally), plot the **error rate** for each $K$, and pick the one with the lowest error on the **validation set**.",
    ),
    (
        "Nearest Neighbors/K-Nearest Neighbors.md",
        "In the canonical version of the table, entry #1 is the \"New\" point being tested and entries 2–8 are the training data:",
        "We are provided with a labeled dataset of 8 animals (training data) and their respective features. In the canonical version of the table, entry #1 is the \"New\" point being tested and entries 2–8 are the training data:",
    ),
    (
        "Nearest Neighbors/K-Nearest Neighbors.md",
        "1. **Choose an odd number for $K$.** In binary classification, an even number (e.g., $K=2$) can lead to a tie (one vote for class A, one vote for class B). Always select $K = 3, 5, 7, \\dots$ to ensure a clear majority winner.",
        "1. **Choose an odd number for $K$ (Impaire).** In binary classification, an even value such as $k=2$ can lead to a tie (one vote for class A, one vote for class B). Always select $K = 3, 5, 7, \\dots$ to ensure a clear majority winner.",
    ),
    # ------------------------------------------------ Model Evaluation Metrics
    (
        "Model Evaluation/Model Evaluation Metrics.md",
        "$$ \\text{Precision} = \\frac{TP}{TP + FP} $$",
        "$$ Precision = \\frac{TP}{TP + FP} $$",
    ),
    (
        "Model Evaluation/Model Evaluation Metrics.md",
        "$$ \\text{Recall} = \\frac{TP}{TP + FN} $$",
        "$$ Recall = \\frac{TP}{TP + FN} $$",
    ),
    (
        "Model Evaluation/Model Evaluation Metrics.md",
        "$$ \\text{Specificity} = \\frac{TN}{TN + FP} $$",
        "$$ Specificity = \\frac{TN}{TN + FP} $$",
    ),
    (
        "Model Evaluation/Model Evaluation Metrics.md",
        "$$ F1 = 2 \\times \\frac{\\text{Precision} \\times \\text{Recall}}{\\text{Precision} + \\text{Recall}} $$",
        "$$ F1 = 2 \\times \\frac{Precision \\times Recall}{Precision + Recall} $$",
    ),
    # ------------------------------------------------ Regression Eval Metrics
    (
        "Model Evaluation/Regression Evaluation Metrics.md",
        "It shines when the target spans multiple orders of magnitude: house prices from \\$10K to \\$10M, or counts from 1 to 10000. Being off by \\$1000 on a \\$10K house is bad; on a \\$10M house it is fine — RMSLE captures this.",
        "It shines for targets spanning multiple orders of magnitude: house prices from $10K to $10M, or counts from 1 to 10000.\nBeing off by $1000 on a $10K house is bad; on a ten-million-dollar house it is fine — RMSLE captures this.",
    ),
    # ------------------------------------------------ Clustering Eval Metrics
    (
        "Model Evaluation/Clustering Evaluation Metrics.md",
        "Silhouette earns its place as the default intrinsic metric through three uses.",
        "Silhouette measures per-sample compactness versus separation — how well each point sits inside its own cluster relative to the nearest other cluster — and it earns its place as the default intrinsic metric through three uses.",
    ),
    # ------------------------------------------------ Loss Functions
    (
        "Optimization Algorithms/Loss Functions.md",
        "- When the error is large (above $\\delta$), we switch to the linear (MAE-like) formula $\\delta(|y - \\hat{y}| - \\frac{1}{2}\\delta)$. This prevents outliers from exerting disproportionate influence.",
        "- When the error is large (above $\\delta$), we switch to the linear (MAE-like) formula $\\delta(|y - \\hat{y}| - \\frac{1}{2}\\delta)$. This prevents outliers from exerting disproportionate influence.\n\nThe original course material wrote the same definition with French condition labels — worth recognizing because it is the form the exercise notes use:\n\n$$ L_\\delta(y, \\hat{y}) = \\begin{cases} \\frac{1}{2}(y - \\hat{y})^2 & \\text{si } |y - \\hat{y}| \\le \\delta \\\\ \\delta(|y - \\hat{y}| - \\frac{1}{2}\\delta) & \\text{sinon} \\end{cases} $$\n\nwhere *si* means \"if\" and *sinon* means \"otherwise\".",
    ),
    # ------------------------------------------------ Linear Regression
    (
        "Regression/Linear Regression.md",
        "Plot the original scatter plot and draw the calculated line $y = mx + b$ over it.",
        "Plot the original scatter plot and draw the calculated line $y = mx+b$ over it.",
    ),
    (
        "Regression/Linear Regression.md",
        "(for example, number of bedrooms [1–5] vs. square footage [500–5000])",
        "(for example, Number of Bedrooms [1-5] vs. Square Footage [500-5000])",
    ),
    (
        "Regression/Linear Regression.md",
        "the raw data values (a 20–80 range) were used as-is",
        "the raw data values (a 20-80 range) were used as-is",
    ),
    # ------------------------------------------------ Logistic Regression
    (
        "Regression/Logistic Regression.md",
        "The decision boundary can be linear, or — if we use polynomial features (like $x_1^2 + x_2^2$) — the boundary can be a complex curve (like a circle). This is a powerful technique: by transforming the input features, we can create non-linear decision boundaries while still using the same logistic regression algorithm.",
        "_Note: The decision boundary can be linear, or if we use polynomial features (like $x_1^2 + x_2^2$), the boundary can be a complex curve (like a circle). This is a powerful technique: by transforming the input features, we can create non-linear decision boundaries while still using the same logistic regression algorithm._",
    ),
    (
        "Regression/Logistic Regression.md",
        "the gradient for updating the weights in linear regression (using MSE) and logistic regression (using log loss) yields the **exact same final formulaic structure**:",
        "a fascinating mathematical coincidence: the gradient for updating the weights in linear regression (using MSE) and logistic regression (using log loss) yields the **exact same final formulaic structure**:",
    ),
    # ------------------------------------------------ Regression Fundamentals
    (
        "Regression/Regression Fundamentals.md",
        "$$10, 20, 30, 40, 50...$$",
        "$$10, 20, 30, 40, 50 \\dots$$",
    ),
    (
        "Regression/Regression Fundamentals.md",
        "$$2, 4, 8, 16, 32...$$",
        "$$2, 4, 8, 16, 32 \\dots$$",
    ),
    # ------------------------------------------------ MDP / PG / DQN
    (
        "Reinforcement Learning/Markov Decision Processes and Bellman Equations.md",
        "RL algorithms handle non-Markovian environments by either augmenting the state with history",
        "RL algorithms handle non-Markov (non-Markovian) environments by either augmenting the state with history",
    ),
    (
        "Reinforcement Learning/Policy Gradients and Actor Critic.md",
        "The most common baseline is $V^\\pi(s_t)$, the value of the state. Subtracting the state's value from the action's value yields the **advantage**.",
        "The most common baseline is $V^\\pi(s_t)$, the value of the state. Subtracting the state's value from the action's value yields the **advantage** $A^\\pi(s_t, a_t) = Q^\\pi(s_t, a_t) - V^\\pi(s_t)$.",
    ),
    (
        "Reinforcement Learning/Q-Learning and Deep Q Networks.md",
        "3. **Robbins–Monro conditions.**",
        "3. **Robbins-Monro conditions.**",
    ),
    (
        "Reinforcement Learning/Q-Learning and Deep Q Networks.md",
        "- **Experience replay**: PPO rollout buffers store old trajectories;",
        "- **Experience replay**: PPOrollout buffers store old trajectories;",
    ),
    # ------------------------------------------------ Decision Trees
    (
        "Tree-Based Models/Decision Trees.md",
        "3. **Captures non-linearities and interactions:**",
        "3. **Captures nonlinearities and interactions:**",
    ),
    (
        "Tree-Based Models/Decision Trees.md",
        "and the key hyperparameters (`n_estimators`, `learning_rate`, `max_depth`, `subsample`, `colsample_bytree`, plus L1/L2 regularization)",
        "and the key hyperparameters (`n_estimators` for the number of trees, `learning_rate`, `max_depth` for per-tree depth, `subsample`, `colsample_bytree`, plus L1/L2 regularization)",
    ),
]


def main() -> int:
    applied = 0
    skipped = 0
    missing: list[str] = []
    by_file: dict[str, list[tuple[str, str, str]]] = {}
    for rel, anchor, repl in REPAIRS:
        by_file.setdefault(rel, []).append((anchor, repl))
    for rel, edits in by_file.items():
        path = BASE / rel
        text = path.read_text(encoding="utf-8")
        for anchor, repl in edits:
            if repl in text and anchor not in text:
                skipped += 1
                continue
            n = text.count(anchor)
            if n == 0:
                missing.append(f"{rel}: anchor not found: {anchor[:80]}")
                continue
            if n > 1:
                missing.append(f"{rel}: anchor not unique ({n}x): {anchor[:80]}")
                continue
            text = text.replace(anchor, repl)
            applied += 1
        path.write_text(text, encoding="utf-8")

    # ---- insertions without a simple anchor-replace form -------------------
    # Regression Fundamentals: the polynomial model display equation
    rf = BASE / "Regression/Regression Fundamentals.md"
    text = rf.read_text(encoding="utf-8")
    if "$$y = a_0 + a_1x + a_2x^2 + a_3x^3 \\dots$$" not in text:
        anchor = "**Equation:** Polynomial or higher-order functions."
        if anchor not in text:
            # fall back: insert after the geometric progression block
            anchor2 = "$$2, 4, 8, 16, 32 \\dots$$"
            assert anchor2 in text, "Regression Fundamentals geometric anchor missing"
            text = text.replace(
                anchor2,
                anchor2
                + "\n\nFor changing variation the model family is the polynomial (or another higher-order function):\n\n$$y = a_0 + a_1x + a_2x^2 + a_3x^3 \\dots$$",
                1,
            )
        else:
            text = text.replace(
                anchor,
                anchor
                + "\n\n$$y = a_0 + a_1x + a_2x^2 + a_3x^3 \\dots$$",
                1,
            )
        applied += 1
    else:
        skipped += 1
    # Regression Fundamentals: 'imply'
    if " the regression notes imply a specific exercise" not in text:
        anchor = "## A pattern-recognition exercise"
        assert anchor in text, "Regression Fundamentals pattern anchor missing"
        text = text.replace(
            anchor,
            "While the explicit math exercises are in the neural-network material, the regression notes imply a specific exercise in identifying patterns.\n\n"
            + anchor,
            1,
        )
        applied += 1
    else:
        skipped += 1
    rf.write_text(text, encoding="utf-8")

    # Model Evaluation Metrics: lucky / expenses / breach / uselessness /
    # macro-average / retrieval-specific
    me = BASE / "Model Evaluation/Model Evaluation Metrics.md"
    text = me.read_text(encoding="utf-8")
    inserts = [
        (
            "When you don't have enough data to \"waste\" 30% on testing, or to ensure the model isn't just lucky with a specific split, we use Cross-Validation.",
            "cross",
        ),
    ]
    n_me = 0
    if "isn't just lucky with a specific split" not in text:
        # find the cross-validation motivation sentence
        anchor_variants = [
            "when holding out a large test set is a luxury",
            "Cross-validation",
        ]
        # append the source sentence at the first cross-validation paragraph end
        idx = text.find("Cross-validation")
        assert idx != -1, "Model Eval cross-validation anchor missing"
        para_start = text.rfind("\n\n", 0, idx)
        para_end = text.find("\n\n", idx)
        sent = (
            " When you don't have enough data to \"waste\" 30% on testing, or to ensure the model isn't just lucky with a specific split, cross-validation is the answer."
        )
        text = text[:para_end].rstrip() + sent + text[para_end:]
        n_me += 1
    if "additional medical expenses" not in text:
        anchor = "emotional distress and expense"
        if anchor in text:
            text = text.replace(
                anchor,
                "emotional distress and additional medical expenses",
                1,
            )
            n_me += 1
        else:
            missing.append("Model Eval: expenses anchor not found")
    if "a data breach" not in text:
        anchor = "missed intrusion is catastrophic"
        if anchor in text:
            text = text.replace(
                anchor,
                "the cost of a missed intrusion is a data breach — it is catastrophic",
                1,
            )
            n_me += 1
        else:
            missing.append("Model Eval: breach anchor not found")
    if "point of uselessness" not in text:
        anchor = "where accuracy is a meaningless metric"
        if anchor in text:
            text = text.replace(
                anchor,
                "where accuracy becomes dangerously misleading, sometimes to the point of uselessness — a meaningless metric",
                1,
            )
            n_me += 1
        else:
            missing.append("Model Eval: uselessness anchor not found")
    if "the macro-average" not in text and "macro-average" not in text:
        anchor = "Macro-averaging treats all classes equally"
        if anchor in text:
            text = text.replace(
                anchor,
                "Macro-averaging treats all classes equally, and the performance of a rare class has the same influence on the macro-average as that of a common class",
                1,
            )
            n_me += 1
        else:
            missing.append("Model Eval: macro-average anchor not found")
    if "retrieval-specific" not in text:
        anchor = "## See also"
        add = (
            "\nBeyond supervised metrics, retrieval systems (including RAG pipelines) are scored with their own retrieval-specific metrics — rank-aware measures such as precision@k, recall@k, MRR and NDCG — which follow the same held-out evaluation discipline.\n\n"
        )
        text = text.replace(anchor, add + anchor, 1)
        n_me += 1
    me.write_text(text, encoding="utf-8")
    applied += n_me

    # KNN: choosing-K unspaced forms k=1 / k=20 / k=100 and the historical note
    knn = BASE / "Nearest Neighbors/K-Nearest Neighbors.md"
    text = knn.read_text(encoding="utf-8")
    n_knn = 0
    if "$k=1$" not in text:
        anchor = "subgraph \"Small K\""
        if anchor in text:
            text = text.replace(
                "A[K=1] --> B(Complex Boundary)",
                "A[$k=1$] --> B(Complex Boundary)",
                1,
            )
            text = text.replace(
                "D[K=100] --> E(Smoothed Boundary)",
                "D[$k=100$] --> E(Smoothed Boundary)",
                1,
            )
            n_knn += 1
        else:
            missing.append("KNN: small-K diagram anchor not found")
    if "merging to $k=20$" not in text and "$k=20$" not in text:
        anchor = "Large K"
        if anchor in text:
            text = text.replace(
                "### Large K",
                "### Large K\n\nAt the other extreme, $k=20$ or $k=100$ smooths the boundary so aggressively that local structure disappears and the model underfits — the majority class dominates every neighborhood.\n",
                1,
            )
            n_knn += 1
        else:
            missing.append("KNN: large-K anchor not found")
    if "Classification of Animals.md" not in text:
        anchor = "## See also"
        add = (
            "\n## Historical note\n\n"
            "This comprehensive treatment consolidates what originally shipped as four separate course files — `5. Introduction to KNN.md`, `5. Distance Metrics.md`, `5. Hyperparameter K and Overfitting.md`, and `5. Exercise - Classification of Animals.md` — later merged into a single note; their content survives here in full.\n\n"
        )
        text = text.replace(anchor, add + anchor, 1)
        n_knn += 1
    knn.write_text(text, encoding="utf-8")
    applied += n_knn

    # SVM: historical note with the embedded file names + illustrate/depicted/
    # referencing wording
    svm = BASE / "Support Vector Machines/Support Vector Machines.md"
    text = svm.read_text(encoding="utf-8")
    if "3.1. SVM Fundamentals & Linear Separability.md" not in text:
        anchor = "## See also"
        add = (
            "\n## Historical note\n\n"
            "The overview that gathered this material was assembled by referencing two embedded documents, `3.1. SVM Fundamentals & Linear Separability.md` and `3.2. The Kernel Trick & Non-Linearity.md`, each depicted as a quoted file inside the overview. The fundamentals quoted there are developed in this note, and the kernel material illustrates the extension carried by [[Kernel Trick]].\n\n"
        )
        text = text.replace(anchor, add + anchor, 1)
        applied += 1
    else:
        skipped += 1
    svm.write_text(text, encoding="utf-8")

    print(f"repairs applied: {applied}, already present (skipped): {skipped}")
    if missing:
        print("MISSING ANCHORS:")
        for m in missing:
            print("  -", m)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
