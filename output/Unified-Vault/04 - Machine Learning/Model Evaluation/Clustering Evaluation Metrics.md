---
title: Clustering Evaluation Metrics
type: reference
aliases:
  - Clustering Metrics
  - Silhouette Coefficient
  - Davies-Bouldin Index
  - Calinski-Harabasz Index
  - Adjusted Rand Index
  - Normalized Mutual Information
  - V-measure
tags:
  - machine-learning
  - model-evaluation
  - clustering
  - unsupervised-learning
  - evaluation-metrics
  - silhouette-coefficient
  - davies-bouldin-index
  - calinski-harabasz-index
  - adjusted-rand-index
  - normalized-mutual-information
  - v-measure
sources:
  - "Clustering Metrics - Silhouette, Davies-Bouldin, ARI, NMI"
created_index: 7
---

Clustering is unsupervised — there are no ground-truth labels to score against — so evaluating a clustering needs its own machinery. The within-cluster sum of squares (WCSS, also called inertia) that K-Means optimizes cannot serve as the judge: it always decreases as clusters are added — trivially, $K = N$ clusters gives WCSS = 0 — so it can neither choose $K$ nor compare algorithms. This note covers the two families that can: **intrinsic** metrics (silhouette, Davies-Bouldin, Calinski-Harabasz) that measure whether clusters are compact and well-separated without needing labels, and **extrinsic** metrics (ARI, NMI, V-measure) that score agreement with reference labels when they exist. The algorithms being evaluated are covered in [[Clustering]]; the broader evaluation landscape is consolidated in [[Model Evaluation Metrics]], and the surrounding map is [[Machine Learning MOC]].

## The clustering evaluation problem

Clustering is unsupervised, so how do you evaluate it? There are two cases:

1. **No ground truth available** (the typical case): evaluate based on the **intrinsic structure** of the clusters — are they compact and well-separated? Metrics: Silhouette, Davies-Bouldin, Calinski-Harabasz.
2. **Ground truth available** (e.g., for benchmarking): compare the predicted clusters to the true labels. Metrics: Adjusted Rand Index (ARI), Normalized Mutual Information (NMI), V-measure.

The reason a dedicated family is needed at all is that the obvious candidate — the WCSS/inertia objective that [[Clustering]] covers alongside the K-Means algorithm — is not a valid quality measure. WCSS always decreases as you add more clusters (trivially, $K = N$ clusters gives WCSS = 0), so it cannot be used to choose $K$ or to compare algorithms. Every metric below exists to answer the question WCSS cannot.

## Intrinsic metrics (no ground truth)

### Silhouette coefficient

For each sample $i$:

$$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$

where:

- $a(i)$ = mean intra-cluster distance (average distance from $i$ to other points in its cluster).
- $b(i)$ = mean nearest-cluster distance (the smallest average distance from $i$ to points in any other cluster).

The Silhouette Coefficient is the average of $s(i)$ over all samples. It ranges from $-1$ to $+1$:

- $+1$: sample is far from neighboring clusters, close to its own — well-clustered.
- $0$: sample is on the boundary between two clusters — ambiguous.
- $-1$: sample is closer to a different cluster than its own — misclassified.

Silhouette measures per-sample compactness versus separation — how well each point sits inside its own cluster relative to the nearest other cluster — and it earns its place as the default intrinsic metric through three uses. It is the standard tool **to choose $K$ in K-Means**: compute Silhouette for $K = 2, 3, \ldots, 10$ and pick the $K$ with the highest score. It **compares clustering algorithms** on the same data. And it **identifies problematic samples** — those with negative Silhouette are likely misclustered, so the per-sample scores are diagnostic, not just the average.

Two pitfalls temper it. It is computationally expensive — $O(n^2)$ for all pairwise distances — so use sampling for large datasets. And it is biased toward convex (round) clusters: it does not work well for non-convex clusters (e.g., moons, circles) even if the clustering is correct.

### Davies-Bouldin index

$$DB = \frac{1}{K} \sum_{i=1}^K \max_{j \neq i} \frac{\sigma_i + \sigma_j}{d(c_i, c_j)}$$

where:

- $K$ is the number of clusters.
- $\sigma_i$ is the average distance from points in cluster $i$ to its centroid (cluster "spread").
- $d(c_i, c_j)$ is the distance between centroids of clusters $i$ and $j$.

**Lower is better.** The index measures the worst-case ratio of (within-cluster spread) to (between-cluster distance) — you want compact clusters far apart, which gives a low DB. The averaging over clusters means each cluster's score is its comparison against the most similar other cluster, so the metric reports how bad the worst-confused cluster pair is on average.

Its selling points are simplicity and speed: it is simpler and faster than Silhouette ($O(nK)$ instead of $O(n^2)$), which makes it good for quick cluster-quality checks. The pitfalls mirror Silhouette's, plus one of its own: the same convexity bias, and the "max" makes it sensitive to the worst cluster pair.

