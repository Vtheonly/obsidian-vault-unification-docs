"""EXT-008: build the clustering/dimensionality-reduction domain term map
from ACTUAL batch content.

Scope: batch 006 (master-ai '04 - Clustering and Dimensionality
Reduction.md', 27 KUs) + batch 007 (ai-course 03.5 K-Means Clustering +
03.8 Dimensionality Reduction, 3 files, 87 KUs). 114 KUs total.

Guarantees enforced before writing state/term-maps/clustering-domain-v1.json:
- every canonical term AND every alias actually occurs (case-insensitive,
  word-boundary) inside at least one KU excerpt in scope — no invented
  vocabulary;
- per-term vault coverage is reported (cross-vault / single-vault preview);
- the map matches the CAP-013 terms format {term: [aliases]}; _-prefixed
  keys are documentation and ignored by the loader.

Writes reports/extraction/ext008-term-map-verification.json. Exits non-zero
on any unverified term/alias. Read-only with respect to source vaults.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
BATCH_006 = REPO_ROOT / "state" / "knowledge-units" / "006-ext008-master-ai-unsupervised.jsonl"
BATCH_007 = REPO_ROOT / "state" / "knowledge-units" / "007-ext008-ai-course-clustering-dimreduction.jsonl"
OUT = REPO_ROOT / "state" / "term-maps" / "clustering-domain-v1.json"
REPORT = REPO_ROOT / "reports" / "extraction" / "ext008-term-map-verification.json"

TERM_MAP: dict[str, list[str]] = {
    # --- clustering core (canonical terms occur in BOTH vaults unless noted) ---
    "clustering": ["regroupement"],  # French gloss verified in ai-course 03.5 L4
    "cluster": [],
    "K-means": ["k-means++", "KMeans"],  # k-means++ ai-course; KMeans sklearn master-ai
    "centroid": ["centroids"],
    "inertia": ["WCSS", "within-cluster"],  # WCSS / within-cluster ai-course only
    "elbow method": ["elbow"],
    "DBSCAN": [],
    "hierarchical": ["agglomerative", "divisive"],  # both aliases master-ai only
    "dendrogram": [],
    "unsupervised": [],
    "initialization": ["random initialization"],
    "labels": [],
    # --- choosing-k bridge: canonical master-ai, aliases ai-course ---
    "choosing k": ["choose k", "number of clusters"],
    # --- dimensionality-reduction core ---
    "dimensionality reduction": [],
    "PCA": ["principal component", "principal components"],
    "variance": [],
    "explained variance": [],  # ai-course only
    "maximum variance": [],
    "covariance matrix": [],  # ai-course only
    "SVD": [],  # ai-course only
    "eigendecomposition": [],  # ai-course only
    "t-SNE": [],
    "perplexity": [],
    "UMAP": [],
    "manifold": [],
    "embedding": ["embeddings"],
    "low-dimensional": [],
    "visualization": ["visualize"],
    "feature space": [],  # ai-course only
    "Student-t": [],  # ai-course only
    "n_components": [],  # master-ai only
    "kernel PCA": [],  # ai-course only
    "autoencoder": [],  # ai-course only
    "curse of dimensionality": [],  # ai-course only
    "nonlinear": ["non-linear"],  # canonical master-ai; hyphenated variant ai-course
    "projection": [],
    "compression": [],
    "information loss": [],  # ai-course only
    # --- clustering quality / density (master-ai only in scope) ---
    "silhouette": ["silhouette score"],
    "eps": ["min_samples"],
    "outlier": ["anomaly"],
    # --- cross-cutting shared vocabulary ---
    "noise": [],
    "distance": [],
    "Euclidean": [],  # ai-course only
    "preprocessing": [],
    "scale": [],  # note: word-boundary match also hits 'large-scale' (ai-course)
    "sklearn": ["scikit-learn"],  # sklearn master-ai; scikit-learn ai-course
    "hyperparameters": ["hyperparameter"],
    "local structure": [],
    "global structure": [],
    "tradeoff": [],  # master-ai only; hyphenated 'trade-off' absent from both batches
}

_COMMENT = (
    "Clustering/dimensionality-reduction domain term/alias map for EXT-008 "
    "cross-vault candidate discovery (CAP-013). Canonical term -> aliases. "
    "Built from the actual content of batch 006 (master-ai '04 - Clustering "
    "and Dimensionality Reduction.md', 27 KUs) and batch 007 (ai-course 03.5 "
    "K-Means Clustering 1 file + 03.8 Dimensionality Reduction 2 files, 87 "
    "KUs, two deterministic single-scope runs concatenated in fixed order); "
    "every term and alias is verified to occur inside at least one in-scope "
    "KU excerpt by scripts/ext008_term_map.py "
    "(reports/extraction/ext008-term-map-verification.json). French alias "
    "'regroupement' verified at ai-course 03.5 line 4 (parenthetical gloss "
    "of 'Clustering'); no other French vocabulary in scope (probe: nuage / "
    "données / algorithme / méthode du coude / variance expliquée / seuil / "
    "étiquette all absent). BRIDGE aliases deliberately connect different "
    "surface forms of the same concept across vaults: 'choosing k' "
    "(master-ai) with 'choose k'/'number of clusters' (ai-course); "
    "'nonlinear' (master-ai) with 'non-linear' (ai-course); 'sklearn' "
    "(master-ai) with 'scikit-learn' (ai-course); 'inertia' (both) with "
    "'WCSS'/'within-cluster' (ai-course). Known spurious-match source, "
    "recorded here so classification dismisses it with evidence: 'scale' "
    "word-boundary matching also hits 'large-scale' (ai-course). Note: "
    "'silhouette' occurs ONLY on the master-ai side in this scope — the "
    "ai-course clustering-METRICS file (batch 005, extracted in EXT-005) "
    "covers silhouette from the metrics angle and is NOT part of this "
    "domain's batches; cross-domain connections wait for synthesis. Keys "
    "starting with _ are documentation and ignored by the loader."
)


def main() -> int:
    kus = []
    for path in (BATCH_006, BATCH_007):
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
    bridged_terms = [
        t for t, entry in coverage.items()
        if t not in cross_vault_terms
        and any(entry[n]["ai-course"] for n in entry)
        and any(entry[n]["master-ai"] for n in entry)
    ]

    report = {
        "command": "scripts/ext008_term_map.py",
        "scope_kus": len(kus),
        "scope": {
            "master-ai": "batch 006 (04 - Clustering and Dimensionality Reduction.md, 27 KUs)",
            "ai-course": "batch 007 (03.5 K-Means Clustering 1 file 41 KUs + 03.8 Dimensionality Reduction 2 files 46 KUs)",
        },
        "terms_count": len(TERM_MAP),
        "aliases_count": sum(len(v) for v in TERM_MAP.values()),
        "cross_vault_terms": sorted(cross_vault_terms),
        "cross_vault_terms_count": len(cross_vault_terms),
        "bridged_terms": sorted(bridged_terms),
        "bridged_terms_count": len(bridged_terms),
        "french_probe": {
            "probes": ["nuage", "données", "algorithme", "méthode du coude", "variance expliquée", "seuil", "étiquette"],
            "found": ["regroupement (ai-course 03.5 L4, parenthetical gloss of 'Clustering')"],
            "conclusion": "one French alias included (regroupement -> clustering); no other French content in scope",
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
        "bridged_terms_count": len(bridged_terms),
        "out": str(OUT.relative_to(REPO_ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
