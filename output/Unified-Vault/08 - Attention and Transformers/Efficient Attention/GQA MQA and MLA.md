---
title: GQA MQA and MLA
type: concept
aliases:
  - GQA MQA MLA
  - Modern Attention
  - Grouped-Query Attention
  - Multi-Query Attention
  - Multi-head Latent Attention
  - GQA
  - MQA
  - MLA
tags:
  - attention
  - efficient-attention
  - kv-cache
  - gqa
  - mqa
  - mla
  - inference
sources:
  - "14 - GQA, MQA, MLA (Modern Attention)"
created_index: 15
---

Multi-query attention (MQA), grouped-query attention (GQA), and multi-head latent attention (MLA) are three modern attention variants that attack the same bottleneck: the KV cache that dominates inference memory for long contexts. Each keeps separate query heads but shrinks what must be cached per token — one shared K/V pair (MQA), a few shared groups (GQA), or a compressed latent vector (MLA). The choice among them is one of the most consequential architectural decisions for inference cost, which is why Llama, Mistral, Gemma, and Qwen standardized on GQA while DeepSeek built its serving economics on MLA.

> [!info] TL;DR
> Three modern attention variants that **share K and V across heads** to shrink the KV cache. MQA (one K/V for all heads) → GQA (groups of heads share K/V) → MLA (compress K/V into a latent vector). Llama, Mistral, Gemma, Qwen use GQA; DeepSeek uses MLA. The biggest single lever for inference memory.

## The problem: KV cache size

At inference, the KV cache dominates memory for long contexts. For a model with $h$ heads and head dim $d_k$, per token the cache stores:

$$
\text{KV per token} = 2 \cdot n_{\text{layers}} \cdot h \cdot d_k \cdot \text{bytes}
$$

A quick back-of-the-envelope for Llama 2 7B (32 layers, 32 heads, 128 head dim, fp16) quotes 256 KB per token — 1 GB for a 4k context and 32 GB for a 128k context — but that figure drops the factor of 2 that counts K and V separately. The arithmetically consistent numbers are $2 \cdot 32 \cdot 32 \cdot 128 \cdot 2 = 524{,}288$ bytes = 0.5 MB per token, hence 2 GB for a 4K context and 64 GB for a 128K context. Either way the conclusion is identical: the cache size limits batch size and context length, and reducing it directly improves throughput.

## Multi-query attention (MQA)

MQA (Shazeer 2019) uses **one K and one V shared across all heads**, while each head still has its own Q:

$$
\text{head}_i = \text{Attention}(Q \mathbf{W}_Q^{(i)}, K \mathbf{W}_K, V \mathbf{W}_V)
$$

The KV cache shrinks to $1/h$ of MHA's size — a 32x reduction for a 32-head model. Quality is slightly worse than MHA, roughly 1% on most benchmarks. MQA is used by PaLM, Falcon, and StarCoder.

## Grouped-query attention (GQA)

GQA (Ainslie et al. 2023) interpolates between the two extremes: **$g$ groups of heads share K and V**, with $h/g$ heads per group. $g=1$ recovers MQA; $g=h$ recovers MHA.

$$
\text{head}_i = \text{Attention}(Q \mathbf{W}_Q^{(i)}, K \mathbf{W}_K^{(\lfloor i/(h/g) \rfloor)}, V \mathbf{W}_V^{(\lfloor i/(h/g) \rfloor)})
$$

The KV cache is $g/h$ of MHA's, and quality nearly matches MHA. The sweet spot is $g \approx h/4$ to $h/8$. GQA is used by Llama 2 70B, Llama 3 (all sizes), Mistral 7B, Mixtral, Gemma, Qwen 2/3, and DeepSeek (some models), and it is the **modern default** for new LLMs: it captures most of MQA's speedup with minimal quality loss.

## Multi-head latent attention (MLA)

MLA (DeepSeek 2024) compresses K and V into a **low-rank latent vector** per token:

