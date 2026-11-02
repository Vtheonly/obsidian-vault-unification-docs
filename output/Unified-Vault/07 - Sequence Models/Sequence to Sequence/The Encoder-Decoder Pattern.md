---
title: The Encoder-Decoder Pattern
type: concept
aliases:
  - Encoder-Decoder
  - Encoder-Decoder architecture
  - Sequence to sequence
  - seq2seq
  - Conditional generation
  - "Encoder-Decoder Pattern — Conditional Generation"
tags:
  - sequence-models
  - encoder-decoder
  - seq2seq
  - rnn
  - conditional-generation
sources:
  - "01. The Encoder-Decoder Pattern — Conditional Generation"
created_index: 14
---

The encoder-decoder pattern is the conceptual bridge from RNNs that classify sequences to RNNs that generate them: two recurrent networks — one that reads a variable-length input, one that writes a variable-length output — joined by a single handoff vector. It is the architecture that made neural translation, summarization, and captioning possible. Its central limitation — everything the decoder knows about the input must fit into one fixed-size vector — is exactly the problem attention was invented to solve, so if you understand this pattern, you understand 80% of the motivation for the Transformer.

## The problem: variable-length input, variable-length output

So far, recurrent networks have handled one of two task shapes. In **many-to-one** learning, the network reads a sequence and emits one label (sentiment classification) — the input is variable-length, but the output is a fixed-size label. In synced **many-to-many** learning, the network emits one label per input token (POS tagging) — input and output have the same length.

But many real tasks have **variable-length input AND variable-length output, with no alignment between them**:

- **Translation:** "how are you?" (3 words) → "comment ça va ?" (3 words, but a 30-word sentence may translate to a 25-word sentence — no fixed ratio).
- **Summarization:** a 500-word article → a 50-word summary.
- **Speech recognition:** 10 seconds of audio (200 frames) → "hello world" (2 words).
- **Code generation:** a natural-language spec (30 tokens) → a Python function (100 tokens).

No single RNN can do this. The input and output live in different spaces, have different lengths, and have no positional correspondence — precisely the kind of mismatch that motivates [[Why Sequence Models]] in the first place. The solution is to use **two** RNNs: one to read the input, one to write the output, with a handoff in between.

## The architecture

### The encoder

The **encoder** is an RNN (an [[LSTM]] or [[GRU]]) that reads the input sequence one token at a time, updating its hidden state. It produces **no output** during this phase — it just reads. At the end, the encoder's final hidden state $h_T^{enc}$ is a summary of the entire input.

$$h_t^{enc} = \mathrm{RNN}_{enc}(h_{t-1}^{enc}, x_t) \quad \text{for } t = 1, \ldots, T$$

After reading all $T$ input tokens, we have $h_T^{enc}$ — a single fixed-size vector that is supposed to contain everything the decoder needs.

### The context vector

$h_T^{enc}$ is repurposed as the **context vector** $c$. In the simplest version, $c = h_T^{enc}$. (In fancier versions, $c$ is a function of all encoder hidden states, but the simple version is the starting point.)

This context vector is the *only* information that passes from the encoder to the decoder. It is the bottleneck — the subject of [[The Bottleneck Problem]] — but for now it suffices to accept that $c$ is the decoder's only view of the input.

### The decoder

The **decoder** is a *second* RNN (again an LSTM or GRU, with its own parameters) that generates the output sequence one token at a time, conditioned on the context vector.

The trick is initialization: **the decoder's initial hidden state is set to the context vector**, $h_0^{dec} = c$. This is how the input "flows into" the decoder.

At each step, the decoder:

1. Takes the previous output token as input — during training, the previous *true* token; during inference, the previous *predicted* token (this asymmetry is the subject of [[Teacher Forcing and Exposure Bias]]).
2. Updates its hidden state: $h_t^{dec} = \mathrm{RNN}_{dec}(h_{t-1}^{dec}, y_{t-1})$.
3. Projects its hidden state to a vocabulary distribution: $p_t = \mathrm{softmax}(W_{out} h_t^{dec})$.
4. Samples (or argmaxes) the next token: $y_t \sim p_t$.
5. Repeats until it emits a special `<EOS>` (end-of-sequence) token.

The loss is the cross-entropy of the predicted distributions against the true target tokens, summed over all decoder steps.

## The full picture

