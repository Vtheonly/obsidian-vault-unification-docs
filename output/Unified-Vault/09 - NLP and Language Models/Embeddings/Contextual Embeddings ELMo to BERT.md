---
title: Contextual Embeddings ELMo to BERT
type: concept
aliases: [Contextual Embeddings, ELMo, "Embeddings from Language Models", "Contextual Embeddings ELMo to BERT", "Contextual Embeddings: ELMo → BERT"]
tags: [nlp, embeddings, contextual-embeddings, elmo, bert, transformers, pretraining]
sources: ["06 - Contextual Embeddings: ELMo → BERT"]
created_index: 1
---

Static embeddings such as those in [[Word2Vec GloVe and FastText]] give every word a single fixed vector, so every occurrence of a word shares one representation regardless of its meaning in context. Contextual embeddings instead compute a vector for each word token conditioned on the entire surrounding sentence. ELMo (February 2018) achieved this with a bidirectional LSTM; BERT (October 2018) replaced the recurrence with a bidirectional Transformer encoder and won decisively. That transition — from one vector per word type to one vector per word token — unlocked modern NLP and set up the pretrain-then-fine-tune paradigm that still dominates the field.

> [!info] TL;DR
> Static embeddings (Word2Vec, GloVe) give each word one fixed vector. **Contextual embeddings** give each word a different vector depending on its context. ELMo (2018) used bidirectional LSTMs; BERT (2018) used bidirectional Transformers. This shift unlocked modern NLP.

## The problem with static embeddings

Word2Vec and GloVe assign each word a single vector. But words are ambiguous. "bank" — river bank? money bank? banked shot? "apple" — fruit? company? "light" — weight? illumination? verb? A single vector must average these senses, blurring them, and the model can't disambiguate from context.

Contextual embeddings solve this by **conditioning the embedding on the entire context**. The vector for "bank" in "I fished by the river bank" differs from the vector for "bank" in "I deposited money in the bank." Instead of one averaged vector per word type, each occurrence gets its own representation.

## How contextual embeddings solve polysemy

The key insight: a word's meaning depends on its context. Static embeddings can't capture this — they assign one vector per word type. Contextual embeddings assign one vector per word **token** — the vector depends on the full sentence.

### Mathematical formulation

For a static embedding model: $\text{embed}(\text{"bank"}) = \mathbf{v} \in \mathbb{R}^d$ — same vector regardless of context.

For a contextual embedding model: $\text{embed}(\text{"bank"} \mid \text{"I went to the river bank"}) = \mathbf{v}_1$, $\text{embed}(\text{"bank"} \mid \text{"I deposited money in the bank"}) = \mathbf{v}_2$, with $\mathbf{v}_1 \neq \mathbf{v}_2$.

The contextual embedding is computed by the Transformer: $\mathbf{v} = \text{Transformer}(\text{sentence})_{\text{position of "bank"}}$. Self-attention lets the model incorporate context from all other words in the sentence, so "bank" can draw on "river" or "money" to select the right sense.

### Empirical evidence

Comparing vectors with cosine similarity makes the difference concrete. Two measurements stand out:

- Cosine similarity between "bank" in "river bank" and "bank" in "bank account": ~0.3 (static) vs. ~0.7 (contextual — both are still "bank" in some sense).
- Cosine similarity between "bank" in "river bank" and "shore" in "river shore": ~0.2 (static — "bank" and "shore" are different words) vs. ~0.85 (contextual — the model knows they mean the same thing in context).

## ELMo (embeddings from language models, 2018)

Peters et al. (2018) used a **bidirectional LSTM** trained as a language model. For each word, the embedding is a weighted combination of the LSTM's hidden states (forward + backward):

$$
\text{ELMo}(word_i) = \gamma \sum_{j=0}^{L} s_j \mathbf{h}_{j, i}
$$

where $\mathbf{h}_{j, i}$ is the hidden state at layer $j$ for word $i$ (concatenating forward and backward), and $s_j$ are learned layer weights.

### Why ELMo was a big deal

ELMo was **contextual**: each word's embedding depends on the whole sentence. It was **pretrained**: trained once on a large corpus, then used as features for many downstream tasks. And it was **state-of-the-art** on many NLP benchmarks when released.

### Limitations

ELMo is LSTM-based — slow to train, and it can't be parallelized. Its contextualization is **shallow**: the LSTM hidden state mixes information across the sentence, but slowly. And it was used as **features** for downstream models, not fine-tuned end-to-end, so task-specific signal never reshaped the representations themselves.

## BERT (bidirectional encoder representations from transformers, 2018)

Devlin et al. (2018) replaced ELMo's LSTM with a Transformer encoder ([[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]]). Four innovations define the model.

