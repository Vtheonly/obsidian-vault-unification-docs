---
title: Autoregressive vs Parallel Encoding
type: concept
aliases:
  - parallel vs autoregressive
  - autoregressive decoding
  - causal vs bidirectional processing
tags:
  - transformers
  - autoregressive
  - parallel-encoding
  - encoder-decoder
  - inference
  - exposure-bias
sources:
  - "03. Autoregressive vs Parallel Encoding"
created_index: 19
---

There are two fundamental ways a model can process a sequence of tokens: in parallel (bidirectionally, all tokens at once) or autoregressively (causally, one token at a time, left to right). The choice is not just an implementation detail — it determines what the model can do, how it trains, and where its bottlenecks are. Parallel encoding gives rich per-token representations but cannot generate; autoregressive decoding generates naturally but sees only the past and is sequentially slow at inference. Hybrids such as Prefix-LM, the full encoder-decoder, and fill-in-the-middle training try to combine the two.

## The two ways to process a sequence

**Parallel (bidirectional):** all tokens are processed simultaneously, and each token's representation can depend on every other token. This is how encoder blocks work (no masking).

**Autoregressive (causal):** tokens are processed one at a time, left to right, and each token's representation can depend only on previous tokens (and itself). This is how decoder blocks work (with causal masking).

The choice between these is not just an implementation detail — it determines what the model can do, how it trains, and where its bottlenecks are.

## Parallel encoding — the encoder's way

In parallel encoding, the entire input sequence is fed to the model at once, and all positions are computed simultaneously. The self-attention matrix is full (no mask) — every position attends to every other position.

```
Input:  [t1, t2, t3, t4, t5]
                ↓ (one forward pass, all positions computed together)
Output: [h1, h2, h3, h4, h5]
```

Each $h_i$ is a function of all of $t_1, \ldots, t_5$. The representation of "bank" in "I sat by the river bank" incorporates information from "river" (which disambiguates "bank" as river-bank, not financial-bank). This is why encoder models (BERT) produce rich contextualized representations — each token sees its full context.

The advantages are rich per-token representations (full bidirectional context), computational efficiency (one forward pass processes the whole sequence), and no exposure bias (there is no autoregressive generation). The decisive disadvantage: **parallel encoding cannot generate sequences.** Generation requires producing one token at a time, but parallel encoding assumes all tokens are available. You cannot "generate token 3" if token 3's representation depends on tokens 4 and 5, which do not exist yet.

Use cases: classification, entity recognition, retrieval, span extraction — anything where the whole input is available and you need to understand it, but not generate.

## Autoregressive decoding — the decoder's way

In autoregressive decoding, the model processes tokens one at a time, left to right. The self-attention is causally masked — position $i$ attends only to positions $1, \ldots, i$.

```
Step 1: [t1]                    → predict t2
Step 2: [t1, t2]                → predict t3
Step 3: [t1, t2, t3]            → predict t4
Step 4: [t1, t2, t3, t4]        → predict t5
Step 5: [t1, t2, t3, t4, t5]    → predict t6 (or <EOS>)
```

Each prediction uses only the past. This is exactly the inference-time behavior: generate token $t+1$ from tokens $1, \ldots, t$, append it, repeat.

The advantages: it is **naturally generative** — the training task (predict next token) matches the inference task (generate next token) — and it can handle variable-length output (generate until `<EOS>`). The disadvantages: **weaker per-token representations**, because position $i$ cannot use information from positions $i+1, \ldots, T$ — the representation of "bank" in "I sat by the river bank" cannot incorporate information from "river" if "bank" comes before "river" (which it does not here, but in general it can). **Sequential inference**: you cannot generate token $t+1$ until token $t$ is generated, which makes inference $O(T)$ sequential steps, even though each step is parallelizable across the model's internal computation. And **exposure bias**: trained on ground-truth previous tokens, tested on model-predicted previous tokens — the training consequence of autoregressive decoding.

Use cases: text generation, translation, summarization, chat — anything where you need to produce a sequence.

## The training-inference alignment

The deepest difference between parallel and autoregressive is the **alignment between training and inference**:

