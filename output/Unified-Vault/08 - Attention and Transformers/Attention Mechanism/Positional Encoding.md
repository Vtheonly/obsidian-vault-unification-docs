---
title: Positional Encoding
type: concept
aliases:
  - "Positional Encoding Overview"
  - "Injecting Order Into a Set"
tags:
  - attention
  - positional-encoding
  - transformers
  - rope
  - sinusoidal
  - long-context
sources:
  - "02. Positional Encoding — Injecting Order Into a Set"
  - "Positional Encoding Overview"
created_index: 6
---

Self-attention, by itself, has no notion of token order: it computes pairwise interactions between tokens, so a permuted input yields a correspondingly permuted output and nothing is lost or gained. Language is order-dependent — "dog bites man" and "man bites dog" share a token set but not a meaning — so Transformers must inject position information explicitly. Positional encoding is the family of techniques that does this, and its evolution from fixed sinusoids through learned embeddings to relative schemes like RoPE and ALiBi tracks the rise of modern long-context LLMs.

> [!info] TL;DR
> Self-attention is **permutation-invariant** — it doesn't know the order of tokens. Positional encoding injects order information. This note surveys the family: sinusoidal, learned, relative (Shaw, Transformer-XL), RoPE, ALiBi, YaRN. Deep dive on RoPE in [[RoPE]].

## The problem: attention has no notion of order

Self-attention computes $Q K^\top$ — a set of pairwise interactions. If you permute the input tokens, the output is the same permutation. The operation treats the sequence as a **set**, not a sequence. Written in full:

$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{Q K^T}{\sqrt{d_k}}\right) V
$$

Permuting the input tokens just permutes the output rows — the attention weights themselves are unchanged. Strictly speaking the map is **permutation-equivariant** (outputs follow the input permutation); because the weights are unchanged by the permutation, the operation is also described as **permutation-invariant**. Under either description the conclusion is the same: attention has no notion of order.

This would be catastrophic for language. "The cat sat on the mat" and "Mat the on sat cat the" would produce identical self-attention outputs (up to permutation), because the operation cannot distinguish them — yet they mean completely different things. "Dog bites man" and "Man bites dog" mean different things for the same reason. The model needs to know which token is in which position.

The RNN did not have this problem because its sequential processing *was* the order — token $t$ was computed after token $t-1$, and the hidden state at step $t$ implicitly encoded "this is step $t$." Self-attention, by being parallel and order-blind, throws this information away. Where a CNN encodes position implicitly through the kernel's receptive field, a purely attentional model cannot. **Positional encoding** is the fix: explicitly inject position information into each token's representation before self-attention, so the model can use position as part of its attention computation.

## Why position matters: a concrete example

Consider "the cat chased the dog" versus "the dog chased the cat." The token sets are identical; only the order differs. Without positional encoding, the self-attention outputs would be identical (up to permutation). With positional encoding, in sentence 1, "chased" attends to "cat" (subject, position 2) and "dog" (object, position 5) — the attention pattern encodes "subject before verb, object after." In sentence 2, "chased" attends to "dog" (subject, position 2) and "cat" (object, position 5) — the same pattern shape, with different tokens filling the subject and object roles.

Without position, "chased" could not distinguish "cat is the subject" from "cat is the object" — both are just "the token 'cat' is in the sentence." Positional encoding is what lets the attention mechanism learn position-dependent patterns like "the token immediately before the verb is usually the subject," along with regularities like subject-verb order and coreference distance.

## Two families of solutions

### Absolute positional encoding

Add a position-dependent vector to each token's embedding:

$$
\mathbf{x}_i = \mathbf{e}_{\text{token}_i} + \mathbf{p}_i
$$

where $\mathbf{p}_i$ encodes position $i$, and the model learns to use this signal. The pros: simple, works for short sequences. The cons: it can't extrapolate beyond the training length (for learned variants) or extrapolates unreliably (for sinusoidal), and it provides no explicit relative position.

### Relative positional encoding

