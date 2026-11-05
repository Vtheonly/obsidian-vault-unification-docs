---
title: Notation Conventions
type: reference
aliases: ["Notation Conventions", "Math Notation", "Symbol Conventions"]
tags: [glossary, notation, conventions, mathematics, reference]
sources: ["03 - Notation Conventions"]
created_index: 4
---

This note defines the mathematical and symbolic notation used throughout the vault. Consistent notation matters because AI engineering spans linear algebra, calculus, probability, information theory, and computer science — each with its own conventions. Without a single reference, the same symbol can mean different things in different notes (e.g., $T$ for temperature vs. $T$ for transpose vs. $T$ for tokens). This note resolves those ambiguities and provides the standard forms for vectors, matrices, attention, gradients, and probability distributions.

## Why notation conventions matter

Mathematical notation in AI is inconsistent across sources. The Transformer paper (Vaswani et al., 2017) uses $d_k$ for key dimension; the BERT paper uses $d$ for hidden size; some tutorials use $H$ for hidden states while others use $h$. Without a reference, readers must infer meaning from context — slow and error-prone.

This note establishes the conventions used throughout the vault. When a note deviates from these conventions, it states the deviation explicitly.

## General principles

Eight typographic rules cover the bulk of the notation:

1. **Bold uppercase** ($\mathbf{X}$): matrices.
2. **Bold lowercase** ($\mathbf{x}$): vectors.
3. **Regular lowercase** ($x$, $i$, $j$): scalars and indices.
4. **Uppercase** ($X$, $T$, $N$): random variables or sizes (context-dependent, stated in the note).
5. **Calligraphic** ($\mathcal{L}$, $\mathcal{D}$): sets, loss functions, distributions.
6. **Greek letters**: parameters ($\theta$, $\phi$), hyperparameters ($\alpha$, $\beta$, $\gamma$), small constants ($\epsilon$).
7. **Subscripts**: indices ($x_i$, $h_t$).
8. **Superscripts**: layer or step ($h^{(l)}$, $z^{(t)}$). Use parentheses to distinguish from exponentiation ($x^2$ vs $x^{(2)}$).

## Linear algebra

### Vectors

Vectors are bold lowercase; their elements are indexed with regular lowercase subscripts.

- $\mathbf{x} \in \mathbb{R}^d$: a real-valued vector of dimension $d$.
- $x_i$: the $i$-th element of $\mathbf{x}$ (1-indexed unless noted).
- $\|\mathbf{x}\|_2$: L2 norm.
- $\|\mathbf{x}\|_1$: L1 norm.
- $\hat{\mathbf{x}} = \mathbf{x} / \|\mathbf{x}\|_2$: the unit vector in the direction of $\mathbf{x}$.

### Matrices

Matrices are bold uppercase, with elements indexed by row and column.

- $\mathbf{X} \in \mathbb{R}^{m \times n}$: a real-valued matrix with $m$ rows and $n$ columns.
- $\mathbf{X}_{ij}$ or $X_{ij}$: the element at row $i$, column $j$.
- $\mathbf{X}^\top$: transpose.
- $\mathbf{X}^{-1}$: inverse (for square matrices).
- $\mathbf{I}$: identity matrix (size inferred from context).

### Operations

The standard product operations each get their own symbol; the dot product returns a scalar, the outer product a matrix.

- $\mathbf{x} \cdot \mathbf{y}$ or $\mathbf{x}^\top \mathbf{y}$: dot product (scalar).
- $\mathbf{x} \otimes \mathbf{y}$: outer product (matrix).
- $\mathbf{X} \mathbf{Y}$: matrix product.
- $\mathbf{X} \odot \mathbf{Y}$: Hadamard (element-wise) product.
- $\text{diag}(\mathbf{x})$: diagonal matrix with $\mathbf{x}$ on the diagonal.

### Norms and similarity

Similarity and distance are defined through the norms above.

- $\cos(\mathbf{x}, \mathbf{y}) = \frac{\mathbf{x} \cdot \mathbf{y}}{\|\mathbf{x}\|_2 \|\mathbf{y}\|_2}$: cosine similarity.
- $\|\mathbf{x} - \mathbf{y}\|_2$: Euclidean distance.

### Decompositions

Matrix factorizations are written as equations with the conventional factor names.

- $\mathbf{X} = \mathbf{U} \mathbf{\Sigma} \mathbf{V}^\top$: SVD.
- $\mathbf{X} = \mathbf{Q} \mathbf{R}$: QR decomposition.
- $\text{eig}(\mathbf{X})$: eigenvalues.

## Tensors

Tensors generalize vectors and matrices to arbitrary order and are distinguished by calligraphic symbols.

