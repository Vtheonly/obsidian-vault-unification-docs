---
title: Self-Attention
type: derivation
aliases:
  - Scaled Dot-product Attention
  - QKV Attention
tags:
  - attention
  - self-attention
  - scaled-dot-product
  - transformer
  - complexity-analysis
sources:
  - "01. Self-Attention — When the Sequence Attends to Itself"
  - "Self-Attention"
created_index: 10
---

Self-attention is attention where the queries, keys, and values all come from the same sequence: every position attends to every other position, with no recurrence in between. It is the operation that makes the RNN redundant and the heart of every Transformer since Vaswani et al. (2017). This note derives the full formula step by step, explains every term including the essential $\sqrt{d_k}$ scaling, works through numeric examples, gives PyTorch implementations from naive to production-grade, and analyzes the quadratic cost that defines the long-context problem.

> [!info] TL;DR
> Each token's representation is recomputed as a weighted average of all tokens' value vectors, where the weights come from the dot-product similarity between its query and each key. The note derives the formula, explains every term, shows why scaling by $\sqrt{d_k}$ is essential, provides full implementation, discusses what attention learns, complexity analysis, comparisons to alternatives, and the role of self-attention across the AI stack.

## The generalization that killed the RNN

Bahdanau attention was **cross-attention**: a decoder attended to an encoder. The query came from one sequence, the keys and values from another. This fixed the encoder-decoder bottleneck, in which a single fixed-length vector had to carry the entire input sequence to the decoder.

The Transformer's key insight (Vaswani et al. 2017) is a generalization: attention is useful even when there is only one sequence. Let every position in a sequence attend to every other position in the *same* sequence. This is **self-attention**, and it is the operation that makes the RNN redundant. Where [[08 - Attention and Transformers/Attention Mechanism/Bahdanau Attention|Bahdanau Attention]] and [[08 - Attention and Transformers/Attention Mechanism/Luong Attention|Luong Attention]] bolted an attention module onto a recurrent encoder-decoder, self-attention replaces the recurrence itself — see [[Origins of Attention]] for how this line of work developed and [[The Bottleneck Problem]] for the limitation it resolves.

## Why self-attention replaces recurrence

Recall the job of the RNN: propagate information across time so that position $t$ can "know about" position $i < t$. The RNN does this by carrying a hidden state forward, applying a transformation at each step. The cost is that information from position $i$ must traverse $|t - i|$ steps to reach position $t$, and each step is an opportunity for the information to be distorted or lost.

Self-attention does this job directly. Position $t$ attends to position $i$ in a single step — there is no chain of intermediate transformations. The attention weight $\alpha_{t,i}$ is computed from the dot product of $t$'s query and $i$'s key, and the value from $i$ flows directly into $t$'s output. The path length between any two positions is 1, regardless of distance.

This is the **path length argument** from [[Long-Range Dependencies]], and it is the deepest reason the Transformer outperforms the RNN on long-range dependencies. It removes the long-range decay problem that plagues recurrence, the same failure mode documented in [[07 - Sequence Models/Motivation and Recurrence/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]] and the motivation behind the shift traced in [[From RNNs to Attention]].

## The formula

For an input sequence $\mathbf{X} \in \mathbb{R}^{n \times d}$ (n tokens, d dimensions — some treatments write $T$ for the number of tokens and $d$ for the model dimension; the two notations are interchangeable), self-attention computes:

$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{Q K^T}{\sqrt{d_k}}\right) V
$$

where:

- $Q = \mathbf{X} \mathbf{W}_Q \in \mathbb{R}^{n \times d_k}$ — **queries**
- $K = \mathbf{X} \mathbf{W}_K \in \mathbb{R}^{n \times d_k}$ — **keys**
- $V = \mathbf{X} \mathbf{W}_V \in \mathbb{R}^{n \times d_v}$ — **values**

$\mathbf{W}_Q, \mathbf{W}_K, \mathbf{W}_V$ are learned projection matrices. In most Transformers $d_k = d_v = d / h$ where $h$ is the number of heads; see [[Multi-Head Attention]].