Modify the attention computation to depend on the **relative offset** $i - j$ between query position $i$ and key position $j$. The model knows "key $j$ is 3 positions to the right of query $i$" rather than "key $j$ is at absolute position 5." The pros: relative encodings generalize better to longer sequences, and relative position is what actually matters for most tasks. The cons: they are more complex and may need per-layer modification (Shaw, Transformer-XL). Relative encodings are dominant in modern LLMs.

## Sinusoidal positional encoding

The original Transformer (Vaswani et al., 2017) adds a fixed, non-learned positional encoding to each token's embedding. For position $pos$ and dimension $i$:

$$PE(pos, 2i) = \sin\left(\frac{pos}{10000^{2i/d}}\right)$$
$$PE(pos, 2i+1) = \cos\left(\frac{pos}{10000^{2i/d}}\right)$$

The same encoding is often written with the position indexed $i$ and the dimension indexed $k$:

$$
\mathbf{p}_{i, 2k} = \sin\left(\frac{i}{10000^{2k/d}}\right)
$$

$$
\mathbf{p}_{i, 2k+1} = \cos\left(\frac{i}{10000^{2k/d}}\right)
$$

Either way, the encoding is a $d$-dimensional vector for each position, where even dimensions are sines and odd dimensions are cosines of varying frequencies. The lowest frequencies cycle slowly (encoding coarse position), and the highest frequencies cycle quickly (encoding fine position).

Why sinusoids? Three reasons. They are **bounded**: sines and cosines live in $[-1, 1]$, so adding them to embeddings does not blow up magnitudes. They are **extrapolatable**: for any fixed offset $k$, $PE(pos + k)$ is a linear function of $PE(pos)$, which means the model can learn to attend to "the token $k$ positions ahead" by learning a linear projection — the relative position is encoded in a learnable way. The hope was that the model could learn to attend by relative position because $\sin(i + \delta)$ is a linear function of $\sin(i), \cos(i)$. And they are **unique**: each position has a unique encoding, since the combined sine/cosine pattern at different frequencies disambiguates positions. In practice the extrapolation is theoretical — sinusoidal encodings do not extrapolate well past the training length, a limitation that motivated the next generation.

The encoding is added (not concatenated) to the token embedding:

$$X = [\text{embed}(w_1) + PE(1), \ldots, \text{embed}(w_T) + PE(T)]$$

Adding rather than concatenating preserves the model dimension $d$ and lets the positional information flow through all subsequent operations (the Q, K, V projections) naturally.

## Learned absolute positional embeddings

Instead of fixed sinusoids, learn a position embedding matrix $E_{pos} \in \mathbb{R}^{T_{max} \times d}$, where $T_{max}$ is the maximum sequence length. The embedding for position $pos$ is simply the $pos$-th row of this matrix, added to the token embedding:

$$X = [\text{embed}(w_1) + E_{pos}(1), \ldots, \text{embed}(w_T) + E_{pos}(T)]$$

Each position $i \in [0, L)$ has a learned embedding vector $\mathbf{p}_i \in \mathbb{R}^d$, and again $\mathbf{x}_i = \mathbf{e}_{\text{token}_i} + \mathbf{p}_i$. This is simpler and empirically performs as well or better than sinusoids. The downside: it cannot extrapolate beyond $T_{max}$ — a hard limit on context length, with position $i \geq L$ undefined. The model has no notion of positions beyond the maximum it was trained on, whereas sinusoidal encodings in principle extrapolate to any length.

In practice, most Transformers of the BERT/GPT/ViT generation use learned positional embeddings, accepting the fixed maximum length; GPT-2 and BERT are the canonical examples. Models that need to handle very long sequences (Longformer, BigBird) use specialized encodings (rotary, ALiBi) that combine the benefits of both. Today, learned absolute embeddings survive mainly in the BERT family with its fixed 512-token context, while modern decoder LLMs have moved on to relative encodings.

## Relative positional encodings

### Shaw relative positional encoding (Shaw et al., 2018)

Instead of adding position to the input, add a learned relative embedding to the keys (and sometimes values):

$$
\text{Attention}(Q, K + \mathbf{R}^{rel}, V)
$$

