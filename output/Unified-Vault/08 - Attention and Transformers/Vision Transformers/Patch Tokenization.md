---
title: Patch Tokenization
type: concept
aliases:
  - patch embedding
  - patchify
  - patch extraction
  - "From Words to Patches"
tags:
  - vision-transformer
  - patch-embedding
  - tokenization
  - positional-embeddings
  - self-attention
sources:
  - "01. From Words to Patches — How ViT Tokenizes an Image"
created_index: 37
---

A Transformer is built to consume sequences of token embeddings, but an image is a 2D grid of pixels — not a sequence. The Vision Transformer bridges this gap with patch tokenization: the image is divided into a grid of non-overlapping square patches, each patch is flattened and linearly projected to the model dimension, positional information is added, and a CLS token is prepended. After this step the image is simply a sequence of vectors, and the Transformer processes it exactly as it would process a sentence.

## The problem: Transformers eat sequences, images are grids

The Transformer was designed for sequences — a list of token embeddings. Language is naturally sequential: tokenize text into words/subwords, embed each, feed the sequence to the Transformer. The architecture does not care what the tokens *are*; it just needs a sequence of vectors.

An image is not a sequence. It is a 2D grid of pixels (or a 3D volume, for color). A 224×224 RGB image is a $224 \times 224 \times 3$ tensor — 150,528 numbers arranged in a grid. Turning that into a sequence of vectors a Transformer can process is the whole problem.

The naive answer — flatten the image into a sequence of pixels — fails catastrophically. A 224×224 image would become a sequence of 50,176 pixels, each a 3-dimensional vector. Self-attention on this sequence would require a $50176 \times 50176$ attention matrix — 2.5 billion entries, completely intractable. And even if it were tractable, treating individual pixels as tokens throws away the spatial structure that makes images meaningful.

The ViT answer (Dosovitskiy et al. 2020): **tokenize the image into patches, not pixels.**

## The ViT tokenization pipeline

### Step 1: split the image into patches

Take a $H \times W \times C$ image (e.g., $224 \times 224 \times 3$) and divide it into a grid of non-overlapping $P \times P$ patches (e.g., $16 \times 16$). This produces:

$$N = \frac{H \times W}{P^2} = \frac{224 \times 224}{16 \times 16} = 196 \text{ patches}$$

Each patch is a $P \times P \times C = 16 \times 16 \times 3 = 768$-dimensional volume — a small sub-image:

```
┌────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┬────┐
│ P  │ P  │ P  │ P  │ P  │ P  │ P  │ P  │ P  │ P  │ P  │ P  │ P  │ P  │
├────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┼────┤
│ P  │ P  │ ... 14 patches per row × 14 rows = 196 patches total
└────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┴────┘
```

### Step 2: flatten each patch into a vector

Each $16 \times 16 \times 3$ patch is flattened into a $768$-dimensional vector. So we have $N = 196$ vectors, each of dimension $768$.

### Step 3: linearly project each patch vector to the model dimension

The 768-dimensional patch vectors are linearly projected to the model dimension $d$ (e.g., $d = 768$ for ViT-Base):

$$z_i = x_i^{patch} W_E + b$$

where $W_E \in \mathbb{R}^{(P^2 \cdot C) \times d}$ is a learned embedding matrix. This is mathematically identical to a $1 \times 1$ convolution with $d$ output channels applied to the flattened patches — or equivalently, a `nn.Linear(768, 768)` applied to each patch.

> [!NOTE] This is exactly how word embeddings work.
> The patch embedding is the visual analog of a word embedding. A word2vec model maps a discrete word index to a continuous vector; the ViT patch embedding maps a discrete patch (a small sub-image) to a continuous vector. Both turn a discrete input into a learnable continuous representation that the Transformer can process.

### Step 4: add positional encoding

Just as in NLP, the Transformer is permutation-equivariant, so the patches need positional encoding to indicate *where in the image* each patch came from. ViT uses **learned 1D positional embeddings** — a matrix $E_{pos} \in \mathbb{R}^{N \times d}$ whose $i$-th row is added to the $i$-th patch embedding:

```
Patch 1 (top-left)     → embed → + PE(1) → z_1
Patch 2 (next in row)  → embed → + PE(2) → z_2
...
Patch 196 (bottom-right) → embed → + PE(196) → z_196
```