| | Parallel (encoder) | Autoregressive (decoder) |
| :--- | :--- | :--- |
| Training task | Fill in masked tokens from full context | Predict next token from past only |
| Inference task | Encode full input, classify/extract | Generate next token from past only |
| Alignment | Good (input is always full) | Perfect (training = inference) |
| Can generate? | No | Yes |

The decoder's perfect training-inference alignment is why it dominates generation. The encoder's richer per-token context is why it dominates understanding.

The modern trend toward decoder-only LLMs (GPT class) is driven by the observation that **if you scale the decoder enough, the disadvantage of unidirectional context mostly disappears.** A large enough decoder-only model has seen so much text that it learns bidirectional patterns implicitly — it can predict a masked token in the middle of a sentence nearly as well as BERT, even though it was trained only on next-token prediction. The decoder's advantage (natural generation, perfect training-inference alignment, any-text-as-training-data) outweighs the encoder's advantage (bidirectional context) once scale closes the gap.

## Hybrid approaches

Several architectures try to get the best of both worlds.

### Prefix-LM (decoder-only with bidirectional prefix)

Process the prompt (input) with bidirectional attention, then switch to causal attention for generation. This gives the input the rich bidirectional context of an encoder while keeping the autoregressive generation of a decoder. Used by T5 (in one mode), PaLM, and LLaMA-2 (with fill-in-the-middle training).

### Encoder-Decoder (full Transformer)

The encoder processes the input in parallel (bidirectionally); the decoder generates the output autoregressively, attending to the encoder via cross-attention. This is the cleanest separation: parallel for understanding, autoregressive for generation. Used by T5, BART, Whisper.

### Fill-in-the-middle (FIM)

Train a decoder-only model not just on next-token prediction but also on "given the text before and after a gap, fill in the gap." This teaches the model to use bidirectional context for infilling while preserving autoregressive generation. Used by Code Llama, StarCoder, and modern code models.

## The inference cost difference

Parallel encoding processes the whole sequence in one forward pass: $O(1)$ forward passes, $O(T^2)$ attention cost.

Autoregressive decoding processes one token at a time: $O(T)$ forward passes, $O(T^2)$ total attention cost (with KV caching). Without caching, it is $O(T^3)$.

This is why **autoregressive generation is slow** — you cannot parallelize across the time dimension of generation, only across the model's internal computation. This is a fundamental limitation of autoregressive models and the subject of **non-autoregressive generation** research (generate all tokens in parallel, accept some quality loss). For modern LLMs, inference cost is dominated by the autoregressive loop. Techniques like speculative decoding (draft with a small model, verify with the large model), KV caching, and quantization are all aimed at making autoregressive generation faster.

## Key takeaways

1. Parallel encoding (encoder) processes all tokens simultaneously with bidirectional attention — rich representations, but cannot generate.
2. Autoregressive decoding (decoder) processes one token at a time with causal masking — naturally generative, but weaker per-token representations.
3. The deepest difference is training-inference alignment: the decoder's task is identical at training and inference; the encoder's is not.
4. Modern decoder-only LLMs dominate because scale closes the bidirectional-context gap, and the decoder's training-data simplicity (any text) + natural generation outweigh the encoder's advantages.
5. Hybrids (Prefix-LM, Encoder-Decoder, FIM) try to combine bidirectional context with autoregressive generation.
6. Autoregressive decoding is fundamentally sequential at inference — the main cost of modern LLMs and the subject of non-autoregressive and speculative decoding research.

## See also

- [[Attention and Transformers MOC]]
- [[BERT vs GPT vs T5]] — the three configurations these processing modes correspond to
- [[Teacher Forcing and Exposure Bias]] — the training consequence of autoregressive decoding
- [[Transformer Decoder Block]] — causal masking and cross-attention in practice
- [[Information Bottleneck and Latent Space]] — what the decoder retrieves from
- [[Choosing the Right Architecture]] — matching the task to a configuration
- [[GPT Family]] — decoder-only at scale
- [[T5 and BART]] — encoder-decoder and prefix-LM hybrids