$$
\mathbf{c}_t = \mathbf{W}_{DKV} \mathbf{x}_t \quad \text{(compress to latent)}
$$

$$
\mathbf{K}_t = \mathbf{W}_{UK} \mathbf{c}_t \quad \text{(decompress to K)}
$$

$$
\mathbf{V}_t = \mathbf{W}_{UV} \mathbf{c}_t \quad \text{(decompress to V)}
$$

The trick is to **cache the latent $\mathbf{c}_t$**, not the full K and V — the latent is much smaller than $h \cdot d_k$. For DeepSeek-V2 the latent dim is ~512 versus full K/V which would be ~16k: a ~32x reduction in KV cache, even better than MQA. To make attention work without decompressing K every time, MLA also uses an "absorb-the-projection-into-Q" trick — the K projection is folded into Q's projection at the start of attention. MLA is used by DeepSeek-V2, DeepSeek-V3, and DeepSeek-R1; its cache is smaller than MQA's — competitive with having $g < 1$ "heads" — and quality matches MHA in DeepSeek's experiments.

## Comparison at a glance

| Variant | KV heads | KV cache (vs MHA) | Quality | Used by |
|---------|----------|-------------------|---------|---------|
| MHA | $h$ | 1.0 | Best | GPT-2/3/4, BERT, T5, original |
| MQA | 1 | $1/h$ | ~1% worse | PaLM, Falcon, StarCoder |
| GQA | $g$ | $g/h$ | ~MHA | **Llama 2/3, Mistral, Gemma, Qwen** |
| MLA | latent | $\ll 1/h$ | MHA-like | **DeepSeek-V2/V3/R1** |

## The KV cache problem in numbers

The KV cache is the dominant memory cost at inference for long contexts. For a model with $L$ layers, $h$ heads, head dimension $d_k$, and sequence length $n$:

$$
\text{KV cache size} = 2 \cdot L \cdot h \cdot d_k \cdot n \cdot \text{bytes per element}
$$

The factor 2 is for K and V. For Llama 2 7B (32 layers, 32 heads, 128 head dim, fp16): per token $2 \cdot 32 \cdot 32 \cdot 128 \cdot 2 = 524{,}288$ bytes = 0.5 MB, so a 4K context costs 2 GB and a 128K context costs 64 GB. (The coarser estimate of 256 KB per token, 1 GB at 4K, 32 GB at 128K, omits that factor of 2 — treat the 0.5 MB / 2 GB / 64 GB figures as the consistent reading.) This is why the KV cache limits batch size and context length, and why reducing it directly improves throughput.

Each variant attacks the cache differently:

- **MHA**: $h$ sets of K, V per token → cache size $\propto h$.
- **MQA**: 1 set of K, V per token → cache size $\propto 1$ (h× reduction).
- **GQA**: $g$ sets of K, V per token → cache size $\propto g$ (h/g× reduction).
- **MLA**: 1 latent vector per token → cache size $\propto d_{\text{latent}}$ (can be smaller than 1 set of K, V).

For Llama 3 8B with GQA (8 KV heads out of 32 attention heads), that is a 4× KV cache reduction versus MHA. This is why Llama 3 8B can serve 128K context on a single H100 — with MHA, the KV cache alone would be 4× larger.

## MLA's "absorb the projection" trick in detail

MLA caches the latent $\mathbf{c}_t = \mathbf{W}_{DKV} \mathbf{x}_t$ (low-dimensional), not the full K and V. At inference, we need K = $\mathbf{W}_{UK} \mathbf{c}_t$ and V = $\mathbf{W}_{UV} \mathbf{c}_t$ — but computing K from $\mathbf{c}_t$ at every step is expensive. The trick: **absorb the K projection into Q**. The attention score is:

$$
\mathbf{q}_i \cdot \mathbf{k}_j = \mathbf{q}_i \cdot \mathbf{W}_{UK} \mathbf{c}_j = (\mathbf{W}_{UK}^T \mathbf{q}_i) \cdot \mathbf{c}_j
$$

