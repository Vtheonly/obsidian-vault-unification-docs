---
title: Linear Algebra Fundamentals
type: concept
aliases:
  - Linear Algebra
  - Linear Algebra for Machine Learning
  - "00. Linear Algebra Fundamentals"
tags:
  - linear-algebra
  - mathematics
  - vectors
  - matrices
  - eigenvalues
  - svd
  - tensors
  - hadamard-product
  - deep-learning
sources:
  - "00. Linear Algebra Fundamentals"
created_index: 18
---

Linear algebra is the language of deep learning: every neural network operation — from $Y = WX + B$ to attention's $QK^\top$ to batch norm's $\gamma / \sqrt{\sigma^2 + \epsilon}$ — is a linear algebra operation. This note provides the minimum linear algebra you need to read any deep learning paper fluently: vectors and their operations, matrices and matrix multiplication, eigendecomposition, the singular value decomposition, tensors, and the Hadamard product. Nothing here has prerequisites — this is the foundational layer that everything else in deep learning builds on. The notes that lean on it most directly are [[Gradients and Gradient Descent]] and [[01 - Foundations/Mathematical Foundations/Jacobians and Hessians|Jacobians and Hessians]]; the notation is fixed in [[Mathematical Notation]], and the story continues on the probability side in [[Probability and Statistics for ML]].

## Vectors

A **vector** $\mathbf{x} \in \mathbb{R}^n$ is an ordered list of $n$ real numbers:

$$\mathbf{x} = \begin{pmatrix} x_1 \\ x_2 \\ \vdots \\ x_n \end{pmatrix}$$

In machine learning the same object plays several roles, and noticing which role a vector plays in a given formula is a large part of reading the literature fluently. A vector can be:

- A data point (features of one example).
- A model's parameters (weights of one layer).
- A gradient (partial derivatives with respect to all parameters).
- An embedding (a word's or image's representation in a continuous space).

### Vector operations

The elementary operations on vectors are:

- **Addition:** $\mathbf{x} + \mathbf{y} = (x_1 + y_1, \ldots, x_n + y_n)$. Component-wise.
- **Scalar multiplication:** $c \mathbf{x} = (cx_1, \ldots, cx_n)$.
- **Dot product (inner product):** $\mathbf{x}^\top \mathbf{y} = \sum_i x_i y_i$. A scalar measuring alignment.
- **Norms:**
  - L2 (Euclidean): $\|\mathbf{x}\|_2 = \sqrt{\sum_i x_i^2}$. The "length."
  - L1 (Manhattan): $\|\mathbf{x}\|_1 = \sum_i |x_i|$. Promotes sparsity (L1 regularization).
  - L∞ (max): $\|\mathbf{x}\|_\infty = \max_i |x_i|$.
- **Outer product:** $\mathbf{x} \mathbf{y}^\top \in \mathbb{R}^{n \times m}$. Produces a matrix.

