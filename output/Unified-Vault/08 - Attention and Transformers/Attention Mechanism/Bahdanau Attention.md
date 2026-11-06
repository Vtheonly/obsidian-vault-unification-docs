---
title: Bahdanau Attention
type: concept
aliases:
  - Bahdanau Attention
  - Additive Attention
tags:
  - attention
  - bahdanau
  - additive-attention
  - seq2seq
  - alignment
  - machine-translation
sources:
  - "Bahdanau Attention"
created_index: 2
---

Bahdanau attention is the original attention mechanism — Bahdanau, Cho, and Bengio's 2014 fix for the sequence-to-sequence information bottleneck. A small feedforward network scores how well each encoder hidden state aligns with the decoder's state, and the decoder reads a weighted average of the encoder states as its context vector at every generation step. Because the alignment function combines its two inputs through a sum inside a $\tanh$, the mechanism is known as additive attention. The pattern it introduced — compute alignment scores, softmax them, take a weighted average — survives unchanged in every attention variant since; only the alignment function has been swapped.

> [!info] TL;DR
> The original attention mechanism (Bahdanau, Cho, Bengio 2014). Uses a small MLP ("additive" attention) to compute alignment scores between decoder state and each encoder hidden state. The decoder then computes a weighted average of encoder states as its context vector at each step.

## Context: the Seq2Seq bottleneck

Bahdanau attention was invented to solve the Seq2Seq information bottleneck — the encoder's final hidden state had to compress the entire source sentence into a single fixed-length vector, and for long sentences that bottleneck lost information. Attention gives the decoder a way to look back at all encoder hidden states at each generation step instead of relying on one compressed summary. The broader story of why attention arose is covered in [[Origins of Attention]] and [[Seq2Seq and the Information Bottleneck]].

## Setup

Given a source sequence $x_1, \ldots, x_{T_x}$ encoded by a bidirectional RNN into hidden states $\mathbf{h}_1^{enc}, \ldots, \mathbf{h}_{T_x}^{enc}$, and a decoder hidden state at step $t$ denoted $\mathbf{h}_t^{dec}$, the mechanism produces a fresh context vector $\mathbf{c}_t$ at every decoding step. Everything below uses this notation.

## The mechanism

### Step 1: compute alignment scores

For each encoder position $i$, compute an alignment score with the current decoder state:

$$
e_{ti} = a(\mathbf{h}_{t-1}^{dec}, \mathbf{h}_i^{enc})
$$

In Bahdanau's original, $a$ is a small feedforward network with a single hidden layer:

$$
a(\mathbf{h}_{t-1}^{dec}, \mathbf{h}_i^{enc}) = \mathbf{v}_a^T \tanh(\mathbf{W}_a \mathbf{h}_{t-1}^{dec} + \mathbf{U}_a \mathbf{h}_i^{enc})
$$

where $\mathbf{W}_a, \mathbf{U}_a, \mathbf{v}_a$ are learned parameters. This is called **additive attention** because it combines the two vectors through a sum inside the $\tanh$.

### Step 2: normalize to attention weights

Softmax over the alignment scores to get a probability distribution over source positions:

$$
\alpha_{ti} = \frac{\exp(e_{ti})}{\sum_{j=1}^{T_x} \exp(e_{tj})}
$$

### Step 3: compute the context vector

Weighted average of encoder hidden states:

$$
\mathbf{c}_t = \sum_{i=1}^{T_x} \alpha_{ti} \mathbf{h}_i^{enc}
$$

### Step 4: use the context in the decoder

The decoder RNN uses $\mathbf{c}_t$ as an additional input:

$$
\mathbf{h}_t^{dec} = \text{RNN}(\mathbf{h}_{t-1}^{dec}, [y_{t-1}; \mathbf{c}_t])
$$

where $[;]$ denotes concatenation.

## Intuition

At each generation step $t$, the decoder asks: "which source words should I focus on right now?" The alignment network $a$ answers by scoring each source position; the softmax turns those scores into a probability distribution; and the context vector is a soft selection from the source — a weighted blend of relevant source hidden states. For translation, this often produces intuitive alignments: when translating the third word of the target, the decoder typically attends to the source word(s) corresponding to that target word.

## A toy worked example

Suppose the source is "the black cat" and we're translating to French, with encoder hidden states $\mathbf{h}_1, \mathbf{h}_2, \mathbf{h}_3$. When generating the first target word "le" (the French definite article), the alignment scores might be $e_{11} = 2.5$ (high — "le" corresponds to "the"), $e_{12} = -0.5$, and $e_{13} = -1.0$. Softmax: $\alpha_{11} \approx 0.92, \alpha_{12} \approx 0.05, \alpha_{13} \approx 0.03$. So

