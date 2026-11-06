---
title: Missing Data and Imputation
type: concept
aliases:
  - Handling Missing Data and Imputation Strategies
  - Missing Data Handling
  - Missing Values
  - Imputation
tags:
  - python
  - data-cleaning
  - preprocessing
  - missing-data
  - imputation
  - pandas
sources:
  - "01. Handling Missing Data and Imputation Strategies"
created_index: 5
---

Real-world data is messy, and one of the most common issues is **missing values** — `NaN`, `null`, `None`. Most machine learning algorithms (Scikit-Learn's Linear Regression is the canonical example) cannot handle missing values and will simply crash rather than train. The goal of any missing-data strategy is to replace the gaps with statistically sound estimates, or remove the affected records entirely, without biasing the dataset — and which strategy is right depends on *why* the data is missing in the first place.

## Identifying missing data

Before fixing it, you must find it. Pandas exposes a Boolean mask of missingness and per-column counts, and combined with Seaborn it can draw a visual heatmap that makes the pattern of missingness jump out:

```python
import pandas as pd
import seaborn as sns

df = pd.read_csv('data.csv')

# 1. Check for nulls (Boolean mask)
print(df.isnull())

# 2. Count missing values per column
print(df.isnull().sum())

# 3. Visual Heatmap of missingness
sns.heatmap(df.isnull(), cbar=False)
```

## Types of missing data

Understanding *why* data is missing dictates *how* to fix it. Statisticians distinguish three mechanisms, each with a different safe response.

### MCAR — missing completely at random

There is no pattern to the missingness at all — a sensor battery died randomly, for instance. Because the gaps carry no information, it is safe to drop the affected rows.

### MAR — missing at random

The missingness depends on *observed* data: men are less likely to report their depression score, but gender *is* recorded. Imputation is preferred here, because the observed features can stand in for the missing value.

### MNAR — missing not at random

The missingness depends on the *unobserved value itself* — people with very high incomes skip the "Income" question. This is the dangerous case: simple fixes are biased by construction, and it requires specialized modeling.

## Deletion

Deletion is best when the missing data is MCAR and accounts for less than 5% of the total. **Listwise deletion** drops entire rows that contain any missing value:

```python
df.dropna(axis=0, inplace=True)
```

**Pairwise deletion** works at the column level, or trims rows with too many gaps:

```python
df.dropna(axis=1, inplace=True) # Drop column if any value is missing
df.dropna(thresh=5)             # Drop row if it has < 5 non-null values
```

## Simple imputation

Simple imputation replaces missing values with a summary statistic of the observed ones. The **mean** is a good fill for normally distributed data:

```python
df['Age'].fillna(df['Age'].mean(), inplace=True)
```

The **median** is robust to outliers and the best general choice:

```python
df['Salary'].fillna(df['Salary'].median(), inplace=True)
```

The **mode** is the option for categorical data:

```python
df['City'].fillna(df['City'].mode()[0], inplace=True)
```

A fourth option is **constant** imputation — filling the gaps with a specific value such as 0 or "Unknown".

## Advanced imputation

Advanced methods use algorithms to predict the missing value based on the other features. The **KNN imputer** finds the 'k' most similar rows and averages their values:

```python
from sklearn.impute import KNNImputer
imputer = KNNImputer(n_neighbors=5)
df_filled = imputer.fit_transform(df)
```

The **iterative imputer (MICE)** goes further and models each feature with missing values as a function of the other features. For **time series**, interpolation fills the gaps based on time trends:

```python
df['Sales'].interpolate(method='linear', inplace=True)
```

## See also

- [[Python Language Overview]]
- [[Feature Scaling and Normalization]]
- [[Categorical Encoding and Text Normalization]]
- [[Outlier Detection and Treatment]]
- [[Duplicate Detection and Record Linkage]]
- [[Exercise - Medical Dataset Pipeline]]
- [[Pandas]]
- [[Seaborn]]
- [[NumPy]]
- [[04 - Machine Learning/Regression/Linear Regression|Linear Regression]]
- [[K-Nearest Neighbors]]
- [[Gaussian Distribution]]
