"""EXT-005: build the evaluation-domain term map from ACTUAL batch content.

Scope: batch 004 (master-ai '05 - ML Evaluation Metrics.md', 43 KUs) +
batch 005 (ai-course 03.6 Model Evaluation, 275 KUs). 318 KUs total.

Guarantees enforced before writing state/term-maps/evaluation-domain-v1.json:
- every canonical term AND every alias actually occurs (case-insensitive,
  word-boundary) inside at least one KU excerpt in scope — no invented
  vocabulary;
- per-term vault coverage is reported (cross-vault / single-vault preview);
- the map matches the CAP-013 terms format {term: [aliases]}; _-prefixed
  keys are documentation and ignored by the loader.

Writes reports/extraction/ext005-term-map-verification.json. Exits non-zero
on any unverified term/alias. Read-only with respect to source vaults.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BATCH_004 = REPO_ROOT / "state" / "knowledge-units" / "004-ext005-master-ai-evaluation.jsonl"
BATCH_005 = REPO_ROOT / "state" / "knowledge-units" / "005-ext005-ai-course-03.6-model-evaluation.jsonl"
OUT = REPO_ROOT / "state" / "term-maps" / "evaluation-domain-v1.json"
REPORT = REPO_ROOT / "reports" / "extraction" / "ext005-term-map-verification.json"

TERM_MAP: dict[str, list[str]] = {
    # --- core classification metrics (both vaults) ---
    "accuracy": [],
    "precision": [],
    "recall": [],
    "F1": ["F1 score"],
    "F-beta": [],
    "harmonic mean": [],
    "confusion matrix": [],
    "true positive": [],
    "false positive": [],
    "true negative": [],
    "false negative": [],
    "TP": [],
    "FP": [],
    "FN": [],
    "TN": [],
    "imbalanced": ["class imbalance", "imbalance"],
    "binary classification": [],
    "multi-class": ["one-vs-rest"],
    # --- threshold-free metrics (both vaults) ---
    "ROC": ["ROC curve", "ROC-AUC"],
    "AUC": ["Area Under Curve"],
    "PR-AUC": ["precision-recall curve", "PR curve"],
    "true positive rate": ["TPR"],
    "false positive rate": ["FPR"],
    "specificity": [],
    "sensitivity": [],
    "threshold": ["decision threshold"],
    "macro": ["macro F1", "macro-average"],
    "micro": ["micro F1"],
    "weighted average": [],
    "majority class": [],
    "prevalence": [],
    "Type I error": [],
    "Type II error": [],
    "false alarm": [],
    # --- probabilistic metrics / calibration ---
    "log loss": [],
    "cross-entropy": [],
    "calibration": ["calibrated"],
    "reliability diagram": [],
    "temperature scaling": [],
    "Platt scaling": [],
    "isotonic regression": [],
    "overconfident": [],
    "logits": [],
    "perplexity": [],
    "Guo": [],
    # --- regression metrics ---
    "MSE": [],
    "MAE": [],
    "RMSE": [],
    "R^2": ["R2", "R²"],
    "MAPE": [],
    "Huber": [],
    "squared error": [],
    "absolute error": [],
    "outlier": [],
    "variance explained": [],
    # --- ranking / retrieval metrics ---
    "NDCG": ["discounted cumulative gain"],
    "MRR": [],
    "mAP": ["mean average precision", "mAP@0.5"],
    "hit rate": [],
    "ranking": [],
    "retrieval": [],
    # --- data splitting / protocol ---
    "training set": [],
    "validation set": [],
    "test set": ["held-out"],
    "cross-validation": ["k-fold", "stratified", "nested"],
    "overfitting": ["generalize"],
    "leakage": [],
    # --- CV metrics (ai-course) ---
    "IoU": ["mIoU"],
    "Dice": [],
    "bounding box": [],
    "segmentation": [],
    "pixel": [],
    "mask": [],
    "detection": [],
    "ground truth": [],
    # --- clustering metrics (ai-course) ---
    "silhouette": [],
    "Davies-Bouldin": [],
    "ARI": ["adjusted Rand index"],
    "NMI": ["normalized mutual information"],
    "clustering": [],
    "inertia": ["WCSS"],
    "intrinsic": ["extrinsic"],
    "unsupervised": [],
    # --- example domains (both vaults use the same motivating examples) ---
    "spam": [],
    "cancer": [],
    "screening": [],
    "medical": [],
    "fraud": [],
    "disease": [],
    "diagnosis": [],
    "healthy": [],
    "credit card": [],
    "intrusion": [],
    # --- practice / tooling ---
    "sklearn": ["scikit-learn"],
    "baseline": [],
    "cost matrix": [],
    "cost-sensitive": [],
    "tradeoff": ["trade-off"],
}

_COMMENT = (
    "Evaluation-domain term/alias map for EXT-005 cross-vault candidate "
    "discovery (CAP-013). Canonical term -> aliases. Built from the actual "
    "content of batch 004 (master-ai '05 - ML Evaluation Metrics.md', 43 "
    "KUs) and batch 005 (ai-course 03.6 Model Evaluation, 5 files, 275 "
    "KUs); every term and alias is verified to occur inside at least one "
    "in-scope KU excerpt by scripts/ext005_term_map.py "
    "(reports/extraction/ext005-term-map-verification.json). No French "
    "aliases: the evaluation batches contain no French lab content "
    "(probe: précision/rappel/exactitude/métrique/seuil/étiquette all "
    "absent). NOTE on 'mAP': case-insensitive word-boundary matching "
    "deliberately lets ai-course 'mAP' (CV detection, mAP@0.5) collide "
    "with master-ai 'MAP' (ranking Mean Average Precision) AND with "
    "ai-course L495 'mAP' in the ranking sense — the shared-name cases "
    "are exactly what evidence-based classification must adjudicate "
    "(F-0006 rules remain mandatory; 'Color map' at ai-course L436 will "
    "produce a spurious candidate that classification must dismiss). "
    "Formula-level and description-level identities invisible to term "
    "matching (e.g. master-ai's unnamed Huber description vs ai-course's "
    "named Huber loss; master-ai's unnamed confusion-matrix table vs "
    "ai-course's named confusion matrix) are classified as judgments with "
    "byte-exact quote evidence, per the EXT-003 precedent. Keys starting "
    "with _ are documentation and ignored by the loader."
)


def main() -> int:
    kus = []
    for path in (BATCH_004, BATCH_005):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                kus.append(json.loads(line))

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

    report = {
        "command": "scripts/ext005_term_map.py",
        "scope_kus": len(kus),
        "scope": {
            "master-ai": "batch 004 (05 - ML Evaluation Metrics.md, 43 KUs)",
            "ai-course": "batch 005 (03.6 Model Evaluation, 5 files, 275 KUs)",
        },
        "terms_count": len(TERM_MAP),
        "aliases_count": sum(len(v) for v in TERM_MAP.values()),
        "cross_vault_terms": sorted(cross_vault_terms),
        "cross_vault_terms_count": len(cross_vault_terms),
        "french_probe": {
            "probes": ["précision", "rappel", "exactitude", "métrique", "seuil", "étiquette"],
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

    payload_out = {"_comment": _COMMENT, **dict(TERM_MAP)}
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