### Bidirectional Transformer encoder

Each token attends to all other tokens (no causal mask). The representation of each word is built from the full context, both left and right, in a single pass.

### Masked language model pretraining

Randomly mask 15% of tokens; predict them from the rest. This forces the model to use bidirectional context, since the answer can sit on either side of the mask:

```
Input:  the man went to the [MASK] to buy [MASK]
Target: store, milk
```

### Next sentence prediction

BERT's second pretraining task predicts whether two sentences are adjacent in the original text. (Later research showed NSP doesn't help much; RoBERTa dropped it.)

### Fine-tuning, not feature extraction

Unlike ELMo, BERT is fine-tuned end-to-end on each downstream task. The same pretrained model is paired with different heads:

- Classification: `[CLS]` token + linear head.
- NER: per-token linear head.
- Q&A: predict start and end positions.

### Impact

BERT set SOTA on 11 NLP benchmarks simultaneously. It kicked off the "pretrain then fine-tune" paradigm that still dominates NLP.

## Why BERT beat ELMo

| Aspect                | ELMo (2018)                     | BERT (2018)                       |
|-----------------------|---------------------------------|-----------------------------------|
| Architecture          | Bidirectional LSTM              | Bidirectional Transformer encoder |
| Context               | Sequential (LSTM hidden states) | Full bidirectional (self-attention) |
| Pretraining           | Language modeling (forward + backward) | Masked Language Modeling (MLM) |
| Quality on GLUE       | 70-75%                          | 80-85%                            |
| Training speed        | Slow (LSTM sequential)          | Fast (Transformer parallel)       |
| Scalability           | Limited (LSTM vanishing gradients) | Scales to billions of params   |

### Why the Transformer beat the LSTM

1. **Full bidirectional context**: BERT's self-attention lets every token attend to every other token in one pass. ELMo's bidirectional LSTM concatenates forward and backward, but each direction is still sequential.
2. **Parallelism**: Transformer layers are fully parallel — they train 10× faster than LSTMs on GPUs.
3. **Scalability**: Transformers scale to billions of parameters without vanishing gradients. LSTMs struggle past a few layers.
4. **MLM pretraining**: BERT's masked LM is harder than ELMo's forward/backward LM, forcing deeper representations.

The net effect: BERT beat ELMo by 10-15% on GLUE.

## The static-to-contextual timeline

The shift from static to contextual embeddings took five years, from the first fixed vectors to the model that made contextualization the default.

### 2013: Word2Vec (static)

Each word maps to one vector, learned via skip-gram or CBOW. "bank" has the same vector whether it's a river bank or a financial bank. Polysemy is a fundamental limitation of the approach.

### 2014: GloVe (static)

GloVe (Global Vectors) learns vectors via matrix factorization of co-occurrence counts. Same limitation as Word2Vec: one vector per word.

### 2018: ELMo (February), then BERT (October)

February 2018 brought ELMo — Peters et al., "Deep Contextualized Word Representations" — with its bidirectional LSTM, where the embedding is the concatenation of forward and backward LSTM hidden states. "bank" in "river bank" finally gets a different vector than "bank" in "bank account". The limitation: being LSTM-based, it is slow to train and has limited context (the LSTM forgets).

October 2018 brought BERT — Devlin et al. — a bidirectional Transformer encoder with MLM pretraining: predicting masked tokens using full bidirectional context. It was massively better than ELMo on downstream tasks. Its limitation: encoder-only, so it is not suited for generation.

### 2019–2020: refinements

RoBERTa improved the pretraining recipe (more data, dynamic masking, no NSP). DistilBERT used knowledge distillation to come in 40% smaller and 60% faster. ALBERT used parameter sharing for fewer parameters at similar quality.

The wider model landscape evolved in parallel:

| Model   | Year | Key change                                     |
|---------|------|------------------------------------------------|
| ELMo    | 2018 | BiLSTM contextual embeddings                   |
| BERT    | 2018 | Bidirectional Transformer; MLM; fine-tune      |
| RoBERTa | 2019 | More data, bigger batches, drop NSP            |
| ALBERT  | 2019 | Factorized embeddings; parameter sharing       |
| T5      | 2019 | Encoder-decoder; text-to-text framing          |
| GPT-2/3 | 2019/20 | Decoder-only; autoregressive; scale         |
| DeBERTa | 2020 | Disentangled attention; enhanced mask decoder  |
| ELECTRA | 2020 | Replaced token detection (more efficient)      |

The three branches split by use: the encoder branch (BERT family — see [[BERT vs GPT vs T5]]) is best for classification, NER, and extraction; the decoder branch (GPT family, [[GPT Family]]) is best for generation; and the encoder-decoder branch ([[T5 and BART]]) handles both.

