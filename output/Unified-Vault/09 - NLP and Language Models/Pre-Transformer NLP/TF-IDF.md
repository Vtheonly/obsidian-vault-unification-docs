---
title: TF-IDF
type: concept
aliases:
  - TF-IDF
  - TFIDF
  - Term Frequency Inverse Document Frequency
tags:
  - nlp
  - information-retrieval
  - tf-idf
  - vector-space-model
  - classical-ir
sources:
  - "09 - TF-IDF"
created_index: 7
---

TF-IDF (Term Frequency-Inverse Document Frequency) scores how important a word is to a document in a corpus: common words get low scores, rare words get high scores. It is the foundation of classical information retrieval — the vector space model that powered search engines before BERT — and still the right baseline for keyword search. This note covers the formula and its variants, why it works, its use in retrieval, comparisons to [[BM25]] and embeddings, limitations, production patterns, and worked examples.

> [!info] TL;DR
> TF-IDF scores a term's importance to a document as (how often it appears in this document) × (how rare it is across the corpus). Common words get low scores; rare words get high scores. It is the foundation of classical IR and still the right baseline for keyword search.

## The formula

For term $t$ in document $d$ in corpus $D$:

$$
\text{tf-idf}(t, d, D) = \text{tf}(t, d) \cdot \text{idf}(t, D)
$$

The product of two factors: how often the term appears in this document (TF), and how rare the term is across the corpus (IDF).

### Term frequency

TF measures how often $t$ appears in $d$. Several variants exist:

- **Raw count**: $\text{count}(t, d)$
- **Normalized**: $\text{count}(t, d) / |d|$ (term frequency divided by document length)
- **Log-scaled**: $1 + \log(\text{count}(t, d))$ (most common; dampens the effect of very frequent terms)
- **Augmented**: $0.5 + 0.5 \cdot \frac{\text{count}(t, d)}{\max_{t'} \text{count}(t', d)}$ (prevents bias toward longer documents)

The log-scaled variant is standard because it dampens the effect of terms that appear many times: a term appearing 100 times isn't 100× more important than one appearing once — with log scaling it's about 7× more important ($1 + \log(100) \approx 5.6$).

### Inverse document frequency

IDF measures how rare $t$ is across the corpus:

$$
\text{idf}(t, D) = \log \frac{|D|}{|\{d \in D : t \in d\}|}
$$

Common words ("the", "and") appear in most documents, so they get low IDF and low TF-IDF. Rare words ("quokka", "topotear") appear in few documents, so they get high IDF and high TF-IDF. A constant-smoothed variant — the sklearn default — avoids division by zero and overly harsh low IDF:

$$\text{idf}(t, D) = \log \frac{1 + |D|}{1 + |\{d : t \in d\}|} + 1$$

