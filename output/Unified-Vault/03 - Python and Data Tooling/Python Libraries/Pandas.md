---
title: Pandas
type: concept
aliases:
  - Python Data Analysis Library
  - Pandas - Data Manipulation and Series
  - pandas Series
tags:
  - python
  - pandas
  - series
  - labeled-data
  - data-manipulation
  - data-analysis
sources:
  - "02. Pandas - Data Manipulation and Series"
created_index: 18
---

**Pandas** (Python Data Analysis Library) builds on top of [[NumPy]] to provide high-level data structures and analysis tools. Its defining move is to introduce the concept of **labels** (indices) to data, making it relational: operations line up values by name rather than by raw position. This note covers the two core structures and the Series — the 1-dimensional labeled array — in depth; the DataFrame gets its own full working treatment in [[DataFrames]].

## The two core structures

1. **Series:** a 1-dimensional labeled array (like a single column in Excel).
2. **DataFrame:** a 2-dimensional labeled data structure (like a whole Excel sheet).

Everything in pandas is one of these two shapes: a single labeled column, or a whole labeled table. The Excel analogy is exact enough to navigate by — a Series is one column of a sheet, a DataFrame is the sheet itself.

## The Series

A Series holds data of any type (integers, strings, floating point numbers, Python objects, etc.). What distinguishes it from a plain sequence is the index attached to the values.

### Creating a Series

```python
import pandas as pd

# From List
s = pd.Series([10, 20, 30])

# From List with Custom Index
s = pd.Series([10, 20, 30], index=['a', 'b', 'c'])

# From Dictionary
data = {'a': 10, 'b': 20, 'c': 30}
s = pd.Series(data)
```

From a plain list, the Series gets a default integer index. Passing `index=` attaches custom labels to the values, and building from a [[Dictionaries|dictionary]] does the same thing automatically — the keys become the index and the values become the data.

### Series components

- **Values:** the underlying NumPy array. Accessed via `s.values`.
- **Index:** the labels. Accessed via `s.index`.

The split matters because the values are just an ordinary NumPy array — everything from [[NumPy]] applies to them — while the index is the layer pandas adds on top.

### Vectorized operations and alignment

Pandas is powerful because it aligns data by **index**, not by position.

```python
s1 = pd.Series([1, 2], index=['a', 'b'])
s2 = pd.Series([10, 20], index=['b', 'a']) # Note order flip

# Pandas matches 'a' to 'a' and 'b' to 'b'
print(s1 + s2)
# Output:
# a    21
# b    12
# dtype: int64
```

Both Series carry the labels `a` and `b`, but in flipped order. Pandas matches `a` to `a` and `b` to `b`, so the result carries `21` under `a` and `12` under `b` — the labeled pairs are added regardless of the order in which each Series stores them.

> [!WARNING] **Missing Data**
> If indices don't match during an operation, Pandas introduces `NaN` (Not a Number) to indicate missing data.

Alignment is therefore double-edged: it protects arithmetic from order mistakes, but any label present in one operand and absent in the other shows up as `NaN` rather than an error — the entry point to the missing-data problems covered in [[Missing Data and Imputation]].

## See also

- [[Python Language Overview]]
- [[NumPy]]
- [[DataFrames]]
- [[Dictionaries]]
- [[Missing Data and Imputation]]
- [[Exercise - Temperature and Grade Analysis]]