Notably, ViT uses **1D** positional embeddings even though the patches are arranged in a 2D grid. The model *learns* the 2D structure from the 1D ordering — empirically, learned 1D encodings work as well as explicit 2D encodings, because the patch indices implicitly encode the 2D position (patch $i$ is at row $i // 14$, column $i \% 14$ for a 14×14 grid). How positional encodings are designed in general is the subject of [[Positional Encoding]] and [[Sinusoidal and Learned Positional Encodings]].

### Step 5: prepend the CLS token

A special learned "class token" (`[CLS]`) is prepended to the sequence. This token has no fixed meaning — it is a learned vector whose final-layer representation is used as the image-level summary for classification (see [[CLS Token]] for why this works).

The final input to the Transformer is:

$$Z_0 = [z_{cls}; z_1 + PE(1); z_2 + PE(2); \ldots; z_N + PE(N)] \in \mathbb{R}^{(N+1) \times d}$$

For ViT-Base with 224×224 images and 16×16 patches: $N+1 = 197$ tokens, each of dimension $d = 768$.

## The full patch embedding in one convolution

The entire "image → token sequence" pipeline can be implemented as a single convolution:

```python
self.patch_embed = nn.Conv2d(3, d, kernel_size=P, stride=P)
# Input:  (B, 3, 224, 224) image
# Output: (B, d, 14, 14)    feature map — one d-dim vector per patch
# Flatten: (B, d, 14, 14) → (B, 196, d)  — a sequence of 196 patch embeddings
```

A $16 \times 16$ convolution with stride 16 extracts the patches and projects them to dimension $d$ in one operation. This is mathematically identical to "split into patches, flatten, linearly project" — the convolution just fuses the two steps.

This single convolution is the **only** place in a ViT where spatial structure is explicitly exploited. After it, the patches are treated as an unordered sequence of tokens, and the Transformer processes them exactly as it would process a sentence.

## Why patches, not pixels

The choice of patch size $P$ is the key hyperparameter of a ViT. It controls the tradeoff between:

- **Sequence length** $N = HW/P^2$: smaller patches → more tokens → $O(N^2)$ attention cost grows.
- **Spatial resolution per token**: smaller patches → finer-grained tokens → more capacity to model fine details.

For $P = 16$ and 224×224 images, $N = 196$ — manageable. For $P = 8$, $N = 784$ — 4× more tokens, 16× more attention cost. For $P = 32$, $N = 49$ — very cheap, but each patch is coarse (32×32 pixels averaged into one token), losing fine detail.

The standard ViT uses $P = 16$ as a compromise. Variants like the Swin Transformer use a hierarchical patch structure (small patches early, merged into larger patches later) to get the best of both worlds, echoing the hierarchical structure of CNNs.

## The design philosophy: minimal image-specific inductive bias

Notice what the ViT patch embedding does *not* do:

- **No convolutions** beyond the initial patch extraction. The Transformer's self-attention handles all inter-patch interaction.
- **No pooling** to reduce spatial resolution. The sequence length stays $N$ throughout the encoder (except for the CLS token aggregation at the end).
- **No local connectivity**. Every patch can attend to every other patch from the first layer.
- **No translation equivariance**. The patches are at fixed positions; the model does not share weights across spatial translations.

This is the opposite design philosophy from CNNs (see [[06 - Computer Vision/CNN Foundations and Philosophy/Introduction and Foundations of CNNs|Introduction and Foundations of CNNs]]), which bake in locality, weight sharing across space, and translation equivariance. The ViT bakes in almost nothing — it treats the image as a bag of patches and lets attention learn the spatial relationships.

This minimal-inductive-bias design is the source of both ViT's greatest strength (it scales better with data) and its greatest weakness (it needs vast amounts of data to learn what CNNs get for free). That tradeoff is developed in [[Inductive Bias]], and the assembled model that this pipeline feeds is covered in [[ViT Architecture]].

## See also

- [[Attention and Transformers MOC]] — area overview
- [[CLS Token]] — the readout token prepended in step 5
- [[ViT Architecture]] — the assembled model this pipeline feeds
- [[Inductive Bias]] — consequences of the minimal-prior design
- [[Embedding Layer]] — the word-embedding analog of the patch projection
- [[Positional Encoding]] and [[Sinusoidal and Learned Positional Encodings]] — how position is added to tokens
- [[Self-Attention]] — what consumes the resulting sequence
- [[06 - Computer Vision/CNN Foundations and Philosophy/Introduction and Foundations of CNNs|Introduction and Foundations of CNNs]] — the CNN design philosophy being challenged