where $\mathbf{R}^{rel}$ depends on relative positions $i - j$, clipped to a maximum relative distance (e.g., $|i - j| \leq 50$). The pros: better generalization, because the same embedding is used for relative distance 5 regardless of absolute position. The cons: it must be added at every attention layer (not just the input), which costs more memory.

### Transformer-XL relative positional encoding (Dai et al., 2019)

Transformer-XL decomposes the attention score into four terms, each with a different relative-position component:

$$
e_{ij} = \underbrace{\mathbf{q}_i \cdot \mathbf{k}_j}_{\text{content-content}} + \underbrace{\mathbf{q}_i \cdot \mathbf{r}_{i-j}^K}_{\text{content-position}} + \underbrace{\mathbf{u} \cdot \mathbf{k}_j}_{\text{global content bias}} + \underbrace{\mathbf{v} \cdot \mathbf{r}_{i-j}^K}_{\text{global position bias}}
$$

where $\mathbf{r}_{i-j}^K$ is a learned relative embedding and $\mathbf{u}, \mathbf{v}$ are global parameters. The pros: state-of-the-art for long-context language models at the time, and the foundation for later work. The cons: complexity — many moving parts.

## RoPE: the modern default

The most widely used positional encoding in 2023+ LLMs (LLaMA, Mistral, Qwen, and also Gemma, DeepSeek, GLM — essentially all modern decoder LLMs) is **Rotary Position Embedding (RoPE)** (Su et al., 2021). RoPE does not add position information to the embedding; instead, it **rotates** the query and key vectors at attention time based on their positions, rotating them in 2D subspaces by an angle proportional to position. The rotation is designed so that $q_m^\top k_n$ depends only on the relative offset $m - n$, not on the absolute positions $m$ and $n$ — rotating $\mathbf{q}$ by $\theta_i$ and $\mathbf{k}$ by $\theta_j$ is equivalent to rotating their dot product by $\theta_i - \theta_j$.

RoPE's advantages: **relative position** is what actually matters for attention ("look 3 tokens back" is more useful than "look at position 47"); it is **extrapolatable** to longer sequences with scaling tricks (with some fine-tuning); and it has **no extra parameters** — the rotations are fixed functions of position, computationally free in the sense that they just multiply Q and K by rotation matrices. The cons: careful handling of the rotation is required, and context extension needs YaRN or NTK-aware scaling.

RoPE is more mathematically involved than sinusoidal or learned encodings, and the full treatment lives in [[RoPE]]. The key takeaway: positional encoding is an active research area, and the field has converged on relative-position encodings (RoPE, ALiBi) for modern long-context models.

## ALiBi: position as a linear bias

ALiBi (Attention with Linear Biases; Press et al., 2022) adds a fixed (non-learned) bias to attention scores that depends linearly on relative distance:

$$
e_{ij} = \mathbf{q}_i \cdot \mathbf{k}_j + m \cdot (j - i)
$$

where $m$ is a head-specific slope, geometrically spaced ($1/2, 1/4, 1/8, \ldots$). The pros: no positional parameters at all, and true extrapolation (trained on 1024 tokens, works on 2048+). The cons: quality is slightly below RoPE in practice, and it is less adopted — used by MPT and BLOOM. The full treatment, including why the extrapolation works, is in [[ALiBi]].

## Context extension: YaRN, NTK-aware scaling, LongRoPE

These are methods to **extend** a RoPE-trained model to longer contexts without retraining. They modify the rotation frequencies so the model can effectively "interpolate" to longer positions. **NTK-aware scaling** scales the rotation frequencies so the highest-frequency rotations stay roughly the same. **YaRN** (Peng et al., 2023) is a more sophisticated interpolation that segments the frequency range and applies different scaling per segment. **LongRoPE** (Microsoft, 2024) searches for non-uniform frequency scaling, achieving 2M-token context. The details of the first two are covered in [[YaRN and NTK-Aware Scaling]].

## The family at a glance

