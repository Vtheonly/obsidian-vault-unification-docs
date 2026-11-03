---
title: Outlier Detection and Treatment
type: concept
aliases:
  - "Outlier Detection and Treatment Methods"
  - "Outlier Detection"
  - "Outlier Treatment"
tags:
  - data-cleaning
  - outliers
  - z-score
  - iqr
  - winsorization
  - boxplot
  - pandas
  - seaborn
  - scipy
sources:
  - "03. Outlier Detection and Treatment Methods"
created_index: 6
---

An **outlier** is a data point that differs significantly from the other observations in a dataset. Outliers arise from measurement error, data entry error, or genuine anomalies such as fraud, and they are never purely cosmetic: an outlier skews the mean and the standard deviation, and it destroys linear regression models. This note walks through the standard workflow — spotting outliers visually with boxplots and scatterplots, confirming them statistically with the z-score and interquartile range (IQR) rules, and then choosing a treatment: drop, cap (Winsorize), or transform.

## What is an outlier

An outlier is a single observation that differs significantly from the rest of the data. The first question to ask about one is where it came from, because the cause determines what should happen to it. Three causes cover most cases: **measurement error** (the value was recorded incorrectly), **data entry error** (the value was mistyped at input), and a **genuine anomaly** such as fraud. The drop strategy below is recommended only when the point is an error or otherwise irrelevant, which implies that genuine anomalies are better served by a treatment that preserves the information they carry.

The impact on downstream analysis is the same whatever the cause: outliers **skew the mean and the standard deviation**, and they **destroy linear regression models**. Outlier handling is therefore a core data-cleaning step, sitting alongside [[Missing Data and Imputation]] and [[Duplicate Detection and Record Linkage]] in the preparation pipeline, before any modeling on the order of [[04 - Machine Learning/Regression/Linear Regression|Linear Regression]] is trusted.

## Visual detection

Before computing anything, plot the data: outliers are usually visible to the eye.

### Boxplots

In a boxplot, the points that fall outside the whiskers are the outliers. A single line of Seaborn is enough to inspect a suspicious column:

```python
sns.boxplot(x=df['Salary'])
```

### Scatterplots

In a scatterplot, outliers appear as points far away from the main cluster. The two plots complement each other: the boxplot judges a value against the distribution of a single column such as `Salary`, while the scatterplot exposes points that sit apart from the cloud the rest of the data forms.

## Statistical detection

Visual inspection flags candidates; statistical rules make the decision explicit and reproducible. The two standard rules are the z-score test and the IQR fences.

### Z-score

The z-score measures how many standard deviations a point is from the mean. The rule is simple: if $|Z| > 3$, the point is an outlier. The rule rests on an assumption — the data is normally distributed (a bell curve; see [[Gaussian Distribution]]).

```python
from scipy import stats
import numpy as np

z_scores = np.abs(stats.zscore(df['Salary']))
# Filter out rows with Z-score > 3
df_clean = df[(z_scores < 3)]
```

Taking the absolute value first lets a single comparison cover both tails: `df_clean` keeps exactly the rows whose $|Z| < 3$.

### Interquartile range

The IQR method is the robust alternative: it is robust to non-normal distributions, and it is the rule used in boxplots. The procedure runs:

1. Calculate **Q1** (25th percentile) and **Q3** (75th percentile).
2. Calculate **IQR = Q3 - Q1**.
3. Define bounds:
   - Lower Bound = $Q1 - 1.5 \times IQR$
   - Upper Bound = $Q3 + 1.5 \times IQR$
4. Any value outside these bounds is an outlier.

```python
Q1 = df['Age'].quantile(0.25)
Q3 = df['Age'].quantile(0.75)
IQR = Q3 - Q1

# Filter
df_clean = df[~((df['Age'] < (Q1 - 1.5 * IQR)) | (df['Age'] > (Q3 + 1.5 * IQR)))]
```

The inner expression marks rows that fall below the lower bound or above the upper bound; negating it with `~` keeps the values inside the fences.

### Choosing between the rules

| Aspect | Z-score | IQR |
|---|---|---|
| Decision rule | Flag if $\|Z\| > 3$ | Flag if outside $Q1 - 1.5 \times IQR$ and $Q3 + 1.5 \times IQR$ |
| Assumption | Data is normally distributed (bell curve) | None — robust to non-normal distributions |
| Where it appears | Explicit statistical test | The whisker rule behind boxplots |

The z-score inherits its 3-standard-deviation cutoff from the normal distribution, so it is the natural choice when that assumption holds; the IQR rule stays reliable on non-normal data, and it is what a boxplot's whiskers are already displaying.

## Treatment strategies

Detection only labels points; treatment decides their fate. Three strategies are standard, and they trade off how much of the original information survives.

### Drop

Remove the outlying rows from the dataset. This is the right choice when the value is an error or the record is irrelevant — there is nothing worth keeping in a mistyped entry. Both detection snippets above already implement dropping: each builds `df_clean` by filtering the DataFrame down to the rows that pass the rule.

### Cap (Winsorization)

Capping keeps the row but limits the value: replace values above the 99th percentile with the 99th percentile value.

```python
upper_limit = df['Age'].quantile(0.99)
df.loc[df['Age'] > upper_limit, 'Age'] = upper_limit
```

The record survives with all of its other columns intact; only the extreme magnitude is trimmed back to the percentile ceiling.

### Transform

A transformation compresses the range of the column, reducing the impact of large values: apply a log or square-root transform.

```python
df['Log_Income'] = np.log(df['Income'])
```

No rows are removed — the transformed column simply pulls extreme values closer to the bulk of the data. Range-compressing column operations of this kind are a close cousin of the techniques covered in [[Feature Scaling and Normalization]].

## See also

- [[Python Language Overview]]
- [[Missing Data and Imputation]]
- [[Duplicate Detection and Record Linkage]]
- [[Feature Scaling and Normalization]]
- [[Categorical Encoding and Text Normalization]]
- [[Pandas]]
- [[DataFrames]]
- [[Seaborn]]
- [[NumPy]]
- [[Gaussian Distribution]]
- [[04 - Machine Learning/Regression/Linear Regression|Linear Regression]]
