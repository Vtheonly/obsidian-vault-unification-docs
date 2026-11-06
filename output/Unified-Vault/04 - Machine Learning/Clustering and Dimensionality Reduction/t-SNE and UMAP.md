---
title: t-SNE and UMAP
type: concept
aliases:
  - t-SNE
  - UMAP
  - t-Distributed Stochastic Neighbor Embedding
  - Uniform Manifold Approximation and Projection
tags:
  - machine-learning
  - unsupervised-learning
  - dimensionality-reduction
  - t-sne
  - umap
  - visualization
  - embeddings
sources:
  - t-SNE and UMAP
  - 04 - Clustering and Dimensionality Reduction
created_index: 3
---

PCA is fast and linear, but it often produces uninformative "blobs" when visualizing complex data — it preserves global variance, not local structure. **t-SNE** and **UMAP** are non-linear dimensionality reduction algorithms designed specifically for **visualization**: they preserve local neighborhoods, so points that are nearby in high-dimensional space remain nearby in the 2D plot. They are the standard tools for visualizing embeddings, clusters, and high-dimensional data, with [[Principal Component Analysis]] as the linear baseline and [[Clustering]] as the other pillar of unsupervised learning. This note covers how each algorithm works, the crowding problem and the Student-t trick, hyperparameter guidance, and how to choose between the three methods.

## t-SNE: t-Distributed Stochastic Neighbor Embedding

**t-SNE** (van der Maaten and Hinton, 2008) reduces dimensionality by preserving **local neighborhoods**: points that are neighbors in high-dimensional space should be neighbors in the 2D embedding. It is a nonlinear reduction optimized for **visualization** (2D or 3D). It preserves local structure (nearby points stay nearby), does NOT preserve global structure (cluster distances are meaningless), is slow on large data — so use it for visualization, not as model input — and is stochastic, meaning different runs give different plots.

### The algorithm

1. **In high-dimensional space:** compute pairwise similarities using a Gaussian kernel. Define $p_{j|i}$ as the probability that point $i$ would pick point $j$ as a neighbor:

$$p_{j|i} = \frac{\exp(-\|x_i - x_j\|^2 / 2\sigma_i^2)}{\sum_{k \neq i} \exp(-\|x_i - x_k\|^2 / 2\sigma_i^2)}$$

The bandwidth $\sigma_i$ is chosen so that each point has the same "perplexity" (effective number of neighbors). Symmetrize: $p_{ij} = (p_{j|i} + p_{i|j}) / (2n)$.

2. **In low-dimensional space:** compute pairwise similarities using a **Student-t distribution** (heavy-tailed):

$$q_{ij} = \frac{(1 + \|y_i - y_j\|^2)^{-1}}{\sum_{k \neq l} (1 + \|y_k - y_l\|^2)^{-1}}$$

The heavy-tailed Student-t (vs. Gaussian in high-D) is the key trick — it prevents the "crowding problem" where moderate-distance high-D points get crushed together in low-D.

3. **Minimize the KL divergence** between $p$ and $q$:

$$C = \sum_{i \neq j} p_{ij} \log \frac{p_{ij}}{q_{ij}}$$

via gradient descent (see [[Gradient Descent]]) — KL divergence is one of the standard [[Loss Functions]]. The result: nearby points in high-D stay nearby in the 2D plot; distant points stay distant.

### Why the Student-t distribution?

The "crowding problem": in high dimensions, there is a lot of "room" — points can be moderately far apart and still be neighbors. In 2D, there is much less room, so if you use a Gaussian for the low-D similarities, all the moderately-distant points get crushed to the same distance. The heavy-tailed Student-t allows moderate-distance points to spread out in 2D, preserving more of the structure.

### What t-SNE is good for

t-SNE shines exactly where PCA's global projections blur together:

- **Visualizing clusters:** t-SNE beautifully separates clusters that overlap in PCA. It is the standard tool for "what does my high-dimensional data look like?"
- **Checking embeddings:** visualize the embeddings from a trained model (word2vec, BERT, ViT) to see if semantically similar items cluster.
- **Exploratory data analysis:** get intuition for the structure of a new dataset.

### What t-SNE is NOT good for

The mirror-image warnings matter just as much:

- **NOT for downstream modeling.** t-SNE is non-parametric (you cannot apply the trained embedding to new data) and does not preserve global structure (distances between clusters are not meaningful). Use PCA or UMAP if you need to embed new data.
- **NOT for interpreting distances.** The distance between two clusters in a t-SNE plot is not meaningful — only within-cluster structure is preserved. Two clusters that appear far apart may actually be close in the original space.
- **NOT for choosing the number of clusters.** t-SNE can create artificial clusters or merge real ones depending on the perplexity. Do not use t-SNE plots to decide $K$ for K-Means.

### Key hyperparameter: perplexity

Perplexity (typically 5–50) controls the effective number of neighbors each point considers. Low perplexity emphasizes very local structure; high perplexity captures more global structure. **Always try multiple perplexities** — the plot can change dramatically.

## UMAP: Uniform Manifold Approximation and Projection

**UMAP** (McInnes et al., 2018) is a newer algorithm with similar goals to t-SNE but several advantages:

1. **Faster:** UMAP is much faster than t-SNE, especially on large datasets.
2. **Preserves global structure better:** UMAP tends to keep both local and global structure, while t-SNE focuses on local.
3. **Reproducible:** UMAP is deterministic; t-SNE (with random initialization) gives different plots each run.
4. **Can embed new data:** UMAP learns a parametric mapping that can be applied to new points. t-SNE cannot (without parametric variants).
5. **Can be used for downstream modeling:** UMAP's embedding is more stable and can be used as features for other models.

### How UMAP works (conceptually)

UMAP assumes the data lies on a **Riemannian manifold** and tries to find a low-dimensional representation that preserves the manifold's topological structure. Concretely:

1. Construct a **fuzzy topological representation** of the high-dimensional data (a weighted graph where edges connect neighbors).
2. Construct a similar representation in low-dimensional space.
3. Minimize the **cross-entropy** between the two representations (similar to KL divergence but with different properties).

The result is similar to t-SNE (local neighborhoods preserved) but with better global structure preservation and computational efficiency.

### UMAP hyperparameters

UMAP's two meaningful knobs both shape the embedding dramatically:

- `n_neighbors` (5–50, default 15): similar to t-SNE's perplexity. Low values emphasize local structure; high values emphasize global.
- `min_dist` (0.0–0.99, default 0.1): how tightly points can pack in the low-D space. Low values produce tighter clusters; high values produce more spread.

These hyperparameters matter: `n_neighbors` and `min_dist` dramatically affect results, so don't use defaults blindly.

## t-SNE vs UMAP vs PCA: which to use?

The three methods line up along the axes of linearity, locality, and deployability:

| | PCA | t-SNE | UMAP |
| :--- | :--- | :--- | :--- |
| Linear or non-linear | Linear | Non-linear | Non-linear |
| Preserves local structure | No | Yes | Yes |
| Preserves global structure | Yes | No | Partially |
| Can embed new data | Yes | No (standard) | Yes |
| Fast on large data | Yes | No | Yes |
| Deterministic | Yes | No | Yes |
| Good for visualization | Sometimes | Yes (the standard) | Yes |
| Good for downstream features | Yes | No | Sometimes |

**Practical recommendation:**

- Start with **PCA** for a quick look and as a baseline.
- Use **t-SNE** for the highest-quality visualization of local structure (especially for embeddings).
- Use **UMAP** when you need speed, global structure, or the ability to embed new data.

## Common pitfalls

The failure modes are well documented, and all of them come from treating a visualization tool as an analysis tool:

1. **Not standardizing first.** Like PCA, t-SNE and UMAP are distance-based — standardize features first, or large-scale features dominate.
2. **Using t-SNE for clustering.** t-SNE can create or merge clusters based on perplexity. Use a real clustering algorithm (K-Means, DBSCAN, HDBSCAN) and visualize with t-SNE.
3. **Interpreting inter-cluster distances.** In t-SNE, the distance between clusters is not meaningful. Only intra-cluster structure is preserved.
4. **Not trying multiple hyperparameters.** t-SNE with perplexity 5 vs 50 can look completely different. Always try multiple values.
5. **Using t-SNE embeddings as features.** t-SNE is non-parametric and does not generalize. Use UMAP or PCA if you need features for a downstream model.