| Method              | Family    | Extrapolates? | Used by                          | Notes                          |
|---------------------|-----------|---------------|----------------------------------|--------------------------------|
| Sinusoidal          | Absolute  | Theoretically | Original Transformer             | Rarely used today              |
| Learned absolute    | Absolute  | No            | GPT-2, BERT                      | Hard context limit             |
| Shaw relative       | Relative  | To a limit    | Some early NMT                   | Clipped max distance           |
| Transformer-XL      | Relative  | Better        | Transformer-XL, some long-context| Complex                        |
| **RoPE**            | Relative  | With scaling  | **Llama, Mistral, Gemma, Qwen**  | Modern default                 |
| ALiBi               | Relative  | Yes (linear)  | MPT, BLOOM                       | Slightly lower quality         |
| YaRN                | RoPE ext  | Yes           | Used to extend RoPE models       | Training-free extension        |
| LongRoPE            | RoPE ext  | Yes (2M+)     | Microsoft models                 | Search-based                   |

## How the family evolved

Each generation addressed the limitation of the previous one:

| Generation | Method | Year | Limitation that motivated the next |
|------------|--------|------|-------------------------------------|
| 1st | Sinusoidal | 2017 | Didn't extrapolate in practice |
| 2nd | Learned absolute | 2018 | Hard context limit; can't extrapolate |
| 3rd | Shaw relative | 2018 | Clipped max distance; per-layer cost |
| 4th | Transformer-XL | 2019 | Complex; many moving parts |
| 5th | RoPE | 2021 | Extrapolation needs YaRN/NTK |
| 5th | ALiBi | 2022 | Locality penalty hurts long-range |
| 6th | YaRN / LongRoPE | 2023-24 | Extends RoPE to 128K-2M |

The current state (2024-2026): RoPE + YaRN is the default for long context; ALiBi is niche; learned absolute is only for the BERT family (fixed 512 context).

## The multi-scale property

Both RoPE and ALiBi use multi-scale design — different frequencies or slopes capture different distance scales. In RoPE, each dimension pair rotates at a different frequency ($\theta_k = 10000^{-2k/d}$); high frequencies capture local position while low frequencies capture long-range structure. In ALiBi, each head has a different slope ($m_h = 1/2^h$); steep slopes attend locally while gentle slopes attend globally. This multi-scale property lets the model attend at multiple distance scales simultaneously, similar to wavelet transforms.

## Why this matters for AI

Positional encoding is **the** mechanism that makes attention work for sequences — without it, attention is just a set operation. The shift from absolute (GPT-2, BERT) to relative (RoPE) was one of the key architectural changes that enabled modern long-context LLMs. Context extension (YaRN, LongRoPE) is one of the most active research areas, because users want longer contexts but retraining is expensive.

The choice of positional encoding also determines **what the model can do at inference**: a model trained with absolute embeddings genuinely cannot process positions past its training length, while RoPE plus scaling can extend 4–32×.

## Production implications

For new model training, use RoPE — it is the de-facto standard and has the best tooling. For extending an existing model's context, use YaRN or NTK-aware scaling; both are training-free (or fine-tune-light) and well-supported in vLLM, TGI, and similar serving stacks. For very long context (1M+), LongRoPE or progressive extension during fine-tuning are the options, and production maturity there is still developing.

Position embedding bugs are subtle: a model with the wrong RoPE configuration will look fine on short sequences but degrade sharply on long ones. Always test on the maximum intended context length.

## Common pitfalls and failure modes