The smoothing prevents two issues. First, division by zero: a term can appear in no documents (this shouldn't happen for query terms, but it can for unknown terms). Second, IDF = 0 for universal terms: without the +1, terms appearing in all documents get IDF = 0, removing them entirely from scoring.

### Why log

The logarithm dampens the effect of extreme values. Without log, a term in 1 document out of 1M has IDF = 1,000,000, and a term in 100 documents has IDF = 10,000 — the rare term dominates retrieval, even if it's not very relevant. With log, the rare term has IDF = $\log(1M) = 13.8$ and the common term has $\log(10K) = 9.2$: the ratio is more reasonable (1.5×, not 100×).

## Why it works

A word that appears in many documents isn't useful for distinguishing them; a word that appears in only a few documents is highly informative for those documents. TF-IDF combines the two signals: TF measures how central the term is to this document, and IDF measures how distinctive the term is across the corpus. The product gives a score that's high for terms that are both frequent in this document and rare across the corpus — exactly the terms that best characterize this document.

### Intuition

Consider a document about "quokkas" (a small marsupial). The word "the" appears 50 times; the word "quokka" appears 10 times. Without IDF, "the" would score higher. But "the" appears in almost every document, so it has low IDF, while "quokka" appears in few documents and has high IDF. The product makes "quokka" the dominant term — which is correct.

## Use in information retrieval

To rank documents for a query $q$: compute the TF-IDF vector for $q$, compute TF-IDF vectors for all documents (precomputed), and rank by cosine similarity to $q$. This is **vector space model retrieval** — classical IR (Salton et al. 1975). Before BERT, this was how search engines worked.

### The vector space model

Each document is represented as a vector in $\mathbb{R}^V$, where $V$ is the vocabulary size; entry $i$ is the TF-IDF score of term $i$ in the document, and most entries are 0 (sparse vector). Queries are also represented as TF-IDF vectors, and retrieval is cosine similarity between query and document vectors:

$$
\text{sim}(q, d) = \cos(\mathbf{q}, \mathbf{d}) = \frac{\mathbf{q} \cdot \mathbf{d}}{\|\mathbf{q}\| \|\mathbf{d}\|}
$$

Cosine similarity normalizes for document length — a long document with many terms doesn't get an unfair advantage.

### Why cosine similarity

Three properties make cosine the standard choice. Length invariance: a 1000-word document and a 100-word document with the same term proportions get the same similarity. Bounded range: cosine lives in $[-1, 1]$, easy to interpret (though TF-IDF vectors are non-negative, so the range is in practice $[0, 1]$). Efficiency: it can be computed via a dot product if the vectors are normalized.

### The inverted index

For large corpora, computing cosine similarity against every document is too slow. The **inverted index** is the data structure that makes TF-IDF retrieval fast: it maps each term to the list of documents containing it:

```
"quokka" → [doc_42, doc_178, doc_902]
"marsupial" → [doc_42, doc_55, doc_178, doc_902, ...]
```

For a query, we only need to look at documents containing at least one query term — much faster than scanning all documents. Elasticsearch, OpenSearch, and Lucene are built on inverted indexes.

## Worked example: retrieval with scikit-learn

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

docs = [
    "the cat sat on the mat",
    "the dog ran in the park",
    "cats and dogs are common pets",
]
query = "cat on mat"

vectorizer = TfidfVectorizer(lowercase=True, stop_words='english')
doc_vectors = vectorizer.fit_transform(docs)
query_vector = vectorizer.transform([query])

sims = cosine_similarity(query_vector, doc_vectors).flatten()
print(sims)  # highest for docs[0]

# Inspect the vocabulary
print(vectorizer.vocabulary_)  # {'cat': ..., 'sat': ..., 'mat': ..., ...}

# Inspect the IDF values
print(vectorizer.idf_)  # [1.69, 1.69, 1.69, ...]
```

### Manual computation

The same arithmetic by hand, for the corpus above (3 documents). Term "cat": its TF in doc_0 is $\log(1) + 1 = 1$ (it appears once). Its TF in doc_2 is also $\log(1) + 1 = 1$ (it appears once, as "cats" — but if we stem, it's the same term). Its IDF is $\log(3/2) \approx 0.41$ (it appears in 2 of 3 docs), so its TF-IDF in doc_0 is $1 \times 0.41 = 0.41$. Term "mat": its TF in doc_0 is 1; its IDF is $\log(3/1) \approx 1.10$ (it appears in 1 of 3 docs), so its TF-IDF in doc_0 is $1 \times 1.10 = 1.10$. "Mat" therefore contributes more to doc_0's score than "cat" — because "mat" is rarer across the corpus.

## Comparison to BM25

[[BM25]] is the successor to TF-IDF, with two improvements. Term saturation: TF-IDF's TF grows linearly (or log-linearly) with count, while BM25's TF saturates — beyond a point, more occurrences don't help. This matches the intuition that a term appearing 100 times isn't 100× more relevant than one appearing once. Length normalization: TF-IDF doesn't explicitly normalize for document length (only via cosine similarity), while BM25 has a length normalization parameter that penalizes long documents. The BM25 formula:

$$
\text{BM25}(t, d, D) = \text{idf}(t, D) \cdot \frac{\text{tf}(t, d) \cdot (k_1 + 1)}{\text{tf}(t, d) + k_1 \cdot (1 - b + b \cdot |d| / \text{avgdl})}
$$

where $k_1$ (typically 1.2) controls saturation and $b$ (typically 0.75) controls length normalization.

When to use which: BM25 for production search (better quality); TF-IDF for teaching and understanding (simpler). Both are "classical IR" — neither has semantic understanding.

## Comparison to embeddings

| Aspect | TF-IDF | Embeddings (BGE, E5, OpenAI) |
|--------|--------|------------------------------|
| Semantic understanding | None | Yes |
| Word order | Ignored | Captured (for contextual embeddings) |
| Vocabulary | Fixed at training | Subword/byte-level |
| Sparse vs. dense | Sparse (100K+ dim) | Dense (768-1536 dim) |
| Compute | Cheap (lookups) | Expensive (model forward pass) |
| Interpretable | Yes (which terms matched) | No (black box) |
| Best for | Keyword queries | Semantic queries |
| Hybrid | Combine with vector | Combine with BM25 |

### When TF-IDF or BM25 beats embeddings

TF-IDF and BM25 win on keyword queries like "error code ERR_4093", where the exact match matters and embeddings may miss it. They win on rare terms like "quokka", which embeddings may never have seen, while TF-IDF handles it naturally. They win on code search, where variable names and function names demand exact matches. They win in legal and medical settings, where the terminology is precise and synonyms are dangerous. And they win as a cheap baseline, when you can't afford embedding model inference.

### When embeddings beat TF-IDF

Embeddings win on semantic queries: "how do I configure auth?" has no exact keywords, but a conceptual match. They win on paraphrased queries: "user login" vs. "user sign in" — embeddings capture the equivalence. They win on cross-lingual queries: a query in English against documents in Chinese is handled by multilingual embeddings. And they win on conceptual search: "things related to machine learning" is exactly the kind of query where embeddings capture concepts that keyword matching cannot.

### Hybrid search

The best of both worlds is to combine BM25 (keyword) and vector (semantic) search, merging the results with **reciprocal rank fusion** (RRF):

$$
\text{RRF score}(d) = \sum_{r \in \text{rankings}} \frac{1}{k + \text{rank}_r(d)}
$$

where $k$ is typically 60. Hybrid search is the production standard for RAG.

## Limitations

TF-IDF has no semantic understanding: "cat" and "feline" are completely unrelated, so a query for "feline" won't match documents about "cats". It has no word order: "dog bites man" and "man bites dog" are identical, because the vector ignores syntax. Its vectors are sparse and high-dimensional: vocabulary can be 100K+, and the sparse vectors are memory-intensive for large vocabularies. It has no contextualization: the same word has the same TF-IDF regardless of context, so "bank" (river) and "bank" (financial) are treated identically. It suffers vocabulary mismatch: synonyms and related terms don't match, because the model only knows exact terms. And it requires stemming or lemmatization: "running", "runs", "ran" are different terms without preprocessing.

These limitations are exactly what embedding-based retrieval (BGE, E5, OpenAI embeddings) addresses. But TF-IDF and BM25 are still widely used because they are cheap (no model to run, just lookups), interpretable (you can see exactly which terms contributed), strong baselines (for keyword-heavy queries, BM25 often beats vector search), and hybrid-ready (combine with vector search for the best of both worlds).

## Why this matters for AI

TF-IDF is the ancestor of vector-based retrieval: understanding it makes the motivation for embeddings clear. For hybrid RAG, BM25 (TF-IDF-derived) is still essential — pure vector search misses exact-match queries. The TF-IDF vector is itself a simple embedding: pre-Word2Vec, this was how documents were embedded. For text classification with limited data, TF-IDF + logistic regression is a strong baseline. And understanding TF-IDF is essential for understanding search engines (Elasticsearch, Lucene) and classical IR.

## Production implications

For keyword search, use [[BM25]] — it's TF-IDF with better saturation and length normalization. For hybrid search (BM25 + vector), weight BM25 higher for keyword-heavy queries and vector higher for semantic queries. TF-IDF + logistic regression is a great baseline for text classification — beat it before reaching for deep learning. For real-time search, use an inverted index (Elasticsearch, OpenSearch) rather than computing TF-IDF on the fly. For multi-lingual corpora, TF-IDF works per-language — don't mix languages in one index. For streaming data, update IDF incrementally as new documents arrive. Control vocabulary size via min_df (minimum document frequency) and max_df (maximum document frequency) to filter rare and common terms. Remove stop words ("the", "and", "is") to focus on content terms. Apply stemming or lemmatization to normalize word forms ("running" → "run"). And include n-grams such as bigrams ("machine learning") to capture multi-word terms.

## Common pitfalls

Most TF-IDF failures are preprocessing and hygiene mistakes. Forgetting to lowercase makes "The" and "the" different tokens — always lowercase. Not removing stop words lets common words dominate the score. Using raw counts instead of log-scaled TF gives long documents unfairly high scores. Comparing TF-IDF across different corpora is meaningless, because IDF depends on the corpus and the values change. Not stemming leaves "running" and "runs" as different terms. Letting the vocabulary grow too large is its own problem — 1M terms means 1M-dimensional vectors, so use min_df/max_df to control it — while filtering too aggressively loses important terms. Forgetting to handle out-of-vocabulary terms means query terms not in the vocabulary silently get zero score. And skipping the inverted index for large corpora is a performance bug: naive cosine similarity is $O(N)$ per query, while an inverted index is $O(\log N)$.

## Worked example: TF-IDF for classification

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

# Load data
texts, labels = load_dataset()

# Build pipeline: TF-IDF + Logistic Regression
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(
        max_features=50000,
        ngram_range=(1, 2),  # unigrams + bigrams
        stop_words='english',
        sublinear_tf=True,  # log-scaled TF
    )),
    ('clf', LogisticRegression(C=1.0, max_iter=1000)),
])

# Train
X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2)
pipeline.fit(X_train, y_train)

# Evaluate
accuracy = pipeline.score(X_test, y_test)
print(f"Accuracy: {accuracy:.3f}")

# Inspect top features per class
feature_names = pipeline.named_steps['tfidf'].get_feature_names_out()
coefs = pipeline.named_steps['clf'].coef_
for i, class_label in enumerate(pipeline.named_steps['clf'].classes_):
    top_features = sorted(zip(feature_names, coefs[i]), key=lambda x: x[1], reverse=True)[:10]
    print(f"\nTop features for class '{class_label}':")
    for name, coef in top_features:
        print(f"  {name}: {coef:.3f}")
```

This baseline often achieves 80-90% of deep learning performance at 1% of the compute. Beat it before reaching for BERT.

## Interview questions

**What does TF-IDF measure?**
How important a term is to a document in a corpus. TF (term frequency) measures how often the term appears in this document; IDF (inverse document frequency) measures how rare the term is across the corpus. The product gives high scores to terms that are both frequent in this document and rare overall.

**Why use log for IDF?**
To dampen the effect of extreme values. Without log, a term in 1 document out of 1M would have IDF 1M, dominating retrieval. With log, the IDF is ~14, a more reasonable ratio to common terms.

**How does TF-IDF differ from BM25?**
BM25 adds term saturation (TF doesn't grow linearly forever) and length normalization (penalizes long documents). Both are classical IR; BM25 is the production standard.

**When would you use TF-IDF instead of embeddings?**
For keyword queries (exact match matters), rare terms (embeddings may not have seen them), code search (variable names), and as a cheap baseline. For hybrid RAG, combine BM25 (TF-IDF-derived) with vector search.

**What are the limitations of TF-IDF?**
No semantic understanding (synonyms don't match), no word order, sparse high-dimensional vectors, and no contextualization (the same word has the same score regardless of context). Embeddings address these, but at higher compute cost.

## Further reading

Salton et al. (1975), *A Vector Space Model for Automatic Indexing*. Manning, Raghavan, Schütze, *Introduction to Information Retrieval*, Chapter 6. Robertson & Zaragoza (2009), *The Probabilistic Relevance Framework: BM25 and Beyond*. sklearn TF-IDF docs: https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html

## See also

- [[NLP and Language Models MOC]]
- [[BM25]] — the production-standard successor
- [[Word2Vec GloVe and FastText]] — neural embeddings, the successor representation
- [[Contextual Embeddings ELMo to BERT]] — contextual embeddings
- [[N-Gram Language Models]] — pre-neural language modeling
- [[Tokenization Overview]] — the preprocessing (lowercasing, stemming, stop words) TF-IDF depends on