The output has shape $\mathbb{R}^{n \times d_v}$ — same number of tokens as input, but each token's representation is now a mixture of all tokens' value vectors. Written as an operation on the input directly:

$$Q = X W_Q, \quad K = X W_K, \quad V = X W_V$$
$$\text{SelfAttention}(X) = \text{softmax}\left(\frac{Q K^\top}{\sqrt{d_k}}\right) V$$

The input $X \in \mathbb{R}^{T \times d}$ is a sequence of $T$ token embeddings. The output is also $\mathbb{R}^{T \times d}$ — a sequence of the same length, where each position's representation is now a weighted average of all positions' values, weighted by attention scores.

Critically, every position can attend to every other position in encoder self-attention; decoder self-attention is masked, covered in [[Transformer Decoder Block]]. Position 1 can attend to position 50; position 50 can attend to position 1. The attention is bidirectional and dense. The per-token mechanics of the three projected roles are developed in [[Queries Keys and Values]] and the scaled dot-product core in [[Scaled Dot-Product Attention]].

## Intuition: a soft database lookup

Think of self-attention as **soft database lookup**:

- **Query** ($Q$): "what am I looking for?"
- **Keys** ($K$): "what do I have?"
- **Values** ($V$): "what do I return if matched?"

Each token issues a query. Every token (including itself) has a key. The dot product $Q K^T$ measures how much each token's key matches each token's query. Softmax normalizes these into weights. The weighted sum of values becomes the new representation of each token.

The crucial difference from a real database: it's **soft** — every value contributes, just with different weights. This makes it differentiable and learnable.

### Why three different projections

Why not just use $\mathbf{X}$ directly as Q, K, V? Because the three projections let the model learn different "views" of the same input:

- $Q = \mathbf{X} \mathbf{W}_Q$: what this token is *looking for* in other tokens.
- $K = \mathbf{X} \mathbf{W}_K$: what this token is *advertising* to other tokens.
- $V = \mathbf{X} \mathbf{W}_V$: what this token *contributes* when attended to.

Without these projections, attention would be a fixed function of $\mathbf{X}$ — no learned parameters, no adaptability. The projections give the model 3$d^2$ learnable parameters per attention layer, which is where most of the attention's expressivity comes from.

### The "self" in self-attention

In **self-attention**, $Q$, $K$, and $V$ all come from the **same** sequence $\mathbf{X}$. The tokens attend to each other. This is the standard attention in encoder layers and decoder layers.

