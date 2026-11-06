---
title: Long-Range Dependencies
type: concept
aliases:
  - Long-Range Dependencies and Why RNNs Struggle
  - long-distance dependencies
tags:
  - sequence-models
  - rnn
  - lstm
  - path-length
  - attention
  - limitations
sources:
  - "02. Long-Range Dependencies and Why RNNs Struggle"
created_index: 10
---

A long-range dependency is a relationship between tokens in a sequence that are far apart — a subject and its verb split by a long clause, a country and the language spoken of it many sentences later, a variable and the line of code that uses it far downstream. This note examines how well recurrent models actually handle such relationships: the honest answer is "not very well," the root cause is sequential access, and the remedy — direct, constant-hop access to any position — is exactly what attention provides.

## What is a long-range dependency?

A **long-range dependency** is a relationship between tokens in a sequence that are far apart. Typical examples:

- "The **keys**, which I forgot were still in my coat pocket from yesterday morning, **are** on the table." — the verb "are" must agree with "keys" despite 15 intervening words.
- "I grew up in **France**. ... [many sentences] ... I speak fluent **French**." — "French" depends on "France" despite hundreds of intervening tokens.
- In code: a variable declared on line 5 may be used on line 500.
- In music: a key signature established in measure 1 governs the harmony of measure 80.

Handling these is the central challenge of sequence modeling. The whole point of using an RNN instead of an n-gram model ([[N-Gram Language Models]]) is to capture dependencies beyond a fixed window. So how well do RNNs actually do it?

## The honest answer: not very well

### Vanilla RNNs fail beyond ~10 steps

As shown in [[07 - Sequence Models/Motivation and Recurrence/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]], the gradient in a vanilla RNN decays exponentially with sequence length. Empirically, vanilla RNNs cannot reliably learn dependencies longer than about 10–20 steps. Beyond that, the gradient signal from the distant past is too small to drive learning, and the model behaves like a short-window n-gram model.

### LSTMs handle ~100–500 steps, with effort

The cell-state highway lets [[LSTM]]s learn longer dependencies. On synthetic tasks like "copy a sequence of 100 tokens seen 100 steps ago," LSTMs can succeed. On real text, they handle subject-verb agreement across 30–50 words reasonably well. But three problems remain:

- **Beyond ~500 steps, even LSTMs struggle.** The forget gate has to stay near 1 for hundreds of steps, and any noise or interference accumulates.
- **Selective retrieval is hard.** An LSTM can maintain a single fact ("subject is plural") across a long distance, but if it needs to retrieve a *specific* fact from a *specific* earlier position (like looking up a variable's value), it struggles — the information is smeared across the cell state, not addressable by position.
- **Training is slow.** Because the recurrence is sequential, training an LSTM on a sequence of length $T$ takes $O(T)$ time with no parallelism across time. Long sequences mean long training.

### The fundamental issue: sequential access

The deepest reason RNNs struggle with long-range dependencies is that **the only way for the decoder at step $t$ to access information from step $i$ is to traverse every step in between.** The information must be carried through $h_i \to h_{i+1} \to \ldots \to h_t$, with each step applying a transformation that may distort or lose it.

This is like trying to find a specific page in a book by reading from the beginning — you have to traverse everything in between. A human flipping to a bookmarked page does not have this problem. A Transformer, which attends directly to any position in $O(1)$ hops, does not have this problem either.

This is the **path length** argument, and it is one of the key motivations for the Transformer ([[The Transformer]]). The Transformer's self-attention ([[Self-Attention]]) connects every position to every other position directly, so the path length between any two tokens is 1, regardless of how far apart they are in the sequence. RNNs have path length $O(T)$; Transformers have path length $O(1)$.

## Empirical evidence: the LAMBADA benchmark

The LAMBADA benchmark (Paperno et al. 2016) tests long-range understanding by asking a model to predict the last word of a passage, where the predictability of the last word depends on text 50+ tokens earlier. The reported results:

| Model | Accuracy |
|---|---|
| Trigram model | ~20% (chance is ~0%) |
| LSTM | ~50% |
| Transformer (GPT-2 small) | ~63% |
| Transformer (GPT-2 large) | ~76% |

The gap between the LSTM and the Transformers (the two [[GPT Family]] models) is not because the Transformer has more parameters — it is because the Transformer has *direct* access to the relevant earlier text, while the LSTM has to carry it through 50 recurrent steps.

## The takeaway

Long-range dependencies are the central challenge of sequence modeling, and the failure pattern is consistent across model families: vanilla RNNs fail beyond ~10 steps due to vanishing gradients; LSTMs handle ~100–500 steps but struggle with selective retrieval and are slow to train because of sequential processing; and the fundamental issue is path length — RNNs require $O(T)$ hops to connect tokens $T$ steps apart, while attention provides $O(1)$. That path-length argument is a key motivation for the Transformer. [[The Bottleneck Problem]] describes the related but distinct fixed-vector limitation of the same encoder-decoder design, and [[From RNNs to Attention]] carries the story forward to attention itself.

## See also

- [[07 - Sequence Models/Chapter Overview|Chapter Overview]]
- [[07 - Sequence Models/Motivation and Recurrence/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]]
- [[LSTM]]
- [[The Bottleneck Problem]]
- [[From RNNs to Attention]]
- [[The Transformer]]
- [[Self-Attention]]
- [[Origins of Attention]]
