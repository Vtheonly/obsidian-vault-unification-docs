---
title: From RNNs to Attention
type: concept
aliases:
  - From RNNs to Attention - The Historical Bridge
  - The Historical Bridge
  - RNNs to Attention
tags:
  - sequence-models
  - rnn
  - attention
  - transformer
  - encoder-decoder
  - history
sources:
  - "03. From RNNs to Attention — The Historical Bridge"
created_index: 9
---

This note is the bridge from the sequence-model material to the attention and Transformer material that follows it. Its job is to make that transition feel inevitable — to show that attention was not an arbitrary invention but the natural next step after the limitations of RNNs became clear. It builds directly on [[The Bottleneck Problem]] and [[Long-Range Dependencies]], and it hands off to the attention mechanisms that resolve them.

> [!info] TL;DR
> The trajectory is RNN → bottleneck → attention (Bahdanau et al. 2015) → self-attention (Vaswani et al. 2017) → Transformer. Each step answers a specific limitation of the previous one, and the Transformer's own unsolved problems — quadratic cost, exposure bias, autoregressive ordering — define the current research frontier.

## The story so far, in four limitations

By 2014, the Encoder-Decoder RNN ([[The Encoder-Decoder Pattern]]) was the state of the art for sequence-to-sequence tasks like translation. But it had four well-understood limitations:

1. **The bottleneck** ([[The Bottleneck Problem]]): the entire input must be compressed into a single fixed-size vector $c$, which is information-theoretically impossible for long inputs.
2. **No lookback**: the decoder cannot revisit specific input tokens; it is stuck with whatever made it into $c$.
3. **Long-range decay** ([[Long-Range Dependencies]]): even with LSTMs, information from far back in the input is degraded by the time it reaches the decoder.
4. **Sequential processing**: the recurrence is inherently sequential — step $t$ cannot be computed until step $t-1$ is done. This makes training slow on long sequences and forbids parallelism across time.

Each of these is a consequence of the same design choice: **the only connection between encoder and decoder is a single vector, passed through a sequential chain of transformations.**

## The 2015 fix: attention (Bahdanau et al.)

Bahdanau, Cho, and Bengio (2015) addressed limitations 1, 2, and 3 with a single idea: **let the decoder compute a different context vector $c_t$ at each output step, as a weighted average of all encoder hidden states.**

$$c_t = \sum_{i=1}^{T} \alpha_{t,i} \cdot h_i^{enc}$$

where $\alpha_{t,i}$ is an attention weight — how much output step $t$ should attend to input step $i$.

This shatters the bottleneck (limitation 1): the decoder is no longer limited to a fixed-size summary. It grants lookback (limitation 2): the decoder can attend to any input position at any output step. And it addresses long-range decay (limitation 3): the path from input $i$ to output $t$ is now a single weighted connection, not a chain of $|t - i|$ recurrent steps.

Limitation 4 (sequential processing) remained — the encoder and decoder were still RNNs, still sequential. But the first three were solved, and translation quality improved dramatically, especially on long sentences. The full mechanism is developed in [[Origins of Attention]] and [[08 - Attention and Transformers/Attention Mechanism/Bahdanau Attention|Bahdanau Attention]].

## The 2017 generalization: self-attention (Vaswani et al.)

The Bahdanau attention was **cross-attention**: the decoder attended to the encoder. But the idea of "compute a context as a weighted average of vectors, with weights computed by a small network" is more general than the encoder-decoder setting.

Vaswani et al. (2017) asked: **what if a sequence attends to itself?** Instead of a decoder attending to an encoder, let every position in a sequence attend to every other position in the *same* sequence. This is **self-attention** ([[Self-Attention]]), and it has a remarkable property: it captures intra-sequence dependencies directly, with path length 1, regardless of distance.

With self-attention, the RNN becomes redundant. The RNN's job was to propagate information across time so that position $t$ could "know about" position $i < t$. Self-attention does this directly: position $t$ attends to position $i$ in a single step. There is no need to carry information through a sequential chain.

So Vaswani et al. dropped the RNN entirely and built a model out of stacked self-attention layers plus feedforward layers. This model is the **Transformer** ([[The Transformer]]), and it addressed all four limitations:

1. **No bottleneck** — every position has direct access to every other position.
2. **Full lookback** — attention weights let each position select what it needs.
3. **No long-range decay** — the path length is 1, not $O(T)$.
4. **Parallel processing** — all positions can be computed simultaneously (no sequential recurrence).

## The design decisions that fall out of this story

Once you understand the trajectory "RNN → bottleneck → attention → self-attention → Transformer," several otherwise-mysterious design decisions become natural.

