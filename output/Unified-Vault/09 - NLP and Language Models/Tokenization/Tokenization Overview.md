---
title: Tokenization Overview
type: concept
aliases: [tokenization, tokenizer, subword tokenization]
tags: [nlp, tokenization, subword-tokenization, bpe, wordpiece, sentencepiece, special-tokens]
sources: ["Tokenization Overview"]
created_index: "10"
---

A language model never reads text directly — it reads integer IDs looked up in an embedding table, and tokenization is the function that performs the conversion. Every property of the tokenizer — vocabulary size, granularity, special tokens, whitespace handling — propagates into the model's cost, speed, and fairness, and the tokenizer is frozen once pretraining is done. Modern LLMs overwhelmingly use subword tokenization, a middle ground between character-level (too fine) and word-level (too sparse), realized by three algorithm families: BPE, WordPiece, and the Unigram language model, with SentencePiece as a popular library implementing two of them. This note is the survey; the per-algorithm deep dives are [[BPE]], [[WordPiece]], and [[SentencePiece]].

> [!info] TL;DR
> Tokenization is the bridge between raw text and the integer IDs a language model consumes. Modern LLMs use **subword tokenization** (BPE, WordPiece, Unigram, SentencePiece) — a sweet spot between character-level (too fine) and word-level (too sparse).

## Why tokenization matters

A language model can't read text — it can only read integer IDs into an embedding table. **Tokenization** is the function:

$$
\text{tokenize}: \text{string} \rightarrow \text{list of integers}
$$

Every choice in the tokenizer affects the model. **Vocabulary size** is the clearest tradeoff: a bigger vocab means fewer tokens per sentence (shorter sequences, faster training and inference) but a bigger embedding matrix (more parameters, more memory) and a slower softmax. **Token granularity** sets where you sit on that curve — finer, character-level tokenization gives a small vocabulary but very long sequences, while coarser, word-level tokenization gives short sequences but a huge vocabulary and the out-of-vocabulary (OOV) problem. Two further choices matter in production: **multilingual coverage** (does the tokenizer handle Chinese, Arabic, code, and emoji well?) and the set of **special tokens** — `[BOS]`, `[EOS]`, `[PAD]`, `[SEP]`, `[CLS]`, chat templates, and tool-calling markers.

The stakes are high because the tokenizer is **frozen after pretraining** — you cannot change it without retraining the model, so getting it right is a high-stakes, one-time decision.

## The three granularities

### Character-level

Here the vocabulary is ASCII (or Unicode) and each character is a token. The pros are a tiny vocabulary and no OOV problem. The cons are severe: sequences become very long (a sentence is dozens of tokens), and the model must learn word structure from scratch.

### Word-level

Here the vocabulary is all words in the training corpus (or the top-N most frequent), and each word is a token. The pros are short sequences and words as meaningful units. The cons are a huge vocabulary, the OOV problem (rare words map to `[UNK]`), and lost morphology — `run`, `running`, and `runs` are unrelated tokens.

### Subword-level (the modern default)

Here the vocabulary consists of commonly-occurring substrings (a few thousand to ~200k). Common words are single tokens; rare words are split into subwords. This gives a small-ish vocabulary, no OOV (any word can be represented), and sequences shorter than character-level. The costs: the tokenizer must be trained on the corpus, and the resulting subwords can be linguistically unintuitive.

## The three main subword algorithms

| Algorithm     | Used by                              | Mechanism                                | Notes                                    |
|---------------|--------------------------------------|------------------------------------------|------------------------------------------|
| [[BPE]]       | GPT-2/3/4, Llama, Mistral, Tiktoken  | Merge most frequent pair, repeat         | Bottom-up; deterministic                 |
| [[WordPiece]] | BERT, DistilBERT, Electra            | Like BPE but maximizes likelihood        | Bottom-up; uses likelihood not frequency |
| Unigram LM    | T5, mT5, ALBERT (via SentencePiece)  | Start big, prune tokens that hurt loss   | Top-down; probabilistic                  |

