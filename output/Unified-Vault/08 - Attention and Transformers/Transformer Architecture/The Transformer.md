---
title: The Transformer
type: concept
aliases:
  - The Full Transformer
  - Full Transformer
  - Original Transformer
  - Vaswani Transformer
tags:
  - transformer
  - encoder-decoder
  - architecture
  - sequence-model
  - attention
sources:
  - "05. The Full Transformer — Assembling the Pieces"
created_index: 32
---

The Transformer (Vaswani et al. 2017) assembles the pieces — embeddings, positional encodings, attention blocks, feedforward networks — into the complete encoder-decoder architecture that replaced the RNN. The encoder stack reads the source sequence into contextualized vectors; the decoder stack generates the target sequence autoregressively while cross-attending to the encoder; a final linear-plus-softmax layer turns decoder states into vocabulary distributions. This note assembles the full architecture, records the original hyperparameters, explains why the design works from three perspectives, and is honest about what it does not do.

> [!info] TL;DR
> Full Transformer = embedding + positional encoding → $N$ encoder blocks → $N$ decoder blocks (with cross-attention) → linear + softmax, trained with cross-entropy under teacher forcing. It works because it is fully parallelizable (unlike RNNs), has $O(1)$ path length between any two positions, and stacks contextualizers. Its limits: $O(T^2)$ attention cost, no memory across sequences, exposure bias, and no built-in hierarchy. Three sub-families — encoder-only, decoder-only, encoder-decoder — divide the task space.

## The full architecture

We now have all the pieces. The full Transformer is:

```
INPUT (source)                    OUTPUT (target, shifted right)
   │                                      │
   ▼                                      ▼
[Token Embedding]                   [Token Embedding]
   + Positional Encoding                 + Positional Encoding
   │                                      │
   ▼                                      ▼
┌──────────────┐                  ┌──────────────────┐
│ Encoder      │                  │ Decoder Block 1  │
│ Block 1      │                  │ (masked SA,      │
│              │                  │  cross-attn, FFN)│
├──────────────┤                  ├──────────────────┤
│ Encoder      │─── cross-attn ──│ Decoder Block 2  │
│ Block 2      │                  ├──────────────────┤
├──────────────┤                  │ ...              │
│ ...          │                  ├──────────────────┤
├──────────────┤                  │ Decoder Block N  │
│ Encoder      │                  └──────────────────┘
│ Block N      │                          │
└──────────────┘                          ▼
       │                            Linear projection
       │                            to vocabulary
       │                                  │
       │                                  ▼
       │                              Softmax
       │                                  │
       │                                  ▼
       │                       Output probabilities
       │                       (over vocabulary)
```

### The encoder stack

The encoder's input is the source sequence (e.g., an English sentence), tokenized and embedded, plus positional encoding. The stack is $N$ encoder blocks (each = self-attention + FFN, with residuals and LayerNorm). The output is a sequence of contextualized vectors $X_{enc} \in \mathbb{R}^{T_{src} \times d}$, one per source token.

### The decoder stack

The decoder's input is the target sequence shifted right (e.g., the French sentence starting with `<BOS>`), tokenized and embedded, plus positional encoding. The stack is $N$ decoder blocks (each = masked self-attention + cross-attention to encoder output + FFN, with residuals and LayerNorm). The output is a sequence of contextualized vectors $Y_{dec} \in \mathbb{R}^{T_{tgt} \times d}$. The final layer is a linear projection to vocabulary size, then softmax, producing a distribution over the vocabulary at each position.

### Training loss

Training minimizes the cross-entropy between the predicted distributions and the true target tokens, summed over all decoder positions. This is teacher forcing (see [[Teacher Forcing and Exposure Bias]]) — the decoder is fed the true previous tokens during training.

## Hyperparameters of the original Transformer

| Hyperparameter | Value |
| :--- | :--- |
| Model dimension $d$ | 512 |
| Number of heads $h$ | 8 |
| Head dimension $d_k = d/h$ | 64 |
| FFN hidden dimension $d_{ff}$ | 2048 (= 4d) |
| Number of encoder blocks $N_{enc}$ | 6 |
| Number of decoder blocks $N_{dec}$ | 6 |
| Positional encoding | Sinusoidal |
| LayerNorm placement | Post-LN (original); Pre-LN (modern) |
| Activation | ReLU (original); GELU (modern) |
| Dropout | 0.1 |
| Optimizer | Adam, with warmup + inverse-sqrt schedule |
| Batch size | ~25k tokens |