In **cross-attention** (encoder-decoder attention), $Q$ comes from one sequence (e.g., the decoder) and $K, V$ from another (e.g., the encoder). Used in encoder-decoder models like T5 and BART (see [[T5 and BART]]), and in multimodal models (LLaVA: decoder queries attend to vision encoder's K, V).

In **masked self-attention** (causal self-attention), $Q$, $K$, $V$ come from the same sequence, but a causal mask prevents token $i$ from attending to tokens $j > i$. Used in decoder-only LLMs (GPT, Llama, Mistral) — see [[GPT Family]] and [[Autoregressive vs Parallel Encoding]].

## What self-attention computes: a contextualizer

After self-attention, the representation at position $t$ is no longer just the embedding of token $t$ — it is a **contextualized** representation that incorporates information from all other tokens, weighted by relevance. The word "bank" in "I sat by the river bank" and in "I deposited cash at the bank" starts with the same embedding but emerges from self-attention with different contextualized representations, because the surrounding tokens pull in different information.

This is the sense in which self-attention is a **contextualizer**: it replaces static word embeddings with dynamic, context-dependent representations. This is why Transformer-based word representations (BERT, GPT) dramatically outperform static embeddings (word2vec, GloVe) on virtually every NLP task — the representation of a word is no longer fixed but adapts to its context. The transition from static to contextual embeddings is traced in [[Word2Vec GloVe and FastText]] and [[Contextual Embeddings ELMo to BERT]].

## Step-by-step derivation

The formula decomposes into six mechanical steps, each of which is a differentiable matrix operation.

### Step 1: project to Q, K, V

Given input $\mathbf{X} \in \mathbb{R}^{n \times d}$, project to three matrices:

$$
Q = \mathbf{X} \mathbf{W}_Q, \quad K = \mathbf{X} \mathbf{W}_K, \quad V = \mathbf{X} \mathbf{W}_V
$$

These projections let the model learn different "views" of the same input — what to look for (Q), what to advertise (K), and what to return (V).

Each projection is a linear layer (matrix multiplication). In PyTorch: `nn.Linear(d, d_k, bias=False)`.

### Step 2: compute similarities

$Q K^T \in \mathbb{R}^{n \times n}$ is a matrix of dot products. Entry $(i, j)$ is the similarity between token $i$'s query and token $j$'s key.

$$
(Q K^T)_{ij} = \sum_{k=1}^{d_k} Q_{ik} K_{jk} = \mathbf{q}_i \cdot \mathbf{k}_j
$$

This is the "compatibility matrix" — how much each query wants to attend to each key. The diagonal entries ($i = j$) are self-similarity (a token attending to itself).

### Step 3: scale

Divide by $\sqrt{d_k}$:

$$
S = \frac{Q K^T}{\sqrt{d_k}}
$$

**Why scale?** See the dedicated section below — this is the most important detail in self-attention.

### Step 4: (optional) apply a mask

For causal attention (decoder), apply a lower-triangular mask:

$$
S_{ij} = \begin{cases} S_{ij} & \text{if } j \leq i \\ -\infty & \text{if } j > i \end{cases}
$$

This prevents token $i$ from attending to future tokens. For padding, mask positions where the input is a `<PAD>` token.

### Step 5: softmax

Apply softmax row-wise (each row of $S$ becomes a probability distribution over tokens):

$$
A = \text{softmax}(S) \quad \text{where} \quad A_{ij} = \frac{\exp(S_{ij})}{\sum_k \exp(S_{ik})}
$$

$A$ is the **attention weight matrix**. Each row sums to 1. Entry $A_{ij}$ is the probability that token $i$ attends to token $j$.

### Step 6: weighted average of values

$$
\text{Output} = A V
$$

The output is $\mathbb{R}^{n \times d_v}$ — same shape as $V$. Each output token is a convex combination of all value vectors, weighted by attention:

$$
\text{Output}_i = \sum_{j=1}^{n} A_{ij} \mathbf{v}_j
$$

Token $i$'s new representation is a weighted average of all tokens' value vectors, with weights from the attention matrix.

### Why a convex combination

Because softmax outputs are non-negative and sum to 1, the output is a **convex combination** of value vectors. This has nice properties:

- The output stays in the convex hull of the value vectors (no extrapolation).
- The output magnitude is bounded by the max value magnitude.
- The gradient flows cleanly through the softmax weights.

## Why scale by √d_k

This is the most important detail in self-attention. Without it, training is unstable for any non-trivial $d_k$.

### The problem

For random $\mathbf{q}, \mathbf{k} \in \mathbb{R}^{d_k}$ with mean 0, variance 1, the dot product $\mathbf{q} \cdot \mathbf{k} = \sum_{i=1}^{d_k} q_i k_i$ has:

- Mean 0
- **Variance $d_k$** (sum of $d_k$ terms, each with variance 1; assuming independence)

So the standard deviation of the dot product grows as $\sqrt{d_k}$.

### The consequence

For large $d_k$ (e.g., 64 or 128), the dot products can be large in magnitude. Softmax then saturates: one entry becomes ≈1, all others ≈0. This creates:

1. **Vanishing gradients** — softmax's gradient is $\approx 0$ when saturated.
2. **Sharp attention** — the model can't learn soft patterns; it's forced into argmax-like behavior.
3. **Training instability** — small changes in input produce large changes in attention weights.

### The fix

Divide by $\sqrt{d_k}$ to bring the standard deviation back to 1:

$$
\text{Var}\left(\frac{\mathbf{q} \cdot \mathbf{k}}{\sqrt{d_k}}\right) = \frac{d_k}{d_k} = 1
$$

This keeps softmax in its "nice" regime (non-saturated, well-conditioned gradients) regardless of dimension.

### Worked example

For $d_k = 64$:

- Without scaling: typical dot product magnitude $\approx \sqrt{64} = 8$.
- With $\sqrt{d_k}$ scaling: typical dot product magnitude $\approx 1$.
- After softmax on logits $\sim (8, 4, -2, ...)$ vs $(1, 0.5, -0.25, ...)$ — the unscaled version saturates much more.

For $d_k = 128$ (typical for Llama 3): dot products can reach ~11 without scaling. After softmax of `(11, 5, 2, ...)`: the top entry gets $\exp(11) / (\exp(11) + \exp(5) + ...) \approx 1.0$. The model can't distinguish between moderately-relevant and irrelevant tokens.

### Derivation: why variance grows as d_k

Each term $q_i k_i$ is the product of two independent standard normal random variables. The variance of the product of two independent standard normals is 1 (since $\mathbb{E}[q_i^2 k_i^2] = \mathbb{E}[q_i^2] \mathbb{E}[k_i^2] = 1$). Summing $d_k$ independent such terms gives variance $d_k$ (variance of sum of independent random variables is the sum of variances).

So the standard deviation is $\sqrt{d_k}$. Dividing by $\sqrt{d_k}$ gives standard deviation 1.

## Worked example: attention on a short sequence

Consider the sentence "The cat sat on the mat" with 5 tokens. Suppose after embedding, each token is a 4-d vector:

```
Token embeddings (5 × 4):
The:  [1.0, 0.0, 0.5, 0.2]
cat:  [0.0, 1.0, 0.3, 0.1]
sat:  [0.2, 0.3, 1.0, 0.4]
on:   [0.1, 0.1, 0.2, 0.8]
the:  [1.0, 0.1, 0.4, 0.3]
mat:  [0.0, 0.8, 0.2, 0.5]
```

After Q, K, V projections (with learned weights), suppose:

```
Q (queries):
The:  [0.5, 0.1]   — "looking for noun-like context"
cat:  [0.8, 0.2]   — "looking for verb context"
...

K (keys):
The:  [0.3, 0.7]   — "I'm a determiner"
cat:  [0.9, 0.1]   — "I'm a noun"
...

V (values):
The:  [0.1, 0.0, 0.5, 0.0]
cat:  [0.0, 0.9, 0.0, 0.1]
...
```

For token "cat" (position 1), the attention scores (before softmax) are:

```
score(cat, The) = q_cat · k_The = 0.8*0.3 + 0.2*0.7 = 0.38
score(cat, cat) = q_cat · k_cat = 0.8*0.9 + 0.2*0.1 = 0.74
score(cat, sat) = q_cat · k_sat = ...
score(cat, on)  = ...
score(cat, the) = ...
score(cat, mat) = ...
```

After scaling by $\sqrt{d_k} = \sqrt{2}$, softmax, and weighted sum of V, "cat"'s new representation mixes its own value with the values of related tokens (likely "The" and "sat"). The output reflects the context "The cat sat" rather than just "cat" in isolation.

## Computational complexity

The self-attention matrix $QK^\top$ is $T \times T$ — every pair of positions interacts. This means:

- **Compute:** $O(T^2 \cdot d_k)$ for the attention matrix, plus $O(T^2 \cdot d_v)$ for the output.
- **Memory:** $O(T^2)$ to store the attention matrix.

For $T = 512$ (a typical sentence), $T^2 = 262144$ — manageable. For $T = 10000$ (a long document), $T^2 = 10^8$ — expensive. For $T = 100000$ (a whole book or a high-resolution image tokenized into patches), $T^2 = 10^{10}$ — prohibitive.

For sequence length $n$ and head dimension $d_k$, the per-step budget is:

| Step                | FLOPs               | Memory                |
|---------------------|---------------------|-----------------------|
| $Q, K, V$ projection| $3 \cdot n \cdot d \cdot d_k$ | $3 \cdot n \cdot d_k$ |
| $Q K^T$             | $n^2 \cdot d_k$     | $n^2$                 |
| Softmax             | $O(n^2)$            | $n^2$                 |
| $A V$               | $n^2 \cdot d_v$     | $n \cdot d_v$         |

The $O(n^2)$ terms are the bottleneck — both compute and memory scale quadratically with sequence length. This is why long-context is hard.

### Concrete numbers

For Llama 3 8B at sequence length 8192, head dim 128, 32 heads, 32 layers:

- Per head, per layer: $8192^2 = 67M$ attention scores.
- Per layer (32 heads): $32 \times 67M = 2.1B$ scores.
- All layers (32): $32 \times 2.1B = 68B$ scores.
- At 4 bytes (FP32): 272 GB of attention scores per forward pass.

Without FlashAttention (which avoids materializing this matrix), this would OOM any GPU. FlashAttention fuses the computation, keeping memory at $O(n)$ instead of $O(n^2)$.

### The quadratic bottleneck

The $O(n^2)$ scaling is the fundamental limitation of standard attention. Doubling the context length quadruples the attention cost. This is why:

- Pre-2022 LLMs had 2K-4K context: $O(n^2)$ at 4K = 16M scores per head per layer.
- 2023 LLMs (Llama 2, GPT-4) extended to 32K-128K via FlashAttention and RoPE scaling.
- 2024-2026 LLMs (Gemini 1.5 Pro, Claude 3.5) reach 200K-2M context via Ring Attention, hybrid architectures, and aggressive optimization.
- Long-context research (Mamba, Hyena, linear attention) aims to break $O(n^2)$ entirely.

This quadratic cost is the main limitation of self-attention and the subject of a large research literature on **efficient attention** — sparse attention, linear attention, flash attention, state-space models. For the core Transformer, we accept the quadratic cost and work with sequences of moderate length. The specific escape routes are covered in [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]], [[Sparse Attention]], [[Linear Attention]], and [[Sliding Window Attention]].