```
ENCODER                              DECODER

 x_1 → [Enc] → h_1                   h_0 = c = h_T
 x_2 → [Enc] → h_2                          ↓
 x_3 → [Enc] → h_3                   [Dec] → y_1 (e.g. "comment")
 ...                                  ↓ y_1
 x_T → [Enc] → h_T ──── c ────      [Dec] → y_2 (e.g. "ça")
                                      ↓ y_2
                                      [Dec] → y_3 (e.g. "va")
                                      ↓ y_3
                                      [Dec] → <EOS>
```

The encoder reads left-to-right and hands off a single vector $c$. The decoder then runs autonomously, generating one token at a time, until it decides to stop.

## Why this design is non-obvious

Three features of this architecture are worth pausing on, because each embodies a decision that could have gone another way.

**Why two separate RNNs?** You might think one RNN could both read and write. But a single RNN has one hidden state, and that state would have to serve as both "summary of the input so far" and "plan for the output so far" — two different jobs. Splitting into encoder and decoder gives each its own state and its own parameters, so each can specialize.

**Why initialize the decoder with $c$ rather than feed $c$ as input at every step?** Both are possible. Initializing is the original (Sutskever et al. 2014) design and works well. Feeding $c$ at every step (Bahdanau et al. 2015, in the attention paper) also works and is slightly more robust — it prevents the decoder from "forgetting" the input over long output sequences. Attention generalizes this idea by feeding a *different* context at every step; see [[From RNNs to Attention]] and [[Origins of Attention]].

**How does the decoder know when to stop?** The decoder is trained to emit a special `<EOS>` token at the end of every target sequence. At inference time, generation halts when `<EOS>` is emitted. This is the mechanism that handles variable output length.

## The information bottleneck

In the diagram above, the entire input sequence — whether it is 5 words or 500 words — is compressed into a single fixed-size vector $c$ before the decoder ever sees it. This is the **bottleneck**, and it is the single most important limitation of the Encoder-Decoder RNN.

Consider translating a 50-word sentence. The encoder must compress the meaning of all 50 words — the subject, the tense, the entities, the relationships, the tone — into a vector of, say, 1024 numbers. The decoder must then reconstruct a 50-word translation in another language from those 1024 numbers alone. This is an extreme information bottleneck, and it has two visible failure modes:

1. **The decoder "forgets" the beginning of the input** by the time it generates the end of the output. The encoder's final hidden state is dominated by the most recent tokens; early tokens have been overwritten.
2. **Long sentences translate worse than short ones.** Empirically, Encoder-Decoder RNN translation quality degrades sharply for sentences above ~30 words, because the fixed-size context cannot hold that much information.

This bottleneck is not an accident of the implementation — it is inherent to the design. And it is *exactly* the problem that **attention** was invented to solve. Instead of forcing the decoder to look at a single context vector, attention lets the decoder "look back" at all the encoder's hidden states and decide, at each output step, which parts of the input are most relevant. That idea is the foundation of modern NLP.

The next two notes flesh out the practical details of training (teacher forcing) and decoding (beam search): [[Teacher Forcing and Exposure Bias]] covers how the decoder is trained and [[Beam Search and Decoding Strategies]] covers how it generates at inference; then [[The Bottleneck Problem]] makes the bottleneck argument precise and hands off to attention.

## What to walk away with

The essentials, compressed:

1. The Encoder-Decoder pattern uses two RNNs: an encoder that reads the input and produces a context vector $c$, and a decoder initialized with $c$ that generates the output token-by-token.
2. The decoder generates until it emits `<EOS>`, which is how variable-length output is handled.
3. The context vector $c$ is the *only* path from encoder to decoder — and it is a fixed-size bottleneck.
4. This bottleneck is the structural limitation that attention was invented to fix.
5. Understanding this pattern is the prerequisite for understanding why attention exists.

## See also

- [[07 - Sequence Models/Chapter Overview|Chapter Overview]]
- [[Why Sequence Models]] — why variable-length input and output break single-network designs.
- [[LSTM]] and [[GRU]] — the recurrent cells used for both halves.
- [[Teacher Forcing and Exposure Bias]] — how the decoder is trained.
- [[Beam Search and Decoding Strategies]] — how the decoder generates at inference.
- [[The Bottleneck Problem]] — the precise statement of this architecture's central limitation.
- [[From RNNs to Attention]] — the bridge from this design to attention.
- [[Origins of Attention]] — how attention was invented to fix this bottleneck.
- [[Attention and Transformers MOC]]