So instead of computing K = $\mathbf{W}_{UK} \mathbf{c}_j$ and then dotting with Q, we precompute $\mathbf{W}_{UK}^T \mathbf{q}_i$ (the "absorbed" Q) and dot with $\mathbf{c}_j$ directly. This avoids materializing K — we work with the latent $\mathbf{c}_j$ directly.

Similarly for V: the output is $\sum_j \alpha_j \mathbf{V}_j = \sum_j \alpha_j \mathbf{W}_{UV} \mathbf{c}_j = \mathbf{W}_{UV} \sum_j \alpha_j \mathbf{c}_j$. We compute the weighted sum of latents, then apply $\mathbf{W}_{UV}$ once at the end. The cache is the small latent, and the projections are absorbed into Q (precomputed) or applied once at the end — this is what makes MLA efficient at inference.

## Quality impact: MHA vs. MQA vs. GQA vs. MLA

Empirical quality (from the GQA and DeepSeek-V2 papers):

| Variant | Quality (vs MHA) | KV cache (vs MHA) | Used by |
|---------|------------------|-------------------|---------|
| MHA | Baseline | 1.0× | GPT-2/3, BERT, T5 |
| MQA | -1 to -2% | 1/h× (e.g., 32×) | PaLM, Falcon, StarCoder |
| GQA (h/8) | -0.1 to -0.5% | 8× | Llama 2 70B, Llama 3, Mistral |
| GQA (h/4) | -0.05 to -0.2% | 4× | Llama 3 8B, Qwen, Gemma |
| MLA | ~MHA (no loss) | >32× | DeepSeek-V2/V3/R1 |

### Why GQA is the sweet spot

GQA with $g \approx h/4$ to $h/8$ captures most of MQA's cache savings with negligible quality loss. The quality cliff happens at $g = 1$ (MQA): going from $g = 2$ to $g = 1$ loses more quality than going from $g = h$ to $g = 2$. This non-linear tradeoff makes $g = h/4$ to $h/8$ the sweet spot, and MQA's additional cache savings (from $g = h/8$ down to $g = 1$) are not worth the quality loss for most use cases.

### Why MLA matches MHA quality

MLA doesn't share K, V across heads — it compresses them into a latent, then decompresses per head. The decompression ($\mathbf{W}_{UK}, \mathbf{W}_{UV}$) is learned, so each head effectively gets its own K, V — just parameterized through a low-rank bottleneck. If the latent dim is large enough (DeepSeek-V2 uses 512), the bottleneck doesn't constrain quality. MQA, by contrast, genuinely shares one K, V across all heads, so its quality loss comes from the sharing itself.

## Worked example: KV cache size comparison

```python
def kv_cache_size(n_layers, n_heads, head_dim, seq_len, n_kv_heads=None, dtype_bytes=2):
    """Compute KV cache size in bytes.
    n_kv_heads: None for MHA, 1 for MQA, g for GQA.
    For MLA, use kv_cache_size_mla instead.
    """
    if n_kv_heads is None:
        n_kv_heads = n_heads  # MHA
    # 2 for K and V
    return 2 * n_layers * n_kv_heads * head_dim * seq_len * dtype_bytes

def kv_cache_size_mla(n_layers, latent_dim, seq_len, dtype_bytes=2):
    """MLA caches the latent, not K and V."""
    return n_layers * latent_dim * seq_len * dtype_bytes

# Llama 3 8B: 32 layers, 32 heads, 128 head dim, GQA with 8 KV heads
mha_size = kv_cache_size(32, 32, 128, 32768, n_kv_heads=32)  # MHA
gqa_size = kv_cache_size(32, 32, 128, 32768, n_kv_heads=8)   # GQA
mqa_size = kv_cache_size(32, 32, 128, 32768, n_kv_heads=1)   # MQA

# DeepSeek-V2: 60 layers, MLA with 512 latent dim
mla_size = kv_cache_size_mla(60, 512, 32768)

print(f"MHA: {mha_size / 1e9:.2f} GB")
print(f"GQA (8 KV heads): {gqa_size / 1e9:.2f} GB  ({mha_size/gqa_size:.1f}× reduction)")
print(f"MQA: {mqa_size / 1e9:.2f} GB  ({mha_size/mqa_size:.1f}× reduction)")
print(f"MLA (DeepSeek-V2): {mla_size / 1e9:.2f} GB")
```