- $\mathcal{X} \in \mathbb{R}^{n_1 \times n_2 \times \cdots \times n_k}$: a $k$-dimensional tensor.
- $\mathcal{X}_{i_1, i_2, \ldots, i_k}$: an element.
- Broadcasting follows NumPy conventions: dimensions of size 1 are repeated.

## Attention

The Transformer attention mechanism has standard notation, used throughout [[Self-Attention]] and [[Multi-Head Attention]]:

- $\mathbf{Q}, \mathbf{K}, \mathbf{V}$: query, key, value matrices. Each row is a token's representation.
- $d_k, d_v$: key and value dimensions (often equal; use $d$ when they are).
- $d_{\text{model}}$: model hidden size.
- $h$: number of attention heads.
- $d_h = d_{\text{model}} / h$: per-head dimension.

Scaled dot-product attention:

$$\text{Attention}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{softmax}\left(\frac{\mathbf{Q} \mathbf{K}^\top}{\sqrt{d_k}}\right) \mathbf{V}$$

Multi-head attention:

$$\text{MultiHead}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h) \mathbf{W}^O$$

where $\text{head}_i = \text{Attention}(\mathbf{Q} \mathbf{W}_i^Q, \mathbf{K} \mathbf{W}_i^K, \mathbf{V} \mathbf{W}_i^V)$.

## Probability

Probability notation keeps random variables, their values, and distributions typographically distinct.

### Random variables

- $X$: a random variable.
- $x$: a specific value of $X$.
- $P(X = x)$ or $P(x)$: probability mass (discrete) or density (continuous).
- $p(x \mid y)$: conditional probability density.

### Distributions

Common distributions are named by their family with parameters in parentheses.

- $\mathcal{N}(\mu, \sigma^2)$: Gaussian with mean $\mu$ and variance $\sigma^2$.
- $\text{Bernoulli}(p)$: Bernoulli with parameter $p$.
- $\text{Cat}(p_1, \ldots, p_K)$: categorical over $K$ classes.
- $\text{Uniform}(a, b)$: uniform on $[a, b]$.

### Statistics

Expectations and related quantities use standard functional notation, and hats mark estimates.

- $\mathbb{E}[X]$: expectation.
- $\text{Var}(X)$: variance.
- $\text{Cov}(X, Y)$: covariance.
- $\hat{\theta}$: an estimate of $\theta$.

### Information theory

The information-theoretic quantities that appear in loss functions are defined as follows.

- $H(X) = -\sum_x p(x) \log p(x)$: entropy.
- $H(p, q) = -\sum_x p(x) \log q(x)$: cross entropy.
- $D_{\text{KL}}(p \| q) = \sum_x p(x) \log \frac{p(x)}{q(x)}$: KL divergence.
- $I(X; Y)$: mutual information.

These definitions are used throughout [[Entropy Cross-Entropy and KL Divergence]].

## Calculus and optimization

Derivative notation distinguishes total, partial, gradient, Jacobian, and Hessian objects; optimization notation centers on the loss and its gradient.

### Derivatives

- $\frac{df}{dx}$: derivative of $f$ with respect to $x$.
- $\frac{\partial f}{\partial x}$: partial derivative.
- $\nabla f$: gradient (vector of partials).
- $\nabla_{\mathbf{x}} f$: gradient with respect to $\mathbf{x}$.
- $\nabla^2 f$ or $\mathbf{H}_f$: Hessian (matrix of second partials).
- $\mathbf{J}_f$: Jacobian.

### Optimization

- $\mathcal{L}(\theta)$: loss function.
- $\theta$: model parameters.
- $\phi$: sometimes used for additional parameters (e.g., discriminator in GANs, value function in RL).
- $\alpha$ or $\eta$: learning rate.
- $\nabla_\theta \mathcal{L}$: gradient of loss with respect to parameters.
- $\theta \leftarrow \theta - \alpha \nabla_\theta \mathcal{L}$: gradient descent update.

## Sequences and time

Sequence modeling reserves $T$ for the sequence length and $t$ for the position index.

- $T$: sequence length (number of tokens). **Not** temperature in this context.
- $t$: time step or position index.
- $\mathbf{x}_t$: the token at position $t$.
- $\mathbf{x}_{1:t}$: the sequence $\mathbf{x}_1, \mathbf{x}_2, \ldots, \mathbf{x}_t$.
- $\mathbf{h}_t^{(l)}$: hidden state at position $t$ in layer $l$.

## Special symbols

A handful of symbols have fixed meanings or explicit disambiguation rules.