$$
\mathbf{c}_1 \approx 0.92 \mathbf{h}_1 + 0.05 \mathbf{h}_2 + 0.03 \mathbf{h}_3
$$

— almost entirely the encoder state for "the". When generating "noir" (black), attention shifts to $\mathbf{h}_2$.

## Why additive

The name "additive" comes from the form $\mathbf{W}_a \mathbf{h}_{t-1}^{dec} + \mathbf{U}_a \mathbf{h}_i^{enc}$ — the two vectors are added (after separate projections) inside the $\tanh$. [[08 - Attention and Transformers/Attention Mechanism/Luong Attention|Luong Attention]] proposed the simpler "multiplicative" form $\mathbf{h}_{t-1}^{dec} \cdot \mathbf{h}_i^{enc}$, which is faster and has fewer parameters. Multiplicative attention is what the Transformer uses today.

## The alignment network: why a small MLP

The alignment function is deliberately shaped as a small single-hidden-layer MLP, and each design choice has a reason. The **additive combination**: the decoder state and encoder state are projected separately and added inside the $\tanh$, which lets the model learn non-linear interactions between the two. The **single hidden layer**: enough capacity to learn alignment, not so much that it overfits — the hidden dim is typically 64-256. The **scalar output**: $\mathbf{v}_a$ projects to a single scalar (the alignment score), which is what gets softmaxed. The **$\tanh$ activation**: bounded and smooth, giving both positive and negative scores.

Luong's multiplicative $e_{ti} = \mathbf{h}_t^{dec} \cdot \mathbf{h}_i^{enc}$ is simpler (no MLP), faster (just a matmul), and has fewer parameters — and it is the form the Transformer chose. Bahdanau's additive form is more expressive (the MLP can learn non-linear alignment) but slower. Empirically, at scale, multiplicative matches or beats additive — which is why every modern LLM uses multiplicative.

## Why Bahdanau uses the previous decoder state

A subtle point: Bahdanau computes alignment using $\mathbf{h}_{t-1}^{dec}$ (the *previous* decoder state), not $\mathbf{h}_t^{dec}$ (the current). This is because the context $\mathbf{c}_t$ is used as input to compute $\mathbf{h}_t^{dec}$:

$$
\mathbf{h}_t^{dec} = \text{RNN}(\mathbf{h}_{t-1}^{dec}, [y_{t-1}; \mathbf{c}_t])
$$

So you can't use $\mathbf{h}_t^{dec}$ to compute $\mathbf{c}_t$ — it would be circular. You use the previous state $\mathbf{h}_{t-1}^{dec}$ to compute the context, then use the context to update the decoder state. Luong's variant uses the *current* decoder state $\mathbf{h}_t^{dec}$ for alignment (computed normally, then attention is applied as a post-processing step). This is a cleaner separation but requires computing the decoder state before knowing what to attend to.

## Implementation in PyTorch

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class BahdanauAttention(nn.Module):
    def __init__(self, enc_dim, dec_dim, attn_dim):
        super().__init__()
        self.W_a = nn.Linear(dec_dim, attn_dim, bias=False)
        self.U_a = nn.Linear(enc_dim, attn_dim, bias=False)
        self.v_a = nn.Linear(attn_dim, 1, bias=False)
    
    def forward(self, h_dec_prev, h_encs):
        # h_dec_prev: (batch, dec_dim)
        # h_encs: (batch, T, enc_dim)
        # Returns: context (batch, enc_dim), weights (batch, T)
        
        # Score: (batch, T, attn_dim) -> (batch, T, 1) -> (batch, T)
        scores = self.v_a(torch.tanh(
            self.W_a(h_dec_prev).unsqueeze(1) + self.U_a(h_encs)
        )).squeeze(-1)
        
        weights = F.softmax(scores, dim=-1)
        context = (weights.unsqueeze(-1) * h_encs).sum(dim=1)
        return context, weights
