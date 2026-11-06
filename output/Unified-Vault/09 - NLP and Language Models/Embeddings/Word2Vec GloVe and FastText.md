---
title: Word2Vec GloVe and FastText
type: concept
aliases: [Word2Vec, GloVe, FastText, "Static Word Embeddings", "Word2Vec, GloVe, FastText"]
tags: [nlp, embeddings, word2vec, glove, fasttext, skip-gram, negative-sampling, static-embeddings]
sources: ["Word2Vec, GloVe, FastText"]
created_index: 2
---

Word2Vec, GloVe, and FastText are the three classical static word embedding algorithms: each learns a fixed vector for every word such that similarity in vector space reflects semantic similarity. Contextual embeddings (ELMo, BERT, GPT — see [[Contextual Embeddings ELMo to BERT]]) superseded them for most NLP work, but static embeddings remain a fast, cheap baseline for vector search, recommender systems, and hybrid keyword retrieval. The skip-gram objective, GloVe's least-squares factorization of co-occurrence counts, and FastText's subword n-grams are also worth understanding on their own terms, because the same ideas power modern embedding models.

> [!info] TL;DR
> Three classical **static word embedding** algorithms. Each maps words to fixed vectors such that similarity in vector space reflects semantic similarity. Superseded for NLP by contextual embeddings (BERT, GPT), but still relevant for retrieval, recommender systems, and as a baseline.

## Static versus contextual embeddings

**Static embeddings**: each word has a single, fixed vector regardless of context. `bank` (river) and `bank` (money) share one vector.

**Contextual embeddings** (ELMo, BERT, GPT): each word's vector depends on its surrounding context. `bank` in "the river bank" gets a different vector than `bank` in "the bank account".

Word2Vec, GloVe, and FastText are static. Modern LLMs produce contextual embeddings as a side effect of their hidden states. But static embeddings are still useful for:

- **Vector search baselines** — fast and cheap.
- **Recommender systems** — item2vec, user2vec.
- **Keyword-based retrieval** — BM25 + word embeddings hybrid.
- **Pre-computed embeddings for downstream tasks** when latency matters.

## Word2Vec (Mikolov et al., 2013)

Word2Vec trains a shallow neural network to learn word vectors. Two variants exist.

### CBOW (continuous bag-of-words)

Predict the center word from its context (surrounding words):

$$
P(w_t \mid w_{t-k}, \ldots, w_{t-1}, w_{t+1}, \ldots, w_{t+k})
$$

The center word's vector is computed by averaging context vectors, then a softmax over the vocabulary.

### Skip-gram

Predict the context words from the center word:

$$
P(w_{t-k}, \ldots, w_{t+k} \mid w_t)
$$

Skip-gram is slower but works better for rare words, and it is the variant used in the canonical `word2vec` released vectors.

### Training objective

Maximize the log-likelihood of observed (word, context) pairs:

$$
\mathcal{L} = \sum_{(w, c) \in D} \log P(c \mid w)
$$

with negative sampling:

$$
\log \sigma(v_c \cdot v_w) + \sum_{i=1}^{K} \mathbb{E}_{w_i \sim P_n} \log \sigma(-v_{w_i} \cdot v_w)
$$

Negative sampling avoids the expensive full-vocabulary softmax by sampling a few "negative" examples. This is what makes Word2Vec fast.

### Famous properties

- **Vector arithmetic captures analogy**: $\vec{king} - \vec{man} + \vec{woman} \approx \vec{queen}$.
- **Similarity**: $\cos(\vec{cat}, \vec{dog}) > \cos(\vec{cat}, \vec{car})$.
- **Linear structure**: gender, tense, and country-capital relations appear as roughly linear directions in the embedding space.

These properties are emergent — not explicitly trained — and were a major reason for the excitement around Word2Vec in 2013.

## The skip-gram negative sampling loss

Skip-gram with negative sampling (SGNS) is the most common Word2Vec variant. The loss for a single (center, context) pair $(w, c)$ with $K$ negative samples $\{w_1, \ldots, w_K\} \sim P_n$:

$$
\mathcal{L}_{\text{SGNS}} = -\log \sigma(v_c \cdot v_w) - \sum_{i=1}^{K} \log \sigma(-v_{w_i} \cdot v_w)
$$

The first term maximizes the dot product of the true (center, context) pair. The second term minimizes the dot product of $K$ random (center, negative) pairs, where negatives are sampled from a noise distribution $P_n$ (typically $P_n(w) \propto \text{count}(w)^{3/4}$ — the 3/4 power downweights frequent words). The dot product is the quantity Word2Vec optimizes; cosine similarity — the dot product of normalized vectors — is the standard metric for comparing the learned vectors.

### Why the 3/4 power for negative sampling?

Frequent words ("the", "of") dominate the corpus. Sampling negatives proportional to raw frequency would mostly sample frequent words, which are easy to distinguish from rare context words. The 3/4 power flattens the distribution: $\text{count}(\text{"the"})^{3/4} / \text{count}(\text{"cat"})^{3/4} < \text{count}(\text{"the"}) / \text{count}(\text{"cat"})$. This gives rare words more chance to be sampled as negatives, providing a stronger learning signal. The 3/4 exponent is empirical — Mikolov et al. tried 0, 0.5, 0.75, 1.0 and found 0.75 works best.

## The analogy property — why it works

The famous property: $\vec{king} - \vec{man} + \vec{woman} \approx \vec{queen}$. Why does this work?

Word2Vec and GloVe learn embeddings where the **vector difference** between related words captures relationships. If $\vec{king} - \vec{queen} \approx \vec{man} - \vec{woman}$ (both differences represent the "male-female" direction), then $\vec{king} - \vec{man} + \vec{woman} \approx \vec{queen}$.

This happens because:

1. **Linear structure**: the embedding space has linear directions for gender, tense, country-capital, etc.
2. **Translation invariance**: the gender direction is roughly the same across word pairs (king-queen, man-woman, actor-actress).
3. **Vector arithmetic**: $a - b + c$ finds the point closest to $c$ translated by the $a - b$ direction.

### Limitations of the analogy property

- **Only works for clean analogies** (gender, tense, country-capital). It fails for complex relationships — "Paris is to France as Tokyo is to ?" works, but "Einstein is to relativity as Darwin is to ?" doesn't.
- **Sensitive to preprocessing** (lowercasing, tokenization, training corpus).
- **The 3CosAdd method** ($a - b + c$) is suboptimal; 3CosMul (Levy & Goldberg 2014) gives better results by using multiplication instead of addition.

## GloVe (Pennington et al., 2014)

GloVe (Global Vectors) is matrix-factorization-based rather than predictive. It explicitly factorizes the **word co-occurrence matrix**.

Let $X_{ij}$ be the number of times word $j$ appears in the context of word $i$. GloVe minimizes:

$$
\mathcal{L} = \sum_{i,j} f(X_{ij}) \left( v_i^T \tilde{v}_j + b_i + \tilde{b}_j - \log X_{ij} \right)^2
$$

where $v_i, \tilde{v}_j$ are word and context vectors, $b_i, \tilde{b}_j$ are biases, and $f(X_{ij})$ is a weighting function that down-weights very frequent co-occurrences (e.g., stopwords). The weighting function is critical: without it, "the" and "of" would dominate the loss.

### Word2Vec versus GloVe

| Aspect              | Word2Vec                              | GloVe                                |
|---------------------|---------------------------------------|--------------------------------------|
| Approach            | Predictive (local context)            | Count-based (global co-occurrence)   |
| Training            | Stochastic, online                    | Batch, on co-occurrence matrix       |
| Memory              | Low (stream over corpus)              | High (store full matrix)             |
| Performance         | Comparable                            | Comparable                           |

In practice, both produce similar-quality vectors on most tasks. GloVe is more reproducible (deterministic given the corpus); Word2Vec has more variance due to stochastic training.

## FastText (Bojanowski et al., 2017)

FastText extends Word2Vec by representing each word as a **bag of character n-grams**. For example, `where` (with n=3) is represented as `<wh, whe, her, ere, re>` plus the whole word `<where>`.

