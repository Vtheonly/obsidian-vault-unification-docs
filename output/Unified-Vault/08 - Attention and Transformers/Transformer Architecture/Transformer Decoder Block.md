---
title: Transformer Decoder Block
type: concept
aliases:
  - Decoder block
  - Transformer decoder block
  - Masked self-attention
  - Cross-attention
tags:
  - transformer
  - decoder
  - causal-masking
  - cross-attention
  - autoregressive-generation
sources:
  - "04. The Transformer Decoder Block — Masking and Cross-Attention"
created_index: 34
---

The Transformer decoder block is the encoder block's generative counterpart. Where an encoder block is symmetric — every position attends to every other position — the decoder block adds two mechanisms that make autoregressive generation and sequence-to-sequence conditioning possible: causal masking in self-attention and cross-attention into the encoder's output. Those two additions give the decoder block three sublayers instead of the encoder's two: masked self-attention, cross-attention, and the position-wise feedforward network, each wrapped in a residual connection and a LayerNorm.

> [!info] TL;DR
> A decoder block = masked self-attention (causal; positions see only the past) + cross-attention (queries from the decoder, keys and values from the encoder) + FFN, each with residual + LayerNorm. The causal mask is an upper-triangular $-\infty$ matrix applied before the softmax; it is what allows parallel training while preserving autoregressive generation. Decoder-only models (GPT, LLaMA) keep the mask but drop cross-attention.

## What the decoder does differently

The encoder block is symmetric: every position attends to every other position. That is fine for understanding tasks — BERT-style classification, entity recognition, reading comprehension — where the whole input is available at once. The decoder differs in two ways.

First, it generates autoregressively: at inference time it produces one token at a time, and each token can only attend to *previously generated* tokens — not future ones. This is enforced by causal masking in self-attention. Second, it attends to the encoder's output: in an encoder-decoder Transformer (for translation, summarization), the decoder needs to look at the input. This is cross-attention — a second attention operation that attends from decoder positions to encoder positions. These two differences mean the decoder block has three sublayers, not two.

## The decoder block in one diagram

```
      Y (decoder input)
        │
        ▼
┌────────────────────┐
│ Masked Multi-Head  │── residual
│ Self-Attention     │
└────────────────────┘
        │
        ▼
┌────────────────────┐
│ LayerNorm          │
└────────────────────┘
        │
        ▼
┌────────────────────┐
│ Multi-Head         │── residual
│ Cross-Attention    │   (Q from decoder, K/V from encoder)
└────────────────────┘
        │
        ▼
┌────────────────────┐
│ LayerNorm          │
└────────────────────┘
        │
        ▼
┌────────────────────┐
│ Feedforward (MLP)  │── residual
└────────────────────┘
        │
        ▼
┌────────────────────┐
│ LayerNorm          │
└────────────────────┘
        │
        ▼
     Output
```

Three sublayers: masked self-attention, cross-attention, FFN — each wrapped in residual + LayerNorm. The two-sublayer anatomy this builds on is in [[Transformer Block]].

## Sublayer 1: masked self-attention

This is standard self-attention with one modification: a mask is applied to the attention matrix to prevent positions from attending to future positions.

The unmasked attention matrix is $Q K^\top \in \mathbb{R}^{T \times T}$. Entry $(i, j)$ is the score for query $i$ attending to key $j$. For causal (autoregressive) generation, position $i$ should only attend to positions $j \leq i$ — the future positions $j > i$ are not yet generated. The mask sets the scores for $j > i$ to $-\infty$ before the softmax:

$$\text{MaskedScores}_{i,j} = \begin{cases} (Q K^\top)_{i,j} & \text{if } j \leq i \\ -\infty & \text{if } j > i \end{cases}$$

After softmax, $e^{-\infty} = 0$, so the attention weights for future positions are exactly zero: position $i$ attends only to positions $1, \ldots, i$.

This is what makes the decoder autoregressive: at inference time, you generate token 1 from just token 1's query (attending to itself and the encoder), then token 2 from tokens 1–2, then token 3 from tokens 1–3, and so on. Each token can only see the past, never the future.

> [!IMPORTANT] The mask is triangular.
> The causal mask is an upper-triangular matrix of $-\infty$ values. This is the "look-ahead mask" — it prevents looking ahead. Visually, the attention matrix becomes lower-triangular: the diagonal and below are real scores, above the diagonal is zero.

### Why masking matters for training

During training, the decoder receives all target tokens at once (teacher forcing — see [[Teacher Forcing and Exposure Bias]]). Without the mask, position 5 could attend to position 10, "cheating" by looking at the answer. The mask prevents this, ensuring that the training loss at each position reflects a genuine prediction task (predict token $t$ from tokens $1, \ldots, t-1$ and the encoder output), not a copy task.