These are the "base" model hyperparameters. The "big" model scales to $d = 1024$, $h = 16$, $d_{ff} = 4096$, $N = 6$, achieving better translation at ~4× the compute.

## Why this architecture works — three perspectives

### It is a fully parallelizable sequence model

Unlike the RNN, every position in the encoder can be computed simultaneously — there is no sequential dependency across time. This makes training on GPUs dramatically faster, which is what enabled training on web-scale datasets.

### It has $O(1)$ path length between any two positions

Unlike the RNN, which requires $O(T)$ steps for information to flow from position 1 to position $T$, the Transformer connects every pair of positions in a single attention operation. This is why it handles long-range dependencies better than RNNs (see [[Long-Range Dependencies]] and [[From RNNs to Attention]]).

### It is a stack of contextualizers

Each encoder block takes a sequence of token representations and contextualizes them — each token's representation becomes a function of all other tokens. Stacking $N$ blocks deepens this contextualization: after 12 blocks, each token's representation encodes not just its local context but the global structure of the sequence. This is analogous to how stacked CNN layers expand the receptive field, except the Transformer's "receptive field" is global from the first block.

## What the Transformer does not do

Being honest about limitations matters as much as praising the design. First, $O(T^2)$ cost: the self-attention matrix is $T \times T$, making the Transformer expensive for very long sequences. This is the subject of efficient-attention research (sparse, linear, flash attention — see [[Sparse Attention]], [[Linear Attention]], and [[08 - Attention and Transformers/Efficient Attention/FlashAttention|FlashAttention]]).

Second, no memory: the Transformer has no persistent state across sequences — each forward pass is independent. This is in contrast to RNNs, which can maintain a hidden state across a session. Memnet, Transformer-XL, and RNN-based retrieval-augmented models try to add memory, but vanilla Transformers are stateless.

Third, exposure bias: the decoder is trained with teacher forcing and suffers from exposure bias at inference (see [[Teacher Forcing and Exposure Bias]]). This is not unique to Transformers — it is a property of autoregressive training — but it remains a limitation.

Fourth, no built-in notion of hierarchy: the Transformer treats all positions uniformly, with no explicit hierarchical structure. CNNs encode spatial hierarchy through pooling; TreeRNNs encode syntactic hierarchy through tree structure. The Transformer learns hierarchy implicitly through attention, which works but is less efficient than an explicit hierarchy would be.

## The three sub-families

The full encoder-decoder Transformer is one design point in a broader space. Three sub-families have emerged, each suited to different tasks. Encoder-only models (BERT, RoBERTa, ViT) are stacks of encoder blocks with bidirectional attention, best for understanding tasks (classification, entity recognition, retrieval). Decoder-only models (GPT, LLaMA, PaLM) are stacks of decoder blocks (without cross-attention) with causal attention, best for generation tasks (text completion, chat, code) — and the dominant architecture for modern LLMs. Encoder-decoder models (T5, BART, and the original Transformer) keep the full encoder + decoder with cross-attention, best for sequence-to-sequence tasks (translation, summarization) where input and output are distinct. The choice between these is the subject of [[BERT vs GPT vs T5]] and [[Choosing the Right Architecture]].

## See also

- [[Attention and Transformers MOC]]
- [[Transformer Block]] and [[Transformer Decoder Block]] — the two block anatomies assembled here
- [[Scaled Dot-Product Attention]], [[Multi-Head Attention]], [[Self-Attention]]
- [[Positional Encoding]], [[Sinusoidal and Learned Positional Encodings]]
- [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]], [[GPT Family]], [[T5 and BART]] — the three sub-families
- [[ViT Architecture]] — the architecture transplanted to vision
- [[From RNNs to Attention]], [[Long-Range Dependencies]], [[Teacher Forcing and Exposure Bias]]
- [[The Encoder-Decoder Pattern]], [[Autoregressive vs Parallel Encoding]]