The same warnings extend across the whole clustering-and-dimensionality-reduction family: using t-SNE distances for analysis is meaningless (use it only for visualization); not standardizing features before PCA lets features with large scale dominate; choosing K wrong is easy because the elbow method is heuristic (check silhouette scores too, per [[Clustering Evaluation Metrics]]); and forgetting that clustering is unsupervised leads to over-reading arbitrary labels (cluster 0 isn't "better" than cluster 1).

## The wider unsupervised toolkit

Both methods sit inside the broader project of finding structure in unlabeled data: clustering groups similar examples, while dimensionality reduction projects high-dim data to a lower-dim space that preserves structure — PCA is the linear approach, t-SNE and UMAP the non-linear ones. On the clustering side, K-Means (the simplest and most-used clustering algorithm) iteratively assigns points to the nearest centroid and recomputes centroids as the mean of their assigned points until assignments stop changing; DBSCAN treats clusters as high-density regions separated by low-density regions, handles arbitrary shapes, and marks outliers as noise; hierarchical clustering builds a dendrogram (agglomerative or divisive) that you cut at the desired level. Selection guidance there: K-means for large data with roughly spherical clusters when you know K; DBSCAN for arbitrary cluster shapes and outlier detection; hierarchical for small data where you want to understand cluster structure.

Autoencoders complete the reduction family as the neural alternative: networks trained to reconstruct their input through a low-dimensional "bottleneck" layer (the bottleneck is the reduced representation), which can capture highly nonlinear structure, can be trained end-to-end with the rest of a model, and come in variants such as VAE (variational, generative), denoising AE (robust), and contractive AE (explicit regularization). Across the whole family: **visualization** → UMAP or t-SNE; **preprocessing for downstream ML** → PCA or UMAP; **nonlinear structure, end-to-end training** → autoencoders; **generative modeling** → VAEs.

## Worked example

The visualization methods in context — the standard unsupervised toolkit in scikit-learn:

```python
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap

# K-means
kmeans = KMeans(n_clusters=5).fit(X)
labels = kmeans.labels_

# PCA
X_pca = PCA(n_components=2).fit_transform(X)

# t-SNE (visualization)
X_tsne = TSNE(n_components=2, perplexity=30).fit_transform(X)

# UMAP
X_umap = umap.UMAP(n_components=2).fit_transform(X)
```

Note the `perplexity=30` argument in the t-SNE call — in practice you sweep this value rather than accept one default.

## Why this matters for AI

Clustering and dimensionality reduction show up all over modern AI systems:

- **Embedding visualization**: UMAP / t-SNE on text or image embeddings reveals clusters, outliers, structure. Essential for inspecting embedding models.
- **Vector DB indexing**: many ANN indexes (e.g., IVF) cluster vectors with k-means for fast retrieval.
- **Data exploration**: before training any model, cluster and visualize to understand the data.
- **Anomaly detection**: cluster outliers or low-density points flag anomalies.
- **Feature compression**: PCA / autoencoders reduce feature dim, speeding downstream training.

## Production implications

A few rules of thumb survive contact with production:

- **Always visualize embeddings with UMAP** before deploying. If the visualization doesn't match your intuition about the data, something is wrong.
- **For real-time clustering**, use mini-batch k-means (sklearn `MiniBatchKMeans`).
- **PCA before K-means** can speed up clustering on high-dim data, but loses interpretability.
- **Anomaly detection with clustering**: compute distance to nearest cluster centroid; flag points with distance > threshold.

## What you should walk away with

The core of these two methods in six points:

1. **t-SNE** preserves local neighborhoods by minimizing KL divergence between high-D and low-D similarity distributions, using a heavy-tailed Student-t in low-D to avoid the crowding problem.
2. **UMAP** is similar but faster, more global-structure-preserving, deterministic, and can embed new data.
3. Both are for **visualization** — they reveal structure but should not be used for downstream modeling (except UMAP, cautiously).
4. **PCA** is linear and global; **t-SNE** is non-linear and local; **UMAP** is non-linear and local+global.
5. Always standardize before applying any of them; always try multiple hyperparameters; do not interpret inter-cluster distances in t-SNE.
6. Start with PCA for a quick look, use t-SNE for high-quality local visualization, use UMAP for speed or when you need to embed new data.

## Further reading

The canonical references for this area of unsupervised learning:

- Hastie et al., *ESL*, Chapter 14 (unsupervised learning).
- McInnes et al. (2018), *UMAP: Uniform Manifold Approximation and Projection*.
- van der Maaten & Hinton (2008), *Visualizing Data using t-SNE*.

## See also

Related notes in the vault:

- [[Machine Learning MOC]]
- [[Principal Component Analysis]]
- [[Clustering]]
- [[Clustering Evaluation Metrics]]
- [[Gradient Descent]]
- [[Loss Functions]]
- [[Bias Variance Tradeoff]]
- [[Matrix Decomposition]]