The mask is what lets us train the decoder in parallel (all positions at once) while preserving the autoregressive property (each position only sees the past). Without it, you would have to train the decoder sequentially, one position at a time, which would forfeit the Transformer's parallelism advantage.

## Sublayer 2: cross-attention

This is the second attention operation, and it is where the decoder "looks at" the encoder's output. The query comes from the decoder; the keys and values come from the encoder:

$$Q_{dec} = Y W_Q^{cross}, \quad K_{enc} = X_{enc} W_K^{cross}, \quad V_{enc} = X_{enc} W_V^{cross}$$
$$\text{CrossAttention} = \text{softmax}\left(\frac{Q_{dec} K_{enc}^\top}{\sqrt{d_k}}\right) V_{enc}$$

The attention matrix here is $T_{dec} \times T_{enc}$ — each decoder position attends to all encoder positions. This is the direct descendant of [[08 - Attention and Transformers/Attention Mechanism/Bahdanau Attention|Bahdanau Attention]], now reformulated as dot-product attention.

Cross-attention is what makes this an encoder-decoder Transformer rather than a decoder-only one: decoder-only models (GPT) omit this sublayer — they have no encoder to attend to. The design choice is covered in [[BERT vs GPT vs T5]].

## Sublayer 3: feedforward

Same as the encoder's FFN — a position-wise MLP providing nonlinearity. No new ideas here; see [[Transformer Block]] for the full treatment.

## How the decoder generates at inference time

At inference, the decoder generates one token at a time:

1. **Step 1:** Feed `<BOS>` (beginning of sequence) as the only input. The decoder produces a distribution over the first output token. Sample (or argmax) token $y_1$.
2. **Step 2:** Feed `<BOS>, y_1` as input. The decoder produces a distribution over the second token. Sample $y_2$.
3. **Step 3:** Feed `<BOS>, y_1, y_2`. Sample $y_3$.
4. ...continue until `<EOS>` is generated.

At each step, the masked self-attention ensures the new token's query can only attend to previously generated tokens, and the cross-attention lets it attend to the encoder's output (which is computed once and reused).

> [!NOTE] KV caching.
> Naively, step $t$ recomputes attention over all $t$ previous tokens, making generation $O(T^2)$ total. In practice, **KV caching** stores the keys and values from previous steps and only computes the new token's Q, K, V, reducing per-step cost to $O(T)$. This is an engineering optimization, not an architectural change — the math is the same.

## Encoder-decoder versus decoder-only

The decoder block as built here has cross-attention, which makes it suitable for sequence-to-sequence tasks (translation, summarization) where there is a distinct input and output. But many modern models (GPT, LLaMA) are decoder-only: they omit cross-attention and use only masked self-attention + FFN. These models are trained on a single sequence (e.g., "predict the next token in this text"), with no separate encoder.

The short version of the trade-off: encoder-decoder is natural for tasks with distinct inputs and outputs; decoder-only is simpler and dominates modern LLMs because it can be trained on any text without needing input/output pairs. [[Autoregressive vs Parallel Encoding]] and [[Choosing the Right Architecture]] develop this design space further; models built on the full pattern are covered in [[T5 and BART]].

## Summary

The essentials in one place: the decoder block has three sublayers — masked self-attention, cross-attention, FFN — each wrapped in residual + LayerNorm. Masked self-attention prevents positions from attending to the future, which is what makes the decoder autoregressive; the mask is an upper-triangular $-\infty$ matrix. Cross-attention lets the decoder attend to the encoder's output — Bahdanau attention reformulated as dot-product attention. The mask is what lets the decoder train in parallel (all positions at once) while preserving the autoregressive property. Decoder-only models (GPT) omit cross-attention and use only masked self-attention + FFN.

## See also

- [[Attention and Transformers MOC]]
- [[Transformer Block]] — the two-sublayer encoder block this note builds on
- [[The Transformer]] — the full assembled architecture
- [[T5 and BART]] — encoder-decoder models built from these blocks
- [[08 - Attention and Transformers/Attention Mechanism/Bahdanau Attention|Bahdanau Attention]] — the ancestor of cross-attention
- [[Scaled Dot-Product Attention]], [[Multi-Head Attention]]
- [[Teacher Forcing and Exposure Bias]], [[The Encoder-Decoder Pattern]]
- [[Autoregressive vs Parallel Encoding]], [[BERT vs GPT vs T5]], [[Choosing the Right Architecture]]
