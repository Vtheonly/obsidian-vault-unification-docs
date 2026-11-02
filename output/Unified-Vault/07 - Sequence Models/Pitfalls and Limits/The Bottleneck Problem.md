---
title: The Bottleneck Problem
type: concept
aliases:
  - The Bottleneck Problem - Why One Vector Is Not Enough
  - context vector bottleneck
  - fixed-vector bottleneck
  - encoder-decoder bottleneck
tags:
  - sequence-models
  - encoder-decoder
  - rnn
  - attention
  - machine-translation
sources:
  - "01. The Bottleneck Problem — Why One Vector Is Not Enough"
created_index: 11
---

In the Encoder-Decoder RNN, the *only* information that passes from the encoder to the decoder is a single fixed-size vector — and that one design choice is responsible for the architecture's most damaging failures. This note states the bottleneck precisely, works through its three failure modes, and previews the fix that Bahdanau, Cho, and Bengio proposed in 2015. Few ideas matter more for what follows: if you understand the bottleneck, you understand why attention was invented; and if you understand why attention was invented, the entire Transformer architecture becomes a natural response to a clear problem rather than an arbitrary stack of matrix multiplications.

> [!info] TL;DR
> The Encoder-Decoder RNN passes a single fixed-size vector $c = h_T^{enc}$ from encoder to decoder. For long inputs this is information-theoretically impossible, so the decoder forgets early tokens, translation quality collapses past ~25–30 words, and the decoder can never look back. Attention fixes all three by computing a fresh context $c_t$ at every decoding step.

## The bottleneck, stated precisely

In the Encoder-Decoder RNN ([[The Encoder-Decoder Pattern]]), the *only* information that passes from the encoder to the decoder is a single fixed-size vector $c$:

$$c = h_T^{enc}$$

where $h_T^{enc}$ is the encoder's final hidden state, of dimension $h$ (typically 256–1024). This vector must encode **everything the decoder needs to generate the entire output sequence** — every entity, every relationship, every stylistic nuance, every word of the input.

For a 10-word sentence, this is feasible. For a 50-word sentence, it is borderline. For a 500-word document, it is information-theoretically impossible: you cannot losslessly compress 500 words of meaning into 1024 numbers, no matter how well-trained the encoder is.

This is the **bottleneck problem**, and it is the structural limitation that Bahdanau, Cho, and Bengio set out to fix in their 2015 paper "Neural Machine Translation by Jointly Learning to Align and Translate" — the paper that introduced attention.

## Three failure modes of the bottleneck

### The decoder forgets the beginning of the input

The encoder's final hidden state $h_T^{enc}$ is, by construction, most influenced by the most recent input tokens. The recurrence $h_t = \tanh(W_h h_{t-1} + W_x x_t)$ means that $h_T$ is a function of $h_{T-1}$, which is a function of $h_{T-2}$, and so on — but each step applies a $\tanh$ that compresses the past. By step $T$, the contribution of $x_1$ has been passed through $T-1$ tanh compressions and is mostly gone.

Empirically, this shows up as: **the decoder handles the end of the input well and the beginning poorly.** A translation model translating a 40-word sentence will produce a fluent translation of the last 15 words and a garbled translation of the first 15.

### Long inputs degrade sharply

Translation quality (measured by BLEU score) of Encoder-Decoder RNNs drops sharply for sentences above ~25–30 words. This is not a tuning problem — it is the information bottleneck biting. The encoder simply cannot compress 30+ words of meaning into a fixed-size vector without loss, and the decoder cannot reconstruct what was lost.

### The decoder cannot "look back"

A human translator does not read a sentence once, close the book, and translate from memory. They constantly glance back at the source — at the specific word they are currently translating, at the surrounding context, at the grammatical structure. The Encoder-Decoder RNN forbids this: the decoder sees the input *only* through $c$, and once $c$ is computed, the input is gone. The decoder cannot decide, at output step 5, "wait, let me check what input word 3 was" — that information is either in $c$ or it is lost.

This is the most fundamental limitation. **The decoder should be able to look back at the input at every step.** Attention is the mechanism that grants this ability.

## The fix, previewed

The fix that Bahdanau et al. proposed is breathtakingly simple in hindsight: **let the decoder look at all the encoder's hidden states, not just the last one, and let it decide at each step which ones are most relevant.**

Concretely, instead of $c = h_T^{enc}$ (one vector, fixed), the decoder computes a *different* context vector $c_t$ at *each* output step $t$, as a weighted average of *all* encoder hidden states:

$$c_t = \sum_{i=1}^{T} \alpha_{t,i} \cdot h_i^{enc}$$

where $\alpha_{t,i}$ is the "attention weight" — how much output step $t$ should attend to input step $i$. These weights are computed by a small neural network (the "attention mechanism") that takes the decoder's current state and each encoder hidden state and outputs a score; the scores are softmaxed to produce $\alpha_{t,i}$.

This single change shatters the bottleneck. The decoder is no longer limited to a fixed-size summary — it has direct, time-varying access to every encoder hidden state. If translating output word 5 requires looking at input word 3, the attention weights $\alpha_{5,3}$ will be high, and $c_5$ will be dominated by $h_3^{enc}$. The decoder becomes a selective reader rather than a fixed-memory generator.

The full attention mechanism is developed in [[Origins of Attention]] and [[08 - Attention and Transformers/Attention Mechanism/Bahdanau Attention|Bahdanau Attention]]; the point here is the *motivation*: **attention exists because a single fixed-size context vector cannot carry enough information from the encoder to the decoder.**

## From weight sharing to direct access

CNNs, RNNs, and the Encoder-Decoder pattern are three architectures that share weight parameters across a structural axis:

- CNNs share weights across **space** (the kernel slides over the image).
- RNNs share weights across **time** (the cell slides over the sequence).
- The Encoder-Decoder bottleneck shows that **time-sharing is not enough** — the decoder needs *direct, non-sequential* access to the encoder's states, not just a compressed summary passed through time.

Attention is the mechanism that provides this direct access. Once you have attention, the natural next question is: **if attention lets the decoder look at all encoder states, do we even need the RNN?** The answer — developed in Vaswani et al. 2017 — is no. You can build a sequence model entirely out of attention, with no recurrence at all. That model is the Transformer ([[The Transformer]]).

The trajectory is: **RNN → bottleneck → attention → self-attention → Transformer.** Each step is a response to a limitation of the previous one, and the bottleneck is the hinge on which the whole trajectory turns.

To walk away with the essentials: the Encoder-Decoder RNN passes a single fixed-size vector $c$ from encoder to decoder — that is the bottleneck; it causes three failures — forgetting early input, degrading on long inputs, and the inability to look back at specific input tokens; attention fixes it by letting the decoder compute a different context $c_t$ at each step, as a weighted average of all encoder hidden states; and understanding this chain of limitations and responses is the key to understanding why the Transformer exists. [[Long-Range Dependencies]] is a related but distinct limitation of the same recurrent design, and [[From RNNs to Attention]] tells the full story of what came after.

## See also

- [[07 - Sequence Models/Chapter Overview|Chapter Overview]]
- [[The Encoder-Decoder Pattern]]
- [[Long-Range Dependencies]]
- [[From RNNs to Attention]]
- [[Origins of Attention]]
- [[08 - Attention and Transformers/Attention Mechanism/Bahdanau Attention|Bahdanau Attention]]
- [[Seq2Seq and the Information Bottleneck]]
- [[The Transformer]]
