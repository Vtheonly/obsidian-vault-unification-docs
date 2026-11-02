---
title: Queries Keys and Values
type: concept
aliases:
  - "Queries, Keys, and Values — The Database Analogy"
  - QKV
  - "Q, K, V"
  - Query key value
tags:
  - attention
  - transformers
  - query-key-value
  - soft-lookup
  - self-attention
  - deep-learning
sources:
  - "02. Queries, Keys, and Values — The Database Analogy"
created_index: 7
---

Attention is easiest to understand as a soft, differentiable version of a database lookup: a query is compared against a set of stored keys, and the values attached to those keys are retrieved in proportion to how well they match. In a Transformer, the query, key, and value matrices are three learned linear projections of the same input, which gives every token three distinct roles. This note develops the database analogy, shows where the three projections come from, and traces the matrix form of the attention operation dimension by dimension.

## The database analogy

Think of a hash map or dictionary lookup: you have a **query** (the key you are looking up), you compare it against a set of stored **keys**, and you retrieve the **value** associated with the matching key. In Python:

```python
database = {"apple": 5, "banana": 3, "cherry": 8}
query = "banana"
result = database[query]  # 3 — exact match, hard lookup
```

This is a **hard lookup**: the query must exactly match one key, and you get back exactly that key's value.

Attention generalizes this to a **soft lookup**:

- The **query** $q$ is a vector (not a string).
- The **keys** $k_1, \ldots, k_T$ are vectors.
- The **values** $v_1, \ldots, v_T$ are vectors.
- The match between $q$ and $k_i$ is measured by a dot product $q^\top k_i$ (not exact equality).
- The retrieved result is a **weighted average** of all values, weighted by the match scores (not a single value).

$$\text{Attention}(q, K, V) = \sum_{i=1}^{T} \text{softmax}(q^\top k_i) \cdot v_i$$

In the hard lookup, the softmax would be a one-hot vector (1 for the matching key, 0 for all others). In the soft lookup, the softmax is a probability distribution that can spread mass across multiple keys, allowing partial matches. This is the entire attention mechanism in one line — everything else is implementation detail.

## Where Q, K, and V come from in a Transformer

In the encoder-decoder attention of [[08 - Attention and Transformers/Attention Mechanism/Bahdanau Attention|Bahdanau Attention]], the query was the decoder's hidden state and the keys and values were the encoder's hidden states — they came from different places, and there was no need to project them. [[The Transformer]] changes this setup: the query, keys, and values are all **learned linear projections of the same input**. Given an input sequence $X \in \mathbb{R}^{T \times d}$ (a sequence of $T$ tokens, each a $d$-dimensional vector):

$$Q = X W_Q \quad K = X W_K \quad V = X W_V$$

where $W_Q, W_K \in \mathbb{R}^{d \times d_k}$ and $W_V \in \mathbb{R}^{d \times d_v}$ are learnable parameter matrices.

This is the key design decision of the Transformer: **the same input is projected three different ways to produce three different roles.** $Q$ is what each token is "looking for" — its query. $K$ is what each token "offers" — its key, to be matched against other tokens' queries. $V$ is what each token "contributes" if attended to — its value.

The reason for three separate projections is that **what you are looking for, what you offer to be matched on, and what you contribute are three different things.** Consider the word "it" in "the cat sat on the mat because **it** was tired." When "it" attends backward to resolve its referent, its **query** encodes "I am a pronoun looking for a singular noun phrase that could be tired." The **key** of "cat" encodes "I am a singular noun, animate, capable of being tired." The **value** of "cat" encodes "the actual semantic content of 'cat' that should flow into 'it' to resolve the reference." These are three different pieces of information, and forcing them into a single representation would be a bottleneck. Three projections let the model learn three different views of each token.

## The matrix form

For a sequence of $T$ tokens, the projections stack into matrices: $Q \in \mathbb{R}^{T \times d_k}$ holds all queries, $K \in \mathbb{R}^{T \times d_k}$ holds all keys, and $V \in \mathbb{R}^{T \times d_v}$ holds all values.