The word's vector is the sum of its n-gram vectors. This has two big advantages:

1. **Better for rare words** — even if `wherefore` is rare, its subword n-grams (`<whe`, `her`, `ere`, ...) are common, so the vector is reasonable.
2. **Better for morphologically rich languages** — German, Russian, Turkish, Arabic benefit greatly because word forms share subwords.

FastText also handles **out-of-vocabulary words** at inference time: any word can be represented as a sum of its n-grams, even if the word itself was never seen.

### Tradeoffs

- FastText vectors are slightly worse than Word2Vec for common English words (the n-grams add noise).
- FastText vectors are much better for rare words, OOV, and morphologically rich languages.
- FastText training is slower (more vectors to learn).

## Evaluating static embeddings

| Benchmark            | What it tests                          | Metric                          |
|----------------------|----------------------------------------|---------------------------------|
| WordSim-353          | Similarity judgments (English)         | Spearman correlation with humans |
| SimLex-999           | Similarity (controls for association)  | Spearman correlation            |
| Analogy (Google)     | `a:b::c:?` analogies                   | Accuracy                        |
| BATS (Bigger Analogy)| Larger analogy set                     | Accuracy                        |
| Concept categorization | Clustering words into categories     | Purity, F1                      |
| Rare word similarity | Similarity for rare words              | Spearman correlation            |

Modern static embeddings (Word2Vec, GloVe, FastText) score ~0.6-0.7 on WordSim-353; contextual embeddings ([[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]]) score ~0.6-0.7 too — the gain from contextualization is smaller than expected for similarity tasks.

## Beyond words: item2vec, node2vec, doc2vec, user2vec

The skip-gram idea generalizes beyond words. **item2vec** runs the same algorithm with "words" as products and "sentences" as user purchase histories — used for product recommendations. **node2vec** treats graph nodes as words and random walks as sentences — used for graph embeddings (social networks, knowledge graphs). **doc2vec** (Paragraph Vector) adds a "document" vector alongside the word vectors and predicts words conditioned on both context and document — used for document similarity. **user2vec** applies the same algorithm to user actions within user sessions — used for user profiling.

The skip-gram objective is a general-purpose tool for learning embeddings of discrete entities from co-occurrence data. This is why it appears in so many domains.

## Worked example (gensim)

The gensim library implements all three algorithms. The first block trains Word2Vec and FastText and loads pre-trained GloVe vectors via `glove2word2vec`:

```python
from gensim.models import Word2Vec, FastText
from gensim.scripts.glove2word2vec import glove2word2vec
from gensim.models import KeyedVectors

# Word2Vec
w2v = Word2Vec(sentences, vector_size=100, window=5, min_count=5, workers=4, sg=1)
w2v.wv['king']  # vector for 'king'
w2v.wv.most_similar('king')

# FastText
ft = FastText(sentences, vector_size=100, window=5, min_count=5, workers=4)
ft.wv['unseenword']  # works! OOV via subwords

# GloVe (load pre-trained)
glove2word2vec('glove.6B.100d.txt', 'glove.6B.100d.w2v.txt')
glove = KeyedVectors.load_word2vec_format('glove.6B.100d.w2v.txt')
glove.most_similar('king')
```

Note the FastText OOV access (`ft.wv['unseenword']`) — Word2Vec would raise an error there, since an OOV word has no vector.

A fuller example trains a skip-gram model, runs the analogy query, and evaluates on WordSim-353 with a Spearman correlation:

```python
from gensim.models import Word2Vec
from gensim.scripts.glove2word2vec import glove2word2vec
from scipy.stats import spearmanr

# Train Word2Vec on a corpus
sentences = [
    ["the", "cat", "sat", "on", "the", "mat"],
    ["the", "dog", "sat", "on", "the", "rug"],
    # ... many more sentences ...
]
model = Word2Vec(
    sentences,
    vector_size=100,      # Embedding dim
    window=5,             # Context window
    min_count=5,          # Ignore words with freq < 5
    workers=4,            # Parallel threads
    sg=1,                 # 1 = skip-gram, 0 = CBOW
    negative=10,          # Number of negative samples
    epochs=5,
)

# Use the model
print(model.wv['king'])                  # Vector for 'king'
print(model.wv.most_similar('king'))      # Most similar words

# Analogy: king - man + woman = ?
result = model.wv.most_similar(positive=['king', 'woman'], negative=['man'])
print(f"king - man + woman = {result[0]}")  # Should be 'queen'

# Evaluate on WordSim-353
import pandas as pd
wordsim = pd.read_csv('wordsim353.csv', header=None, names=['word1', 'word2', 'human_score'])
model_scores = []
for _, row in wordsim.iterrows():
    if row['word1'] in model.wv and row['word2'] in model.wv:
        sim = model.wv.similarity(row['word1'], row['word2'])
        model_scores.append(sim)
    else:
        model_scores.append(None)

valid = [(h, m) for h, m in zip(wordsim['human_score'], model_scores) if m is not None]
rho, _ = spearmanr([h for h, _ in valid], [m for _, m in valid])
print(f"WordSim-353 Spearman correlation: {rho:.4f}")  # ~0.6-0.7 for a good model
```

The tokenization used to build `sentences` must match the tokenization behind any pre-trained vectors — [[Tokenization Overview]] is the pre-embedding step that determines this.

## Production implications

Pre-trained vectors are widely available (GloVe: 6B / 42B / 840B tokens; Word2Vec: Google News 300d; FastText: 157 languages) — use these rather than training from scratch. Vector size matters: 100–300 dimensions is the sweet spot, since larger vectors capture more but cost more to store and search. For OOV handling, if your domain has rare or novel words, prefer FastText or a modern contextual embedder. And for modern RAG, use contextual embedders (BGE, E5, GTE, OpenAI); static embeddings are mostly a baseline now.

## Common pitfalls and failure modes

Most practical failures with static embeddings come from mismatches between your pipeline and the one used to produce the vectors. The classic pitfalls:

- **Lowercasing** — most pre-trained vectors are lowercased. Match this when encoding.
- **Tokenization mismatch** — pre-trained vectors were tokenized a specific way. If you split differently, you'll have OOV.
- **Comparing across models** — Word2Vec, GloVe, FastText vectors live in different spaces. Don't compute similarity across them.
- **Using static embeddings for context-dependent tasks** — for word sense disambiguation, contextual embeddings are essential.

The same failures in debugging-table form:

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| OOV words return errors | Word not in vocab | Use FastText (handles OOV via subwords); or fall back to character n-grams |
| Comparing across models | Different embedding spaces | Don't compute similarity across Word2Vec and GloVe — they live in different spaces |
| Lowercasing mismatch | Pre-trained vectors are lowercased | Match the preprocessing; lowercase your text |
| Tokenization mismatch | Pre-trained vectors expect specific tokenization | Use the same tokenizer as the pre-trained vectors |
| Similarity is wrong | Using dot product instead of cosine similarity | Normalize embeddings; use cosine similarity (dot product of normalized vectors) |

## Why this matters

Historically, Word2Vec kicked off the embedding revolution in 2013 — the idea that you could learn useful representations from unlabeled text underpins all of modern NLP. Static embeddings are still useful for retrieval, recommender systems, and baselines: they are cheap to compute, easy to deploy, and their vectors can be stored and searched in vector memory backends. The "vector arithmetic" insight extends beyond words — item2vec, node2vec, doc2vec, and user2vec all apply the same skip-gram idea to different domains. Modern embedding models (BGE, E5, OpenAI embeddings) are the descendants — they produce contextual embeddings of whole sentences and documents, but the underlying idea (learn vectors from co-occurrence) is the same.

## Further reading

- Mikolov et al. (2013), *Efficient Estimation of Word Representations in Vector Space*.
- Mikolov et al. (2013), *Distributed Representations of Words and Phrases and their Compositionality* (negative sampling).
- Pennington et al. (2014), *GloVe: Global Vectors for Word Representation*.
- Bojanowski et al. (2017), *Enriching Word Vectors with Subword Information* (FastText).

## Interview questions