## Why self-attention is parallelizable and the RNN is not

The RNN is **sequential**: step $t$ depends on step $t-1$, so you cannot compute step $t$ until step $t-1$ is done. Training an RNN on a sequence of length $T$ takes $O(T)$ serial time, regardless of how many GPUs you have.

Self-attention is **parallel**: all $T$ queries are computed simultaneously (it is just a matrix multiplication), and all $T \times T$ attention weights are computed simultaneously. Training a Transformer on a sequence of length $T$ takes $O(1)$ serial time (with enough parallelism), plus the $O(T^2)$ total work distributed across GPUs.

This is the second key advantage of the Transformer over the RNN, after the path-length argument. The ability to parallelize across time is what made it feasible to train Transformers on web-scale datasets — you can use GPUs efficiently in a way that RNNs fundamentally cannot.

## Self-attention vs convolution vs recurrence

It is illuminating to compare self-attention to the other two weight-sharing architectures:

| Property | CNN | RNN | Self-attention |
| :--- | :--- | :--- | :--- |
| Weight sharing axis | Space (kernel slides) | Time (cell slides) | None — all pairs interact |
| Receptive field | Local, grows with depth | Local, grows linearly with steps | Global — every position sees every other |
| Path length between distant tokens | $O(\log T)$ with stacked layers | $O(T)$ | $O(1)$ |
| Parallelizable across the axis | Yes | **No** | Yes |
| Parameter count vs. input size | Independent | Independent | Independent |
| Inductive bias | Translation equivariance, locality | Temporal order, Markov-ish | Almost none (just permutation equivariance) |

