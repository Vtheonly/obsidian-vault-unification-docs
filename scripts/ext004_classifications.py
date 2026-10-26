#!/usr/bin/env python3
"""Generate EXT-004 overlap classification records (EXT-004).

Builds state/classifications/002-ext004-tree-based-overlap.jsonl from the
orchestrator's evidence review of CAP-013 candidates over batch 003 +
the master-ai tree-based subset of batch 002 (tree domain).

Safety properties (inherited from the EXT-003 pattern):
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
    REPO / "state/knowledge-units/003-ext004-ai-course-03.7-tree-based-models.jsonl",
    REPO / "state/knowledge-units/002-ext002-master-ai-supervised-learning.jsonl",
]
OUT = REPO / "state/classifications/002-ext004-tree-based-overlap.jsonl"
CLS_SCHEMA = REPO / "schemas/overlap-classification.schema.json"

CANDIDATE_REF = (
    "reports/extraction/ext004-overlap-candidates.json (+ pairs JSONL; "
    "CAP-013 run 2026-10-26 over batch 003 (ai-course 03.7 Tree-Based "
    "Models, 94 KUs) + the 30 master-ai tree KUs of batch 002 "
    "(reports/extraction/ext004-master-ai-tree-subset.jsonl) with "
    "state/term-maps/tree-domain-v1.json)"
)
CLASSIFIED_BY = "EXT-004 orchestrator (Z AI / GLM 5.3 session, 2026-10-26)"
METHOD = (
    "CAP-013 word-boundary candidate discovery + orchestrator excerpt review: "
    "both sides' KU excerpts read in full from the committed batches; "
    "evidence quotes are byte-exact fragments; overlap_type assigned per "
    "docs/KNOWLEDGE_AND_PROVENANCE.md section 7 (pair-level, separate from "
    "disposition)"
)
DATE = "2026-10-26"


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
        if fragment.split("\n")[0] in line:
            start_idx = i
            break
    if start_idx is None:
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
                "task_id": "EXT-004",
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

    # ---- 0001 recursive partitioning ----
    add(
        "OC-ext004-0001",
        "Decision tree as recursive partitioning of the feature space",
        "Semantic Duplicate",
        "Both vaults define a decision tree by the same core claim: it "
        "recursively splits/partitions the feature space and assigns a "
        "prediction per region. Master-ai states it twice (TL;DR and body, "
        "'recursively splits the feature space'); the course states it in "
        "the body and the summary ('recursively partitions the feature "
        "space into regions' / 'recursively splits the feature space into "
        "regions, predicting the majority class (classification) or mean "
        "(regression) in each region'). The course adds what the prediction "
        "is per region (majority class / mean); master-ai's TL;DR adds the "
        "ensemble framing. The duplicated core claim is the recursive "
        "feature-space partitioning itself; the additions are elaboration "
        "around it, not a different claim.",
        [
            R("fc09470c42d8", "A decision tree recursively partitions the feature space into regions, and assigns a prediction to each region."),
            R("bd8919bbf2fc", "A decision tree recursively splits the feature space into regions, predicting the majority class (classification) or mean (regression) in each region"),
            R("7159f6da0ea8", "A decision tree recursively splits the feature space:"),
            R("f9686292a5bb", "Decision trees recursively split feature space."),
        ],
    )

    # ---- 0002 regression-tree criterion ----
    add(
        "OC-ext004-0002",
        "Regression-tree split criterion (target variance / MSE)",
        "Semantic Duplicate",
        "Both vaults give the same regression-tree criterion: split to "
        "reduce the variance of the target in the node, which is MSE "
        "minimization. Master-ai names it compactly ('variance reduction, "
        "MSE' as the regression split criterion, and 'reduces variance (for "
        "regression)' in the training rule); the course states the impurity "
        "is the variance of the target values, gives the variance formula, "
        "and explicitly equates it with minimizing MSE like linear "
        "regression. Same claim; the course supplies the formula and the "
        "MSE-equivalence explanation that master-ai compresses into two "
        "words.",
        [
            R("d5cfd5d3fd1a", "For regression trees, the impurity is the **variance** of the target values in the node:"),
            R("5d97f07f3e7d", "$$\\text{Var}(S) = \\frac{1}{|S|} \\sum_{i \\in S} (y_i - \\bar{y}_S)^2$$"),
            R("a89ed237f729", "This is equivalent to minimizing **MSE** — regression trees minimize MSE, just like linear regression"),
            R("69cee9f5ab21", "or reduces variance (for regression)"),
            R("2a3138f78aa9", "- **Regression**: variance reduction, MSE."),
        ],
    )

    # ---- 0003 stopping criteria ----
    add(
        "OC-ext004-0003",
        "Tree-construction stopping criteria",
        "Semantic Duplicate",
        "Both vaults end recursive tree construction on the same three "
        "conditions: a maximum depth is reached, too few samples remain, "
        "or the node is pure. The course's construction procedure item 5 "
        "('all samples in a node have the same label (pure), or a stopping "
        "criterion is met (max depth, min samples per leaf, etc.)' — 'etc.' "
        "is the source's own word, not an elision here) and master-ai's "
        "'Recursion stops when: max depth reached, too few samples, or "
        "pure node' list the same condition set; only wording and ordering "
        "differ.",
        [
            R("149cb4e9b937", "5. Stop when: all samples in a node have the same label (pure), or a stopping criterion is met (max depth, min samples per leaf, etc.)."),
            R("22f292bb0294", "Recursion stops when: max depth reached, too few samples, or pure node."),
        ],
    )

    # ---- 0004 RF mechanism ----
    add(
        "OC-ext004-0004",
        "Random Forest mechanism (bootstrap training + feature randomness + aggregate)",
        "Semantic Duplicate",
        "Both vaults define Random Forests with the same three-part "
        "mechanism: many trees trained on bootstrap samples of the data, "
        "random feature subsets at splits, then aggregation by averaging "
        "(regression) or majority vote (classification). Master-ai's "
        "one-sentence definition ('Train N decision trees on bootstrap "
        "samples of the data, with random feature subsets at each split. "
        "Average (regression) or majority-vote (classification).') and its "
        "TL;DR ('Random forests average many trees') carry all three parts; "
        "the course carries them across its definition ('averaging many "
        "trees, each trained on a slightly different view of the data'), "
        "the feature-randomness rule ('At each split, the tree is not "
        "allowed to consider all features') and the bagging step list "
        "('Aggregate: for classification, majority vote; for regression, "
        "average'). Same mechanism; the course unpacks it into a four-step "
        "procedure with the ~37% out-of-bag quantification (classified "
        "separately as partial-depth bagging mechanics).",
        [
            R("8baaa5aca519", "**Random Forests** (Breiman, 2001) fix this by **averaging many trees**, each trained on a slightly different view of the data."),
            R("7060e76c4bac", "At each split, the tree is not allowed to consider all features."),
            R("8a5ad1cf132d", "4. **Aggregate:** for classification, majority vote; for regression, average."),
            R("2cf7d3cd250f", "Train $N$ decision trees on bootstrap samples of the data, with random feature subsets at each split. Average (regression) or majority-vote (classification)."),
            R("f9686292a5bb", "Random forests average many trees."),
        ],
    )

    # ---- 0005 averaging reduces variance ----
    add(
        "OC-ext004-0005",
        "Averaging many trees reduces variance without increasing bias",
        "Semantic Duplicate",
        "Near-verbatim duplicated claim: the course says 'The averaging "
        "reduces variance without increasing bias' (and in its "
        "bias-variance decomposition: 'Bias: unchanged ... Variance: "
        "reduced (averaging decorrelated trees)'); master-ai says "
        "'averaging many high-variance, low-bias trees reduces variance "
        "without increasing bias'. Master-ai additionally names the "
        "bias-variance tradeoff concept and links its dedicated note; the "
        "course additionally explains WHY bias is unchanged (each tree is "
        "still an unpruned tree). The shared claim is identical.",
        [
            R("8baaa5aca519", "The averaging reduces variance without increasing bias, producing a model that is more accurate and more stable than any single tree."),
            R("b08466fa2eb4", "- **Variance:** reduced (averaging decorrelated trees)."),
            R("13c25810c708", "**Why it works**: averaging many high-variance, low-bias trees reduces variance without increasing bias."),
        ],
    )

    # ---- 0006 boosting sequential ----
    add(
        "OC-ext004-0006",
        "Gradient boosting trains trees sequentially, each correcting the previous",
        "Semantic Duplicate",
        "Near-verbatim duplicated definition: the course ('train many trees "
        "sequentially, where each tree corrects the errors of the previous "
        "ones'; summary: 'Gradient boosting trains trees sequentially') "
        "and master-ai ('boosting trains trees sequentially, each "
        "correcting the previous one's errors'; TL;DR: 'builds trees "
        "sequentially, each correcting the previous'). The course adds the "
        "weak-learner characterization and the explicit bagging-vs-boosting "
        "contrast ('Random Forests (bagging): train many trees "
        "independently ... averaging reduces the variance' vs 'Bagging: "
        "independent trees, strong learners, reduce variance. / Boosting: "
        "sequential trees, weak learners, reduce bias.'); master-ai adds "
        "the contrast with averaging independent trees. The duplicated "
        "core is the sequential error-correction structure.",
        [
            R("d1f5a04eff99", "**Gradient Boosting:** train many trees **sequentially**, where each tree corrects the errors of the previous ones."),
            R("04314c53363f", "Gradient boosting trains trees **sequentially**"),
            R("70a78aa32e0a", "**Random Forests (bagging):** train many trees **independently** on bootstrap samples, then average."),
            R("d11c38215d07", "- Bagging: independent trees, strong learners, reduce variance."),
            R("6571e98b5c45", "**boosting** trains trees sequentially, each correcting the previous one's errors."),
            R("f9686292a5bb", "builds trees sequentially, each correcting the previous"),
        ],
    )

    # ---- 0007 function space ----
    add(
        "OC-ext004-0007",
        "Boosting as gradient descent in function space (residual = negative gradient)",
        "Semantic Duplicate",
        "Both vaults give the same deep insight: boosting is gradient "
        "descent in function space, where each tree fits the negative "
        "gradient of the loss (the residual for MSE). The course states "
        "the pseudo-residuals are the negative gradient of the loss and "
        "'gradient boosting is gradient descent where each parameter is a "
        "tree'; master-ai states 'residual = negative gradient of MSE' and "
        "'Boosting is functional gradient descent in function space — each "
        "tree takes a step in the direction that reduces the loss'. Same "
        "claim in both; the course generalizes to any differentiable loss "
        "(classified separately as algorithm-generality partial overlap).",
        [
            R("6537002a02fe", "the pseudo-residuals are the negative gradient of the loss with respect to the prediction"),
            R("6e2b25632c13", "**gradient boosting is gradient descent where each \"parameter\" is a tree, and the gradient tells us what tree to add next.**"),
            R("8b7c09a02821", "(residual = negative gradient of MSE)"),
            R("8b7c09a02821", "Boosting is functional gradient descent in function space — each tree takes a step in the direction that reduces the loss."),
        ],
    )

    # ---- 0008 final model formula ----
    add(
        "OC-ext004-0008",
        "Final boosting model as base prediction plus shrunken sum of trees (formula identity)",
        "Semantic Duplicate",
        "Formula-level identity: both vaults write the per-step update and "
        "the final model as F_m = F_{m-1} + nu * (tree) and F_M = F_0 + nu "
        "* sum of trees. Notation differs (course: h_m with an explicit "
        "per-leaf step size gamma; master-ai: T_m with gamma absorbed), "
        "and master-ai uses \\mathbf{x} bolding. Term matching cannot see "
        "this identity (notation equivalence is invisible to word-boundary "
        "matching); the classification rests on the byte-exact formula "
        "evidence, per the EXT-003 precedent for formula-level pairs.",
        [
            R("f5d4a445a43f", "$$F_m(x) = F_{m-1}(x) + \\nu \\cdot \\gamma_{jm} \\cdot h_m(x)$$"),
            R("b753c1a1772b", "The final model is $F_M(x) = F_0(x) + \\nu \\sum_{m=1}^M \\gamma_m h_m(x)$ — a sum of $M$ trees."),
            R("9f96e8d2229d", "Update: $F_m(\\mathbf{x}) = F_{m-1}(\\mathbf{x}) + \\nu \\cdot T_m(\\mathbf{x})$"),
            R("11106098b781", "The final model: $F_M(\\mathbf{x}) = F_0(\\mathbf{x}) + \\nu \\sum_{m=1}^M T_m(\\mathbf{x})$."),
        ],
    )

    # ---- 0009 shallow weak learners ----
    add(
        "OC-ext004-0009",
        "Shallow trees (depth 3-8) as weak learners in boosting",
        "Semantic Duplicate",
        "Both vaults prescribe shallow trees (depth 3-8) for boosting "
        "because each tree is a weak learner and strength comes from "
        "accumulation. The course: 'boosting uses shallow trees (depth "
        "3-8). This is because each tree is a weak learner'; master-ai: "
        "'Shallow (3-8) works best — each tree is weak but they "
        "accumulate' plus the pitfall 'Too-deep trees — high variance. "
        "Keep max_depth in 3-8.' Same recommendation with the same "
        "numeric range and the same weak-learner rationale.",
        [
            R("d1f5a04eff99", "Each tree is a **weak learner** (high bias, low variance — typically a shallow tree)"),
            R("58c2bf3926eb", "boosting uses shallow trees (depth 3–8). This is because each tree is a weak learner"),
            R("fb11dd97fc42", "`max_depth`: per-tree depth. Shallow (3–8) works best — each tree is weak but they accumulate."),
            R("ce70e488dfc4", "**Too-deep trees** — high variance. Keep max_depth in 3–8."),
        ],
    )

    # ---- 0010 LR tradeoff + early stopping ----
    add(
        "OC-ext004-0010",
        "Learning rate / n_estimators tradeoff with early stopping",
        "Semantic Duplicate",
        "Both vaults state the same tuning doctrine: a lower learning rate "
        "with more trees generally generalizes better, and training should "
        "use early stopping. The course: 'lower learning rate with more "
        "trees usually gives better performance ... then lower nu and "
        "increase M with early stopping' and 'the learning rate ... "
        "(typically 0.01-0.1)'; master-ai: 'Lower = needs more trees but "
        "often better generalization. Typical: 0.01-0.1.' and 'Early "
        "stopping is essential — it halts training when validation loss "
        "stops improving'. The course's table gives a wider learning-rate "
        "range (0.01-0.3) than its own prose (0.01-0.1) and master-ai's "
        "0.01-0.1; the prose-level claim is duplicated.",
        [
            R("b54ac788ce22", "**The learning rate / n_estimators tradeoff:** lower learning rate with more trees usually gives better performance (but slower training)."),
            R("b54ac788ce22", "then lower $\\nu$ and increase $M$ with early stopping"),
            R("11e95e63c162", "where $\\nu \\in (0, 1]$ is the **learning rate** (typically 0.01–0.1) that shrinks each tree's contribution."),
            R("fb11dd97fc42", "`learning_rate` ($\\nu$): step size. Lower = needs more trees but often better generalization. Typical: 0.01–0.1."),
            R("2fa41b6feddb", "Early stopping is essential — it halts training when validation loss stops improving, preventing overfitting."),
        ],
    )

    # ---- 0011 SOTA for tabular ----
    add(
        "OC-ext004-0011",
        "Gradient boosted trees as state of the art for tabular data",
        "Semantic Duplicate",
        "Both vaults assert gradient boosting is the state of the art for "
        "tabular/structured data and back it with production/Kaggle "
        "adoption. The course: 'Gradient Boosted Trees are the state of "
        "the art for tabular data' with the three dominant implementations "
        "winning 'most Kaggle competitions on structured data'; master-ai "
        "TL;DR: 'For tabular data, gradient boosting is still SOTA in 2026 "
        "— beating deep learning on most benchmarks' and 'All three are "
        "widely used in production and Kaggle competitions.' Master-ai "
        "adds an era qualifier ('still ... in 2026'); the core claim is "
        "duplicated.",
        [
            R("6798624ebcac", "Gradient Boosted Trees are the **state of the art for tabular data**."),
            R("6798624ebcac", "win most Kaggle competitions on structured data and are the default choice in industry for tabular ML"),
            R("f9686292a5bb", "**For tabular data, gradient boosting is still SOTA in 2026** — beating deep learning on most benchmarks."),
            R("cc0e47dca6fc", "All three are widely used in production and Kaggle competitions."),
        ],
    )

    # ---- 0012 high variance ----
    add(
        "OC-ext004-0012",
        "Single decision trees have high variance (small data changes produce different trees)",
        "Semantic Duplicate",
        "Near-verbatim duplicated claim: the course (weaknesses list: "
        "'High variance: a small change in the data can produce a "
        "completely different tree'; RF file: 'A single decision tree has "
        "high variance — small changes in the training data produce very "
        "different trees') and master-ai ('High variance — small data "
        "changes produce very different trees'). Same claim, near-identical "
        "wording; the course adds the greedy-split mechanism explanation "
        "for why the instability happens.",
        [
            R("30deb1b4da64", "1. **High variance:** a small change in the data can produce a completely different tree."),
            R("0caf2f0156c6", "A single decision tree has high variance — small changes in the training data produce very different trees."),
            R("bc0226d67be7", "- **High variance** — small data changes produce very different trees."),
        ],
    )

    # ---- 0013 cannot extrapolate ----
    add(
        "OC-ext004-0013",
        "Trees cannot extrapolate (constant predictions per leaf)",
        "Semantic Duplicate",
        "Near-verbatim duplicated claim with the same mechanism: "
        "predictions are constant in each leaf, so values outside the "
        "training range cannot be produced. The course (trees: 'Cannot "
        "extrapolate: predictions are constant within each leaf; the tree "
        "cannot predict values outside the training range'; forests: "
        "'like single trees, the forest predicts constant values within "
        "leaves') and master-ai ('Cannot extrapolate (predictions are "
        "constant in each leaf)'). The course extends the claim to "
        "forests; master-ai states it for trees only — an extension, not "
        "a difference.",
        [
            R("30deb1b4da64", "4. **Cannot extrapolate:** predictions are constant within each leaf; the tree cannot predict values outside the training range."),
            R("196a7ae9cca3", "1. **Cannot extrapolate:** like single trees, the forest predicts constant values within leaves."),
            R("bc0226d67be7", "- Cannot extrapolate (predictions are constant in each leaf)."),
        ],
    )

    # ---- 0014 Gini/entropy/IG depth ----
    add(
        "OC-ext004-0014",
        "Splitting-criteria treatment for classification (Gini impurity, entropy, information gain)",
        "Partial Overlap",
        "The overlap is the topic membership: both vaults name Gini "
        "impurity, information gain and entropy as the classification "
        "split criteria. The non-overlapping remainder is depth: the "
        "course derives everything (Gini formula, entropy formula with "
        "log2, information-gain definition, pure/max-impurity boundary "
        "values, probabilistic interpretations, and the practice note that "
        "Gini vs entropy rarely matters and Gini is the scikit-learn "
        "default), while master-ai only lists the names ('Gini impurity, "
        "information gain (entropy)') in two list lines. Master-ai's "
        "list-level reference is fully contained in the course's "
        "treatment; the course's formulas and guidance have no "
        "counterpart.",
        [
            R("c8cc24efb294", "$$\\text{Gini}(S) = 1 - \\sum_{k=1}^K p_k^2$$"),
            R("6d9197be6238", "$$\\text{Entropy}(S) = -\\sum_{k=1}^K p_k \\log_2 p_k$$"),
            R("e9bab6f5e19c", "The impurity reduction from a split is called **Information Gain** (for entropy) or **Gini decrease** (for Gini):"),
            R("262250b1989e", "In practice, they give nearly identical trees. Gini is slightly faster to compute (no logarithm) and is the default in scikit-learn."),
            R("69cee9f5ab21", "Common split criteria:"),
            R("2a3138f78aa9", "- **Classification**: Gini impurity, information gain (entropy)."),
        ],
    )

    # ---- 0015 tree strengths ----
    add(
        "OC-ext004-0015",
        "Decision-tree strengths",
        "Partial Overlap",
        "Four shared strengths, each stated on both sides: "
        "interpretability (course: if-then rules a human can read; "
        "master-ai: trace any prediction through the tree); handling "
        "mixed/categorical-and-numerical features (course: 'Handles mixed "
        "data types'; master-ai: 'Handles categorical and numerical "
        "features naturally'); no feature scaling (course: 'no scaling "
        "needed'; master-ai: 'No feature scaling needed'); and "
        "nonlinearities with interactions (both: 'Captures "
        "non-linearities and interactions' / 'Captures nonlinearities and "
        "interactions'). Course-unique strengths: no distributional "
        "assumptions and robustness to outliers (splits based on order, "
        "not magnitude). Master-ai contributes no unique strength here. "
        "Shared core with a course-only extension, hence partial overlap.",
        [
            R("33cdde124900", "1. **Interpretability:** a tree is a sequence of if-then rules that a human can read."),
            R("33cdde124900", "2. **Handles mixed data types:** numerical and categorical features, no scaling needed."),
            R("33cdde124900", "5. **Robust to outliers:** splits are based on order, not magnitude."),
            R("0164e3b62daf", "- Interpretable — you can trace any prediction through the tree."),
            R("0164e3b62daf", "- No feature scaling needed."),
            R("0164e3b62daf", "- Captures nonlinearities and interactions."),
        ],
    )

    # ---- 0016 bagging mechanics ----
    add(
        "OC-ext004-0016",
        "Bagging mechanics (bootstrap aggregating procedure)",
        "Partial Overlap",
        "Both vaults invoke bootstrap sampling as the bagging mechanism, "
        "but at different depths. Master-ai references 'bootstrap samples "
        "of the data' in one clause of its Random Forest definition "
        "without defining bootstrap; the course defines the full procedure "
        "(draw a random sample of size n with replacement; ~37% left "
        "out-of-bag; train unpruned trees for low bias; repeat B times, "
        "typically 100-1000) and quantifies the variance effect "
        "(sigma^2/B for independent models, less in practice). The shared "
        "part is the bootstrap-sample reference; the procedure detail, "
        "OOB quantification and unpruned-trees rationale are "
        "course-unique.",
        [
            R("516929e868b2", "The core technique is **bagging** (Bootstrap Aggregating):"),
            R("8a5ad1cf132d", "1. **Bootstrap sample:** draw a random sample of size $n$ from the training data **with replacement**."),
            R("a7f032135db8", "averaging $B$ **independent** models with variance $\\sigma^2$ each reduces the variance to $\\sigma^2 / B$"),
            R("2cf7d3cd250f", "Train $N$ decision trees on bootstrap samples of the data"),
        ],
    )

    # ---- 0017 feature randomness ----
    add(
        "OC-ext004-0017",
        "Feature randomness at splits (random feature subsets)",
        "Partial Overlap",
        "Both vaults include random feature subsets at each split as part "
        "of Random Forests. Master-ai mentions it as one clause ('with "
        "random feature subsets at each split'); the course explains the "
        "mechanism and its purpose — trees consider only a random subset "
        "of features per split (typically sqrt(d) for classification, d/3 "
        "for regression), forcing different trees to split on different "
        "features and thereby decorrelating them. Shared mechanism "
        "reference; quantified defaults and the decorrelation rationale "
        "are course-unique.",
        [
            R("7060e76c4bac", "it considers only a **random subset** of features (typically $\\sqrt{d}$ for classification, $d/3$ for regression"),
            R("adee87baa95a", "This forces different trees to split on different features, decorrelating them."),
            R("2cf7d3cd250f", "with random feature subsets at each split"),
        ],
    )

    # ---- 0018 GBM algorithm generality ----
    add(
        "OC-ext004-0018",
        "Gradient boosting algorithm steps (residual fitting; general loss vs MSE special case)",
        "Partial Overlap",
        "Both vaults present the same algorithm skeleton: initialize with "
        "a constant F_0 (mean of y), iteratively compute residuals of the "
        "current prediction, fit a tree to them, update with a learning "
        "rate. The non-overlapping remainder is generality and step size: "
        "the course computes pseudo-residuals as the negative gradient of "
        "a general loss L (with the MSE special case called out: 'For MSE "
        "loss, this is just r_i = y_i - F_{m-1}(x_i) — the ordinary "
        "residual') and adds a per-leaf optimal step size gamma; "
        "master-ai's loop is the MSE-only special case (plain residuals) "
        "with no per-leaf gamma. Master-ai's steps are contained in the "
        "course's general formulation; the general-loss form and the "
        "gamma step are course-unique depth.",
        [
            R("0953e25545a6", "Initialize the prediction $F_0(x)$ as a constant (the mean for regression, the log-odds for classification)."),
            R("b30204f3bd85", "1. **Compute the pseudo-residuals:** for each sample $i$, compute the negative gradient of the loss with respect to the current prediction:"),
            R("dc6e19706994", "$$r_i = -\\frac{\\partial L(y_i, F_{m-1}(x_i))}{\\partial F_{m-1}(x_i)}$$"),
            R("0c0eb817964f", "For MSE loss, this is just $r_i = y_i - F_{m-1}(x_i)$ — the ordinary residual."),
            R("ff1b68d26f4f", "3. **Find the optimal step size:** for each leaf of $h_m$, find the value $\\gamma$ that minimizes the loss when added to the current prediction:"),
            R("9f96e8d2229d", "1. Start with a constant prediction $F_0(\\mathbf{x})$ (e.g., mean of $y$)."),
            R("9f96e8d2229d", "- Compute residuals $r_i = y_i - F_{m-1}(\\mathbf{x}_i)$."),
            R("9f96e8d2229d", "- Train a tree $T_m$ to predict the residuals."),
        ],
    )

    # ---- 0019 hyperparameters ----
    add(
        "OC-ext004-0019",
        "Gradient boosting hyperparameters",
        "Partial Overlap",
        "Both vaults list substantially the same hyperparameter set: "
        "n_estimators (number of trees), learning_rate, max_depth, "
        "subsample, colsample_bytree and regularization "
        "(min_child_weight; L1/L2 via reg_alpha/reg_lambda on the course "
        "side, L1/L2 + gamma on the master-ai side), and both carry the "
        "stochastic-sampling idea (course: 'Stochastic gradient boosting: "
        "using subsample < 1 and colsample_bytree < 1 ... decorrelates the "
        "trees and improves generalization'; master-ai compressed: "
        "'subsample: fraction of data per tree (adds randomness, like "
        "bagging)'). The non-overlapping remainder: the course presents a "
        "table with typical ranges (n_estimators 100-10000, "
        "learning_rate 0.01-0.3, max_depth 3-8, min_child_weight 1-10, "
        "reg 0-10) plus the learning-rate/n_estimators tradeoff; master-ai "
        "adds the effect-direction notes ('More = lower bias, higher "
        "variance') and gamma. Shared parameter set with different "
        "elaborations on each side.",
        [
            R("93410dbc12d8", "| `n_estimators` ($M$) | Number of trees | 100–10000 |"),
            R("93410dbc12d8", "| `learning_rate` ($\\nu$) | Shrinkage per tree | 0.01–0.3 |"),
            R("93410dbc12d8", "| `reg_alpha`, `reg_lambda` | L1/L2 regularization | 0–10 |"),
            R("fb11dd97fc42", "- `n_estimators` (M): number of trees. More = lower bias, higher variance."),
            R("fb11dd97fc42", "- `subsample`: fraction of data per tree (adds randomness, like bagging)."),
            R("fb11dd97fc42", "- Regularization: L1, L2, min_child_weight, gamma."),
        ],
    )

    # ---- 0020 XGBoost innovations ----
    add(
        "OC-ext004-0020",
        "XGBoost innovations",
        "Partial Overlap",
        "Both vaults describe XGBoost as the original major gradient "
        "boosting library and credit the same three innovations: "
        "regularization, second-order gradients and missing-value "
        "handling. Master-ai's one line ('the original; introduced "
        "regularization, second-order gradients, handling of missing "
        "values') is contained in the course's five-item list (regularized "
        "learning objective with explicit L1/L2 on tree weights; "
        "second-order gradients using gradient and Hessian; "
        "sparsity-aware missing-value/sparse handling; approximate "
        "histogram-based split finding; system optimization: cache-aware, "
        "out-of-core, parallelization). The course also dates its "
        "dominance era ('dominant library from 2016 to 2019'); the "
        "origin-year discrepancy is classified separately "
        "(OC-ext004-0027).",
        [
            R("914b4252a732", "The original major gradient boosting library. Key innovations:"),
            R("62e88755554f", "- **Regularized learning objective:** explicit L1/L2 regularization on the tree weights."),
            R("62e88755554f", "- **Second-order gradients:** uses both the gradient and the Hessian (second derivative) of the loss, for better split decisions."),
            R("62e88755554f", "- **Sparsity-aware:** handles missing values and sparse features natively."),
            R("4cd275d4b9d3", "**XGBoost** (2014) — the original; introduced regularization, second-order gradients, handling of missing values."),
        ],
    )

    # ---- 0021 LightGBM innovations ----
    add(
        "OC-ext004-0021",
        "LightGBM innovations",
        "Partial Overlap",
        "Both vaults identify LightGBM as Microsoft's speed-focused "
        "implementation using histogram-based splitting and being faster on "
        "large data. Master-ai's line ('LightGBM (2017) — Microsoft; "
        "histogram-based splits, faster on large data') is contained in the "
        "course's four-innovation treatment (histogram-based splitting with "
        "the O(n*d) -> O(bins*d) cost reduction; leaf-wise growth and its "
        "overfitting caveat; Gradient-based One-Side Sampling; Exclusive "
        "Feature Bundling) plus the 3-10x-faster quantification. Shared "
        "identity and headline innovation; the mechanism details are "
        "course-unique.",
        [
            R("45ca52f1b3cf", "Microsoft's implementation, focused on **speed and memory efficiency**. Key innovations:"),
            R("4965cb0914cb", "- **Histogram-based splitting:** bins continuous features into histograms, reducing split-finding cost from $O(n \\cdot d)$ to $O(\\text{bins} \\cdot d)$."),
            R("4965cb0914cb", "- **Leaf-wise growth:** grows trees leaf-by-leaf (the leaf with the highest delta loss) rather than level-by-level."),
            R("458555b63b32", "LightGBM is typically 3–10× faster than XGBoost with similar accuracy, making it the default for large datasets."),
            R("4cd275d4b9d3", "**LightGBM** (2017) — Microsoft; histogram-based splits, faster on large data."),
        ],
    )

    # ---- 0022 CatBoost innovations ----
    add(
        "OC-ext004-0022",
        "CatBoost innovations",
        "Partial Overlap",
        "Both vaults position CatBoost (Yandex) as the categorical-focused "
        "implementation with native categorical handling that removes "
        "one-hot encoding. Master-ai's line ('handles categorical features "
        "natively, often best out-of-the-box' plus the production note "
        "'CatBoost saves you from one-hot encoding headaches') is contained "
        "in the course's three-innovation treatment (target-statistics "
        "encoding with ordering to avoid leakage; ordered boosting reducing "
        "prediction shift; symmetric trees for fast inference). Shared "
        "positioning and native-categorical claim; the three mechanisms are "
        "course-unique. Year note (context, not classified evidence): "
        "master-ai dates CatBoost 2018; the course section heading dates it "
        "(Yandex, 2017), but headings are outside KU excerpts, so the year "
        "difference is recorded here for synthesis-time reconciliation, "
        "mirroring the XGBoost era-dating classification OC-ext004-0027 "
        "which does have excerpt evidence on both sides.",
        [
            R("c67f964952f3", "Focused on **categorical features**. Key innovations:"),
            R("06afc9a45b58", "- **Native categorical handling:** encodes categoricals using target statistics (with careful ordering to avoid leakage), eliminating the need for one-hot encoding."),
            R("06afc9a45b58", "- **Ordered boosting:** each tree is trained on residuals computed from a model that did not see that sample, reducing the prediction shift"),
            R("06afc9a45b58", "- **Symmetric trees:** all nodes at the same depth use the same split condition, making inference very fast (a single comparison per level)."),
            R("4cd275d4b9d3", "**CatBoost** (2018) — Yandex; handles categorical features natively, often best out-of-the-box."),
            R("e60459699db7", "**CatBoost for categorical features** — if your data has many categoricals, CatBoost saves you from one-hot encoding headaches."),
        ],
    )

    # ---- 0023 GBT vs DL on tabular ----
    add(
        "OC-ext004-0023",
        "Why gradient boosting beats deep learning on tabular data",
        "Partial Overlap",
        "The shared part is the adoption claim: gradient boosting is the "
        "right default for tabular data while deep learning dominates "
        "unstructured data (images, text, audio) and very large datasets. "
        "Both vaults make it (course: use GBT when the data is tabular; "
        "unstructured means neural networks; master-ai: deep learning "
        "dominates unstructured data and very large tabular datasets; for "
        "typical enterprise tabular data, gradient boosting is the right "
        "choice). The non-overlapping remainder: master-ai supplies the "
        "empirical basis and five mechanistic reasons (Grinsztajn et al. "
        "2022; irregular target functions/non-smooth features; no feature "
        "scaling; implicit feature selection; robustness to irrelevant "
        "features; smaller data regimes), while the course supplies the "
        "data-size thresholds (1000+ samples to use GBT, <100 to avoid) "
        "and the implementation-choice guidance.",
        [
            R("6798624ebcac", "Gradient Boosted Trees are the **state of the art for tabular data**."),
            R("da70383725dc", "- The data is tabular (structured)."),
            R("fcd4069ba7d2", "- The data is unstructured (images, text, audio) — use neural networks."),
            R("a36bf0fd301a", "Empirical studies (e.g., Grinsztajn et al. 2022) consistently show tree-based models beat deep learning on tabular data. Reasons:"),
            R("1bae66000393", "1. **Trees handle irregular target functions and non-smooth features** naturally. Neural networks assume some smoothness."),
            R("1bae66000393", "2. **No feature scaling needed**. Neural networks are sensitive to feature scale."),
            R("183b47187d21", "Deep learning dominates **unstructured data** (text, images, audio) and **very large tabular datasets** (millions of rows)."),
        ],
    )

    # ---- 0024 feature importance caveats ----
    add(
        "OC-ext004-0024",
        "Feature importance and its caveats",
        "Partial Overlap",
        "Both vaults treat feature importance as a tree-model capability "
        "that must be used with care, but with different caveats. The "
        "shared part: feature importance exists as a natural byproduct of "
        "tree training. The course defines the impurity-reduction "
        "aggregation, warns that impurity-based importance is biased "
        "toward high-cardinality features and prescribes permutation "
        "importance for an unbiased measure; master-ai warns against "
        "treating importance as causation ('it's not. SHAP is closer but "
        "still correlational') and lists feature importance together with "
        "SHAP values and tree traces under interpretability. Same topic "
        "and same 'handle with care' stance; the specific caveats "
        "(statistical bias vs causal inference) and remedies (permutation "
        "importance vs SHAP) differ per side.",
        [
            R("cb224d6f8b47", "Random Forests provide a natural **feature importance** measure: for each feature, sum the impurity reduction across all splits that use that feature, averaged over all trees."),
            R("d78f2e2924d8", "> [!WARNING] Impurity-based importance is biased toward high-cardinality features."),
            R("d78f2e2924d8", "Use **permutation importance** (shuffle each feature and measure the accuracy drop) for an unbiased measure."),
            R("ce70e488dfc4", "- **Treating \"feature importance\" as causation** — it's not. SHAP is closer but still correlational."),
            R("beedefedd83d", "**Interpretability**: tree-based models offer feature importance, SHAP values, individual tree traces."),
        ],
    )

    # ---- 0025 ASCII tree example ----
    add(
        "OC-ext004-0025",
        "Worked customer-purchase decision-tree example",
        "Partial Overlap",
        "Both vaults teach the tree structure with an ASCII example of a "
        "customer-purchase prediction: an age test at the root, an income "
        "test below one branch, and buy/not-buy outcomes at the leaves. "
        "The shared pedagogical device and domain (will-the-customer-buy "
        "with age and income thresholds) overlap; the specifics differ per "
        "side: the course uses Age > 30? / Income > 50K? with probability "
        "leaves (Buy = Yes (85%), Buy = No (70%), Buy = No (90%)), while "
        "master-ai uses age > 35? / income > 60k? with a third feature "
        "(student?) and categorical leaves (buy/hold/sell). Neither "
        "example contains the other; they are sibling illustrations of "
        "the same concept.",
        [
            R("992d303d5293", "**Example:** a tree for predicting \"will the customer buy?\" might be:"),
            R("35bafb2a9336", "Age > 30?"),
            R("35bafb2a9336", "Buy = Yes (85%)"),
            R("6a24268005b4", "age > 35?"),
            R("6a24268005b4", "income > 60k?"),
        ],
    )

    # ---- 0026 RF math formalization ----
    add(
        "OC-ext004-0026",
        "Random Forest mathematical formalization (ensemble formula vs variance analysis)",
        "Complementary Content",
        "Related but non-overlapping mathematical treatments of Random "
        "Forest averaging. Master-ai formalizes the estimator itself (the "
        "ensemble-average formula f-hat_RF(x) = (1/N) sum_i T_i(x)); the "
        "course formalizes the variance effect (averaging B independent "
        "models of variance sigma^2 each reduces variance to sigma^2/B, "
        "with the caveat that correlated trees achieve less). Neither "
        "unit contains the other's claim: one defines the model, the "
        "other analyzes its variance. Both are needed for a complete "
        "treatment — the definition and the analysis — hence "
        "complementary content rather than partial overlap.",
        [
            R("7f0636ae66d8", "\\hat{f}_{\\text{RF}}(\\mathbf{x}) = \\frac{1}{N} \\sum_{i=1}^{N} T_i(\\mathbf{x})"),
            R("a7f032135db8", "averaging $B$ **independent** models with variance $\\sigma^2$ each reduces the variance to $\\sigma^2 / B$"),
            R("a7f032135db8", "so the reduction is less than $\\sigma^2 / B$ — but still substantial"),
        ],
    )

    # ---- 0027 XGBoost era dating ----
    add(
        "OC-ext004-0027",
        "XGBoost era dating (2014 vs 2016)",
        "Conflict or Historical Difference",
        "The two vaults (and master-ai internally) date XGBoost "
        "differently, and the difference is a genuine historical "
        "distinction rather than an error on one side: master-ai's "
        "implementation list says 'XGBoost (2014)' while its own Further "
        "Reading cites 'Chen & Guestrin (2016), XGBoost: A Scalable Tree "
        "Boosting System'; the course frames XGBoost as 'the dominant "
        "library from 2016 to 2019'. Historically, both dates label real "
        "events: the XGBoost library was first released in March 2014 "
        "(master-ai's '(2014)' plausibly refers to the library), while "
        "the paper by Chen & Guestrin is arXiv:1603.02754 (submitted "
        "March 2016) and was published at KDD 2016 — so master-ai mixes "
        "a library-release year with a paper-publication year without "
        "distinguishing them (internally inconsistent within one note). "
        "Synthesis must reconcile explicitly — recommended: cite Chen & "
        "Guestrin (2016, KDD; arXiv March 2016; library first released "
        "2014) — rather than silently picking one vault's year. "
        "Term-evidence note: the course's section heading also dates the "
        "library '(Chen and Guestrin, 2016)', but headings are outside "
        "KU excerpts, so the course-side evidence here is the "
        "dominance-era claim.",
        [
            R("4cd275d4b9d3", "**XGBoost** (2014) — the original; introduced regularization, second-order gradients, handling of missing values."),
            R("95e4ec08ef9b", "Chen & Guestrin (2016), *XGBoost: A Scalable Tree Boosting System*."),
            R("a78451b5ab75", "XGBoost was the dominant library from 2016 to 2019 and remains widely used."),
        ],
    )

    # ---- 0028 RF strengths / baseline ----
    add(
        "OC-ext004-0028",
        "Random Forest as a strong, low-tuning baseline for tabular data",
        "Partial Overlap",
        "Both vaults make the same claim cluster: Random Forests are "
        "robust, need little/minimal tuning, and are the strong "
        "default/baseline to try first on tabular data. The course "
        "('Strong default: works well out-of-the-box with minimal tuning. "
        "Often the first algorithm to try on tabular data'; summary: 'a "
        "strong default for tabular data — minimal tuning, robust, "
        "parallelizable'; and the weaknesses-item framing that RFs are "
        "the \"strong baseline\" while boosting is the \"state of the "
        "art\") and master-ai ('Random forests are robust, fast, and "
        "need little tuning. They're a great baseline for tabular "
        "data.') overlap on robustness, low tuning and the "
        "strong-baseline positioning. Non-shared remainder: the course "
        "adds parallelizability, the first-algorithm-to-try advice and "
        "the boosting-is-more-accurate comparison; master-ai adds speed. "
        "Added during EXT-004 review repairs (coverage gap identified by "
        "EXT-004-REVIEW Check 5: master-ai's baseline line participated "
        "in no other record).",
        [
            R("db11fc059424eabb", "1. **Strong default:** works well out-of-the-box with minimal tuning. Often the first algorithm to try on tabular data."),
            R("ffe5b19a4e9b1727", "5. Random Forests are a strong default for tabular data — minimal tuning, robust, parallelizable."),
            R("ffe5b19a4e9b1727", "6. They are typically less accurate than gradient boosting but easier to use and harder to mess up."),
            R("db4d196a7ae9cca3", "RFs are the \"strong baseline\"; boosting is the \"state of the art.\""),
            R("a3dac7cc037901e0", "Random forests are robust, fast, and need little tuning. They're a great baseline for tabular data."),
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