[[SentencePiece]] is not an algorithm — it's a tokenizer library that implements BPE and Unigram, plus treats whitespace as a regular character (so it's language-agnostic and reversible). The three algorithms produce similar quality in practice; BPE is the most common due to its simplicity and Tiktoken's speed.

## The tokenization pipeline

A modern LLM tokenizer performs several steps in order. **Normalization** lowercases (sometimes), strips accents (sometimes), and normalizes unicode. **Pre-tokenization** splits the text on whitespace and punctuation, but keeps certain patterns together (e.g., numbers, URLs). **Subword segmentation** applies the BPE / WordPiece / Unigram merges. **Post-processing** adds special tokens (`[BOS]`, `[EOS]`) and converts to IDs.

For example, GPT-4's `tiktoken` tokenizer pre-tokenizes with a regex that splits text into chunks like "word", "  ", "123", "!", and so on. Each chunk is then BPE-tokenized independently.

## Vocabulary size tradeoffs

The embedding matrix is `vocab_size × hidden_dim`. For a 4096-dim model with 128k vocab, that's 524M parameters just for embeddings — comparable to a small model on its own. For Llama 3 8B (hidden_dim = 4096, vocab = 128K), the embedding matrix is 128K × 4096 × 2 bytes (bf16) = 1 GB. How big a share of the model that is depends on what you count: the input lookup table alone is 524M parameters, 6.6% of the 8B total, while counting embedding parameters more broadly (input matrix plus the same-sized output projection when embeddings are untied) reaches roughly 12%. Either way it is one of the largest single components of the model.

| Vocab size | Embedding params (4096-dim) | Pros                                       | Cons                                              |
|------------|------------------------------|--------------------------------------------|---------------------------------------------------|
| 32K        | 131M                         | Small embedding matrix, fast softmax       | Longer sequences, more "splits" of rare words     |
| 64K        | 262M                         | Balanced                                   | Bigger embedding matrix                           |
| 128K       | 524M                         | Shorter sequences, better multilingual     | Bigger embedding matrix, slower softmax           |
| 256K       | 1.05B                        | Excellent multilingual, very short seqs    | Embedding matrix dominates; softmax is slow       |

