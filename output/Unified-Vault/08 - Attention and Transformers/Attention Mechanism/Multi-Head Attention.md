---
title: Multi-Head Attention
type: concept
aliases:
  - MHA
tags:
  - attention
  - multi-head-attention
  - transformer
  - head-specialization
sources:
  - "04. Multi-Head Attention — Parallel Relationship Patterns"
  - "Multi-Head Attention"
created_index: 4
---

Multi-head attention (MHA) runs $h$ parallel attention "heads", each with its own learned Q/K/V projections, and concatenates their outputs through a shared output projection. Each head can specialize in a different relationship pattern — syntax, coreference, induction, position — instead of one head averaging over all of them. MHA has been the default attention in every Transformer since Vaswani et al. (2017), and its modern variants MQA, GQA, and MLA trade a little quality for much cheaper inference.

> [!info] TL;DR
> Multi-Head Attention runs $h$ parallel attention "heads", each with its own learned Q/K/V projections, and concatenates the results. Heads can specialize in different relations (syntax, coreference, induction, copy, etc.). MHA is the default attention in Transformers; modern variants include MQA, GQA, and MLA.

## The problem with single-head attention

A single attention head computes one attention distribution per query. That distribution answers one question: "which tokens should this token attend to?" But language has many simultaneous relationship types:

- **Syntactic:** "sat" should attend to "cat" (subject) and "mat" (object of preposition).
- **Coreference:** attention from pronouns to their referents — "it" should attend to "cat".
- **Discourse:** "however" should attend to the previous sentence (to contrast with it).
- **Lexical:** "bank" (of a river) should attend to "river" nearby to disambiguate from "bank" (financial).

A single attention head must choose *one* of these patterns per query. If "it" attends to "cat" for coreference, it cannot *also* attend to "sat" for syntax in the same head — the softmax forces a single distribution. The model has to average over these needs, producing a blurry compromise that serves none of them well. Put in the vocabulary of [[Self-Attention]], a single head computes **one** weighted average of value vectors — a limited operation that can capture only one "kind" of relation at a time. This is the problem multi-head attention solves.

## The solution: run attention h times in parallel

Instead of one attention operation, run $h$ of them (the "heads") in parallel, each with its own learned projections $W_Q^{(i)}, W_K^{(i)}, W_V^{(i)}$. Each head can learn a different relationship pattern:

$$\text{head}_i = \text{Attention}(Q W_Q^{(i)}, K W_K^{(i)}, V W_V^{(i)})$$

The $h$ heads' outputs are concatenated and projected back to the model dimension:

$$\text{MultiHead}(Q, K, V) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h) W_O$$

where $W_O$ is a learned projection matrix. In the equivalent notation used in the deep-dive treatment below:

$$
\text{head}_i = \text{Attention}(Q \mathbf{W}_Q^{(i)}, K \mathbf{W}_K^{(i)}, V \mathbf{W}_V^{(i)})
$$

$$
\text{MHA}(Q, K, V) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h) \mathbf{W}_O
$$

One head might attend to syntactic dependents, another to coreference, another to the previous token, and so on; the output projection $\mathbf{W}_O$ mixes the heads back together.

Each head operates on a **reduced dimension** $d_k = d / h$, so that the total computation is roughly the same as single-head attention at full dimension. For $d = 512$ and $h = 8$, each head uses $d_k = 64$ — small enough that the dot products are well-conditioned (after scaling) but large enough to encode meaningful patterns. The mechanics inside each head are exactly the scaled dot-product operation covered in [[Scaled Dot-Product Attention]] and [[Queries Keys and Values]].

## Why concatenation works

The concatenation of $h$ heads, each of dimension $d_v = d/h$, produces a vector of dimension $d$. The projection $W_O$ then mixes these back into the model dimension. This is structurally identical to:

1. **Grouped convolutions** in CNNs (see [[06 - Computer Vision/Architecture and Connectivity/ResNet Bottleneck Blocks and Architectural Variants|ResNet Bottleneck Blocks and Architectural Variants]]), where different groups learn different features.
2. **Multi-channel feature maps** in CNNs, where each channel can specialize.

