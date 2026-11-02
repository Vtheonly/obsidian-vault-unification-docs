---
title: Origins of Attention
type: concept
aliases:
  - "Attention as Soft Lookup"
  - "Origins of Attention"
  - "Soft lookup"
tags:
  - attention
  - seq2seq
  - encoder-decoder
  - machine-translation
  - history
sources:
  - "01. Attention as Soft Lookup — From Bahdanau to Dot-Product"
  - "Origins of Attention"
created_index: 5
---

Attention was invented to fix a specific failure of RNN-based Seq2Seq translation: the entire source sentence had to be squeezed into a single fixed-length vector, and quality degraded as sentences grew longer. Bahdanau, Cho, and Bengio's remedy — letting the decoder re-inspect every encoder state at each output step — generalizes into the idea of attention as a soft, differentiable lookup. That idea, refined from additive scoring to dot-product scoring, is the direct ancestor of the Transformer and of every modern LLM.

> [!info] TL;DR
> Attention was invented (Bahdanau et al., 2014) to solve a specific problem: RNN-based Seq2Seq models compressed the entire source sentence into a single fixed-length vector, creating an information bottleneck. Attention let the decoder "look back" at the source at every step. This single idea reshaped NLP and eventually became the Transformer.

## The problem: the Seq2Seq bottleneck

Before attention, neural machine translation used an **encoder-decoder RNN**. An encoder RNN (LSTM or GRU) reads the source sentence word by word, updating its hidden state; the final hidden state $\mathbf{c}$ — the "thought vector" — serves as a fixed-length summary of the entire source; and a decoder RNN initializes from $\mathbf{c}$ and generates the target sentence word by word.

$$
\mathbf{h}_t^{enc} = \text{RNN}(\mathbf{h}_{t-1}^{enc}, x_t)
$$

$$
\mathbf{c} = \mathbf{h}_T^{enc}
$$

$$
\mathbf{h}_t^{dec} = \text{RNN}(\mathbf{h}_{t-1}^{dec}, y_{t-1}, \mathbf{c})
$$

The decoder must generate the entire output from $\mathbf{c}$ alone, and this is the bottleneck: all information about a 50-word source sentence has to pass through a single vector of, say, 1024 dimensions. The consequences are severe. Sentence length is limited — early models degraded sharply past 30 words. The encoder is forced to compress at the start of the sentence and remember until the end, and RNNs with long dependencies suffer [[07 - Sequence Models/Motivation and Recurrence/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]]. And the per-token hidden states are wasted, because the decoder only ever sees the final one. For short sentences $\mathbf{c}$ has enough capacity; for long sentences it cannot hold all the information, the decoder "forgets" early parts of the source, and translation quality degrades with sentence length. Sutskever et al.'s original Seq2Seq paper offered a telling workaround: reverse the source sentence before encoding, so that the most recently processed (and best remembered) tokens are the ones most relevant to the first output words.

## Attention as a soft lookup

The core idea can be stated in one sentence: **attention is a soft, differentiable lookup: given a query, retrieve a weighted average of a set of values, where the weights measure how relevant each value is to the query.** Everything else — the Bahdanau formulation, the dot-product formulation, the scaling, the multi-head structure — is a specific instantiation of this idea. Hold onto the "soft lookup" framing and every variant will feel like a natural variation.

Bahdanau, Cho, and Bengio proposed the fix: **let the decoder compute a *different* context vector $c_t$ at each output step $t$, as a weighted average of *all* encoder hidden states.**

$$c_t = \sum_{i=1}^{T} \alpha_{t,i} \cdot h_i^{enc}$$

or, in the bold-vector notation of the original formulation, as a sum over the $T$ source positions:

$$\mathbf{c}_t = \sum_{i=1}^{T} \alpha_{ti} \mathbf{h}_i^{enc}$$

The compact inline form $\mathbf{c}_t = \sum_{i=1}^n \alpha_{ti} \mathbf{h}_i$ says the same thing; $\alpha_{ti}$ are the attention weights — how much to attend to source position $i$ at target step $t$. The decoder uses $\mathbf{c}_t$ (different at each step) plus its own hidden state to generate the next token. When translating output word 5, the model might attend strongly to input word 3 (the word being translated) and weakly to everything else, so $c_5 \approx h_3^{enc}$. This single change fixed the bottleneck: the decoder no longer depends on one compressed vector but has direct, time-varying access to every encoder state.