### 2020 and beyond: sentence transformers and modern embedding models

Sentence-BERT pools BERT outputs into sentence embeddings. Modern embedding models — BGE, GTE, E5, OpenAI text-embedding-3 — are trained for retrieval, not MLM; they are covered in detail under modern contextual embedding models below.

## Worked examples

### BERT for classification

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModelForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=2)

inputs = tokenizer("This movie was great!", return_tensors="pt")
outputs = model(**inputs)
logits = outputs.logits  # (1, 2)
```

Fine-tuning is standard supervised training on labeled data, with learning rate ~2e-5 and 3–5 epochs.

### Comparing static and contextual embeddings

```python
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity

# Static: Word2Vec (simulated)
# In practice: from gensim.models import KeyedVectors
# word2vec["bank"] = same vector for all contexts

# Contextual: BERT
tokenizer = AutoTokenizer.from_pretrained("bert-base-uncased")
model = AutoModel.from_pretrained("bert-base-uncased")

def get_contextual_embedding(sentence, target_word):
    """Get BERT's contextual embedding for target_word in sentence."""
    inputs = tokenizer(sentence, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    # Find the position of target_word
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    target_pos = tokens.index(target_word)
    # Return the contextual embedding (last hidden state)
    return outputs.last_hidden_state[0, target_pos].numpy()

# Same word, different contexts
v1 = get_contextual_embedding("I sat by the river bank", "bank")
v2 = get_contextual_embedding("I deposited money in the bank", "bank")
v3 = get_contextual_embedding("I sat by the river shore", "shore")

print(f"bank (river) vs. bank (money): {cosine_similarity([v1], [v2])[0][0]:.3f}")
print(f"bank (river) vs. shore (river): {cosine_similarity([v1], [v3])[0][0]:.3f}")

# Expected: bank-vs-bank ~0.7 (same word, different sense)
# bank (river) vs. shore (river) ~0.85 (different word, same meaning in context)
# This demonstrates contextual embeddings capture meaning, not just word type
```

The expected numbers match the empirical pattern above: ~0.7 for the same word across senses, ~0.85 for different words with the same in-context meaning.

## Production implications

For classification, NER, and extraction tasks, a fine-tuned BERT-family model is often the right choice — smaller, faster, and more accurate than an LLM. For embeddings in retrieval / RAG, use sentence-transformers or BGE (BERT-family encoders with contrastive training). BERT models are cheap to fine-tune (an hour on a single GPU) and cheap to serve. For generation, BERT is the wrong tool — use a decoder-only model (Llama, GPT).

## Common pitfalls and failure modes

The recurring mistakes when working with BERT-family models all trace back to how the model was pretrained and what it can and cannot do. The classics:

- **Using BERT for generation** — it can't generate; it's bidirectional.
- **Wrong tokenizer** — `bert-base-uncased` requires lowercased input, and it tokenizes with WordPiece ([[WordPiece]]).
- **Forgetting `[CLS]` and `[SEP]`** — most HuggingFace tokenizers add these automatically with `tokenizer(text)`, but raw `encode` may not.
- **Max sequence length** — BERT is limited to 512 tokens. For longer documents, use a sliding window or Longformer.

The corresponding failure modes seen in deployed systems:

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| BERT embeddings not capturing domain semantics | BERT trained on general text | Fine-tune on domain data; use domain-specific model |
| Sentence embeddings poorly clustered | Mean pooling inadequate | Use CLS token; or use Sentence-BERT / BGE |
| Embeddings from different layers inconsistent | Wrong layer choice | Use last 4 layers averaged (BERTology finding); or last layer |
| Cross-model similarity meaningless | Different embedding spaces | Never compare embeddings from different models |
| BERT slow for retrieval | Encoder is heavy | Use Sentence-BERT (smaller); or BGE-small |

## Modern contextual embedding models (2024-2026)

The BERT lineage evolved into modern embedding models optimized for retrieval:

| Model                  | Year | Base architecture | Training signal                | Best for                |
|------------------------|------|-------------------|--------------------------------|-------------------------|
| BERT                   | 2018 | Encoder           | MLM + NSP                      | Classification, NER     |
| Sentence-BERT          | 2019 | Encoder           | Mean pooling + contrastive     | Sentence similarity     |
| SimCSE                 | 2021 | Encoder           | Contrastive (dropout)          | Sentence embeddings     |
| E5                     | 2022 | Encoder           | Text-text contrastive          | Retrieval               |
| BGE                    | 2023 | Encoder           | Multi-stage contrastive        | Retrieval, multilingual |
| GTE                    | 2023 | Decoder (Llama)   | Contrastive                    | Retrieval               |
| OpenAI text-embedding-3| 2024 | Unknown           | Contrastive                    | General-purpose         |

The key shift: from MLM pretraining (BERT) to **contrastive pretraining** (BGE, E5, GTE). Modern embedding models are trained directly for retrieval quality, not language modeling. Concretely, they use positive pairs (query, relevant doc) and negative pairs (query, irrelevant doc) with InfoNCE loss. They also use larger context (512→8K), sometimes decoder architectures (GTE uses Llama), and multi-stage training (pretrain → fine-tune → distill).

## Why this matters

BERT kicked off the modern NLP era — the pretrain-then-fine-tune paradigm originated here. BERT-style models are still widely used in production for classification, NER, and embedding (sentence-transformers). The shift from static to contextual embeddings was the conceptual leap that made LLMs possible. For retrieval / RAG, BERT-family encoders power many embedding models (BGE and E5 are descendants of the BERT architecture). Probing — analyzing what BERT encodes — is the natural interpretability companion to this line of models.

## Further reading

- Peters et al. (2018), *Deep Contextualized Word Representations* (ELMo).
- Devlin et al. (2019), *BERT: Pre-training of Deep Bidirectional Transformers*.
- Liu et al. (2019), *RoBERTa: A Robustly Optimized BERT Pretraining Approach*.

## Interview questions

1. **What's the key difference between static and contextual embeddings?**
   Static (Word2Vec, GloVe): one vector per word type — "bank" has the same vector regardless of context. Contextual (ELMo, BERT): one vector per word token — "bank" in "river bank" gets a different vector than "bank" in "bank account". Contextual embeddings are computed by the Transformer incorporating the full sentence context via self-attention.

2. **Why did BERT replace ELMo?**
   Four reasons. (1) Full bidirectional context: BERT's self-attention lets every token attend to every other in one pass; ELMo's bidirectional LSTM concatenates forward/backward, each still sequential. (2) Parallelism: Transformer layers train 10× faster than LSTMs on GPUs. (3) Scalability: Transformers scale to billions of parameters without vanishing gradients; LSTMs struggle past a few layers. (4) MLM pretraining is harder than ELMo's forward/backward LM, forcing deeper representations. Result: BERT beat ELMo by 10-15% on GLUE.

3. **How do contextual embeddings solve polysemy?**
   A word's meaning depends on context. Static embeddings assign one vector per word type — they can't distinguish "bank" (river) from "bank" (money). Contextual embeddings assign one vector per word token, computed by the Transformer incorporating the full sentence: self-attention lets "bank" attend to "river" (giving the water-bank vector) or to "money" (giving the financial-bank vector). Empirically, the cosine similarity between "bank" in different contexts is ~0.7 (still "bank"), but between "bank" and "shore" in the same context it is ~0.85 (same meaning).

4. **What is MLM, and why is it better than standard LM for pretraining?**
   MLM (Masked Language Modeling): mask 15% of tokens, predict them from the full bidirectional context. Standard LM: predict the next token from left context only. MLM is better because (1) it is bidirectional — it uses both left and right context; (2) it is harder — forcing deeper representations; (3) it is more sample-efficient — every masked token is a training signal. BERT's MLM beat ELMo's forward/backward LM by 10-15% on GLUE.

5. **How do modern embedding models (BGE, GTE) differ from BERT?**
   BERT is pretrained with MLM (language modeling). Modern embedding models (BGE, GTE, E5) are pretrained with **contrastive learning** — directly optimized for retrieval quality. They use positive pairs (query, relevant doc) and negative pairs (query, irrelevant doc), with InfoNCE loss. This produces embeddings better suited for retrieval than BERT's MLM embeddings. Modern embedding models also use larger context (512→8K), decoder architectures (GTE uses Llama), and multi-stage training (pretrain → fine-tune → distill).

6. **When would you use BERT vs. a modern embedding model?**
   Use BERT for classification, NER, and token-level tasks (where MLM pretraining helps). Use modern embedding models (BGE, GTE) for retrieval, semantic search, and RAG (where contrastive pretraining helps). BERT's MLM embeddings are okay for retrieval but not optimal — they weren't trained for it. Modern embedding models are 5-20% better on retrieval benchmarks.

## See also

- [[NLP and Language Models MOC]]
- [[Word2Vec GloVe and FastText]] — static predecessors
- [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]] — the architecture in depth
- [[The Transformer]]
- [[Self-Attention]]
- [[LSTM]]
- [[WordPiece]] — BERT's tokenizer
- [[CLS Token]]
- [[BERT vs GPT vs T5]]
- [[GPT Family]]
- [[T5 and BART]]
- [[Perplexity]]
