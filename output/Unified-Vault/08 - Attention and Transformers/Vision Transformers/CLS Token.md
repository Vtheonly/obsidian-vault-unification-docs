---
title: CLS Token
type: concept
aliases:
  - CLS token
  - class token
  - "[CLS]"
  - classification token
tags:
  - vision-transformer
  - cls-token
  - self-attention
  - classification
  - readout
sources:
  - "02. The CLS Token and Why It Works"
created_index: 35
---

After the Transformer encoder of a Vision Transformer has contextualized its input, the model still has to collapse a sequence of vectors into a single vector that a linear classifier can score. The CLS ("classification") token is ViT's answer: a learned vector, prepended to the patch embeddings before the first block, whose final-layer representation serves as the image-level summary. It is a learnable, attention-based alternative to the global average pooling that CNNs conventionally use for the same job, and it is the same device BERT uses to summarize a sentence.

## The classification problem

After the Transformer encoder processes the $N+1$ patch tokens (the $N$ patches plus the prepended CLS token), we have a sequence of $N+1$ contextualized vectors, each of dimension $d$. To classify the image (e.g., "is this a cat or a dog?"), we need to reduce this sequence to a single vector that can be fed to a linear classifier.

There are two natural ways to do this. **Global Average Pooling (GAP)** averages all $N$ patch vectors, producing one $d$-dimensional summary — this is what CNNs do for their image-level summaries (see [[Advanced Pooling and Global Average Pooling]]). The **CLS token** instead uses the final-layer representation of a special token, prepended at the input, as the summary. ViT uses the CLS token, and the reasons why are instructive.

## What the CLS token is

The CLS token is a single learned vector, prepended to the sequence of patch embeddings before the first Transformer block:

$$Z_0 = [\mathbf{z_{cls}}; z_1 + PE(1); \ldots; z_N + PE(N)]$$

The CLS token has no fixed meaning — it is a *learned* parameter, just like the patch embedding matrix or the positional embeddings. At initialization it is random; during training, it learns to be whatever the model needs it to be. How the patch sequence and its positional embeddings are built is covered in [[Patch Tokenization]].

As the sequence passes through the Transformer blocks, the CLS token participates in self-attention like any other token. At each layer, it attends to the patch tokens (and to itself), accumulating information from across the image. By the final layer, the CLS token's representation is a **global summary of the image**, computed by attention rather than by averaging.

At the end, only the CLS token's final-layer representation is used:

$$\text{logits} = \text{Linear}(z_{cls}^{(L)})$$

where $L$ is the number of layers. The patch tokens' final representations are discarded for classification, though they may be used for other tasks such as segmentation.

## Why the CLS token instead of GAP

Three reasons, in increasing order of importance.

### Attention is smarter than averaging

GAP computes an unweighted average of all patch representations. Every patch contributes equally, regardless of whether it is relevant to the classification task — a patch containing the background sky contributes as much as a patch containing the cat's face. The CLS token, by contrast, attends to patches with **learned weights**. If the task is "cat vs dog," the CLS token can learn to attend strongly to face patches and weakly to background patches, producing a summary that emphasizes discriminative regions. This is strictly more expressive than averaging: averaging is the special case in which all attention weights are equal.

### The CLS token can aggregate information across layers

In a deep Transformer, the CLS token's representation at layer $L$ is the result of $L$ rounds of attention. At each round it can decide which patches to pull information from, and those patches' representations have themselves been contextualized by previous rounds. The CLS token thus aggregates not just the patches but the *refined, contextualized* patches — a richer summary than the raw average.

### The CLS token is task-specific without architectural changes

GAP produces the same summary regardless of the task. If you switch from cat-vs-dog to person-detection, the GAP summary is the same — only the final linear classifier changes. The CLS token, by contrast, is a learned parameter that adapts to the task: for cat-vs-dog it learns to attend to animal-related patches; for person-detection it learns to attend to person-related patches. The same Transformer backbone can serve many tasks by simply re-training the CLS token (and the final classifier) — the patch representations do not need to change.

## Why prepending a learned token works at all

This is the deepest question, and the answer reveals something important about attention. At first glance, prepending a meaningless learned vector to a sequence of meaningful patch embeddings seems arbitrary — why should a token that starts as random noise become a useful image summary?

The answer is that **attention is symmetric and learnable**. The CLS token's query at each layer is a learned projection of its current representation. At initialization this query is random, so the CLS token attends to random patches and accumulates random information — useless. But the attention weights and the CLS token's representation are *trained by backpropagation*: the gradient signal from the classification loss flows back through the CLS token's representation and its query projections, adjusting them so that the CLS token learns to attend to whatever patches are most useful for the task.

In other words, the CLS token is a **learnable readout point**. The Transformer encoder builds rich contextualized representations of all patches; the CLS token learns to query those representations in a task-relevant way. The architecture provides the substrate (attention); training determines the readout. This is the same principle as the `[CLS]` token in [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]] — a learnable aggregation point that adapts to the downstream task — and it is one of the more elegant design choices in modern deep learning: instead of designing a fixed aggregation rule (like GAP), let the model learn the aggregation.

## CLS token vs GAP — the empirical verdict

In practice, both work. The original ViT paper used the CLS token; follow-up work (notably "Early Convolutions Help Transformers See Further" and the Swin Transformer) showed that GAP works comparably, especially when the model is pretrained on large datasets. The current consensus: the **CLS token** is slightly better for small-to-medium datasets, where the learnable aggregation helps; **GAP** is slightly better for very large datasets, where the model has enough data to learn good patch representations and the CLS token's learnable aggregation is redundant; and for most practical purposes the difference is within noise.

The CLS token's main advantage is conceptual: it makes the "image summary" an explicit, learned, task-adaptive quantity, rather than an implicit byproduct of averaging.

## See also

- [[Attention and Transformers MOC]] — area overview
- [[Patch Tokenization]] — where the CLS token enters the input sequence
- [[ViT Architecture]] — the full model that uses this readout
- [[Inductive Bias]] — the broader CNN-vs-ViT tradeoff this token participates in
- [[Self-Attention]] and [[Queries Keys and Values]] — the mechanism the readout learns to steer
- [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]] — the same [CLS] trick in NLP
- [[Advanced Pooling and Global Average Pooling]] — the CNN-style alternative readout