The last row is the deepest difference. CNNs encode a strong prior: "patterns repeat across space, and nearby pixels are more related than distant ones." RNNs encode a different prior: "the past influences the future, in order." Self-attention encodes almost no prior: it lets the data decide what relates to what. This is why ViTs need more data than CNNs — with less inductive bias, the model must learn the prior from data, as discussed in [[Inductive Bias]] and [[ViT Architecture]].

## Comparison to other sequence mixers

Self-attention isn't the only way to mix information across sequence positions. Alternatives:

| Sequence Mixer | Complexity | Strengths | Weaknesses |
|----------------|------------|-----------|------------|
| Self-attention | $O(n^2)$ | Content-based routing; flexible; interpretable | Quadratic cost; long-context hard |
| RNN/LSTM | $O(n)$ | Linear cost; recurrent state | Sequential (no parallelism); vanishing gradients |
| Convolution | $O(n \cdot k)$ | Local patterns; parallel | Fixed receptive field; not content-based |
| Mamba/SSM | $O(n)$ | Linear; selective; hardware-efficient | Less interpretable; newer (less mature) |
| Hyena (long conv) | $O(n \log n)$ | Sub-quadratic; FFT-efficient | Less flexible than attention |
| Linear attention | $O(n)$ | Linear; kernelized | Lower expressivity; quality drops |