The analogy is precise: each attention head is like a convolutional channel, specialized to detect a particular kind of relationship. The projection $W_O$ is like a $1 \times 1$ convolution that mixes channels.

## The bandwidth argument

There is a subtle but important reason multi-head attention outperforms single-head at the same total dimension: **bandwidth**.

A single attention head at dimension $d$ produces a weighted average of values. The weighted average is a *lossy* summary — it collapses $T$ vectors into one, throwing away any information not captured by the average. A single head has bandwidth $d$ (the dimension of the output).

Multi-head attention with $h$ heads at dimension $d/h$ each produces $h$ *separate* weighted averages, each of dimension $d/h$. These are concatenated to a vector of dimension $d$ — the same total bandwidth — but the $h$ averages are computed independently, so they can capture $h$ different "views" of the input without averaging them together. The information capacity is the same, but it is partitioned into $h$ independent channels rather than smeared across one.

This is the same reason a CNN with 64 channels outperforms a CNN with 1 channel at the same parameter count: **parallel specialization beats serial averaging.**

## Dimensionality and constant compute

To keep compute roughly constant when varying $h$, the per-head dimension is $d_k = d_{\text{model}} / h$. The original Transformer has $d_{\text{model}} = 512$, $h = 8$, $d_k = 64$. The full shape inventory:

- Each head's projections: $\mathbf{W}_Q^{(i)}, \mathbf{W}_K^{(i)} \in \mathbb{R}^{d_{\text{model}} \times d_k}$, $\mathbf{W}_V^{(i)} \in \mathbb{R}^{d_{\text{model}} \times d_v}$.
- Each head's output: $\mathbb{R}^{n \times d_v}$.
- Concatenated output: $\mathbb{R}^{n \times (h \cdot d_v)} = \mathbb{R}^{n \times d_{\text{model}}}$ (when $d_v = d_k = d_{\text{model}}/h$).
- Output projection: $\mathbf{W}_O \in \mathbb{R}^{d_{\text{model}} \times d_{\text{model}}}$.

The compute bookkeeping makes the constant-cost property explicit. Compare the original Transformer's MHA against single-head attention at the same $d_{\text{model}}$:

- **Single-head** ($d_k = d_{\text{model}} = 512$): $Q K^T$ is $(N, 512) \times (512, N) = O(N^2 \cdot 512)$.
- **Multi-head** ($h = 8, d_k = 64$): 8 heads, each $Q_i K_i^T$ is $(N, 64) \times (64, N) = O(N^2 \cdot 64)$. Total: $8 \times O(N^2 \cdot 64) = O(N^2 \cdot 512)$. Same!

The trick: total dimension is preserved ($h \cdot d_k = d_{\text{model}}$), so compute is constant. But you get $h$ parallel attention patterns instead of one. The cost is slightly more parameters (the Q/K/V projections are $3 \times d_{\text{model}}^2$ regardless of $h$, but the output projection adds $d_{\text{model}}^2$).

In practice, all heads are computed in a single batched matmul — there's no per-head Python loop. The trick: project to a larger matrix and `reshape` to (batch, h, n, d_k).

## What different heads actually learn

When you train a Transformer and inspect the attention patterns of different heads, you find interpretable specializations. Beyond the syntactic, coreference, and positional patterns predicted by design, empirically observed families include:

- **Positional heads:** attention to the previous token, the next token, or tokens at a fixed offset — these effectively learn n-gram-like patterns.
- **Rare-word heads:** attention to rare or content-heavy words, ignoring function words.
- **Delimiter heads:** attention to punctuation or sentence boundaries, segmenting the input.
- **Copy heads:** attend to a token to copy it verbatim, common in early layers of decoder models.
- **Noise heads:** attend broadly and uniformly; seem to do "averaging".