## How the attention weights are computed

The attention weights $\alpha_{t,i}$ must satisfy four requirements. They must be **non-negative** (they are weights in a weighted average); they must **sum to 1** over $i$ (so $c_t$ is a convex combination); they must be **differentiable** (so they can be trained by backpropagation); and they must be **a function of both the decoder state and the encoder state** (so the model can learn *what to attend to*).

The standard way to achieve all four is to compute a **score** $s_{t,i}$ for each (decoder step $t$, encoder position $i$) pair, then softmax over $i$:

$$\alpha_{t,i} = \frac{\exp(s_{t,i})}{\sum_{j=1}^{T} \exp(s_{t,j})}$$

Bahdanau's original paper writes the same computation with an energy term $e_{ti} = a(\mathbf{h}_{t-1}^{dec}, \mathbf{h}_i^{enc})$, where $a(\cdot, \cdot)$ is a learned alignment function (a small MLP in Bahdanau's original):

$$
\alpha_{ti} = \frac{\exp(e_{ti})}{\sum_j \exp(e_{tj})}
$$

The score function is where the variants differ. The two most important:

### Bahdanau (additive) attention

$$s_{t,i} = v^\top \tanh(W_s \cdot s_{t-1}^{dec} + W_h \cdot h_i^{enc})$$

where $s_{t-1}^{dec}$ is the decoder's previous hidden state, $h_i^{enc}$ is the encoder hidden state at position $i$, and $v, W_s, W_h$ are learnable parameters. It is called "additive" because the two states are projected and *added* before the tanh; equivalently, it is a small feedforward network that scores the match between decoder and encoder states, with alignment score $\mathbf{v}^T \tanh(\mathbf{W}_s \mathbf{s} + \mathbf{W}_h \mathbf{h})$.

### Dot-product (multiplicative) attention

$$s_{t,i} = (s_{t-1}^{dec})^\top h_i^{enc}$$

or, with learned projections:

$$s_{t,i} = (W_Q \cdot s_{t-1}^{dec})^\top (W_K \cdot h_i^{enc})$$

This is just a dot product between (projected) decoder and encoder states. It is cheaper than Bahdanau's form (no tanh, no intermediate projection) and empirically works as well or better. Luong et al. (2015) made the same simplification with the alignment score $\mathbf{s}^T \mathbf{W} \mathbf{h}$ — simpler and faster. **The Transformer uses dot-product attention**, so this is the variant that became dominant.

## Why dot-product attention works: the geometric intuition

A dot product measures **alignment** — how much two vectors point in the same direction. If the decoder's state at output step $t$ and the encoder's state at input position $i$ point in similar directions, their dot product is large, and the attention weight $\alpha_{t,i}$ will be high.

Geometrically, the decoder is "asking a question" (what am I translating right now?), and each encoder position is "offering an answer" (I am this kind of word, with this kind of meaning). The dot product measures how well the question matches each answer. Softmax turns these match scores into a probability distribution, and the weighted average retrieves a blended answer. This is exactly a **soft lookup** — a database query where the keys and the query are vectors, the match function is a dot product, and the retrieval is a weighted average rather than a hard selection. The database framing is made precise in [[Queries Keys and Values]], which introduces the Q/K/V notation the Transformer uses.

## A worked example: translating "the black cat"

Suppose we are translating "the black cat" to French ("le chat noir"). The encoder produces three hidden states: $h_1^{enc}$ (for "the"), $h_2^{enc}$ (for "black"), $h_3^{enc}$ (for "cat"). The decoder generates three output words.

At output step 1 (generating "le"), the decoder's state asks: "I need the French determiner. Which input word is the determiner?" The score $s_{1,1}$ (with "the") is high; $s_{1,2}$ (with "black") and $s_{1,3}$ (with "cat") are low. The attention weights come out as $\alpha_{1,1} = 0.9, \alpha_{1,2} = 0.05, \alpha_{1,3} = 0.05$, so the context is $c_1 \approx 0.9 \cdot h_1^{enc}$ — almost entirely "the".

At output step 2 (generating "chat"), the decoder's state asks for the French noun. The score $s_{2,3}$ (with "cat") is high, attention concentrates as $\alpha_{2,3} = 0.85$, and $c_2 \approx 0.85 \cdot h_3^{enc}$ — almost entirely "cat".