The dot product deserves the most attention, because it is the foundation of attention ($Q K^\top$ is a matrix of dot products), neural network layers ($\mathbf{w}^\top \mathbf{x}$ is a single neuron's pre-activation), and distance computations ($\|\mathbf{x} - \mathbf{y}\|_2^2 = \|\mathbf{x}\|^2 - 2\mathbf{x}^\top \mathbf{y} + \|\mathbf{y}\|^2$). That last identity is why distance-based methods, such as K-Means clustering, ultimately reduce to dot products and norms (see [[Clustering]]).

## Matrices

A **matrix** $A \in \mathbb{R}^{m \times n}$ is a 2D array of $m$ rows and $n$ columns. In ML, matrices represent:

- A dataset ($X \in \mathbb{R}^{n \times d}$: $n$ samples, $d$ features).
- A weight layer ($W \in \mathbb{R}^{d_{out} \times d_{in}}$).
- An attention matrix ($A \in \mathbb{R}^{T \times T}$).
- A covariance matrix ($\Sigma \in \mathbb{R}^{d \times d}$).

### Matrix operations

The standard matrix operations, with the facts about them that get used constantly:

- **Addition:** $A + B$, component-wise (must be same shape).
- **Scalar multiplication:** $cA$.
- **Matrix multiplication:** $AB$. The $(i,j)$ entry is $\sum_k A_{ik} B_{kj}$. Requires $A \in \mathbb{R}^{m \times k}$, $B \in \mathbb{R}^{k \times n}$; produces $\mathbb{R}^{m \times n}$.
- **Transpose:** $A^\top$, swap rows and columns. $(AB)^\top = B^\top A^\top$.
- **Inverse:** $A^{-1}$, the matrix such that $A^{-1} A = I$. Only exists for square, full-rank matrices.
- **Trace:** $\text{tr}(A) = \sum_i A_{ii}$ (sum of diagonal). $\text{tr}(AB) = \text{tr}(BA)$.
- **Determinant:** $|A|$ or $\det(A)$. Zero iff $A$ is not invertible.

### Why matrix multiplication is the central operation

A neural network layer is $\mathbf{y} = W \mathbf{x} + \mathbf{b}$ — a matrix multiplication followed by a vector addition. Stacking layers composes matrix multiplications. The entire forward pass of a deep network is a sequence of matrix multiplies (with nonlinearities in between). This is why GPUs, which are optimized for matrix multiplication, are so effective for deep learning — the entire computation reduces to dense linear algebra.

Attention is also matrix multiplication: $\text{softmax}(QK^\top / \sqrt{d_k}) V$ is two matrix multiplies and a softmax. The efficiency of attention on GPUs comes from this — it is just dense linear algebra, like everything else in DL.

## Eigendecomposition and eigenvalues

A vector $\mathbf{v}$ is an **eigenvector** of a square matrix $A$ if $A \mathbf{v} = \lambda \mathbf{v}$ for some scalar $\lambda$ (the **eigenvalue**). The eigenvector's direction is unchanged by the transformation $A$; only its magnitude is scaled by $\lambda$.

For a symmetric matrix $A = A^\top$ (which includes all covariance matrices and all $A^\top A$ matrices), the eigendecomposition is:

$$A = Q \Lambda Q^\top$$

where $Q$ is orthogonal (columns are eigenvectors) and $\Lambda$ is diagonal (eigenvalues).

### Why eigenvalues matter for ML

Five staples of machine learning are eigenvalue statements at heart:

1. **PCA**: the principal components are the eigenvectors of the data's covariance matrix, sorted by eigenvalue. The eigenvalues tell you how much variance each component captures (see [[Principal Component Analysis]]).
2. **Hessian analysis** (optimization): the eigenvalues of the Hessian (matrix of second derivatives of the loss) tell you about the loss landscape's curvature. Positive eigenvalues = bowl (minimum); negative = ridge (saddle); mixed = saddle point (see [[01 - Foundations/Mathematical Foundations/Jacobians and Hessians|Jacobians and Hessians]]).
3. **Spectral clustering**: clustering using the eigenvectors of a graph Laplacian.
4. **PageRank**: the stationary distribution of a Markov chain is the top eigenvector of the transition matrix.
5. **Stability of RNNs**: the eigenvalues of the recurrent weight matrix $W_h$ determine whether gradients vanish (spectral radius < 1) or explode (spectral radius > 1). See [[07 - Sequence Models/Motivation and Recurrence/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]].

## Singular value decomposition

SVD decomposes any matrix $A \in \mathbb{R}^{m \times n}$ into three matrices:

$$A = U \Sigma V^\top$$

where:

- $U \in \mathbb{R}^{m \times m}$ is orthogonal (left singular vectors).
- $\Sigma \in \mathbb{R}^{m \times n}$ is diagonal (singular values, non-negative, sorted).
- $V \in \mathbb{R}^{n \times n}$ is orthogonal (right singular vectors).

SVD exists for **any** matrix (not just square symmetric ones) and is the most useful matrix decomposition in numerical linear algebra.

### Why SVD matters for ML

Four applications make SVD the workhorse decomposition:

1. **PCA**: principal component analysis is SVD of the centered data matrix. The principal components are the right singular vectors; the explained variance is the squared singular values.
2. **Low-rank approximation**: truncating SVD to the top $k$ singular values gives the best rank-$k$ approximation to $A$ (Eckart-Young theorem). This is the foundation of:
   - **Latent semantic analysis** (LSA) in NLP.
   - **Collaborative filtering** for recommender systems.
   - **LoRA** (Low-Rank Adaptation) for efficient LLM fine-tuning — represent weight updates as $AB$ where $A, B$ are low-rank (see [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]]).