The attention weights are computed as:

$$A = \text{softmax}\left(\frac{Q K^\top}{\sqrt{d_k}}\right) \in \mathbb{R}^{T \times T}$$

(The $\sqrt{d_k}$ factor is the one piece of the formula not justified here; it is derived in [[Scaled Dot-Product Attention]].)

The output is:

$$\text{Output} = A V \in \mathbb{R}^{T \times d_v}$$

So the full attention operation is:

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{Q K^\top}{\sqrt{d_k}}\right) V$$

This is a beautifully compact formula, and the dimensions trace cleanly. $Q K^\top$: $(T \times d_k) \times (d_k \times T) = T \times T$ — the score matrix, whose entry $(i,j)$ is the match between token $i$'s query and token $j$'s key. Softmax is applied row-wise, so each row of $A$ sums to 1; row $i$ is the attention distribution of token $i$ over all tokens. $A V$: $(T \times T) \times (T \times d_v) = T \times d_v$ — the output, whose row $i$ is the weighted average of all values, weighted by token $i$'s attention distribution.

The whole operation is **two matrix multiplications and a softmax**. That is it. This simplicity is why attention is so computationally efficient on GPUs — it is just dense linear algebra.

## Why this is more general than a hard lookup

A hard lookup (hash map) is the special case where the softmax is replaced by an argmax (one-hot) and the dot product is replaced by exact equality (or some other hard match function). Relaxing both to be continuous buys three things:

- **Partial matches** — the query can attend to multiple keys at once, weighted by match quality.
- **Gradient flow** — the softmax is differentiable, so the model can learn the projections $W_Q, W_K, W_V$ by backpropagation.
- **Soft retrieval** — the output is a blend of multiple values, which is useful when no single key is a perfect match.

This is the sense in which attention is a "neural database" — it generalizes lookup to be soft, differentiable, and learnable.

## The three roles, illustrated

Consider self-attention on the sentence "the cat sat on the mat." The word "sat" might attend as follows:

| Token | Query of "sat" looks for... | Key of token offers... | Value of token is... |
| :--- | :--- | :--- | :--- |
| "the" | (low relevance) | determiner | determiner content |
| "cat" | singular noun, animate, agent | singular noun, animate | "cat" semantic content |
| "sat" | (self) | verb, past tense | "sat" semantic content |
| "on" | preposition | preposition | "on" semantic content |
| "the" | determiner | determiner | determiner content |
| "mat" | singular noun, inanimate, location | singular noun, inanimate | "mat" semantic content |

The query of "sat" is looking for "what sat, and where?" Its attention weights will be high on "cat" (the agent) and "mat" (the location), and the weighted average of their values will produce a contextualized representation of "sat" that incorporates both. This is how [[Self-Attention|self-attention]] builds meaning from a bag of tokens — each token reaches out to the tokens it needs and pulls in their content.

## What to walk away with

Five points summarize the whole construction. Attention is a soft, differentiable generalization of dictionary lookup. The query (what you're looking for), keys (what's offered to match), and values (what's contributed on match) are three learned linear projections of the same input — three different views, because looking-for, offering, and contributing are three different roles. The full operation is $\text{softmax}(QK^\top / \sqrt{d_k}) V$ — two matrix multiplies and a softmax. The whole thing is just dense linear algebra, which is why it is fast on GPUs. And self-attention ([[Self-Attention]]) is the special case where $Q$, $K$, $V$ all come from the *same* sequence.

## See also

- [[Attention and Transformers MOC]]
- [[Origins of Attention]] — attention as soft lookup, from Bahdanau to dot-product
- [[Scaled Dot-Product Attention]] — why the scores are divided by $\sqrt{d_k}$
- [[Self-Attention]] — the special case where Q, K, and V come from the same sequence
- [[Multi-Head Attention]] — running the soft lookup in parallel across many subspaces
- [[08 - Attention and Transformers/Attention Mechanism/Bahdanau Attention|Bahdanau Attention]] — encoder-decoder attention where query and keys/values came from different places