**Why positional encodings?** Self-attention has no notion of order — it treats the sequence as a set. But order matters for sequences (see [[Why Sequence Models]]). Positional encodings ([[Positional Encoding]]) inject order information back in. The RNN did not need this because its sequential processing *was* the order; the Transformer needs it because its parallel processing *erases* order.

**Why multi-head attention?** A single attention head can learn one pattern of relationships ("which input word should I translate now?"). But language has many simultaneous relationship types — syntactic, semantic, coreference, discourse. Multi-head attention ([[Multi-Head Attention]]) lets the model learn multiple relationship patterns in parallel, like multiple feature maps in a CNN.

**Why the $\frac{1}{\sqrt{d_k}}$ scaling?** Without scaling, the dot products grow with dimension $d_k$, pushing the softmax into saturated regions where gradients vanish. The scaling keeps the softmax in a well-behaved range. This is a numerical-stability detail, not a deep idea — but it is necessary.

**Why LayerNorm instead of BatchNorm?** BatchNorm depends on batch statistics, which are ill-defined for variable-length sequences and small batches. LayerNorm normalizes across the feature dimension per-token, so it is batch-independent and sequence-length-independent. This is the same reason LayerNorm is used in RNNs (see [[05 - Neural Network Foundations/Training Dynamics and Stability/Batch Normalization|Batch Normalization]] for the alternatives).

Each of these is a response to a specific problem that arises when you replace recurrence with attention. None of them is arbitrary; each falls out of the design.

## What the Transformer does *not* solve

It is worth being honest about what the Transformer does not fix:

1. **Quadratic cost in sequence length.** Self-attention compares every pair of positions, so it is $O(T^2)$ in memory and compute. RNNs are $O(T)$. For sequences of 1000 tokens this is fine; for sequences of 100,000 tokens (long documents, high-resolution images) it becomes prohibitive. This has driven a large research literature on efficient attention: [[Sparse Attention]], [[Linear Attention]], [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]], and state-space models like Mamba.
2. **Exposure bias.** Transformers still use teacher forcing for training and still suffer from exposure bias at inference (see [[Teacher Forcing and Exposure Bias]]).
3. **The ordering problem for generation.** A Transformer decoder generates left-to-right, just like an RNN decoder. It cannot generate tokens in parallel or in arbitrary order. This is a limitation of the *decoder* design, not of attention itself, and it has driven work on non-autoregressive generation ([[Autoregressive vs Parallel Encoding]]).

These are the frontiers of current research, and they are the natural next limitations to attack after the Transformer's wins have been consolidated.

## Where this leads next

Everything needed for the attention and Transformer material is now in place. You know why sequence models exist (07.1; [[Why Sequence Models]]), how RNNs work and why they fail (07.1, 07.2; [[The Recurrent Neuron]], [[LSTM]], [[Backpropagation Through Time]], [[07 - Sequence Models/Motivation and Recurrence/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]]), the Encoder-Decoder pattern and its bottleneck (07.3, 07.4; [[The Encoder-Decoder Pattern]], [[The Bottleneck Problem]]), and the fact that attention was invented to fix that bottleneck while self-attention generalizes attention to the point where the RNN becomes redundant.

The build order that follows mirrors this story: first attention as an operation ([[Origins of Attention]], [[08 - Attention and Transformers/Attention Mechanism/Bahdanau Attention|Bahdanau Attention]]); then self-attention as its application to a single sequence ([[Self-Attention]]); then multi-head attention for parallel relationship patterns ([[Multi-Head Attention]]); then positional encoding to inject order ([[Positional Encoding]]); then the full encoder block ([[Transformer Block]]) and the full decoder block ([[Transformer Decoder Block]]); then the Vision Transformer — how this NLP invention conquered computer vision ([[ViT Architecture]]); and finally the encoder-vs-decoder design space ([[BERT vs GPT vs T5]]).

Nothing in that material will feel arbitrary: every component is a response to a limitation you have already seen. The trajectory to carry forward is RNN → bottleneck → attention (Bahdanau 2015) → self-attention (Vaswani 2017) → Transformer, with each step a response to a specific limitation of the previous one; the Transformer's design decisions — positional encoding, multi-head attention, the $\frac{1}{\sqrt{d_k}}$ scaling, LayerNorm — all natural responses to the problems of replacing recurrence with attention; and its remaining open problems — quadratic cost, exposure bias, and autoregressive ordering — the frontier to attack next.

## See also

- [[07 - Sequence Models/Chapter Overview|Chapter Overview]]
- [[The Bottleneck Problem]]
- [[Long-Range Dependencies]]
- [[The Encoder-Decoder Pattern]]
- [[Attention and Transformers MOC]]
- [[Origins of Attention]]
- [[08 - Attention and Transformers/Attention Mechanism/Bahdanau Attention|Bahdanau Attention]]
- [[The Transformer]]