The best-documented head types from empirical studies (Voita et al. 2019, Olsson et al. 2022):

| Head type         | What it does                                          | Example                                          |
|-------------------|-------------------------------------------------------|--------------------------------------------------|
| Previous-token    | Always attends to position $t-1$                      | Helps with local context                         |
| Induction         | Finds previous occurrences of current token, attends to next token | Critical for in-context learning            |
| Syntactic         | Attends to syntactic heads (subject → verb)            | Parsing                                          |
| Coreference       | Attends to antecedents of pronouns                     | "it" → the noun it refers to                    |
| Copy              | Attends to a token to copy it verbatim                 | Repetition, quoting                              |
| Noise / redundant | Attends broadly and uniformly; seems to do averaging   | Can be pruned                                    |

Not every head learns something interpretable — some are noisy or redundant — but the interpretable ones confirm that the multi-head structure does what it claims: learn multiple relationship patterns in parallel.

### The induction head — key for in-context learning

An **induction head** (Olsson et al. 2022) is a two-head circuit that enables in-context learning:

1. Head 1 (previous-token): at position $t$, attends to $t-1$, copying its token ID into the residual stream.
2. Head 2 (induction): at position $t$, looks for previous occurrences of the token at $t-1$, then attends to the token *after* that occurrence.

This allows the model to complete patterns like "A B C ... A B → C" — it sees "A B" earlier, recognizes the pattern, and predicts "C". Induction heads emerge suddenly during training and are strongly correlated with in-context learning ability. They are among the best-understood circuits in Transformers and a central object of study in mechanistic interpretability.

### Head pruning

Many heads are redundant or noise. Voita et al. (2019) showed that 30-50% of heads can be pruned with minimal quality loss. The critical heads (induction, syntactic) must be kept; the rest are disposable. Head pruning is a real production technique for inference speedup. Tools: `torch-pruning`, HuggingFace's `prune_heads`.

## The output projection — why it's needed

After concatenating $h$ heads, you have a tensor of shape $(B, N, h \cdot d_k) = (B, N, d_{\text{model}})$. Naively, this is the output. But the concatenated heads haven't been mixed — each head's output is independent. The output projection $\mathbf{W}_O \in \mathbb{R}^{d_{\text{model}} \times d_{\text{model}}}$ mixes the heads:

$$
\text{MHA}(Q, K, V) = \text{Concat}(\text{head}_1, \ldots, \text{head}_h) \mathbf{W}_O
$$

Without $\mathbf{W}_O$, the heads can't share information. With it, the model can learn to combine head outputs in arbitrary ways. The output projection is essential — don't forget it.

## Implementation in PyTorch

The implementation below fuses the Q, K, V projections into a single linear layer, reshapes into heads, and runs batched scaled dot-product attention:

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, n_heads):
        super().__init__()
        assert d_model % n_heads == 0
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        
        self.W_qkv = nn.Linear(d_model, 3 * d_model, bias=False)
        self.W_o   = nn.Linear(d_model, d_model, bias=False)
    
    def forward(self, x, mask=None):
        B, N, D = x.shape
        # Project to Q, K, V in one matmul, then reshape to (B, h, N, d_k)
        qkv = self.W_qkv(x)  # (B, N, 3*D)
        q, k, v = qkv.split(D, dim=-1)
        q = q.view(B, N, self.n_heads, self.d_k).transpose(1, 2)  # (B, h, N, d_k)
        k = k.view(B, N, self.n_heads, self.d_k).transpose(1, 2)
        v = v.view(B, N, self.n_heads, self.d_k).transpose(1, 2)
        
        # Scaled dot-product attention (per head, batched)
        scores = (q @ k.transpose(-2, -1)) * (self.d_k ** -0.5)  # (B, h, N, N)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))
        attn = F.softmax(scores, dim=-1)
        out = attn @ v  # (B, h, N, d_k)
        
        # Concat heads and project
        out = out.transpose(1, 2).contiguous().view(B, N, D)
        return self.W_o(out), attn