The 64k–128k range is the sweet spot for English + code; GPT-4 uses ~100k, and only heavily multilingual models push to 200k+ (Gemma's 256K SentencePiece vocabulary is the extreme case). The size of this matrix is why some models use **tied embeddings** (input and output share the matrix) or **factorized embeddings** (e.g., ALBERT).

**Tied embeddings** share the matrix between the input (token → vector) and the output (vector → token probabilities), saving `vocab_size × hidden_dim` parameters. They are used by Llama, Mistral, and most modern LLMs. The tradeoff: the input embedding (good for token representation) and the output projection (good for predicting the next token) may have different optimal geometries. Untying them (as in GPT-2 and T5) gives slightly better quality but doubles the embedding parameter count.

**Factorized embeddings** (ALBERT) replace `vocab × hidden` with `vocab × factorized_dim + factorized_dim × hidden` where `factorized_dim << hidden`, drastically reducing parameters for large vocabs. They are rarely used in modern LLMs because the quality loss outweighs the parameter savings.

## Special tokens

Every tokenizer has special tokens:

| Token          | Purpose                                                    |
|----------------|------------------------------------------------------------|
| `[PAD]`        | Padding to fixed batch length.                             |
| `[BOS]` / `[CLS]` | Beginning of sequence / classification head.            |
| `[EOS]`        | End of sequence — model emits this to stop.               |
| `[SEP]`        | Separator between segments (BERT).                        |
| `[UNK]`        | Out-of-vocabulary fallback (subword tokenizers don't need this in practice). |
| `<\|im_start\|>`, `<\|im_end\|>` | Chat template markers (ChatML, etc.).      |
| `<\|tool_call\|>`, `<\|tool_response\|>` | Tool-calling markers.                  |

The choice of chat template and special tokens is a major part of **instruction tuning** and is what makes a base model into a chat model.

## The token economy — why tokenization drives cost

LLM APIs are priced per token, not per character or word, which makes tokenization a direct cost driver. Empirical ratios for English text under the GPT-4 tokenizer: 1 token ≈ 4 characters (English); 1 token ≈ 0.75 words (English); 1 token ≈ 1.5 characters (Chinese); 1 token ≈ 2-3 characters (code, especially with whitespace — rough estimates for code range up to ~3-4 characters per token depending on tokenizer and code style). In concrete terms:

- 1M English words ≈ 1.3M tokens ≈ $0.13 (GPT-4o-mini input)
- 1M Chinese characters ≈ 670K tokens ≈ $0.07
- 1M lines of Python code ≈ 10-20M tokens ≈ $1-2

For production systems, **token counting is the basis of cost**. Always count tokens before sending a request (`len(tokenizer.encode(text))`), not characters. Token-aware chunking, caching, and routing all rely on accurate counts. On the operations side — LLMOps and MLOps — token budgeting drives prompt management and cost optimization, and PII redaction has to be applied to text before it is tokenized and sent to an API.

### The non-English tax

Tokenizers trained mostly on English assign multi-byte UTF-8 sequences to individual byte tokens, which means non-English text requires 2-5× more tokens per character (Chinese is typically taxed 2-3×). A Chinese sentence that's 50 characters might be 100+ tokens, while the equivalent English translation is 30 tokens. This is a real fairness issue: non-English users pay more for the same capability. Modern tokenizers (Qwen, DeepSeek) are trained with more multilingual data to reduce this tax.

## Tokenizer versions and compatibility

Tokenizers are versioned, and mixing versions produces silently wrong outputs:

| Model             | Tokenizer          | Vocab size | Notes                                  |
|-------------------|--------------------|------------|----------------------------------------|
| GPT-2            | `r50k_base`        | 50,257     | Original byte-level BPE                |
| GPT-3 / Codex    | `r50k_base` / `p50k_base` | 50,257 / 50,281 | Slight additions for code        |
| GPT-3.5 / GPT-4  | `cl100k_base`      | 100,357    | Major revision; better multilingual    |
| GPT-4o           | `o200k_base`       | 200,019    | Larger vocab; better non-English       |
| Llama 1/2        | SentencePiece BPE  | 32,000     | `▁` space convention                   |
| Llama 3          | Tiktoken-style BPE | 128,256    | Larger vocab; better multilingual      |
| Mistral 7B       | SentencePiece BPE  | 32,000     | Similar to Llama 2                     |
| Qwen 2/2.5       | Tiktoken-style BPE | 151,665+   | Strong Chinese / code coverage         |
| Gemma            | SentencePiece      | 256,000    | Very large vocab for multilingual      |
| DeepSeek-V3      | BPE                | 129,280    | Similar to Llama 3                     |

**Pin the tokenizer version in your model registry.** GPT-3 used `r50k_base`; GPT-3.5/4 use `cl100k_base`; GPT-4o uses `o200k_base`. The encodings are NOT interchangeable — a model trained with one will produce garbage with another.

## Worked example: token counting and cost estimation

```python
import tiktoken

class TokenCostEstimator:
    def __init__(self, model='gpt-4o', encoding='o200k_base'):
        self.encoding = tiktoken.get_encoding(encoding)
        # Pricing as of 2026 (illustrative)
        self.prices = {
            'gpt-4o': {'input': 2.50 / 1e6, 'output': 10.00 / 1e6},
            'gpt-4o-mini': {'input': 0.15 / 1e6, 'output': 0.60 / 1e6},
            'gpt-4': {'input': 30.00 / 1e6, 'output': 60.00 / 1e6},
        }

    def count_tokens(self, text: str) -> int:
        return len(self.encoding.encode(text))

    def estimate_cost(self, prompt: str, expected_output_tokens: int = 500) -> dict:
        input_tokens = self.count_tokens(prompt)
        output_tokens = expected_output_tokens
        price = self.prices[self.model]
        input_cost = input_tokens * price['input']
        output_cost = output_tokens * price['output']
        return {
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': input_tokens + output_tokens,
            'input_cost_usd': input_cost,
            'output_cost_usd': output_cost,
            'total_cost_usd': input_cost + output_cost,
        }

estimator = TokenCostEstimator(model='gpt-4o')
text = """Large language models are neural networks trained on vast amounts of text data.
They can generate human-like text, answer questions, and perform various language tasks."""
print(estimator.estimate_cost(text, expected_output_tokens=200))
```

## Why this matters for AI

Tokenization affects every aspect of the model: training cost (sequence length), inference latency (tokens generated), embedding matrix size, multilingual fairness, code understanding, and math understanding. Tokenizer bugs are silent — if your chat template is wrong, the model will still produce reasonable-sounding output but be subtly worse; many "my model is dumb" issues trace to tokenization. Tokenizer choice also affects evaluation: different tokenizers make the same model benchmark differently because of sequence-length effects. And there is a genuine fairness dimension — tokenizers trained mostly on English make non-English text require 2-5× more tokens (the "tax" on non-English users), a real issue in production.

## Production implications

**Tokenizer versioning** is critical: the model and tokenizer are a pair, and mismatched versions produce garbage — pin both in your model registry. **Token counting** is the basis of cost: APIs charge per token, so budget per request by counting tokens before sending; use `len(tokenizer.encode(text))`, not `len(text.split())`. **Context window math** — context length is measured in tokens, not characters: a 128k-token context holds roughly 100k English words or 50k Chinese characters (depending on tokenizer). **Streaming output** — generate tokens one at a time and decode incrementally; be aware that BPE/WordPiece can produce partial multi-byte characters mid-stream, so use `skip_special_tokens=True` and incremental decode.

## Common pitfalls

Using the **wrong tokenizer for the model** — e.g., the GPT-2 tokenizer for a Llama model — silently produces nonsense. **Forgetting to add special tokens**: base models often need `[BOS]` prepended, and chat models need their template applied. **Counting characters instead of tokens** leads to wrong context-window and cost estimates. **Adding tokens without resizing embeddings**: when you add special tokens for fine-tuning, you must resize the embedding matrix and initialize the new rows — forgetting this causes index-out-of-bounds errors or garbage. **Decoding partial tokens**: BPE merges can span multi-byte UTF-8 boundaries, so decode only complete tokens.

## Common failure modes

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Garbage output from a model | Wrong tokenizer version | Pin tokenizer in model registry; verify with `tokenizer.encode` test |
| Cost is 5× expected | Counting characters, not tokens | Use `len(tokenizer.encode(text))` for cost estimation |
| Model can't do arithmetic | Numbers are split into single digits | Use a tokenizer that keeps multi-digit numbers together (Llama 3, Qwen) |
| Non-English text is expensive | Tokenizer trained mostly on English | Use a multilingual tokenizer (Qwen, Gemma, GPT-4o) |
| Adding special tokens breaks the model | Embedding matrix not resized | Call `model.resize_token_embeddings(len(tokenizer))` after adding |
| Streaming produces partial UTF-8 | BPE merges span multi-byte boundaries | Use incremental decode; accumulate bytes until a complete codepoint |
| Chat template not applied | Base model used without chat template | Apply the model's chat template (ChatML, Llama-3 format, etc.) |

## Interview questions

**Why do modern LLMs use subword tokenization instead of word-level or character-level?** Subword tokenization hits the sweet spot between word-level (too sparse, huge vocab, OOV problem) and character-level (too fine, very long sequences). Common words become single tokens (efficient); rare words are split into subwords (no OOV); sequences are short (faster training/inference); vocabulary is bounded (~32K-256K). This is why every modern LLM uses BPE, WordPiece, or Unigram — they're all subword algorithms.

**What's the difference between BPE, WordPiece, and Unigram?** BPE (bottom-up) starts with characters and repeatedly merges the most frequent pair; used by GPT-2/3/4, Llama, Mistral. WordPiece (bottom-up) is like BPE but selects merges that maximize the likelihood of the training data (not just frequency); used by BERT. Unigram (top-down) starts with a large vocab and iteratively prunes tokens whose removal least decreases likelihood; it produces multiple valid segmentations and uses Viterbi at encode time; used by T5 and ALBERT. SentencePiece is a library that implements both BPE and Unigram. All three produce similar quality; BPE is the most common due to simplicity and Tiktoken's speed.

**How does the choice of tokenizer affect non-English users?** Tokenizers trained mostly on English assign multi-byte UTF-8 sequences to individual byte tokens, so non-English text requires 2-5× more tokens per character than English. A Chinese sentence that's 50 characters might be 100+ tokens, while the equivalent English translation is 30 tokens. This is the "non-English tax" — non-English users pay more for the same capability. Modern tokenizers (Qwen, Gemma, GPT-4o) are trained with more multilingual data to reduce this tax; GPT-4o's `o200k_base` is significantly better for non-English than GPT-3.5's `cl100k_base`.

**What happens if you add a special token during fine-tuning without resizing the embedding matrix?** The model produces garbage or crashes. The tokenizer returns an index beyond the embedding matrix's range, causing an index-out-of-bounds error — or, if the index happens to be within range, the model uses an existing token's embedding for the new special token, producing semantically wrong outputs. The fix: always call `model.resize_token_embeddings(len(tokenizer))` after adding special tokens. The new rows are initialized with random values, so you also need to fine-tune to teach the model what the new tokens mean.

**Why is the embedding matrix so large, and how do tied embeddings help?** The embedding matrix is `vocab_size × hidden_dim`. For Llama 3 8B (vocab = 128K, hidden = 4096): 524M parameters just for embeddings — 6.6% of the 8B total (roughly 12% if the same-sized output projection is counted as well). Tied embeddings share the matrix between input (token → vector) and output (vector → token probabilities), saving `vocab_size × hidden_dim` parameters; used by Llama, Mistral, and most modern LLMs. The tradeoff: the input embedding and output projection may have different optimal geometries; untied (GPT-2, T5) gives slightly better quality but doubles the parameter count.

**How would you handle streaming token decoding where BPE merges span multi-byte UTF-8 boundaries?** BPE merges can produce byte sequences that are partial UTF-8 codepoints mid-stream, and naive decoding produces errors. Three approaches: (1) **accumulate bytes** until you have a complete UTF-8 codepoint, tracking the expected byte count from the leading byte (1-4 bytes for UTF-8); (2) use `errors='replace'` in decode to substitute replacement characters for partial sequences — visually ugly but won't crash; (3) use the tokenizer's streaming API (HuggingFace's `decode_incremental` or `convert_tokens_to_string`). Production serving frameworks (vLLM, TGI) handle this automatically.

## Further reading

The primary papers behind each family, plus the practical documentation:

- Sennrich, Haddow, Birch (2016), *Neural Machine Translation of Rare Words with Subword Units* — original BPE for NMT.
- Wu et al. (2016), *Google's Neural Machine Translation System* — WordPiece.
- Kudo (2018), *SentencePiece: A simple and language independent subword tokenizer*.
- HuggingFace tokenizers docs: https://huggingface.co/docs/tokenizers

## Connections to other concepts

[[BPE]] is the dominant algorithm and carries the deep dive on merges, byte-level encoding, and pre-tokenization. [[WordPiece]] is BERT's likelihood-based variant, and [[SentencePiece]] is the language-agnostic library implementing BPE and Unigram. Static word embeddings predate subword tokenization — see [[Word2Vec GloVe and FastText]] — and tokenization choices also change how perplexity is measured and compared ([[Perplexity]]). The embedding-matrix consequences of vocabulary size (tied vs. untied, resizing) are treated in [[Embedding Layer]]. Further afield, the special-token and chat-template material belongs to instruction tuning; constrained decoding operates at the token level; RAG ingestion uses token-aware chunking; prompt management and cost optimization both budget by token count.

## See also

- [[NLP and Language Models MOC]]
- [[BPE]]
- [[WordPiece]]
- [[SentencePiece]]
- [[Word2Vec GloVe and FastText]]
- [[Perplexity]]
- [[Embedding Layer]]
- [[Large Language Models MOC]]