```

## A masked worked example

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class BahdanauAttention(nn.Module):
    def __init__(self, enc_dim, dec_dim, attn_dim):
        super().__init__()
        self.W_a = nn.Linear(dec_dim, attn_dim, bias=False)
        self.U_a = nn.Linear(enc_dim, attn_dim, bias=False)
        self.v_a = nn.Linear(attn_dim, 1, bias=False)

    def forward(self, h_dec_prev, h_encs, mask=None):
        # h_dec_prev: (batch, dec_dim)
        # h_encs: (batch, T, enc_dim)
        # mask: (batch, T) — 1 for valid, 0 for padding

        # Score: (batch, T, attn_dim) -> (batch, T, 1) -> (batch, T)
        scores = self.v_a(torch.tanh(
            self.W_a(h_dec_prev).unsqueeze(1) + self.U_a(h_encs)
        )).squeeze(-1)

        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))

        weights = F.softmax(scores, dim=-1)  # (batch, T)
        context = torch.bmm(weights.unsqueeze(1), h_encs).squeeze(1)  # (batch, enc_dim)
        return context, weights

# Test with a toy translation example
batch, T, enc_dim, dec_dim, attn_dim = 2, 5, 16, 16, 32
attn = BahdanauAttention(enc_dim, dec_dim, attn_dim)

h_dec_prev = torch.randn(batch, dec_dim)
h_encs = torch.randn(batch, T, enc_dim)
mask = torch.tensor([[1, 1, 1, 0, 0], [1, 1, 1, 1, 1]])  # Variable-length sequences

context, weights = attn(h_dec_prev, h_encs, mask)
print(f"Context shape: {context.shape}")  # (2, 16)
print(f"Weights shape: {weights.shape}")  # (2, 5)
print(f"Weights sum: {weights.sum(dim=-1)}")  # Should be 1.0 for each batch
print(f"Masked weights (should be 0 for padding):\n{weights}")
```

The mask matters as soon as a batch mixes source lengths: padding positions are set to $-\infty$ before the softmax so they receive exactly zero weight.

## Bahdanau's legacy in modern transformers

Modern Transformers don't use Bahdanau attention directly, but the core idea — "compute alignment scores, softmax, weighted average" — is invariant. The differences are enumerable. Self-attention replaces encoder-decoder attention: Q, K, V all come from the same sequence. Multiplicative (dot-product) alignment replaces additive. Multi-head replaces single attention. And there is no RNN at all — the Transformer removes the recurrence entirely, attending in parallel. But the conceptual lineage is direct: Bahdanau → Luong → Vaswani (self-attention) → multi-head attention → modern LLMs. Understanding Bahdanau is essential for understanding what attention *is* — a dynamic routing of information from a source to a query.

## Why this matters

Bahdanau attention is the **historical origin** of all modern attention mechanisms. The concept — "compute alignment scores, softmax, weighted average" — is invariant across Bahdanau, Luong, and self-attention; only the alignment function changes. Cross-attention in modern Transformers (T5, BART, FLAN) is essentially Bahdanau attention with a multiplicative alignment function. And understanding Bahdanau is the clearest way to understand **what attention is doing**: dynamic routing of information from a source sequence to a target query.

## Production implications

You won't implement Bahdanau attention in production — modern Transformers use self-attention — but you will see the attention pattern everywhere: cross-attention in encoder-decoder models; cross-attention in diffusion models (text → image); and cross-attention in multimodal models (image patches → text tokens). All of these are direct descendants of Bahdanau's idea: a query attends to keys, producing a weighted average of values.

## Common pitfalls and failure modes

Three conceptual pitfalls recur. Confusing additive and multiplicative attention: they're functionally similar but parameterized differently, and the Transformer uses multiplicative (dot-product). Forgetting that Bahdanau uses the **previous** decoder state $\mathbf{h}_{t-1}^{dec}$, not the current — the context is used to compute the current state. And treating attention weights as explanations: they're often intuitive (especially for translation) but can be misleading.

Operationally, the failure modes cluster around masking, capacity, and training dynamics:

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Attention weights are uniform (no specialization) | Insufficient training; or learning rate too low | Train longer; increase LR; check that gradients flow to the alignment network |
| Attention weights focus on padding | Mask not applied | Pass a mask to softmax (set padding positions to -inf before softmax) |
| Attention doesn't help translation quality | Encoder/decoder dims mismatch; or alignment network too small | Match dims; increase attn_dim (64-256 typical) |
| NaN in attention weights | All scores are -inf (all positions masked) | Ensure at least one valid position per query |

## Interview questions

1. **Q: Why does Bahdanau attention use the previous decoder state $\mathbf{h}_{t-1}^{dec}$ instead of the current $\mathbf{h}_t^{dec}$?**
   A: Because the context $\mathbf{c}_t$ is used as input to compute $\mathbf{h}_t^{dec}$: $\mathbf{h}_t^{dec} = \text{RNN}(\mathbf{h}_{t-1}^{dec}, [y_{t-1}; \mathbf{c}_t])$. Using $\mathbf{h}_t^{dec}$ would be circular — you'd need the context to compute the decoder state, but you'd need the decoder state to compute the context. Using the previous state $\mathbf{h}_{t-1}^{dec}$ breaks the circularity: compute context from previous state, then update decoder state using the context. Luong's variant uses the current decoder state by reorganizing the computation (compute decoder state normally, then apply attention as post-processing).