3. **Pseudoinverse**: $A^+ = V \Sigma^+ U^\top$ (where $\Sigma^+$ inverts non-zero singular values) gives the least-squares solution to $A\mathbf{x} = \mathbf{b}$. This is how the Normal Equation $(X^\top X)^{-1} X^\top y$ for linear regression works — and SVD tells you when it fails (when $X$ is rank-deficient). See [[04 - Machine Learning/Regression/Linear Regression|Linear Regression]].
4. **Matrix compression**: a $1000 \times 1000$ matrix (1M numbers) can often be approximated by rank-10 SVD (20K numbers) with minimal error — the basis of model compression.

## Tensors

A **tensor** is the generalization of vectors (1st-order) and matrices (2nd-order) to arbitrary order. A 3rd-order tensor has three axes; a 4th-order tensor has four.

In deep learning:

- A batch of grayscale images is a 4th-order tensor: $(\text{batch}, \text{channels}, \text{height}, \text{width})$.
- A batch of RGB images is also 4th-order: $(\text{batch}, 3, H, W)$.
- A sequence of token embeddings is 3rd-order: $(\text{batch}, \text{sequence}, \text{embedding})$.

Tensor operations (contraction, reshaping, broadcasting) generalize matrix operations. The key skill for working with deep learning frameworks (PyTorch, TensorFlow) is **tensor shape manipulation** — knowing how to reshape, transpose, and broadcast tensors to make operations work. See [[Demystifying Tensors - Volumes, Depth, and Data Formats]] for the CNN-specific treatment, and [[Tensors and Broadcasting]] for the broadcasting side.

## The Hadamard product

The **Hadamard product** $A \odot B$ is element-wise multiplication: $(A \odot B)_{ij} = A_{ij} \cdot B_{ij}$. This is distinct from matrix multiplication $AB$.

The Hadamard product appears in:

- **LSTM gates:** $C_t = f_t \odot C_{t-1} + i_t \odot \tilde{C}_t$ — the forget gate element-wise scales the cell state (see [[LSTM]]).
- **Dropout:** the dropout mask is element-wise multiplied with activations (see [[05 - Neural Network Foundations/Training Dynamics and Stability/Dropout and Regularization|Dropout and Regularization]]).
- **Attention masking:** the causal mask is element-wise added to the attention scores (setting future positions to $-\infty$); see [[Scaled Dot-Product Attention]].

> [!warning] A common source of bugs
> Confusing $\odot$ (Hadamard) with $\cdot$ or juxtaposition (matrix multiplication) is a common source of bugs — pay attention to which one a paper or code is using.

## What you should walk away with

1. **Vectors** are ordered lists; dot products measure alignment; norms measure length.
2. **Matrices** are 2D arrays; matrix multiplication is the central operation of DL (every layer is a matmul).
3. **Eigenvalues/eigenvectors** capture the "natural axes" of a linear transformation; they underlie PCA, Hessian analysis, RNN stability, and spectral methods.
4. **SVD** decomposes any matrix into orthogonal-diagonal-orthogonal form; it is the foundation of PCA, low-rank approximation, pseudoinverse, and LoRA.
5. **Tensors** generalize matrices to arbitrary order; DL frameworks operate on tensors.
6. **Hadamard product** ($\odot$) is element-wise multiplication, distinct from matrix multiplication; common in gates, dropout, and masking.

## See also

- [[Foundations MOC]]
- [[Mathematical Notation]]
- [[Gradients and Gradient Descent]]
- [[01 - Foundations/Mathematical Foundations/Jacobians and Hessians|Jacobians and Hessians]]
- [[Probability and Statistics for ML]]
- [[Vectors]]
- [[Dot Product]]
- [[Matrix Multiplication]]
- [[Matrix Decomposition]]
- [[Tensors and Broadcasting]]
- [[Principal Component Analysis]]
- [[Clustering]]
- [[04 - Machine Learning/Regression/Linear Regression|Linear Regression]]
- [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]]
- [[07 - Sequence Models/Motivation and Recurrence/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Batch Normalization|Batch Normalization]]
- [[LSTM]]
- [[Demystifying Tensors - Volumes, Depth, and Data Formats]]
- [[Scaled Dot-Product Attention]]