```

The single matmul for QKV projection and the batched per-head attention are crucial for GPU efficiency.

### Worked example: MHA with causal masking

A production-flavored version registers the causal mask once as a buffer and dispatches the attention core to PyTorch's scaled-dot-product kernel, which uses FlashAttention when available:

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, n_heads, max_seq_len=2048):
        super().__init__()
        assert d_model % n_heads == 0
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads

        # Fused QKV projection (more efficient than separate)
        self.qkv = nn.Linear(d_model, 3 * d_model, bias=False)
        self.o = nn.Linear(d_model, d_model, bias=False)

        # Causal mask buffer (registered once)
        mask = torch.tril(torch.ones(max_seq_len, max_seq_len)).bool()
        self.register_buffer('causal_mask', mask.view(1, 1, max_seq_len, max_seq_len))

    def forward(self, x):
        B, N, D = x.shape
        # Fused QKV: (B, N, 3D) -> 3 × (B, N, D)
        qkv = self.qkv(x)
        q, k, v = qkv.split(D, dim=-1)

        # Reshape to (B, h, N, d_k)
        q = q.view(B, N, self.n_heads, self.d_k).transpose(1, 2)
        k = k.view(B, N, self.n_heads, self.d_k).transpose(1, 2)
        v = v.view(B, N, self.n_heads, self.d_k).transpose(1, 2)

        # Use PyTorch's SDPA (dispatches to FlashAttention when available)
        mask = self.causal_mask[:, :, :N, :N]
        out = F.scaled_dot_product_attention(q, k, v, attn_mask=mask, is_causal=True)

        # Concat heads and project
        out = out.transpose(1, 2).contiguous().view(B, N, D)
        return self.o(out)

# Test
mha = MultiHeadAttention(d_model=512, n_heads=8)
x = torch.randn(2, 128, 512)  # Batch 2, seq_len 128
out = mha(x)
print(f"Input: {x.shape}, Output: {out.shape}")  # Both (2, 128, 512)
print(f"Parameters: {sum(p.numel() for p in mha.parameters()):,}")  # ~1.05M (4 × 512²)
```

This is where MHA lives inside the full model: one attention sublayer of the [[Transformer Block]], repeated across the layers of [[The Transformer]].

## Modern variants

### Multi-query attention (MQA)

**Multi-Query Attention** (Shazeer, 2019) shares K and V across all heads; only Q is per-head. This dramatically reduces the size of the KV cache (the main memory cost at inference) at a small quality cost.

- KV cache size: $\frac{1}{h}$ of MHA.
- Used by: PaLM, Falcon, StarCoder.

### Grouped-query attention (GQA)

**Grouped-Query Attention** (Ainslie et al., 2023) is the intermediate point: $g$ groups of heads share K and V. $g=1$ is MQA; $g=h$ is MHA.

- KV cache size: $\frac{g}{h}$ of MHA.
- Best quality/speed tradeoff in practice.
- Used by: **Llama 2 (70B), Llama 3, Mistral 7B, Gemma, Qwen 2/3**, most modern LLMs.

### Multi-head latent attention (MLA)

**Multi-head Latent Attention** (DeepSeek, 2024) is more aggressive: it compresses K and V into a low-rank latent vector, then decompresses per-head. This can achieve KV cache sizes even smaller than MQA while maintaining MHA-like quality.

- Used by: **DeepSeek-V2, DeepSeek-V3**.

### Variant summary

| Variant  | Q heads | K/V heads | KV cache (relative to MHA) | Quality | Used by                       |
|----------|---------|-----------|----------------------------|---------|-------------------------------|
| MHA      | h       | h         | 1.0                        | Best    | GPT-2/3, BERT, T5             |
| MQA      | h       | 1         | 1/h                        | Slightly worse | PaLM, Falcon, StarCoder |
| GQA      | h       | g         | g/h                        | Near-MHA | Llama 2/3, Mistral, Gemma   |
| MLA      | h       | (latent)  | << 1/h                     | MHA-like | DeepSeek-V2/V3               |