Expected output (32K context, fp16): MHA ~16.8 GB; GQA (8 KV heads) ~4.2 GB (4× reduction); MQA ~0.5 GB (32× reduction); MLA ~0.2 GB (84× reduction vs MHA, though with a different model architecture — 60 layers of a 512-dim latent rather than Llama 3's 32 layers of cached K/V).

## Choosing the right attention variant

| Use case | Recommended | Why |
|----------|-------------|-----|
| Small model (< 1B) | MHA | Quality matters more; cache is small anyway |
| Medium model (1-10B) | GQA (h/4) | Good quality/cache balance; standard |
| Large model (10-100B) | GQA (h/8) or MLA | Cache dominates; need aggressive reduction |
| Very large (100B+) | MLA | Best cache efficiency for MoE serving |
| Long context (128K+) | GQA or MLA + quantization | Cache is the bottleneck |
| Mobile / edge | MQA | Maximum cache reduction; quality OK for small models |

The choice ultimately depends on the quality/cache tradeoff for your specific scale and use case: small models should keep MHA because the cache is small and quality dominates, mid-size models take GQA as the standard balance, and very large or long-context models lean on MLA (optionally combined with cache quantization) because cache economics dominate serving cost.

## Why it matters

The choice of attention variant is one of the **most consequential architectural decisions** for inference cost. GQA is why Llama 3 8B can serve 128k context on a single H100 — with MHA, the KV cache alone would be 4x larger. MLA is why DeepSeek-V3 has such aggressive economics: the cache is small enough that serving is cheap. And for agents that maintain long contexts across turns, the attention variant directly affects how many concurrent agents you can serve.

## Production implications

Use GQA for new model designs; it is the modern default. DeepSeek's MLA is more complex to implement but offers the best cache efficiency — watch for adoption in other models. On the inference-engine side, vLLM, TGI, and TensorRT-LLM all support GQA, while MLA support is more recent (vLLM added it in late 2024).

PagedAttention-style paged KV caches are another complementary cache optimization that can be stacked on top. KV cache quantization (INT8, FP8) is likewise **orthogonal** to head sharing — combine it with GQA/MLA for compounding savings. GQA's 4× reduction plus INT8's 2× reduction gives 8× total cache reduction, which is standard practice for serving large models with long context: Llama 3 70B with GQA + INT8 KV cache can serve 128K context on 2 H100s. With GQA alone you can fit roughly 4x more concurrent requests than MHA at the same context length.

## Common pitfalls and failure modes

The classic GQA bug is **forgetting to expand K/V across heads after caching**: GQA stores $g$ sets of K/V, but attention needs $h$ sets — use `repeat_interleave` to expand the cached tensors to all heads. MLA implementation bugs are common because the projection-folding trick is subtle; use the official DeepSeek implementation and verify the absorbed Q. Config typos around `num_key_value_heads` versus `num_attention_heads` are easy to make and silently give the wrong number of KV heads. Finally, never assume quality is identical to MHA — MQA in particular can hurt quality on some tasks, so always benchmark.

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Quality drops after switching to MQA | MQA too aggressive | Use GQA with more groups (e.g., h/4 instead of 1) |
| GQA model slower than expected | Not expanding K/V after cache | Use `repeat_interleave` to expand cached K/V to all heads |
| MLA implementation wrong | Projection folding bug | Use official DeepSeek implementation; verify absorbed Q |
| Wrong number of KV heads in config | `num_key_value_heads` typo | Check config: `num_attention_heads` vs `num_key_value_heads` |
| Quality varies across tasks | Some tasks more sensitive to KV sharing | Benchmark on diverse tasks; consider MLA for no quality loss |

## Interview questions

**What problem do GQA, MQA, and MLA solve?** The KV cache dominates inference memory for long contexts. MHA stores $h$ sets of K, V per token, so the cache grows with head count. MQA (1 set), GQA ($g$ sets), and MLA (latent) reduce the cache by sharing/compressing K, V across heads, which improves throughput and enables longer contexts. For Llama 3 8B with GQA, the cache is 4× smaller than MHA — enabling 128K context on a single H100.

**Why is GQA the sweet spot, not MQA?** GQA with $g \approx h/4$ to $h/8$ captures most of MQA's cache savings with negligible quality loss. The quality cliff is at $g = 1$ (MQA) — going from $g = 2$ to $g = 1$ loses more quality than going from $g = h$ to $g = 2$. This non-linear tradeoff makes $g = h/4$ to $h/8$ optimal; MQA's additional cache savings (from $g = h/8$ to $g = 1$) aren't worth the quality loss for most use cases.

**How does MLA achieve smaller cache than MQA without quality loss?** MLA compresses K, V into a low-dimensional latent $\mathbf{c}_t = \mathbf{W}_{DKV} \mathbf{x}_t$. The cache stores $\mathbf{c}_t$ (e.g., 512-dim) instead of full K, V (e.g., 16K-dim for all heads). At inference, MLA uses the "absorb the projection" trick: precompute $\mathbf{W}_{UK}^T \mathbf{q}$ (absorbed Q), dot with $\mathbf{c}_j$ directly — no need to materialize K. Each head effectively gets its own K, V (via learned decompression), so quality matches MHA. MQA shares one K, V across all heads, so its quality loss comes from sharing.

**Why does Llama 3 use GQA instead of MLA?** Three reasons. (1) GQA is simpler to implement — no projection-folding trick. (2) GQA was established (Llama 2 70B used it) when Llama 3 was designed in 2023; MLA was published in 2024. (3) GQA's quality/cache tradeoff is good enough for Llama 3's scale. MLA is more complex but offers better cache efficiency — adopted by DeepSeek for their 671B MoE where cache economics matter more. Future Llama models may adopt MLA.

**How would you choose between MHA, GQA, and MLA for a new model?** Small model (<1B): MHA — quality matters, cache is small. Medium (1-10B): GQA (h/4) — good balance, standard. Large (10-100B): GQA (h/8) or MLA — cache dominates. Very large (100B+): MLA — best cache efficiency. Long context (128K+): GQA or MLA + KV cache quantization. The choice depends on the quality/cache tradeoff for your specific scale and use case.

**Can you combine GQA with KV cache quantization?** Yes — they're orthogonal. GQA/MLA reduce the number of K, V sets; quantization reduces the bytes per element. Combined: GQA (4× reduction) + INT8 quantization (2× reduction) = 8× total cache reduction. This is standard for serving large models with long context — e.g., Llama 3 70B with GQA + INT8 KV cache can serve 128K context on 2 H100s.

## Further reading

- Shazeer (2019), *Fast Transformer Decoding with One Write-Head* (MQA).
- Ainslie et al. (2023), *GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints*.
- DeepSeek-AI (2024), *DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model* (MLA).

## See also

- [[Attention and Transformers MOC]]
- [[Multi-Head Attention]] — the baseline these variants modify.
- [[Self-Attention]] — the underlying mechanism.
- [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]] — complementary compute-side efficiency.
- [[Sliding Window Attention]] — orthogonal KV cache reduction (constant $O(w)$ cache).
- [[Sparse Attention]] — restricts the attention pattern itself.
- [[Mixture of Experts]] — DeepSeek-V2/V3 pair MLA with a MoE architecture.
- [[The Transformer]]
- [[DeepSeek Architecture]]
- [[KV Cache Mechanics]]
