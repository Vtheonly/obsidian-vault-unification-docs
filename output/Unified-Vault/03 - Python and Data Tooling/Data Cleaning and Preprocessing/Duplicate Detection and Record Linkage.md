---
title: Duplicate Detection and Record Linkage
type: concept
aliases:
  - "Duplicate Detection"
  - "Record Linkage"
  - "Fuzzy Matching"
tags:
  - data-cleaning
  - duplicates
  - record-linkage
  - fuzzy-matching
  - levenshtein-distance
  - soundex
  - pandas
  - data-quality
sources:
  - "02. Duplicate Detection and Record Linkage"
created_index: 2
---

Duplicate records inflate dataset size, bias statistical results, and lead to data leakage in ML models — for example, the same record ending up in both the Train and Test sets. Removing them is a three-level problem: **exact duplicates** (rows where every single column is identical), **partial duplicates** (rows identical except for a unique ID or timestamp), and **fuzzy matches** (the same entity recorded with typos and spelling variations). This note covers the pandas `duplicated()` / `drop_duplicates()` tooling for the first two levels, and fuzzy matching — Levenshtein distance and phonetic algorithms — for the third.

## Why duplicates matter

Duplicates are not a harmless formatting nuisance. They **inflate dataset size**, so repeated rows weigh more than they should in any count or average; they **bias statistical results**, because summaries computed over duplicated rows no longer describe distinct real-world entities; and they cause **data leakage** in ML models when the same record appears in both the Train and Test sets — the model is then evaluated on data it has already seen. The train/test discipline that leakage violates is introduced in [[Introduction to Machine Learning]], and how contamination distorts held-out evaluation is covered in [[Model Evaluation Metrics]].

## Exact duplicates

Exact duplicates are rows where every single column is identical. pandas detects them with `duplicated()`, which returns a Boolean Series marking the repeated occurrences, and removes them with `drop_duplicates()`:

```python
# 1. Check for duplicates (Returns Boolean Series)
print(df.duplicated().sum())

# 2. View duplicate rows
duplicates = df[df.duplicated()]

# 3. Drop duplicates
df.drop_duplicates(inplace=True)
```

The three steps form a safe rhythm: count the duplicates first, inspect the rows that were flagged, and only then drop them. `df.duplicated().sum()` totals the flagged rows, `df[df.duplicated()]` slices out the duplicate rows themselves so they can be reviewed before anything is deleted, and `df.drop_duplicates(inplace=True)` removes them from the DataFrame in place.

## Partial duplicates

The exact-match test misses the most common real-world case: rows that are identical *except* for a unique ID or timestamp. Two records carrying the same name, email, and phone but different ID values are duplicates for every practical purpose, yet the all-columns comparison will not flag them. The fix is to define duplication on a **subset** of columns:

```python
# Check duplicates based on specific columns
subset = ['Name', 'Email', 'Phone']
print(df.duplicated(subset=subset).sum())

# Drop, keeping the first (or last) occurrence
df.drop_duplicates(subset=subset, keep='first', inplace=True)
```

Passing `subset=['Name', 'Email', 'Phone']` restricts both detection and removal to those columns, and `keep='first'` (or `keep='last'`) decides which occurrence survives the drop.

## Fuzzy matching and record linkage

Neither exact matching nor subset matching can handle **typos and variations**: "John Smith" vs. "Jon Smith" vs. "J. Smith" are three spellings that may denote the same person. Deciding that such strings refer to the same entity is the record linkage problem, and it is solved with string-similarity calculations such as the **Levenshtein Distance**. The standard libraries are `fuzzywuzzy` and `textdistance`.

A fuzzy matcher scores a messy input against a list of known-good values and returns the best match together with a confidence:

```python
from fuzzywuzzy import process

# List of correct names
choices = ["Apple", "Banana", "Orange"]

# Messy input
process.extractOne("Aplle", choices)
# Output: ('Apple', 91) -> 91% match confidence
```

Here `process.extractOne("Aplle", choices)` returns `('Apple', 91)`: the closest candidate and its 91% match confidence.

Edit distance is not the only usable signal — phonetic matching attacks the same problem from the sound side:

> [!TIP] **Soundex**
> Phonetic algorithms (like Soundex or Metaphone) index words by how they *sound*. Useful for matching names with different spellings (e.g., "Smith" vs "Smyth").

## See also

- [[Python Language Overview]]
- [[Missing Data and Imputation]]
- [[Outlier Detection and Treatment]]
- [[Feature Scaling and Normalization]]
- [[Categorical Encoding and Text Normalization]]
- [[Pandas]]
- [[DataFrames]]
- [[Introduction to Machine Learning]]
- [[Model Evaluation Metrics]]
- [[Exercise - Medical Dataset Pipeline]]
