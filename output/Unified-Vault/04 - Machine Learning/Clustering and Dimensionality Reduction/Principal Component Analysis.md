---
title: Principal Component Analysis
type: concept
aliases:
  - PCA
tags:
  - machine-learning
  - unsupervised-learning
  - dimensionality-reduction
  - principal-component-analysis
  - feature-engineering
sources:
  - Principal Component Analysis (PCA)
  - 04 - Clustering and Dimensionality Reduction
created_index: 2
---

PCA is the foundational dimensionality reduction algorithm: it reduces high-dimensional data to a lower-dimensional representation while preserving as much variance as possible. It is used for visualization, compression, noise reduction, and as a preprocessing step for other algorithms. It is the linear member of the reduction family — the non-linear methods [[t-SNE and UMAP]] take over where linear projections fail, and [[Clustering]] is the other pillar of unsupervised learning that often consumes PCA's output. This note covers the problem PCA solves, the variance-maximization intuition, the algorithm in both its eigendecomposition and SVD forms, what PCA captures and misses, its practical uses, and its caveats.

## The problem: high-dimensional data is hard

Real-world data is often high-dimensional: a 224×224 image is 150,528-dimensional; a 1000-word document in TF-IDF is 1000-dimensional; a gene expression profile is 20,000-dimensional. High dimensionality causes three distinct problems:

1. **Curse of dimensionality:** distances become less meaningful, nearest neighbors become less useful, models overfit (see [[Bias Variance Tradeoff]]).
2. **Computational cost:** algorithms scale as $O(d)$ or $O(d^2)$ in dimension.
3. **Visualization:** you cannot plot 20-dimensional data.

**Dimensionality reduction** finds a low-dimensional representation that captures the important structure. PCA is the linear approach; t-SNE and UMAP are the non-linear approaches. More broadly, unsupervised learning finds structure in unlabeled data — clustering groups similar examples while dimensionality reduction projects high-dim data to a lower-dim space that preserves structure — and both are essential for exploration, visualization, and as preprocessing for downstream models.

## The intuition: find the directions of maximum variance

PCA finds the **directions in which the data varies the most** and projects the data onto those directions. The intuition: the directions with the most variance contain the most information; the directions with little variance are mostly noise and can be discarded.

Concretely: if your data is 3D but lies mostly on a flat 2D plane (with small noise perpendicular to the plane), PCA will find the two directions defining the plane (high variance) and discard the perpendicular direction (low variance). The data is reduced from 3D to 2D with minimal information loss.

In short, PCA is a linear projection to the directions of maximum variance — fast, deterministic, with no hyperparameters except the number of components — which makes it a good baseline and preprocessing step, though it only captures linear structure.

## The algorithm

1. **Center the data:** subtract the mean of each feature, so the data is centered at the origin.
2. **Compute the covariance matrix:** $\Sigma = \frac{1}{n} X^\top X$ (for centered $X$).
3. **Eigendecompose** the covariance matrix: $\Sigma = Q \Lambda Q^\top$.
4. **Sort eigenvalues** in descending order. The eigenvectors (columns of $Q$) corresponding to the top $k$ eigenvalues are the **principal components** — the $k$ directions of maximum variance.
5. **Project:** the reduced representation is $X_{reduced} = X Q_k$, where $Q_k$ is the matrix of the top $k$ eigenvectors.

The eigenvalues tell you how much variance each component captures. The ratio $\lambda_i / \sum_j \lambda_j$ is the **fraction of variance explained** by component $i$. Plotting the cumulative explained variance helps you choose $k$ — pick the smallest $k$ that explains, say, 95% of the variance. The number of components is PCA's one real knob.

### The SVD connection

PCA is equivalent to **SVD of the centered data matrix**. If $X = U \Sigma V^\top$, then the principal components are the columns of $V$, and the reduced representation is $U_k \Sigma_k$ (the top $k$ columns of $U$ times the top $k$ singular values). SVD is numerically more stable than explicitly forming the covariance matrix, so most PCA implementations use SVD internally.

## What PCA captures and what it misses

PCA's strengths and blind spots both follow from it being a linear, global, unsupervised projection.

### What PCA captures

- **Linear structure:** the directions of maximum variance, assuming they are linear.
- **Global structure:** the principal components are global — they describe the entire dataset.

### What PCA misses

- **Non-linear structure:** if the data lies on a curved manifold (e.g., the "swiss roll" dataset), PCA cannot unroll it — it finds the best linear projection, which mixes the roll's layers. Use t-SNE, UMAP, or an autoencoder for non-linear structure.
- **Local structure:** PCA preserves global variance, not local neighborhoods. Two points that are far apart in the original space but happen to align along a principal component may appear close in the PCA projection.
- **Class structure:** PCA is unsupervised — it does not know about labels and may project away the directions that separate classes. **Linear Discriminant Analysis (LDA)** is the supervised alternative that maximizes between-class variance.

## Practical use

PCA earns its place as the default baseline because it slots into so many workflows.

### Visualization

Project high-dimensional data to 2D or 3D for plotting. PCA is fast and deterministic, making it a good first look. But PCA often produces a "blob" because it preserves global variance, not local structure — t-SNE and UMAP usually produce more interpretable visualizations.