1. **Explain the skip-gram negative sampling loss.**
   For a (center, context) pair $(w, c)$ with $K$ negative samples: $\mathcal{L} = -\log \sigma(v_c \cdot v_w) - \sum_{i=1}^{K} \log \sigma(-v_{w_i} \cdot v_w)$. The first term maximizes the dot product of the true pair; the second minimizes the dot product of $K$ random (center, negative) pairs, where negatives are sampled from $P_n(w) \propto \text{count}(w)^{3/4}$. The 3/4 power downweights frequent words, giving rare words more chance to be sampled as negatives. This avoids the expensive full-vocabulary softmax and makes Word2Vec fast.

2. **Why does the analogy property ($\vec{king} - \vec{man} + \vec{woman} \approx \vec{queen}$) work?**
   Word2Vec and GloVe learn embeddings where the vector difference between related words captures relationships. If $\vec{king} - \vec{queen} \approx \vec{man} - \vec{woman}$ (both differences represent the "male-female" direction), then $\vec{king} - \vec{man} + \vec{woman} \approx \vec{queen}$. This works because: (1) the embedding space has linear directions for gender, tense, country-capital, etc.; (2) translation invariance — the gender direction is roughly the same across word pairs; (3) vector arithmetic finds the point closest to $c$ translated by the $a - b$ direction. Limitations: only works for clean analogies; sensitive to preprocessing.

3. **What's the difference between Word2Vec, GloVe, and FastText?**
   **Word2Vec** (Mikolov 2013): predictive, local context. Skip-gram or CBOW. Trained online. **GloVe** (Pennington 2014): count-based, global co-occurrence matrix. Factorizes the co-occurrence matrix. Trained in batch. More reproducible (deterministic given corpus). **FastText** (Bojanowski 2017): extends Word2Vec with character n-grams. Each word is a bag of n-grams plus the whole word. Better for rare words, OOV, and morphologically rich languages. Slower to train. All three produce similar quality on common English words; FastText wins for rare/OOV/morphological cases; GloVe is most reproducible; Word2Vec is most widely implemented.

4. **How would you choose between static and contextual embeddings for a RAG system?**
   Use contextual embeddings (BGE, E5, GTE, OpenAI) for production RAG. They handle polysemy ("bank" in different contexts gets different vectors), outperform static on retrieval benchmarks by 10-20%, and are the modern default. Use static embeddings (Word2Vec, FastText) for: (1) cheap baselines; (2) recommender systems (item2vec); (3) OOV handling without a neural model; (4) keyword-based hybrid search (BM25 + static embeddings). For most modern RAG, contextual is the right choice.

5. **Why does FastText handle OOV words while Word2Vec doesn't?**
   FastText represents each word as a bag of character n-grams (e.g., `where` = `<wh, whe, her, ere, re>` + `<where>`). The word's vector is the sum of its n-gram vectors. At inference, any word — even one never seen in training — can be represented as a sum of its n-grams, which are likely common. Word2Vec has no subword decomposition: an OOV word has no vector. This is why FastText is preferred for morphologically rich languages (German, Russian, Turkish, Arabic) where word forms share subwords.

6. **What is item2vec and how does it relate to Word2Vec?**
   Item2vec applies the skip-gram algorithm to products instead of words. "Words" are products, "sentences" are user purchase histories. The model learns product embeddings where products appearing in similar contexts (bought by similar users) have similar vectors. Used for product recommendations, similarity-based search, and clustering. The same idea generalizes to node2vec (graph nodes via random walks), doc2vec (documents), and user2vec (user actions). The skip-gram objective is a general-purpose tool for learning embeddings of discrete entities from co-occurrence data.

## See also

- [[NLP and Language Models MOC]]
- [[Contextual Embeddings ELMo to BERT]] — the successor
- [[Tokenization Overview]] — the pre-embedding step
- [[BM25]] — hybrid keyword + embedding retrieval
- [[BPE]]
- [[WordPiece]]
- [[SentencePiece]]
- [[Embedding Layer]]
- [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]] — the contextual embedding revolution
- [[Agents and Tooling MOC]]
- [[Cosine Similarity]]
- [[Vectors]]