Self-attention won because:

1. **Content-based routing**: attention weights depend on content, not just position. This is more flexible than convolution or RNN.
2. **Parallelism**: all positions can be computed in parallel (during training). RNNs are inherently sequential.
3. **Long-range dependencies**: any token can attend to any other in one step. RNNs need many steps.
4. **Empirical quality**: at scale, attention-based models consistently outperform alternatives.

The 2024-2026 trend is toward **hybrid architectures** (Mamba + attention, Jamba) that combine attention's flexibility with SSM's efficiency.

## Implementation in PyTorch

The derivation translates directly into a compact module. Three increasingly practical versions follow: naive, causally masked, and the grouped-query and fused forms used in modern LLMs.

### Basic implementation

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class SelfAttention(nn.Module):
    def __init__(self, d_model, d_k=None):
        super().__init__()
        d_k = d_k or d_model
        self.W_q = nn.Linear(d_model, d_k, bias=False)
        self.W_k = nn.Linear(d_model, d_k, bias=False)
        self.W_v = nn.Linear(d_model, d_k, bias=False)
        self.scale = d_k ** -0.5
    
    def forward(self, x, mask=None):
        Q = self.W_q(x)  # (batch, n, d_k)
        K = self.W_k(x)
        V = self.W_v(x)
        
        # (batch, n, d_k) @ (batch, d_k, n) -> (batch, n, n)
        scores = Q @ K.transpose(-2, -1) * self.scale
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))
        
        attn = F.softmax(scores, dim=-1)
        out = attn @ V  # (batch, n, d_k)
        return out, attn
```

### Causal masking for decoder-only LLMs

To prevent token $i$ from attending to tokens $j > i$ (i.e., enforce autoregressive generation), apply a causal mask:

```python
n = x.size(1)
mask = torch.tril(torch.ones(n, n, device=x.device, dtype=torch.bool))  # lower triangle = True
scores = scores.masked_fill(~mask, float('-inf'))
```

After softmax, masked positions have weight 0 — token $i$ only attends to tokens $\leq i$.

### With GQA (grouped-query attention)

Modern LLMs use GQA, where multiple query heads share a single K, V pair. This reduces KV cache size:

```python
class GQASelfAttention(nn.Module):
    def __init__(self, d_model, n_heads, n_kv_heads):
        super().__init__()
        self.n_heads = n_heads
        self.n_kv_heads = n_kv_heads
        self.n_rep = n_heads // n_kv_heads  # how many query heads per KV head
        self.head_dim = d_model // n_heads
        
        self.W_q = nn.Linear(d_model, n_heads * self.head_dim, bias=False)
        self.W_k = nn.Linear(d_model, n_kv_heads * self.head_dim, bias=False)
        self.W_v = nn.Linear(d_model, n_kv_heads * self.head_dim, bias=False)
        self.W_o = nn.Linear(n_heads * self.head_dim, d_model, bias=False)
    
    def forward(self, x):
        B, T, D = x.shape
        Q = self.W_q(x).view(B, T, self.n_heads, self.head_dim).transpose(1, 2)
        K = self.W_k(x).view(B, T, self.n_kv_heads, self.head_dim).transpose(1, 2)
        V = self.W_v(x).view(B, T, self.n_kv_heads, self.head_dim).transpose(1, 2)
        
        # Repeat K, V to match Q's head count
        K = K.repeat_interleave(self.n_rep, dim=1)  # (B, n_heads, T, head_dim)
        V = V.repeat_interleave(self.n_rep, dim=1)
        
        scale = self.head_dim ** -0.5
        scores = (Q @ K.transpose(-2, -1)) * scale  # (B, n_heads, T, T)
        attn = F.softmax(scores, dim=-1)
        out = attn @ V  # (B, n_heads, T, head_dim)
        
        out = out.transpose(1, 2).contiguous().view(B, T, -1)
        return self.W_o(out)