Never mix positional encodings — combining absolute embeddings with RoPE gives two positional signals that can interfere, and the model receives conflicting information about position. Picking one is the rule; if you need both extrapolation (RoPE's strength via YaRN) and long-range attention, use RoPE + YaRN, which gives extrapolation without the locality penalty. Mixing positional encodings is an implementation bug, not a design choice.

Other classic mistakes: a wrong RoPE base or scaling factor makes the model produce plausible-looking but subtly wrong outputs; forgetting to apply the causal mask *and* the positional encoding shortchanges the model — both are needed; and truncating positions past the training length means that for absolute encodings you must train at the maximum intended length, while for RoPE you can extend with YaRN.

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Mixing positional encodings | Combining absolute + RoPE | Pick one; they conflict |
| Wrong RoPE config | Wrong `rope_theta` or scaling | Check model card; pass correct config |
| Forgetting causal mask AND positional encoding | Both needed | Apply both; positional encoding alone isn't enough |
| Truncating past training length | Absolute embeddings | Use RoPE + YaRN for extension |

## Interview questions

1. **What's the difference between absolute and relative positional encoding?** Absolute adds a position-dependent vector to each token: $\mathbf{x}_i = \mathbf{e}_i + \mathbf{p}_i$, and the model infers position from $\mathbf{p}_i$. Relative modifies the attention computation to depend on the relative offset $i - j$. Absolute is simpler but can't extrapolate (learned) or extrapolates unreliably (sinusoidal). Relative generalizes to longer sequences and captures what matters for most tasks. Modern LLMs use RoPE — a relative encoding with no learned parameters and no extra compute.

2. **Why did relative encodings replace absolute encodings?** Three reasons. (1) **Extrapolation** — relative encodings generalize to sequences longer than training; absolute can't (learned) or does so unreliably (sinusoidal). (2) **What matters is relative** — for most tasks (translation, Q&A, code), the relative position of tokens matters more than absolute. (3) **Long context** — modern LLMs need 128K+ context; absolute embeddings would require training at that length, which is expensive. Relative encodings (RoPE + YaRN) can extend post-hoc.

3. **Which positional encoding would you use for a new model?** RoPE. It's the de-facto standard (Llama, Mistral, Qwen, DeepSeek, Gemma all use it): no learned parameters, no extra compute, relative encoding, extensible with YaRN/NTK. For the BERT family (fixed 512 context), learned absolute is fine. For new modalities (audio, video), consider learned 2D/3D positional embeddings. But for text LLMs, RoPE is the answer.

4. **How does positional encoding interact with context extension?** Absolute (learned): can't extend — positions past the training length are undefined. Sinusoidal: theoretically extrapolates, but quality degrades. RoPE: extrapolates with YaRN/NTK scaling (4× zero-shot, 8-16× with fine-tuning, 2M+ with LongRoPE). ALiBi: native extrapolation (train on 1024, test on 2048+), but with a locality penalty. The choice of positional encoding determines how easily you can extend context post-hoc — this is why RoPE won.

5. **What is the multi-scale property of positional encodings?** Both RoPE and ALiBi use multi-scale design — different frequencies/slopes capture different distance scales. RoPE: each dimension pair rotates at a different frequency ($\theta_k = 10000^{-2k/d}$); high frequencies capture local position, low frequencies capture long-range. ALiBi: each head has a different slope ($m_h = 1/2^h$); steep slopes attend locally, gentle slopes attend globally. This multi-scale property lets the model attend at multiple distance scales simultaneously, similar to wavelet transforms.

6. **Why can't you combine absolute embeddings with RoPE?** They conflict. Absolute embeddings add position info to the input; RoPE rotates Q and K. Combining gives two positional signals that can interfere — the model receives conflicting information about position. Pick one. If you need both extrapolation (RoPE's strength via YaRN) and long-range attention (absolute's strength), use RoPE + YaRN — it gives extrapolation without the locality penalty. Mixing positional encodings is an implementation bug, not a design choice.

## Further reading

- Vaswani et al. (2017), *Attention Is All You Need* — sinusoidal.
- Shaw et al. (2018), *Self-Attention with Relative Position Representations*.
- Dai et al. (2019), *Transformer-XL*.
- Su et al. (2021), *RoFormer: Enhanced Transformer with Rotary Position Embedding*.
- Press et al. (2022), *Train Short, Test Long: Attention with Linear Biases* (ALiBi).
- Peng et al. (2023), *YaRN: Efficient Context Window Extension of Large Language Models*.

## See also

- [[Attention and Transformers MOC]]
- [[Self-Attention]]
- [[Scaled Dot-Product Attention]]
- [[RoPE]]
- [[ALiBi]]
- [[Sinusoidal and Learned Positional Encodings]]
- [[YaRN and NTK-Aware Scaling]]
- [[Multi-Head Attention]]
- [[Transformer Block]]
- [[The Transformer]]
- [[Embedding Layer]]