For a deep treatment of these variants, see [[GQA MQA and MLA]].

## How many heads?

The number of heads is a hyperparameter. Typical values:

| Model | $d$ | $h$ | $d_k = d/h$ |
| :--- | :--- | :--- | :--- |
| Transformer (original, 2017) | 512 | 8 | 64 |
| BERT-base | 768 | 12 | 64 |
| BERT-large | 1024 | 16 | 64 |
| GPT-2 small | 768 | 12 | 64 |
| GPT-3 | 12288 | 96 | 128 |

Notice that $d_k$ is almost always kept at 64 or 128. This is not a coincidence — $d_k = 64$ is small enough for well-conditioned dot products (after scaling) and large enough to encode meaningful patterns. The model scales by increasing $d$ and $h$ together, keeping $d_k$ roughly constant.

**Empirically:** too few heads (1–2) underfit because each head must average over too many relationship types. Too many heads (e.g., $h = d$, so $d_k = 1$) underfit because each head has too little capacity to compute a meaningful dot product. The sweet spot is $d_k \in [32, 128]$, which is why essentially all production Transformers land there.

## Why this matters

MHA is the **default attention** in every Transformer since 2017. If you read any architecture paper, you need to understand it.

The choice of MHA / MQA / GQA / MLA is one of the most consequential architectural decisions for **inference cost** (KV cache size). Llama 2/3 use GQA specifically to make consumer-GPU inference feasible.

Head specialization is the basis of mechanistic interpretability — understanding what individual heads do gives us insight into what the model has learned. Head pruning is a real production technique — you can prune 30–50% of heads with minimal quality loss, giving a free inference speedup.

## Production implications

In production, the design guidance that follows from the above is concrete. Always use FlashAttention for MHA — it's 5–10x faster than naive attention. Prefer GQA over MHA for new model designs — the inference speedup is substantial and the quality loss is small. Head pruning can be applied post-hoc to existing models. Tools: `torch-pruning`, HuggingFace's `prune_heads`. Finally, quantize the KV cache to INT8 or FP8 to halve memory — critical for long-context inference, since the cache is the dominant memory cost at serving time (the reason PagedAttention and continuous batching systems exist).

## Common pitfalls and failure modes

- **Forgetting to reshape Q, K, V to (B, h, N, d_k)** — without the head dimension, you compute a single big attention instead of $h$ parallel ones.
- **Wrong concatenation order** — must be consistent with the head dimension split.
- **Treating all heads as equal** — they're not. Some are critical, some are noise. Don't prune blindly.
- **Forgetting the output projection** — concatenating heads without $\mathbf{W}_O$ loses information.

The failure modes show up as recognizable symptoms:

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Wrong output shape | Forgot to transpose head dim back before reshape | Ensure `(B, h, N, d_k)` → `(B, N, h, d_k)` via `.transpose(1, 2)` before `.view` |
| NaN in attention | Softmax over masked positions | Set masked positions to `-inf` before softmax; ensure at least one valid position |
| Slow attention (no FlashAttention) | Not using SDPA or `attn_implementation="flash_attention_2"` | Use `F.scaled_dot_product_attention` or set `attn_implementation` in HuggingFace |
| Head dim not multiple of 8 | Tensor Core underutilization | Choose `d_model` and `n_heads` so `d_k` is a multiple of 8 (or 16 for fp8) |
| All heads attend similarly | Insufficient training; or heads collapsed | Train longer; check init; reduce LR |

## Interview questions

**Why does MHA set $d_k = d_{\text{model}} / h$?** To keep compute constant when varying $h$. Single-head with $d_k = 512$: $O(N^2 \cdot 512)$. Multi-head with $h = 8, d_k = 64$: 8 heads × $O(N^2 \cdot 64) = O(N^2 \cdot 512)$. Same total compute, but 8 parallel attention patterns instead of 1. The trick: total dimension is preserved ($h \cdot d_k = d_{\text{model}}$). The cost is slightly more parameters (output projection adds $d_{\text{model}}^2$).

