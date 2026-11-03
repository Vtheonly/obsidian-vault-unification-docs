---
title: DataFrames
type: concept
aliases:
  - DataFrame
  - DataFrames - Deep Dive and Operations
  - pandas DataFrame
tags:
  - python
  - pandas
  - dataframes
  - data-manipulation
  - data-cleaning
  - groupby
  - data-analysis
sources:
  - "03. DataFrames - Deep Dive and Operations"
created_index: 14
---

A **DataFrame** is a table of data consisting of rows and columns, and it is the primary tool for data manipulation in Python. It is the two-dimensional, labeled structure that [[Pandas]] provides on top of [[NumPy]], and nearly every data project spends most of its time inside one. This note is a working tour of the DataFrame lifecycle: creating and loading, inspecting, selecting with `loc` and `iloc`, filtering, cleaning, aggregating with `groupby`, and merging with other DataFrames.

## Creating and loading

The two everyday entry points are constructing a DataFrame from a dictionary of lists and reading one from a CSV file:

```python
# From Dictionary of Lists
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'City': ['NY', 'LA', 'SF']
}
df = pd.DataFrame(data)

# From CSV (Most common)
df = pd.read_csv('data.csv')
```

With the dictionary form, each key becomes a column name and each list supplies that column's values, so the DataFrame comes out already labeled. The CSV form is the most common in practice, because most data arrives as files on disk.

## Inspecting

Before manipulating anything, inspect. Five calls cover the first look at a new dataset:

- `df.head(n)`: view first n rows.
- `df.tail(n)`: view last n rows.
- `df.info()`: summary of columns, non-null counts, and data types (Dtypes).
- `df.describe()`: statistical summary (mean, min, max, quartiles) for numeric columns.
- `df.shape`: tuple (rows, columns).

`head` and `tail` show the top and bottom of the table, `info` reveals the schema — columns, non-null counts and dtypes — which is where missing values first show themselves, `describe` gives the statistical picture of the numeric columns, and `shape` states the raw size as a `(rows, columns)` tuple.

## Selecting with loc and iloc

This is the most common source of confusion for beginners. The two accessors look alike but select on different things:

| Method | Full Name | Description | Syntax Example |
| :--- | :--- | :--- | :--- |
| **`.loc`** | Location | Select by **Label** (Name). Inclusive bounds. | `df.loc[0:5, 'Age']` |
| **`.iloc`** | Integer Location | Select by **Position** (Index). Exclusive upper bound. | `df.iloc[0:5, 1]` |

`.loc` selects by label — row and column names — and its slice bounds are inclusive, so `df.loc[0:5, 'Age']` includes row label 5. `.iloc` selects by integer position and follows Python's slicing convention with an exclusive upper bound, so `df.iloc[0:5, 1]` returns the first five rows (positions 0 through 4) of the second column. When row labels happen to be integers, the same numbers give different answers through the two accessors — which is precisely the trap.

## Filtering (conditional selection)

Syntax: `df[condition]`

```python
# Select rows where Age is greater than 30
adults = df[df['Age'] > 30]

# Multiple conditions (Use & for AND, | for OR)
target = df[(df['Age'] > 25) & (df['City'] == 'NY')]
```

A condition on a column evaluates to a boolean Series, and indexing the DataFrame with it keeps the rows where that Series is `True`. Multiple conditions combine with `&` for AND and `|` for OR, with each condition wrapped in its own parentheses.

## Data cleaning methods

Four methods handle the standard cleaning passes:

- `df.dropna()`: drop rows with missing values (NaN).
- `df.fillna(value)`: replace NaN with a specific value (e.g., mean or 0).
- `df.drop_duplicates()`: remove duplicate rows.
- `df.astype()`: convert data types (e.g., string to float).

`dropna` and `fillna` are the two answers to missing values — delete the row, or substitute a specific value such as the column mean or 0 — and the wider strategies for dealing with gaps are treated in [[Missing Data and Imputation]]. `drop_duplicates` removes repeated rows (the broader problem of catching them is covered in [[Duplicate Detection and Record Linkage]]), and `astype` rewrites column types, for example string to float.

## Aggregation and grouping

The "Split-Apply-Combine" strategy.

```python
# Group by City and calculate mean Age
df.groupby('City')['Age'].mean()

# Multiple Aggregations
df.groupby('City').agg({
    'Age': ['mean', 'max'],
    'Name': 'count'
})
```

`groupby` implements split-apply-combine: it splits the rows into groups by a key, applies a function to each group, and combines the results into a new table indexed by the key. The simple form computes one statistic per group — the mean `Age` for each `City`. The `.agg` form applies several aggregations at once, specified per column: the mean and max of `Age` and the count of `Name` for each city.

## Merging

Two tools combine DataFrames:

- `pd.concat([df1, df2])`: stack DataFrames on top of each other (vertically).
- `pd.merge(df1, df2, on='key', how='inner')`: join DataFrames (horizontally) like SQL (inner, outer, left, right).

`concat` stacks tables vertically, one on top of the other, while `merge` performs a relational join on a shared key, with the familiar SQL flavors — inner, outer, left and right — selected through the `how` argument.

## See also

- [[Python Language Overview]]
- [[Pandas]]
- [[NumPy]]
- [[Missing Data and Imputation]]
- [[Duplicate Detection and Record Linkage]]
- [[Exercise - Temperature and Grade Analysis]]
- [[Exercise - Medical Dataset Pipeline]]
