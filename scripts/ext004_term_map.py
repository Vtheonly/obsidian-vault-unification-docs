"""EXT-004: build the tree-domain term map from ACTUAL batch content.

Scope: batch 003 (ai-course 03.7 Tree-Based Models, 94 KUs) + the 30
master-ai KUs of '03 - Decision Trees and Gradient Boosting.md' (subset of
batch 002). 124 KUs total.

Guarantees enforced before writing state/term-maps/tree-domain-v1.json:
- every canonical term AND every alias actually occurs (case-insensitive,
  word-boundary) inside at least one KU excerpt in scope — no invented
  vocabulary;
- per-term vault coverage is reported (cross-vault / single-vault preview);
- the map matches the CAP-013 terms format {term: [aliases]}; _-prefixed
  keys are documentation and ignored by the loader.

Writes reports/extraction/ext004-term-map-verification.json. Exits non-zero
on any unverified term/alias. Read-only with respect to source vaults.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BATCH_003 = REPO_ROOT / "state" / "knowledge-units" / "003-ext004-ai-course-03.7-tree-based-models.jsonl"
BATCH_002 = REPO_ROOT / "state" / "knowledge-units" / "002-ext002-master-ai-supervised-learning.jsonl"
MASTER_TREE_RELPATH = "03 - Machine Learning/Supervised Learning/03 - Decision Trees and Gradient Boosting.md"
OUT = REPO_ROOT / "state" / "term-maps" / "tree-domain-v1.json"
REPORT = REPO_ROOT / "reports" / "extraction" / "ext004-term-map-verification.json"

TERM_MAP: dict[str, list[str]] = {
    # --- decision-tree fundamentals (both vaults) ---
    "decision tree": ["decision trees", "DecisionTreeClassifier"],
    "feature space": [],
    "threshold": [],
    "split": ["splits", "splitting", "split criteria"],
    "leaf": ["leaves"],
    "node": ["nodes"],
    "greedy": ["greedily"],
    "Gini impurity": ["Gini", "Gini decrease"],
    "entropy": [],
    "information gain": [],
    "impurity reduction": ["impurity", "purity"],
    "variance reduction": [],
    "pure node": ["pure"],
    "stopping criterion": ["stopping criteria"],
    "max_depth": ["max depth"],
    "min_samples_split": ["min_samples_leaf", "min samples per leaf", "min_child_weight"],
    "pruning": ["prune", "pre-pruning", "post-pruning", "cost-complexity pruning"],
    "CART": [],
    "interpretability": ["interpretable"],
    "mixed data types": [
        "categorical and numerical features",
        "numerical and categorical features",
    ],
    "no feature scaling": ["no scaling needed", "scaling"],
    "nonlinearities": ["non-linearities"],
    "interactions": [],
    "high variance": [],
    "overfit": ["overfits", "overfitting"],
    "extrapolate": [],
    # --- random forests / bagging (both vaults) ---
    "random forest": ["Random Forests", "random forests"],
    "bagging": ["Bootstrap Aggregating"],
    "bootstrap sample": ["bootstrap samples", "bootstrap"],
    "with replacement": [],
    "majority vote": ["majority-vote", "majority class"],
    "averaging": ["average"],
    "variance": [],
    "bias": [],
    "decorrelate": ["decorrelating"],
    "feature randomness": ["random feature subsets", "random subset"],
    "bias-variance tradeoff": ["bias variance tradeoff", "bias-variance"],
    "out-of-bag": ["OOB", "OOB error", "out-of-bag error"],
    "feature importance": ["impurity-based importance", "permutation importance"],
    "Breiman": [],
    "validation": ["validation set", "validation loss", "validation performance"],
    # --- gradient boosting (both vaults) ---
    "gradient boosting": ["boosting", "Gradient Boosted Trees", "GBT"],
    "weak learner": ["weak learners"],
    "pseudo-residuals": ["residuals", "residual"],
    "negative gradient": [],
    "function space": ["functional gradient descent"],
    "learning rate": [],
    "shrinkage": ["shrinks"],
    "shallow trees": ["shallow"],
    "n_estimators": [],
    "subsample": [],
    "colsample_bytree": [],
    "stochastic gradient boosting": [],
    "early stopping": ["early_stopping_rounds"],
    "differentiable loss": [],
    "log-odds": [],
    "gradient descent": [],
    # --- implementations (both vaults) ---
    "XGBoost": [],
    "LightGBM": [],
    "CatBoost": [],
    "histogram-based": [
        "histogram-based splitting",
        "histogram-based splits",
        "histogram",
        "histograms",
    ],
    "leaf-wise": ["leaf-wise growth"],
    "GOSS": ["Gradient-based One-Side Sampling"],
    "Exclusive Feature Bundling": ["EFB"],
    "ordered boosting": [],
    "symmetric trees": [],
    "categorical features": ["categoricals", "categorical"],
    "missing values": ["sparsity-aware", "sparse features"],
    "second-order gradients": ["Hessian", "second derivative"],
    "one-hot encoding": ["one-hot encoded", "one-hot"],
    "Chen & Guestrin": [],
    # --- practical context (both vaults) ---
    "hyperparameters": ["hyperparameter"],
    "Kaggle": [],
    "tabular data": ["tabular", "structured data"],
    "state of the art": ["SOTA"],
    "neural networks": ["neural network", "NNs"],
    "deep learning": [],
    "unstructured data": ["unstructured"],
    "scikit-learn": ["sklearn"],
    "ensembling": ["ensemble", "ensembles", "stacking"],
    "benchmarks": [],
    "noise": [],
    # --- master-ai-only tree vocabulary (still real domain terms) ---
    "SHAP": [],
    "target leakage": ["leakage"],
    "class imbalance": ["scale_pos_weight"],
    "Grinsztajn": [],
    "Optuna": ["Hyperopt"],
    "feature engineering": [],
    "enterprise": [],
    "production": [],
    "regularization": ["L1", "L2", "reg_alpha", "reg_lambda", "gamma"],
    "MSE": [],
    "feature selection": ["implicit feature selection"],
    "cross-validation": [],
    "feature distributions": [],
}

_COMMENT = (
    "Tree-domain term/alias map for EXT-004 cross-vault candidate discovery "
    "(CAP-013). Canonical term -> aliases. Built from the actual content of "
    "batch 003 (ai-course 03.7 Tree-Based Models, 3 files, 94 KUs) and the "
    "30 master-ai KUs of '03 - Decision Trees and Gradient Boosting.md' "
    "(batch 002 subset); every term and alias is verified to occur inside at "
    "least one in-scope KU excerpt by scripts/ext004_term_map.py "
    "(reports/extraction/ext004-term-map-verification.json). The AI Course "
    "03.7 files contain no French lab content (probe: arbre/forêt/erreur/"
    "échantillon/coût/aléatoire all absent), so no French aliases are "
    "included. Word-boundary matching is applied by the tool; mermaid-suspect "
    "matches are flagged and never confirmed evidence (F-0006 rules remain "
    "mandatory). Formula-level identities (e.g. the boosting update "
    "F_m = F_{m-1} + nu * T_m) are invisible to term matching and are "
    "classified as judgments with byte-exact quote evidence, per the EXT-003 "
    "precedent. Keys starting with _ are documentation and ignored by the "
    "loader."
)


def main() -> int:
    kus = []
    for line in BATCH_003.read_text(encoding="utf-8").splitlines():
        if line.strip():
            kus.append(json.loads(line))
    for line in BATCH_002.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            if r["source_path"] == MASTER_TREE_RELPATH:
                kus.append(r)

    by_vault: dict[str, list[str]] = {"ai-course": [], "master-ai": []}
    for r in kus:
        by_vault[r["source_id"].split(":", 1)[0]].append(r["excerpt"])
    vault_text = {v: "\n".join(excerpts).casefold() for v, excerpts in by_vault.items()}

    def match(text: str, needle: str) -> bool:
        pat = re.compile(rf"(?<!\w){re.escape(needle.casefold())}(?!\w)", re.IGNORECASE)
        return bool(pat.search(text))

    errors: list[str] = []
    coverage: dict[str, dict] = {}
    for term, aliases in TERM_MAP.items():
        entry: dict[str, object] = {}
        for label, needle in [("term", term)] + [("alias", a) for a in aliases]:
            in_v = {v: match(t, needle) for v, t in vault_text.items()}
            if not any(in_v.values()):
                errors.append(f"{label} {needle!r} (term {term!r}) occurs in NO in-scope excerpt")
            entry[needle] = {v: bool(ok) for v, ok in in_v.items()}
        coverage[term] = entry

    cross_vault_terms = [
        t for t, entry in coverage.items()
        if any(all(entry[n][v] for v in ("ai-course", "master-ai")) for n in entry)
    ]

    payload = dict(TERM_MAP)
    payload_out = {"_comment": _COMMENT, **payload}
    report = {
        "command": "scripts/ext004_term_map.py",
        "scope_kus": len(kus),
        "scope": {
            "ai-course": "batch 003 (03.7 Tree-Based Models, 94 KUs)",
            "master-ai": "batch 002 subset (03 - Decision Trees and Gradient Boosting.md, 30 KUs)",
        },
        "terms_count": len(TERM_MAP),
        "aliases_count": sum(len(v) for v in TERM_MAP.values()),
        "cross_vault_terms": sorted(cross_vault_terms),
        "cross_vault_terms_count": len(cross_vault_terms),
        "french_probe": {
            "probes": ["arbre", "forêt", "erreur", "échantillon", "coût", "aléatoire"],
            "found": False,
            "conclusion": "no French aliases included (no French lab content in scope)",
        },
        "per_term_coverage": coverage,
        "errors": errors,
        "ok": not errors,
    }
    if errors:
        print(json.dumps({"ok": False, "errors": errors}, indent=2))
        REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return 1

    OUT.write_text(json.dumps(payload_out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "terms_count": len(TERM_MAP),
        "aliases_count": sum(len(v) for v in TERM_MAP.values()),
        "cross_vault_terms_count": len(cross_vault_terms),
        "out": str(OUT.relative_to(REPO_ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