**What is an induction head and why is it important?** An induction head (Olsson et al. 2022) is a two-head circuit that enables in-context learning. Head 1 (previous-token) copies the token ID from position $t-1$ into the residual stream. Head 2 (induction) looks for previous occurrences of the token at $t-1$, then attends to the token *after* that occurrence. This allows pattern completion: "A B C ... A B → C". Induction heads emerge suddenly during training and are strongly correlated with in-context learning ability. They're one of the best-understood circuits in Transformers.

**Why is the output projection $\mathbf{W}_O$ needed?** After concatenating $h$ heads, you have $(B, N, h \cdot d_k) = (B, N, d_{\text{model}})$, but the heads haven't been mixed — each head's output is independent. $\mathbf{W}_O$ mixes the heads, letting the model learn to combine head outputs in arbitrary ways. Without it, heads can't share information, and the model loses expressive power. The output projection is essential — don't forget it.

**How much can you prune heads without quality loss?** 30-50% of heads can be pruned with minimal quality loss (Voita et al. 2019). Critical heads (induction, syntactic, coreference) must be kept; noise/redundant heads can be removed. Head pruning is a real production technique for inference speedup. The approach: measure each head's importance (e.g., via L0 regularization or sensitivity analysis), prune the least important, fine-tune briefly to recover. Tools: `torch-pruning`, HuggingFace's `prune_heads`.

**What's the difference between MHA, MQA, GQA, and MLA?** **MHA**: $h$ query heads, $h$ K/V heads. Best quality, most memory. Used by GPT-2/3, BERT, T5. **MQA** (Shazeer 2019): $h$ query heads, 1 K/V head. KV cache is $1/h$ of MHA. Slight quality loss. Used by PaLM, Falcon, StarCoder. **GQA** (Ainslie 2023): $h$ query heads, $g$ K/V heads (between MHA and MQA). Best quality/speed tradeoff. Used by Llama 2/3, Mistral, Gemma, Qwen. **MLA** (DeepSeek 2024): compresses K/V into a low-rank latent vector, then decompresses per-head. KV cache smaller than MQA, MHA-like quality. Used by DeepSeek-V2/V3.

**How would you implement MHA efficiently in PyTorch?** Three key optimizations: (1) **Fused QKV projection** — one `nn.Linear(d_model, 3*d_model)` instead of three separate linears. Saves kernel launches. (2) **Single reshape + transpose** — `q.view(B, N, h, d_k).transpose(1, 2)` produces `(B, h, N, d_k)` in one operation. (3) **Use `F.scaled_dot_product_attention`** (SDPA) — dispatches to FlashAttention when available, handling masking, scaling, and the softmax in a fused kernel. Never write `softmax(Q @ K.T / sqrt(d)) @ V` manually in production.

## Further reading

- Vaswani et al. (2017), *Attention Is All You Need* — introduced MHA.
- Shazeer (2019), *Fast Transformer Decoding with One Write-Head* — MQA.
- Ainslie et al. (2023), *GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints*.
- Voita et al. (2019), *Analyzing Multi-Head Self-Attention: Specialized Heads Do the Heavy Lifting, the Rest Can Be Pruned*.
- DeepSeek-AI (2024), *DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model* — MLA.

## See also

- [[Attention and Transformers MOC]]
- [[Self-Attention]]
- [[Scaled Dot-Product Attention]]
- [[Queries Keys and Values]]
- [[GQA MQA and MLA]]
- [[The Transformer]]
- [[Transformer Block]]
- [[Transformer Decoder Block]]
- [[Origins of Attention]]
- [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]]
- [[GPT Family]]
- [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]]
- [[10 - Large Language Models/Context and KV Cache/KV Cache Mechanics|KV Cache Mechanics]]
- [[16 - Interpretability and Research/Interpretability/Mechanistic Interpretability|Mechanistic Interpretability]]