### Preprocessing

Reduce dimensionality before applying another algorithm (KNN, SVM, clustering). This speeds up the downstream algorithm and can improve accuracy by removing noise dimensions — [[K-Nearest Neighbors]] and [[Support Vector Machines]] are typical consumers. But it can also remove useful information — test with and without PCA.

### Compression

PCA is a lossy compression method. For image compression, PCA (via SVD) can compress a 1000×1000 image to a rank-50 approximation with minimal perceptual loss. This is the foundation of the JPEG-2000 standard and many recommendation systems.

### Noise reduction

If the signal lies in the top $k$ principal components and the noise is spread across all dimensions, projecting to the top $k$ components removes the noise. This is the basis of "PCA denoising" in signal processing and genomics.

## Limitations and caveats

1. **PCA assumes linearity.** If the data's structure is non-linear, PCA misses it. Use kernel PCA (see [[Kernel Trick]]), t-SNE, UMAP, or autoencoders.
2. **PCA is sensitive to scaling.** Features with large scale dominate the variance. **Always standardize** (subtract mean, divide by std) before PCA, or features with large numerical ranges will dominate.
3. **PCA is unsupervised.** It may discard directions that are important for a downstream supervised task. Consider supervised alternatives (LDA) or just train the model on the full data.
4. **Interpreting components is hard.** Each principal component is a linear combination of all original features. You can inspect the coefficients (the "loadings") to see which features contribute, but the components rarely correspond to clean semantic concepts.
5. **Choosing $k$ is heuristic.** The "elbow" in the explained variance plot or a threshold (95% variance) are common heuristics, but there is no principled answer.

## PCA in the unsupervised toolkit

PCA does not live alone. The other pillar of unsupervised learning is clustering: K-Means, the simplest and most-used clustering algorithm, iteratively assigns each point to the nearest centroid and recomputes centroids as the mean of their assigned points until assignments stop changing; DBSCAN treats clusters as high-density regions separated by low-density regions, handles arbitrary shapes, and marks outliers as noise; hierarchical clustering builds a dendrogram (agglomerative or divisive) that you cut at the desired level. Selection guidance there: K-means for large data with roughly spherical clusters when you know K; DBSCAN for arbitrary cluster shapes and outlier detection; hierarchical for small data where you want to understand cluster structure.

On the reduction side, t-SNE is the non-linear method optimized for 2D or 3D visualization — it preserves local structure but not global structure, is slow on large data, and is stochastic, giving different plots on different runs; UMAP is the modern alternative — faster, better at preserving global structure, and able to generalize to new points so it can serve as a preprocessing step (unlike t-SNE), with meaningful hyperparameters (`n_neighbors`, `min_dist`); autoencoders are neural networks trained to reconstruct their input through a low-dimensional "bottleneck" layer (the bottleneck is the reduced representation), capturing highly nonlinear structure, trainable end-to-end with the rest of a model, with variants such as VAE (variational, generative), denoising AE (robust), and contractive AE (explicit regularization). Across the whole family: **visualization** → UMAP or t-SNE; **preprocessing for downstream ML** → PCA or UMAP; **nonlinear structure, end-to-end training** → autoencoders; **generative modeling** → VAEs.

## Worked example

PCA in context — the standard unsupervised toolkit in scikit-learn, with clustering and the nonlinear embedding methods alongside it:

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

## Common pitfalls

The classic mistakes span the whole clustering-and-dimensionality-reduction family:

- **Using t-SNE distances for analysis** — they're meaningless. Use it only for visualization.
- **Not standardizing features before PCA** — features with large scale dominate.
- **Choosing K wrong** — elbow method is heuristic; check silhouette scores too.
- **Forgetting that clustering is unsupervised** — labels are arbitrary; cluster 0 isn't "better" than cluster 1.
- **UMAP hyperparameters matter** — `n_neighbors` and `min_dist` dramatically affect results; don't use defaults blindly.

## What you should walk away with

The core of PCA in six points:

1. PCA finds the directions of maximum variance and projects the data onto them, reducing dimensionality while preserving variance.
2. It is computed via eigendecomposition of the covariance matrix (or equivalently, SVD of the centered data matrix).
3. The eigenvalues tell you the variance explained by each component; choose $k$ by the cumulative explained variance.
4. **Always standardize** features before PCA, or large-scale features dominate.
5. PCA captures linear, global structure. It misses non-linear and local structure — use t-SNE/UMAP for those.
6. Uses: visualization, preprocessing, compression, denoising. But it is unsupervised and may discard task-relevant directions.

## Further reading

The canonical references for this area of unsupervised learning:

- Hastie et al., *ESL*, Chapter 14 (unsupervised learning).
- McInnes et al. (2018), *UMAP: Uniform Manifold Approximation and Projection*.
- van der Maaten & Hinton (2008), *Visualizing Data using t-SNE*.

## See also

Related notes in the vault:

- [[Machine Learning MOC]]
- [[Clustering]]
- [[t-SNE and UMAP]]
- [[Clustering Evaluation Metrics]]
- [[K-Nearest Neighbors]]
- [[Support Vector Machines]]
- [[Kernel Trick]]
- [[Bias Variance Tradeoff]]
- [[Matrix Decomposition]]