### Calinski-Harabasz index (variance ratio criterion)

$$CH = \frac{\text{between-cluster dispersion}}{\text{within-cluster dispersion}} \times \frac{n - K}{K - 1}$$

**Higher is better.** The Calinski-Harabasz index measures the ratio of between-cluster variance to within-cluster variance, normalized by degrees of freedom.

It is very fast to compute ($O(n)$) and good for high-dimensional data, which makes it the cheapest of the three intrinsic options. The pitfalls: the same convexity bias as the others, and it is biased toward larger $K$ — the normalization helps but does not fully correct.

## Extrinsic metrics (with ground truth)

These compare predicted clusters to true labels. They do not require the label and cluster IDs to match — they measure whether samples in the same true class are in the same predicted cluster (and vice versa), which is what makes them usable across arbitrary label permutations and differing cluster counts.

### Adjusted Rand index (ARI)

The Rand Index measures the fraction of pairs of samples that are "correctly" grouped (both in the same cluster, or both in different clusters). The **Adjusted** Rand Index corrects for chance:

$$ARI = \frac{RI - \mathbb{E}[RI]}{\max(RI) - \mathbb{E}[RI]}$$

- $ARI = 1$: perfect match.
- $ARI = 0$: random clustering.
- $ARI < 0$: worse than random (rare).

ARI is the default when you have ground-truth labels and want to compare clusterings. It works when the number of clusters may differ from the number of true classes, and its range is bounded and interpretable. Its pitfalls: it requires ground truth, which is not available in most real clustering applications, and it is sensitive to the number of clusters — it tends to be higher when $K$ matches the true number of classes.

### Normalized mutual information (NMI)

$$NMI = \frac{I(C, Y)}{\sqrt{H(C) \cdot H(Y)}}$$

where $I(C, Y)$ is the mutual information between clusters $C$ and labels $Y$, and $H$ is entropy.

- $NMI = 1$: perfect match.
- $NMI = 0$: clusters and labels are independent.

NMI is the choice when you want an information-theoretic measure — how much does knowing the cluster tell you about the label? It handles different numbers of clusters and classes naturally. The pitfall is that it is **not adjusted for chance**: NMI is not zero for random clustering when $K$ is large. Use **Adjusted Mutual Information (AMI)** for a chance-corrected version.

### V-measure

$$V = \frac{2 \cdot \text{homogeneity} \cdot \text{completeness}}{\text{homogeneity} + \text{completeness}}$$

where:

- **Homogeneity:** each cluster contains only members of a single class (precision-like).
- **Completeness:** all members of a class are in the same cluster (recall-like).

V-measure is the harmonic mean of homogeneity and completeness — analogous to F1 score for clustering. Its diagnostic value comes from the two components: use it when you want to separately diagnose whether the problem is "impure clusters" (low homogeneity) or "split classes" (low completeness).

## Choosing a clustering metric

| Situation | Recommended metric |
| :--- | :--- |
| No ground truth, choosing K | Silhouette (compute for each K, pick the max) |
| No ground truth, fast check | Davies-Bouldin or Calinski-Harabasz |
| Ground truth available | ARI (chance-corrected, bounded) or AMI |
| Information-theoretic preference | NMI (or AMI for chance correction) |
| Diagnosing purity vs completeness | V-measure (with homogeneity and completeness reported separately) |

The choice reduces to two questions: do you have ground truth, and what aspect of clustering quality do you care about? Without labels, Silhouette is the workhorse for choosing $K$ (score each candidate $K$ and take the max), with Davies-Bouldin and Calinski-Harabasz as faster coarse checks — remembering that lower is better for Davies-Bouldin and higher is better for Calinski-Harabasz. With labels, ARI gives a chance-corrected, bounded agreement score; NMI gives the information-theoretic reading but needs AMI when chance correction matters at large $K$; and V-measure decomposes the failure into impure clusters versus split classes, which is why its two components should be reported separately whenever the diagnosis matters.

## The convexity caveat

All the intrinsic metrics (Silhouette, Davies-Bouldin, Calinski-Harabasz) implicitly favor **convex** clusters — round, compact blobs. They will give poor scores to correct clusterings of non-convex data (e.g., two concentric circles, a moons dataset) even when the clustering is semantically correct.

> [!warning] Intrinsic metrics judge shape, not meaning
> A low Silhouette or Davies-Bouldin score on non-convex data does not mean the clustering is wrong — it means the metric cannot see that shape as good. Diagnose the geometry before trusting the score.

For non-convex data, use **DBSCAN** or **spectral clustering** (which handle non-convex shapes) instead of K-Means, and evaluate with extrinsic metrics (if ground truth is available) or with **density-based metrics** (DBCV — Density-Based Cluster Validity).

## See also

The metric families and the algorithms they judge:

- [[Machine Learning MOC]]
- [[Model Evaluation Metrics]]
- [[Clustering]]
- [[Principal Component Analysis]]
- [[t-SNE and UMAP]]