At output step 3 (generating "noir"), the decoder's state asks for the French adjective. The score $s_{3,2}$ (with "black") is high, $\alpha_{3,2} = 0.9$, and $c_3 \approx 0.9 \cdot h_2^{enc}$ — almost entirely "black".

Notice the alignment: the attention weights form a (roughly) diagonal matrix, because French and English word order happen to align here. For language pairs with different word order (e.g., English→Japanese), the attention matrix would be non-diagonal — and that is exactly the kind of structural information attention can learn.

The alignment-matrix view is one of attention's most interpretable aspects. For a longer sentence the weights $\alpha_{ti}$ form an alignment matrix showing which source word corresponds to which target word:

```python
# For English → French translation:
# Source: "the cat sat on the mat"
# Target: "le chat s'est assis sur le tapis"

# Attention weights (simplified):
#         the   cat   sat   on   the   mat
# le     [0.7   0.2   0.0   0.0  0.1    0.0]  # "le" attends to "the"
# chat   [0.1   0.8   0.0   0.0  0.1    0.0]  # "chat" attends to "cat"
# s'est  [0.0   0.0   0.7   0.2  0.0    0.0]  # "s'est" attends to "sat"
# assis  [0.0   0.0   0.8   0.1  0.0    0.0]  # "assis" attends to "sat"
# sur    [0.0   0.0   0.0   0.9  0.0    0.0]  # "sur" attends to "on"
# le     [0.1   0.0   0.0   0.0  0.7    0.2]  # "le" attends to "the"
# tapis  [0.0   0.0   0.0   0.0  0.1    0.8]  # "tapis" attends to "mat"
```

This alignment is **learned** — the model isn't told the alignment, it discovers it through training. The attention weights are interpretable in a way that RNN hidden states are not, and for translation they often recover word-alignments that match linguistic intuition.

## From one context to per-step context

The single most important conceptual shift from the Encoder-Decoder RNN to attention is this: **before attention, one context vector $c$ for the entire output; with attention, one context vector $c_t$ per output step, computed on-the-fly from all encoder states.** This shift is what makes the decoder a *selective reader* rather than a *fixed-memory generator*.

Concretely, the change buys three things. **Variable-length compression**: the summary $\mathbf{c}_t$ is now different at each step, focused on the relevant source words. **Long sentences**: with no information bottleneck, quality no longer degrades with length. **Interpretability**: the attention weights $\alpha_{ti}$ can be visualized as an alignment matrix between source and target. And the shift is what makes the next generalization — self-attention — natural: if attention lets a decoder read an encoder, why not let a sequence read *itself*?

## Why this was a big deal

Before attention, NMT was losing to phrase-based statistical MT (Moses) on long sentences. After attention, NMT pulled ahead — and within two years, every major MT system was neural. The attention paper has been cited 100,000+ times.

But attention's bigger impact was conceptual: it showed that **the way to handle variable-length sequences is dynamic routing, not fixed compression**. This insight, plus the realization that attention doesn't actually need the RNN, became the Transformer (Vaswani et al., 2017).

## From RNN+attention to the Transformer

The Transformer paper's key insight: **the RNN is unnecessary**. Attention alone, with positional information, can do everything the RNN+attention combo could do — and it's parallelizable. The Transformer made three changes: it removed the RNN entirely; it made attention the core operation (self-attention instead of encoder-decoder attention); and it added positional encoding to compensate for losing the RNN's implicit order processing. The derivation of self-attention itself is covered in [[Self-Attention]].

### From cross-attention to self-attention

Bahdanau attention was **cross-attention** — the decoder attends to the encoder, two different sequences. The leap to **self-attention** (Transformer, 2017) was: why not attend within the same sequence? In a sentence, each word's meaning depends on the other words in the same sentence — "bank" in "river bank" versus "bank account" means something different depending on context. Self-attention lets each word attend to all other words in the same sequence, building contextual representations.

The reason self-attention replaced RNNs is a contrast in computational structure. An RNN is sequential — it processes one token at a time, with the hidden state carrying information forward. Self-attention is parallel — every token attends to every other in one step, with no sequential bottleneck. The result: Transformers train 10× faster than RNNs on GPUs (parallelism) and capture long-range dependencies better (no vanishing gradients through time). The conceptual path runs cross-attention (Bahdanau, 2014) → self-attention (Transformer, 2017) → modern attention (GQA, MLA, 2023+); each step refined the attention mechanism for a new use case.