2. **Q: What's the difference between additive (Bahdanau) and multiplicative (Luong) attention?**
   A: **Additive** (Bahdanau): $e_{ti} = \mathbf{v}_a^T \tanh(\mathbf{W}_a \mathbf{h}_{dec} + \mathbf{U}_a \mathbf{h}_{enc})$. Uses a small MLP to compute alignment. More expressive (non-linear), but slower and more parameters. **Multiplicative** (Luong): $e_{ti} = \mathbf{h}_{dec} \cdot \mathbf{h}_{enc}$. Just a dot product. Simpler, faster (maps to matmul), fewer parameters. Empirically, at scale, multiplicative matches or beats additive — which is why the Transformer (and every modern LLM) uses multiplicative. Additive is still used in some encoder-decoder models (T5, BART) for cross-attention.

3. **Q: How does Bahdanau attention solve the Seq2Seq information bottleneck?**
   A: Before Bahdanau, Seq2Seq models compressed the entire source sentence into a single fixed-length vector (the encoder's final hidden state). For long sentences, this bottleneck lost information. Bahdanau attention lets the decoder "look back" at all encoder hidden states at each generation step, dynamically selecting which source words are relevant. The context vector $\mathbf{c}_t$ is a weighted average of encoder states, with weights determined by the alignment network. This effectively gives the decoder access to the entire source sequence, not just a compressed summary.

4. **Q: Why is Bahdanau attention called "additive"?**
   A: Because the alignment function adds the (separately projected) decoder state and encoder state inside the $\tanh$: $\mathbf{W}_a \mathbf{h}_{dec} + \mathbf{U}_a \mathbf{h}_{enc}$. The two vectors are added (after projection) before the non-linearity. This is in contrast to Luong's "multiplicative" attention, which uses a dot product $\mathbf{h}_{dec} \cdot \mathbf{h}_{enc}$ (multiplication, not addition). The naming refers to how the two vectors are combined inside the alignment function.

5. **Q: How does modern cross-attention in Transformers relate to Bahdanau attention?**
   A: Cross-attention in encoder-decoder Transformers (T5, BART) is essentially Bahdanau attention with a multiplicative alignment function. The decoder's queries attend to the encoder's keys and values, producing a weighted average of encoder states — exactly what Bahdanau did. The differences: (1) multiplicative (dot-product) instead of additive (MLP) alignment; (2) multi-head instead of single attention; (3) no RNN — the Transformer removes the recurrence. But the conceptual structure (decoder queries attend to encoder states) is identical to Bahdanau.

6. **Q: Can you use Bahdanau attention with a Transformer?**
   A: Technically yes, but there's no reason to. Bahdanau attention was designed for RNN-based Seq2Seq — it uses the RNN's hidden states as queries/keys/values. Transformers don't have RNN hidden states; they use learned Q/K/V projections. If you replaced Transformer cross-attention with Bahdanau-style additive alignment, you'd lose: (1) the matmul efficiency (additive is slower); (2) multi-head specialization; (3) the ability to scale (additive attention has more parameters per head). Modern Transformers use multiplicative attention because it's faster, simpler, and scales better. Bahdanau is historically important but not used in production Transformers.

## Further reading

- Bahdanau, Cho, Bengio (2014), *Neural Machine Translation by Jointly Learning to Align and Translate*.
- Luong et al. (2015), *Effective Approaches to Attention-based Neural Machine Translation* — comparison with multiplicative.

## See also

- [[Attention and Transformers MOC]]
- [[Origins of Attention]] — the broader context
- [[08 - Attention and Transformers/Attention Mechanism/Luong Attention|Luong Attention]] — the simpler multiplicative variant
- [[Self-Attention]] — the Transformer's generalization
- [[Multi-Head Attention]] — multiple parallel attentions
- [[Queries Keys and Values]] — the modern Q/K/V vocabulary for the same idea
- [[Scaled Dot-Product Attention]] — the multiplicative alignment that won
- [[T5 and BART]] — modern encoder-decoder models with cross-attention
- [[The Encoder-Decoder Pattern]] — the Seq2Seq skeleton this mechanism plugged into
- [[From RNNs to Attention]] — the transition this mechanism began
- [[Seq2Seq and the Information Bottleneck]] — what Bahdanau attention fixed