- $\tau$: temperature (in softmax and sampling). When used, state explicitly to avoid confusion with $T$.
- $\sigma$: sigmoid function, $\sigma(x) = 1 / (1 + e^{-x})$. **Not** standard deviation (use $s$ or $\sigma_X$ with subscript for std).
- $\text{softmax}$: the softmax function, $\text{softmax}(\mathbf{x})_i = \frac{e^{x_i}}{\sum_j e^{x_j}}$.
- $\epsilon$: small constant (e.g., for numerical stability).
- $\top$: transpose (as superscript).
- $\approx$: approximately equal.
- $\sim$: sampled from (e.g., $x \sim \mathcal{N}(0, 1)$).
- $\propto$: proportional to.

## Reinforcement learning

Reinforcement learning notation follows the standard MDP vocabulary of states, actions, rewards, and policies; see [[Markov Decision Processes and Bellman Equations]] for the underlying framework.

- $s_t$: state at time $t$.
- $a_t$: action at time $t$.
- $r_t$: reward at time $t$.
- $\pi(a \mid s)$: policy (probability of action $a$ given state $s$).
- $\gamma$: discount factor.
- $Q(s, a)$: action-value function.
- $V(s)$: state-value function.
- $A(s, a) = Q(s, a) - V(s)$: advantage function.

## Information theory in ML context

Two symbols carry alignment-specific meaning in RLHF-style training.

- $\text{KL}(\pi \| \pi_{\text{ref}})$: KL penalty (used in RLHF to keep policy close to reference).
- $\beta$: KL penalty coefficient.

## Subscripts and superscripts summary

The table below collects the subscript and superscript conventions in one place.

| Symbol                  | Meaning                                        |
|-------------------------|------------------------------------------------|
| $x_i$                   | Element $i$ of vector $\mathbf{x}$.            |
| $X_{ij}$                | Element at row $i$, column $j$ of $\mathbf{X}$. |
| $\mathbf{h}^{(l)}$      | Hidden state at layer $l$.                     |
| $\mathbf{h}_t$          | Hidden state at time step $t$.                 |
| $\mathbf{h}_t^{(l)}$    | Hidden state at time $t$, layer $l$.           |
| $\theta_t$              | Parameters at training step $t$.               |
| $\hat{y}$               | Predicted value of $y$.                        |
| $\bar{x}$               | Mean of $x$.                                   |

## Common conflicts and disambiguation

The same symbol is routinely overloaded across the literature; the table lists the frequent conflicts and the resolution adopted here.

| Symbol | Common Meaning 1         | Common Meaning 2                | Resolution                                |
|--------|--------------------------|----------------------------------|--------------------------------------------|
| $T$    | Sequence length          | Temperature                      | Use $\tau$ for temperature.                |
| $H$    | Hidden size              | Entropy                          | Context-dependent; state in note.          |
| $h$    | Hidden state             | Number of attention heads        | Use $d_{\text{model}}$ for size, $h$ for heads. |
| $\sigma$ | Sigmoid                | Standard deviation               | Use $s$ for std; $\sigma_X$ if needed.     |
| $N$    | Number of samples        | Sequence length (some papers)    | Use $T$ for sequence length.               |
| $K$    | Number of classes        | Number of attention heads (rare) | Use $h$ for heads; $K$ for classes.        |
| $V$    | Value matrix             | Vocabulary size (some papers)    | Use $\|V\|$ for vocab size.                   |
| $D$    | Dataset                  | Dimension                        | Use $d$ for dimension; $\mathcal{D}$ for dataset. |

One resolution deserves a spelling outside the grid: the $V$ row's rule keeps the cardinality notation for the vocabulary size exactly as the source writes it, $|V|$ — the table cell escapes those pipes only so the row renders with four columns.

## Code conventions

In code blocks, variable names mirror the mathematical symbols so that code can be read directly against the equations.

- Variables match the math: `Q`, `K`, `V`, `d_model`, `num_heads`.
- Function names are lowercase with underscores: `scaled_dot_product_attention`.
- Class names are PascalCase: `MultiHeadAttention`.
- Constants are UPPER_CASE: `MAX_SEQ_LEN`.

## References

The conventions in this note are based on:

- Vaswani et al. (2017) — Transformer notation ($Q, K, V, d_k$).
- Goodfellow, Bengio, Courville (2016) — Deep Learning textbook conventions.
- Bishop (2006) — Pattern Recognition and Machine Learning conventions.
- NumPy / PyTorch documentation — programming conventions.

When the material a note covers uses different conventions, the note either:

1. Adopts these conventions (preferred), or
2. Uses the source's conventions and states the mapping.

## See also

The companion reference notes, plus the area where most of this notation is exercised:

- [[Glossary MOC]] — the glossary hub
- [[A-Z Terms]] — glossary of AI engineering terms
- [[Acronyms Index]] — index of acronyms
- [[Mathematics MOC]] — where most of this notation is used