## Variants of pre-Transformer attention

The original Bahdanau attention used a small MLP as the alignment function $a(\cdot, \cdot)$ — "additive" attention. Luong et al. (2015) proposed simpler "multiplicative" variants — dot product, general, and others; the deep comparison lives in [[08 - Attention and Transformers/Attention Mechanism/Luong Attention|Luong Attention]] and [[08 - Attention and Transformers/Attention Mechanism/Bahdanau Attention|Bahdanau Attention]].

Several other variants were explored in the same era. **Global vs local attention** (Luong et al., 2015) chooses between attending to all source positions (global) or just a window (local). **Hard vs soft attention** (Xu et al., 2015) distinguishes the differentiable weighted average (soft) from picking a single position (hard), the latter requiring REINFORCE to train. **Monotonic attention** (Raffel et al., 2017) enforces that attention moves forward, which is useful for tasks with monotonic alignment (e.g., ASR).

## The historical timeline

### 2014 (September): Seq2Seq (Sutskever et al.)

RNN encoder + RNN decoder for translation. The problem: a single fixed-length "thought vector" creates an information bottleneck. The workaround: reverse the source sentence, which made the relevant information the most recently processed.

### 2014 (September): Bahdanau attention (Bahdanau, Cho, Bengio)

Added attention to Seq2Seq: the decoder computes a weighted average of encoder hidden states at each step. This solved the bottleneck — the decoder can retrieve any source position. Bahdanau used **additive attention** (alignment score = $\mathbf{v}^T \tanh(\mathbf{W}_s \mathbf{s} + \mathbf{W}_h \mathbf{h})$). The paper appeared in September 2014 and is also widely cited as 2015 — both dates refer to the same work.

### 2015: Luong attention (Luong et al.)

Simplified Bahdanau's attention. Used **multiplicative attention** (alignment score = $\mathbf{s}^T \mathbf{W} \mathbf{h}$) — simpler and faster. Introduced "local attention" — attending to a window around a predicted position (a precursor to sliding window attention).

### 2017: The Transformer (Vaswani et al.)

"Attention Is All You Need" — removed RNNs entirely; attention only. **Self-attention**: attend within the same sequence, not cross-sequence attention to another sequence. **Multi-head attention**: multiple attention heads in parallel. **Scaled dot-product attention**: $\text{softmax}(QK^T / \sqrt{d_k}) V$. Solved the RNN's sequential bottleneck — fully parallel.

### 2018 and after: modern attention

[[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]] (2018) brought bidirectional self-attention for encoding; GPT (2018+) brought causal self-attention for generation. Efficient attention (2020+) — FlashAttention, sparse, linear, sliding window — attacked the quadratic cost. Modern attention (2023+) — GQA, MQA, MLA — reduced the KV cache. Each step refined attention for a new use case: translation, encoding, generation, efficiency, serving.

## Why this matters for AI

Attention is the **foundation of every modern LLM**; if you don't understand the Seq2Seq bottleneck, you don't understand why attention exists. The progression RNN → RNN+attention → Transformer is the canonical example of how architectural ideas evolve, and studying it teaches you how to think about model design.

Many modern architectures revisit these ideas directly: linear attention, sparse attention, and hybrid SSM-attention models all explore different points in the "how to handle variable-length sequences" design space. And **cross-attention** — the original Bahdanau idea — is still everywhere: T5, BART, FLAN, diffusion models (cross-attention to text), and multimodal models (cross-attention between modalities).

## Production implications

For most modern applications you don't implement attention yourself — you use a Transformer library. But understanding the mechanics is essential for choosing between models (GQA vs MHA matters for inference latency), for debugging (why is my model ignoring the end of the long context?), and for understanding inference cost (the KV cache is attention's memory).

Long-context failures often look like the original Seq2Seq bottleneck: the model "forgets" the middle of the context. This is the modern version of the problem attention was invented to solve, and modern long-context architectures (Ring Attention, Infini-Attention) are modern solutions.

## Interview questions

The points interviewers probe most about attention's origins, with the answers worth internalizing:

1. **What specific problem was attention invented to solve?** RNN Seq2Seq's information bottleneck. Seq2Seq compressed the entire source sentence into a single fixed-length vector $\mathbf{c}$; for long sentences, $\mathbf{c}$ couldn't hold all the information, and translation quality degraded with length. Attention solved this by giving the decoder per-step access to all encoder hidden states, computed as a weighted average $\mathbf{c}_t = \sum_i \alpha_{ti} \mathbf{h}_i$. The bottleneck was broken — the decoder could retrieve any source position at any time.