```

### Using FlashAttention in production

For production, always use FlashAttention (or a similar fused implementation):

```python
# Using PyTorch's built-in scaled_dot_product_attention (uses FlashAttention-2)
out = F.scaled_dot_product_attention(
    Q, K, V,
    attn_mask=causal_mask,
    dropout_p=0.0,
    is_causal=True,  # for causal masking
)
```

This is 5-10× faster than the naive implementation and uses 5-10× less memory (no $n \times n$ matrix materialized).

## What attention actually learns

Empirical studies (especially mechanistic interpretability) have found attention heads specializing in:

- **Previous-token attention** — attend to the immediately preceding token. Common in early layers; helps with local context.
- **Induction heads** — attend to the previous occurrence of the current token, then to the token after it. Critical for in-context learning. Example: if the model has seen "Alice Bob Charlie Alice", an induction head helps it predict "Bob" after the second "Alice" by attending to the "Bob" that followed the first "Alice".
- **Syntactic heads** — attend to syntactic dependents (subject → verb, etc.). Found in middle layers.
- **Copy heads** — attend to a token to copy it verbatim to the output. Common in early layers of decoder models.
- **Long-range dependency heads** — attend across long distances (e.g., pronoun to antecedent).
- **Rare token heads** — attend to rare tokens, possibly for lookup.

These patterns emerge naturally during pretraining and are not explicitly supervised.

### Attention pattern visualization

Attention patterns can be visualized as heatmaps. Common patterns:

- **Diagonal**: token attends to itself (identity).
- **Sub-diagonal**: token attends to previous token (local context).
- **Off-diagonal bands**: token attends to tokens N positions back.
- **Vertical lines**: token attends to specific "anchor" tokens (e.g., punctuation, BOS).
- **Block structure**: tokens within a syntactic unit (clause, sentence) attend to each other.

These patterns are studied in mechanistic interpretability to understand what models actually compute.

## Why this matters

Self-attention is the single most important operation in modern AI. Every LLM forward pass is dominated by self-attention + FFN computations (see [[Feed-Forward Network]]). Understanding self-attention is non-negotiable for:

- Reading any Transformer paper.
- Debugging training or inference issues.
- Understanding modern architectural innovations (GQA, MLA, MoE, FlashAttention).
- Choosing inference optimizations (KV cache, PagedAttention, spec decoding).
- Understanding interpretability research (attention patterns, induction heads).

## Production implications

In production systems, the properties above translate into concrete engineering guidance. The $O(n^2)$ cost is the dominant scaling concern: at sequence length 8192, attention is ~67M scores per head per layer; at 128k, it's ~16B. This is what makes long-context expensive.

The KV cache is the inference optimization that makes autoregressive generation tractable. FlashAttention fuses the $Q K^T \rightarrow$ softmax $\rightarrow \times V$ computation into a single IO-aware kernel, avoiding materializing the $n \times n$ attention matrix in HBM — critical for any modern LLM. For causal masking, precompute the mask once per sequence length; don't recompute per forward pass.

Attention quantization is another lever: FP8 attention (Hopper+) doubles throughput, but needs careful scaling to avoid numerical issues. Two structural approximations round out the toolbox: sliding window attention (Mistral) attends only to a window of W previous tokens for $O(n \cdot W)$ instead of $O(n^2)$, combined with global attention for full coverage; and sparse attention attends to a subset of positions (Longformer, BigBird), reducing cost but losing some expressivity.

## Common pitfalls

- **Forgetting the scaling** — causes training instability, especially for larger $d_k$. Symptom: loss spikes early in training, then diverges.
- **Applying softmax over the wrong axis** — should be over the last axis (key dimension) so each query row sums to 1. Wrong axis = each key column sums to 1, which is meaningless.
- **Masking with 0 instead of -inf** — softmax of 0 still gives non-zero weight. Use `-inf` (or a very large negative number like -1e9 for fp16 safety).
- **Forgetting to apply the mask before softmax** — masking after softmax does nothing (the weights are already normalized).
- **Not using a fused implementation** — naive PyTorch is 5–10× slower than FlashAttention. Always use FlashAttention in production.
- **Wrong head dimension** — $d_k$ must divide $d_{model}$. For $d_{model} = 4096$ and 32 heads, $d_k = 128$. Off-by-one gives shape mismatch.
- **Numerical issues with FP16** — for large $d_k$, even scaled scores can overflow FP16. Use FP32 accumulation or BF16.
- **Attention sink** — early LLMs found that attention concentrates on the first token (BOS), even when it's irrelevant. This is the "attention sink" phenomenon. Fix: include dummy tokens that attention can "dump" into.
- **Forgetting the output projection** — after attention, multiply by $\mathbf{W}_O$ to mix heads. Forgetting this loses head combination.

## Interview questions

**Why do we scale by $\sqrt{d_k}$ and not $d_k$?** The dot product of two random unit-variance vectors has standard deviation $\sqrt{d_k}$. Dividing by $\sqrt{d_k}$ brings the standard deviation back to 1, keeping softmax in its non-saturated regime. Dividing by $d_k$ would over-suppress, making attention too uniform.

**What happens if you forget the causal mask in a decoder-only model?** The model can "see" future tokens during training, learning to copy them rather than predict. Training loss drops to near zero, but the model produces gibberish at inference (when future tokens aren't available).

**Why does attention have $O(n^2)$ complexity?** The $Q K^T$ matrix has shape $n \times n$ — every query must be compared to every key. This is the fundamental cost. Reducing it requires approximations (sparse attention, linear attention, FlashAttention's memory optimization).

**What's the difference between self-attention and cross-attention?** In self-attention, Q, K, V all come from the same sequence. In cross-attention, Q comes from one sequence (e.g., decoder) and K, V from another (e.g., encoder). Cross-attention is used in encoder-decoder models and multimodal models.

**Why does GQA reduce KV cache size?** With MHA, each of $h$ heads has its own K, V. With GQA, $n_{kv} < h$ heads share K, V. The KV cache is proportional to $n_{kv}$, so for $n_{kv} = h/4$ (Llama 3), the cache is 4× smaller.

**What is an induction head?** An attention head that attends to the previous occurrence of the current token, then to the token after it. This enables in-context learning: if the model sees "A B C A", an induction head helps predict "B" after the second "A". Induction heads are critical for few-shot learning.

## Further reading

- Vaswani et al. (2017), *Attention Is All You Need* — the original Transformer paper, introduced scaled dot-product self-attention.
- The Annotated Transformer (Harvard NLP) — line-by-line implementation.
- Karpathy's "Let's build GPT from scratch" video — best pedagogical treatment.
- Olsson et al. (2022), *In-context Learning and Induction Heads* — mechanistic interpretability of attention.
- Dao et al. (2022), *FlashAttention: Fast and Memory-Efficient Exact Attention* — the production implementation.

## See also

- [[Attention and Transformers MOC]]
- [[Scaled Dot-Product Attention]]
- [[Queries Keys and Values]]
- [[Multi-Head Attention]]
- [[Origins of Attention]]
- [[08 - Attention and Transformers/Attention Mechanism/Bahdanau Attention|Bahdanau Attention]]
- [[08 - Attention and Transformers/Attention Mechanism/Luong Attention|Luong Attention]]
- [[Positional Encoding]]
- [[RoPE]]
- [[The Transformer]]
- [[Transformer Block]]
- [[Transformer Decoder Block]]
- [[GQA MQA and MLA]]
- [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]]
- [[Sparse Attention]]
- [[Linear Attention]]
- [[Sliding Window Attention]]
- [[Autoregressive vs Parallel Encoding]]
- [[From RNNs to Attention]]
- [[Long-Range Dependencies]]
- [[The Bottleneck Problem]]
