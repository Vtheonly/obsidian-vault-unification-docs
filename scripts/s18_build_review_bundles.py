#!/usr/bin/env python3
"""DISC-002 session 18: build Tier C review bundles (per domain, per (file,term)
combo with per-KU evidence) for subagent review.

Inputs:
  scratch/s18-tiers-<domain>.jsonl        (tier assignments from s18_dext_tiering)
  state/knowledge-units/012..070 regen batches (KU excerpts by ku_id)
  state/dossiers/<domain>-v1.json         (original concept labels for the rubric)

Outputs:
  scratch/s18-review/<domain>-bundle.json  (pretty JSON; one entry per
    (file, term) combo, each listing the undecided KUs with excerpt evidence)
  scratch/s18-review/<domain>-manifest.json (combo + KU-verdict counts)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "scratch" / "s18-review"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FNAME = {"regression": "regression", "tree-based": "tree", "evaluation": "evaluation",
         "clustering": "clustering", "generalization": "generalization",
         "training-stability": "training-stability"}

DOMAIN_SCOPE = {
    "regression": ("linear and logistic regression: model forms, cost/loss functions "
                   "(MSE, MAE, log loss), normal equations/OLS, gradient descent for "
                   "regression, convexity, feature scaling, sigmoid/softmax, decision "
                   "boundaries, log-odds, maximum likelihood and MAP estimation, "
                   "Bayesian linear regression, ridge/lasso/regularization for "
                   "regression, multicollinearity, class imbalance handling, R^2 and "
                   "regression metrics, polynomial/non-linear regression, sklearn "
                   "linear-model workflow"),
    "tree-based": ("decision trees, random forests, bagging, gradient boosting, XGBoost/"
                   "LightGBM/CatBoost: splitting criteria (Gini, entropy, information "
                   "gain), tree construction, pruning, bias-variance behavior of trees, "
                   "boosting mechanics (pseudo-residuals, shrinkage, second-order "
                   "gradients), categorical-feature and missing-value handling, "
                   "histogram/leaf-wise growth, tabular-data practice and benchmarks"),
    "evaluation": ("model-evaluation metrics and methodology: accuracy, precision, "
                   "recall, F-family, confusion matrix, ROC/AUC/PR-AUC, threshold and "
                   "sensitivity/specificity, macro/micro/weighted averaging, imbalanced-"
                   "classification examples, log loss/cross-entropy, calibration and "
                   "reliability, regression metrics (MSE/MAE/RMSE/R^2/MAPE/Huber), "
                   "ranking metrics (NDCG/MRR/mAP/hit rate), CV metrics (IoU/Dice), "
                   "clustering metrics (silhouette, Davies-Bouldin, ARI, NMI), "
                   "train/val/test methodology, leakage, cost-sensitive evaluation"),
    "clustering": ("clustering and dimensionality reduction: K-means, centroids, "
                   "inertia, elbow method, DBSCAN, hierarchical clustering, "
                   "dendrograms, PCA/variance/covariance/eigendecomposition/SVD, "
                   "t-SNE/UMAP/manifold learning, kernel PCA, autoencoders for "
                   "dimensionality reduction, curse of dimensionality, choosing k, "
                   "silhouette and cluster validation"),
    "generalization": ("generalization and regularization: bias-variance tradeoff, "
                       "overfitting/underfitting, model complexity and capacity, "
                       "learning curves, double descent, L1/L2/ridge/elastic net, "
                       "weight decay, dropout and its variants, early stopping, data "
                       "augmentation, label smoothing, batch normalization effects on "
                       "generalization, covariate shift, ensembling for variance "
                       "reduction"),
    "training-stability": ("weight initialization and training stability: Xavier/He "
                           "schemes, fan_in/fan_out, symmetry breaking, vanishing/"
                           "exploding gradients, gradient flow, saturation of "
                           "activations, dying ReLU, skip connections, normalization "
                           "layers for stability, gradient clipping/norm monitoring, "
                           "loss spikes, NaN debugging, warmup, numerical stability, "
                           "FP16, LoRA/MuP/Fixup initialization"),
}


def load_jsonl(path: Path) -> list[dict]:
    out = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                out.append(json.loads(line))
    return out


def build_ku_index() -> dict[str, dict]:
    idx: dict[str, dict] = {}
    for p in sorted((REPO / "state" / "knowledge-units").glob("0[1-7][0-9]-regen001-*.jsonl")):
        for r in load_jsonl(p):
            idx[r["knowledge_unit_id"]] = {
                "excerpt": r.get("excerpt", ""),
                "heading_path": r.get("heading_path", []),
                "unit_type": r.get("unit_type", ""),
                "source_lines": r.get("source_lines", []),
            }
    return idx


def main() -> int:
    ku_index = build_ku_index()
    print(f"KU index: {len(ku_index)} KUs from regen batches")
    grand_combos = grand_kus = 0
    for domain, fn in FNAME.items():
        tiers = load_jsonl(REPO / "scratch" / f"s18-tiers-{fn}.jsonl")
        dossier = json.loads((REPO / "state" / "dossiers" / f"{domain}-v1.json").read_text())
        concept_labels = [c["label"] for c in dossier["concepts"]]

        # collect undecided (file, term) combos with their KUs and match evidence
        combos: dict[tuple[str, str], dict] = {}
        pair_ref: dict[tuple[str, str], list[str]] = {}
        for p in tiers:
            if p["tier"] != "C":
                continue
            for side in ("side_a", "side_b"):
                s = p[side]
                if s["verdict"] != "undecided":
                    continue
                key = (s["source_path"], p["topic"])
                entry = combos.setdefault(key, {
                    "domain": domain, "file": s["source_path"], "vault": s["vault"],
                    "term": p["topic"], "pair_kind": None, "kus": {}})
                entry["vault"] = s["vault"]
                kid = s["ku_id"]
                ku = entry["kus"].setdefault(kid, {
                    "ku_id": kid, "heading_path": [], "unit_type": "",
                    "source_lines": [], "excerpt": "", "matches": []})
                ku_rec = ku_index.get(kid, {})
                ku["heading_path"] = ku_rec.get("heading_path", s.get("heading_path", []))
                ku["unit_type"] = ku_rec.get("unit_type", "")
                ku["source_lines"] = ku_rec.get("source_lines", [])
                ku["excerpt"] = (ku_rec.get("excerpt", "") or "")[:400]
                pair_ref.setdefault(key, []).append(p["candidate_id"])

        # attach match evidence from the pair files (contexts per KU+term)
        for p in load_jsonl(REPO / "scratch" / f"dossier-ext-{fn}-pairs.jsonl"):
            key = None
            for side, mk in (("ku_a", "matches_a"), ("ku_b", "matches_b")):
                s = p[side]
                key = (s["source_path"], p["topic"])
                if key in combos:
                    entry = combos[key]
                    kid = s["ku_id"]
                    if kid in entry["kus"]:
                        for m in p[mk][:3]:
                            mm = {"alias": m.get("alias"), "matched_text": m.get("matched_text"),
                                  "source_line": m.get("source_line"),
                                  "context": (m.get("context", "") or "")[:160],
                                  "mermaid_node_suspect": m.get("mermaid_node_suspect", False),
                                  "unit_is_code_block": m.get("unit_is_code_block", False)}
                            if mm not in entry["kus"][kid]["matches"]:
                                entry["kus"][kid]["matches"].append(mm)

        bundle = {
            "domain": domain,
            "domain_scope": DOMAIN_SCOPE[domain],
            "original_concepts": concept_labels,
            "instructions": (
                "For each combo below (a source file + matched term), decide for EVERY "
                "listed knowledge unit (KU) whether it carries domain-relevant concept "
                "content about the term: participate (definition, equation, derivation, "
                "mechanics, worked example, code walkthrough, application/project "
                "insight, interview pitfall, historical note, or critical distinction) "
                "or reject (bare mention, navigation, config line, homonym/different "
                "sense, or unrelated-domain usage). Terms named __exact_hash__ / "
                "__exact_normalized__ are cross-vault duplicated passages: participate "
                "only if the duplicated content itself is domain-relevant. Use the "
                "excerpt + matches as evidence; the heading path and source lines give "
                "location. Output JSONL to the assigned output path: one line per combo "
                '{"domain","file","term","ku_verdicts":{ku_id:"participate"|"reject"},'
                '"rationale":"one line"} — every listed ku_id MUST appear exactly once.'),
            "combos": [],
        }
        n_kus = 0
        for key in sorted(combos):
            entry = combos[key]
            entry["kus"] = [entry["kus"][k] for k in sorted(entry["kus"])]
            n_kus += len(entry["kus"])
            entry["pair_ids_sample"] = pair_ref.get(key, [])[:3]
            bundle["combos"].append(entry)
        out = OUT_DIR / f"{domain}-bundle.json"
        out.write_text(json.dumps(bundle, indent=1, ensure_ascii=False) + "\n",
                       encoding="utf-8")
        manifest = {"domain": domain, "combos": len(bundle["combos"]),
                    "ku_verdicts_expected": n_kus,
                    "bundle": str(out.relative_to(REPO))}
        (OUT_DIR / f"{domain}-manifest.json").write_text(
            json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
        grand_combos += len(bundle["combos"])
        grand_kus += n_kus
        print(f"{domain:20s} combos={len(bundle['combos']):5d} ku_verdicts={n_kus:5d} "
              f"bundle={out.name} ({out.stat().st_size//1024}KB)")
    print(f"GRAND: combos={grand_combos} ku_verdicts={grand_kus}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
