---
title: Embedding Layer
type: concept
aliases: [Token Embeddings, Token Embedding Layer, Un-embedding, Output Embedding]
tags: [transformer, embeddings, token-embeddings, tied-weights, parameter-efficiency]
sources: ["06 - Embedding Layer"]
created_index: 24
---

The embedding layer maps the integer token IDs produced by the tokenizer into dense vectors — the interface between discrete tokens and continuous vectors. It is one of the simplest neural network components, a learned lookup table, but also one of the largest, often a double-digit percentage of a modern model's parameters. The same design question reappears at the output, where an "un-embedding" matrix maps hidden states back to vocabulary scores, raising the tied-versus-untied decision.

> [!info] TL;DR
> The embedding layer maps token IDs (integers) to dense vectors. It's a simple lookup table — but a huge one. For Llama 3 (128k vocab, 4096 dim), the embedding matrix is ~1B parameters, ~14% of the model. Important for parameter efficiency, tied-weights decisions, and quantization.

## The mechanism

An embedding layer is a learned lookup table:

$$
\mathbf{e}_i = \mathbf{E}[i]
$$

where $\mathbf{E} \in \mathbb{R}^{|V| \times d}$ is the embedding matrix, $|V|$ is the vocabulary size, and $d$ is the model dimension. The $i$-th row is the embedding for token $i$.

Selecting a row this way is mathematically equivalent to a one-hot multiplication:

$$
\mathbf{e}_i = \text{onehot}(i) \cdot \mathbf{E}
$$

but in practice it is implemented as a gather, not a matmul — the integer index directly selects the row.

## Worked implementation

```python
import torch.nn as nn

class TokenEmbedding(nn.Module):
    def __init__(self, vocab_size, d_model):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
    
    def forward(self, token_ids):
        # token_ids: (B, T) ints
        return self.embedding(token_ids)  # (B, T, d_model)
```

That's it — the embedding layer is one of the simplest neural network components in deep learning. Its practical importance comes from secondary effects: parameter share, quantization behavior, and resizing during fine-tuning. It sits underneath every [[Transformer Block]].

## Embedding size considerations

For Llama 3 8B, the vocabulary is 128k tokens and $d = 4096$, so one embedding matrix holds $128k \times 4096 = 524M$ parameters — about 1 GB of weights in fp16, roughly 14% of the model. (The ~1B figure also quoted for Llama 3's embeddings corresponds to counting the input lookup table together with the untied output projection, which is another matrix of the same size.)

Vocabulary size is therefore a genuine design tradeoff: a bigger vocab yields shorter sequences (fewer tokens per sentence) and better multilingual coverage, but a bigger embedding matrix; a smaller vocab means longer sequences and a smaller matrix, but worse multilingual coverage and worse rare-word handling. Modern LLMs have converged on 32k–128k vocab as the sweet spot.

## Tied versus untied embeddings

The output layer (the un-embedding) is also a $\mathbb{R}^{d \times |V|}$ matrix mapping hidden states to vocabulary logits — should the input and output share weights?

### Tied (shared) embeddings

$$\mathbf{E}_{\text{out}} = \mathbf{E}_{\text{in}}^T$$

Tying saves $|V| \cdot d$ parameters, which is significant — it can be 10–30% of the model. It is also theoretically motivated: similar tokens should have similar input and output representations, so a single table can serve both roles. Tied embeddings are used by GPT-2, early Llama, and many small models.

### Untied embeddings

Untied models keep separate input and output matrices. This costs more parameters but gives slightly better quality in some studies. Untied embeddings are used by Llama 2/3, Mistral, and many modern models. The trend has been toward untied — the extra parameters are worth the quality gain, and modern models can afford them.

## Positional information

Positional information can be added to the token embeddings directly — $\mathbf{x} = \mathbf{E}_{\text{token}}[i] + \mathbf{E}_{\text{pos}}[i]$, with the positional table learned or sinusoidal (see [[Positional Encoding]] and [[Sinusoidal and Learned Positional Encodings]]) — or injected via [[RoPE]], which is applied to the queries and keys inside attention rather than to the embeddings. Modern LLMs such as Llama and Mistral use RoPE — there is no positional embedding in the input layer.

## Embedding scaling

Some models scale the token embeddings by $\sqrt{d_{model}}$:

$$
\mathbf{x} = \sqrt{d_{model}} \cdot \mathbf{E}_{\text{token}}[i] + \mathbf{E}_{\text{pos}}[i]
$$

This compensates for the relatively small magnitude of learned embeddings compared to positional encodings. It was used in the original Transformer and is less common in modern LLMs.

## Quantization challenges

Embedding matrices are tricky to quantize. Low-frequency tokens have few training examples, so their embeddings are noisy to begin with, and quantization noise compounds this. INT4 embedding quantization typically loses more quality than INT4 weight quantization on other layers, which is why many INT4 inference setups keep the embeddings in FP16.

## Worked forward example

```python
# Batching
token_ids = torch.tensor([[1, 2, 3], [4, 5, 0]])  # batch of 2, seq_len 3, 0 is padding
embeddings = embedding_layer(token_ids)
# Shape: (2, 3, d_model)

# Add positional encoding (if not using RoPE)
x = embeddings + positional_encoding[:3]
```

Padding positions are gathered like any other row, so they must be masked downstream.

## Why this matters

Embedding layers are the interface between discrete tokens and continuous vectors — every model has one. Embedding size is a major architectural decision affecting parameter count, multilingual ability, and sequence length economics. For fine-tuning, the embedding layer often needs resizing when you add special tokens; forgetting this causes index-out-of-bounds errors. For RAG and retrieval, sentence embedding models such as BGE and E5 are essentially embedding layers trained with contrastive loss — the same mechanism applied to sentences and documents rather than tokens (see [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]]).

## Production implications

The vocabulary is frozen after pretraining — you can't add tokens without retraining, or at least fine-tuning the embedding layer. When adding special tokens, call `model.resize_token_embeddings(len(tokenizer))` after adding them; the new rows are randomly initialized and fine-tuning is what teaches them. For multi-tenant serving, embeddings are shared across all requests — no per-tenant customization without fine-tuning. For multilingual work, check the tokenizer's coverage of your target language: a 32k English-focused tokenizer may use 3x more tokens for Chinese text, which affects both cost and context.

## Common pitfalls

Common failure modes:

- **Forgetting to resize embeddings when adding tokens** — index-out-of-bounds crash or garbage output.
- **Random-init new tokens without fine-tuning** — the new tokens produce garbage; always fine-tune.
- **Mixing tied/untied when loading a model** — mismatched state dict errors; match the model's original design.
- **Treating the embedding lookup as a matmul** — semantically equivalent but 100x slower; use `nn.Embedding` (gather), not `onehot @ E`.
- **The padding token's embedding** — should be zeros or otherwise not affect downstream computation; mask properly.

## Further reading

Three papers anchor this topic:

- Vaswani et al. (2017), *Attention Is All You Need* — original embedding + sinusoidal.
- Press & Wolf (2017), *Using the Output Embedding to Improve Language Models* (tied embeddings).
- Chung et al. (2020), *Extending Multilingual BERT to Low-Resource Languages* (vocabulary considerations).

## See also

- [[Attention and Transformers MOC]]
- [[Transformer Block]]
- [[Feed-Forward Network]]
- [[Positional Encoding]]
- [[Sinusoidal and Learned Positional Encodings]]
- [[RoPE]]
- [[Tokenization Overview]]
- [[Word2Vec GloVe and FastText]]
- [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]]