2. **What's the difference between cross-attention and self-attention?** Cross-attention (Bahdanau, 2014): the decoder attends to the encoder — different sequences. Self-attention (Transformer, 2017): a sequence attends to itself — the same sequence. Self-attention is the natural extension: each word attends to all other words in the same sentence to build contextual representations. The conceptual leap was realizing that the attention mechanism works within a sequence, not just across sequences.

3. **Why did attention replace RNNs?** Three reasons. (1) Parallelism: self-attention processes all tokens in parallel while RNNs are sequential, so Transformers train 10× faster on GPUs. (2) Long-range dependencies: attention has direct access to any position, while RNNs suffer vanishing gradients through time. (3) Bottleneck removal: attention gives per-step access to all positions, while an RNN compresses into a fixed hidden state. The Transformer (2017) removed RNNs entirely — "Attention Is All You Need".

4. **What do attention weights represent, and are they interpretable?** In cross-attention (translation), the weights $\alpha_{ti}$ represent word alignments — which source word corresponds to which target word. This is interpretable and was a major selling point of early attention. In self-attention, the weights show which tokens each token attends to — useful for analysis but less directly interpretable. Caveat: attention weights are correlational, not causal — high attention doesn't mean the model "uses" that information.

5. **How did Bahdanau attention differ from Luong attention?** Bahdanau (2014) used **additive attention**: alignment score = $\mathbf{v}^T \tanh(\mathbf{W}_s \mathbf{s} + \mathbf{W}_h \mathbf{h})$ — a small neural network. Luong (2015) used **multiplicative attention**: alignment score = $\mathbf{s}^T \mathbf{W} \mathbf{h}$ — a simple dot product. Luong's is simpler and faster; Bahdanau's is more expressive. Modern Transformers use the multiplicative form (scaled dot-product) for efficiency. Luong also introduced "local attention" — a precursor to sliding window attention.

6. **Trace the evolution from Bahdanau attention to modern Transformers.** (1) Bahdanau (2014): cross-attention for Seq2Seq translation — solved the bottleneck. (2) Luong (2015): simplified to multiplicative attention; introduced local attention. (3) Transformer (2017): self-attention within a sequence; removed RNNs; multi-head attention; scaled dot-product. (4) BERT/GPT (2018): bidirectional/causal self-attention for pretraining. (5) Efficient attention (2020+): FlashAttention, sparse, linear. (6) Modern attention (2023+): GQA, MQA, MLA for KV cache reduction. Each step refined attention for a new use case — translation, encoding, generation, efficiency, serving.

## What to take away

Attention is a soft, differentiable lookup — a weighted average of values, weighted by relevance to a query. Bahdanau attention fixed the Encoder-Decoder bottleneck by computing a different context $c_t$ at each step from all encoder hidden states. The weights are softmaxed scores, and the score function can be additive (Bahdanau) or dot-product (Transformer). Dot-product attention measures geometric alignment between query and key vectors — the "match" in a soft lookup. And the key shift from one context to per-step context is what turned the decoder into a selective reader.

## Further reading

- Bahdanau, Cho, Bengio (2014), *Neural Machine Translation by Jointly Learning to Align and Translate* — the original attention paper.
- Sutskever et al. (2014), *Sequence to Sequence Learning with Neural Networks* — the Seq2Seq model attention fixed.
- Luong et al. (2015), *Effective Approaches to Attention-based Neural Machine Translation* — multiplicative attention.
- Vaswani et al. (2017), *Attention Is All You Need* — the Transformer.

## See also

- [[Attention and Transformers MOC]]
- [[08 - Attention and Transformers/Attention Mechanism/Bahdanau Attention|Bahdanau Attention]]
- [[08 - Attention and Transformers/Attention Mechanism/Luong Attention|Luong Attention]]
- [[Self-Attention]]
- [[Multi-Head Attention]]
- [[Scaled Dot-Product Attention]]
- [[Queries Keys and Values]]
- [[From RNNs to Attention]]
- [[The Encoder-Decoder Pattern]]
- [[The Bottleneck Problem]]
- [[Long-Range Dependencies]]
- [[07 - Sequence Models/Motivation and Recurrence/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]]
