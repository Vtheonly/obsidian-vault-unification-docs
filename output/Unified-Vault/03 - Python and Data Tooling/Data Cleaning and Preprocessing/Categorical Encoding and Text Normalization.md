---
title: Categorical Encoding and Text Normalization
type: concept
aliases:
  - Categorical Encoding
  - Label Encoding
  - Ordinal Encoding
  - One-Hot Encoding
  - Target Encoding
  - Mean Encoding
tags:
  - python
  - data-cleaning
  - preprocessing
  - categorical-encoding
  - one-hot-encoding
  - text-normalization
  - scikit-learn
sources:
  - "05. Categorical Encoding and Text Normalization"
created_index: 1
---

Models require numbers, not strings, so categorical values such as "Red" and "Blue" must be converted to a numerical format before any estimator will accept them. The choice of encoding depends on the cardinality of the feature and the type of model — the wrong choice can silently inject a fake ordering, explode the dimensionality, or leak the target into the features. This note walks through the full workflow: normalize the raw text first, then choose among label, one-hot, target and specialized encodings, and finish with the same fit-on-train discipline that governs [[Feature Scaling and Normalization]].

## Text normalization before encoding

Before encoding, clean the text to ensure consistency. The standard steps are:

1. **Lowercasing:** "Apple" -> "apple"
2. **Stripping whitespace:** " Apple " -> "apple"
3. **Removing special characters:** "Apple!" -> "apple"
4. **Replacing typos/synonyms:** "NYC", "N.Y.C.", "New York City" -> "new york"

```python
df['City'] = df['City'].str.lower().str.strip()
```

Without normalization, "Apple", "apple", and "Apple " would be encoded as three different categories — wasting dimensionality and splitting signal across spurious categories.

## Label and ordinal encoding

Label encoding assigns a unique integer to each category: "Low" -> 0, "Medium" -> 1, "High" -> 2. Its advantage is compactness — a single column. The cost is that the integers imply an **order** (ordinality) the model takes literally: it thinks $2 > 0$. Use it only for genuinely **ordinal** data (rankings, levels, sizes). Do **not** use it for nominal data — categories with no inherent order such as colors, cities, names — because the model will incorrectly infer an order that does not exist.

```python
from sklearn.preprocessing import LabelEncoder, OrdinalEncoder
le = LabelEncoder()
df['Encoded_Rank'] = le.fit_transform(df['Rank'])

# OrdinalEncoder is better for features (LabelEncoder is for targets):
oe = OrdinalEncoder(categories=[['Low', 'Medium', 'High']])  # specify the order
df['Encoded_Level'] = oe.fit_transform(df[['Level']])
```

Note the division of labor in that snippet: `OrdinalEncoder` is the better tool for features and lets you pin the category order explicitly, while `LabelEncoder` is designed for targets.

## One-hot encoding

One-hot encoding (OHE) creates a new binary column — a dummy variable — for *each* category:

- "Red" -> [1, 0, 0]
- "Green" -> [0, 1, 0]
- "Blue" -> [0, 0, 1]

With no implied order, OHE is a natural fit for nominal data. The drawback is the **curse of dimensionality**: if a category has 10,000 unique values (e.g., zip codes), you create 10,000 columns.

```python
# Using Pandas
df_ohe = pd.get_dummies(df, columns=['Color'], drop_first=True)
# drop_first=True removes one column to prevent multicollinearity (Dummy Variable Trap).

# Using sklearn (better for ML pipelines, handles unseen categories):
from sklearn.preprocessing import OneHotEncoder
ohe = OneHotEncoder(drop='first', sparse_output=False, handle_unknown='ignore')
encoded = ohe.fit_transform(df[['Color']])
```

**`handle_unknown='ignore'`** is critical: at test time you may encounter a category not seen in training. Without this flag, the encoder crashes; with it, unknown categories produce all-zeros.

## Target encoding (mean encoding)

Target encoding replaces a category with the **mean of the target variable** for that category — "Seattle" becomes 0.65 if 65% of Seattle samples in training are positive. It shines on high-cardinality categorical features (city names, zip codes, user IDs) where OHE would create too many columns. The risk is **overfitting**: the encoding must be calculated on training data only, using cross-validation within the training set to compute the means.

```python
# sklearn 1.3+ has a proper TargetEncoder (handles the leakage correctly):
from sklearn.preprocessing import TargetEncoder
te = TargetEncoder()
df['City_Encoded'] = te.fit_transform(df[['City']], df['Target'])

# Manual implementation (with K-fold to avoid leakage):
from sklearn.model_selection import KFold
import numpy as np

kf = KFold(n_splits=5, shuffle=True, random_state=42)
df['City_Encoded'] = 0.0
for train_idx, val_idx in kf.split(df):
    means = df.iloc[train_idx].groupby('City')['Target'].mean()
    df.loc[val_idx, 'City_Encoded'] = df.loc[val_idx, 'City'].map(means).fillna(df['Target'].mean())
```

Why K-fold? If you compute the target mean for each category on the full training set and then assign it to the same rows, you leak each row's target into its own feature. K-fold prevents this: each row's encoding is computed from the *other* folds' targets.

## Other encoding schemes

Four further options cover special cases:

- **Frequency encoding** replaces a category with its frequency in the training set — simple and workable at high cardinality, but it loses information about the target.
- **Binary encoding** converts the integer label to binary and then one-hot encodes each bit — a compromise between label encoding and OHE that uses $O(\log_2 K)$ columns instead of $K$.
- **Hashing trick (feature hashing)** hashes each category into a fixed-size array — no memory overhead, but collisions are possible; used in large-scale systems (Vowpal Wabbit, online learning).
- **Embeddings** map each category to a learned dense vector, as in NLP word embeddings — the most powerful approach for very high cardinality, but it requires a neural network to learn the embeddings.

## Choosing the right encoding

| Situation | Recommended Encoding |
| :--- | :--- |
| Ordinal data (Low/Medium/High) | OrdinalEncoder (specify the order) |
| Nominal, low cardinality (< 15 categories) | One-Hot Encoding |
| Nominal, high cardinality (15-1000 categories) | Target Encoding (with K-fold) |
| Nominal, very high cardinality (> 1000 categories) | Target Encoding, Hashing, or Embeddings |
| Tree-based models | Label/Frequency encoding is often fine (trees can split on integers) |
| Linear models, NN, SVM | OHE or Target Encoding (trees handle raw integers; linear models cannot) |

## Fit on train, transform both

The same discipline as scaling applies: **never fit the encoder on the full dataset** — fit on train, transform both. Or use a `Pipeline` with a `ColumnTransformer`:

```python
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

preprocessor = ColumnTransformer([
    ('num', StandardScaler(), ['Age', 'Salary']),
    ('cat', OneHotEncoder(handle_unknown='ignore'), ['City', 'Color'])
])

pipe = Pipeline([
    ('preprocess', preprocessor),
    ('model', LogisticRegression())
])
pipe.fit(X_train, y_train)
pipe.score(X_test, y_test)
```

The `ColumnTransformer` applies different transformations to different columns — scaling for numerical, OHE for categorical — and the Pipeline guarantees no leakage. The encoding and imputation sides of the same workflow are covered in this note and in [[Missing Data and Imputation]], and the whole sequence is exercised in [[Exercise - Medical Dataset Pipeline]].

## Key takeaways

1. **Label/Ordinal encoding:** integers, only for ordinal data (implied order).
2. **One-hot encoding:** binary columns, for nominal data, but curse of dimensionality at high cardinality.
3. **Target encoding:** mean of target per category, for high cardinality, but must use K-fold to avoid leakage.
4. **Other options:** frequency, binary, hashing and embeddings for special cases.
5. **Always fit on train, transform both** — or use `ColumnTransformer` + `Pipeline`.
6. Tree models can handle label encoding; linear models and NNs need OHE or target encoding.

## See also

- [[Python Language Overview]]
- [[Feature Scaling and Normalization]]
- [[Missing Data and Imputation]]
- [[Outlier Detection and Treatment]]
- [[Duplicate Detection and Record Linkage]]
- [[Exercise - Medical Dataset Pipeline]]
- [[Pandas]]
- [[Decision Trees]]
- [[Random Forests and Bagging]]
- [[Gradient Boosting]]
- [[04 - Machine Learning/Regression/Logistic Regression|Logistic Regression]]
- [[Artificial Neural Networks]]
- [[Data Preparation for Neural Networks]]
- [[Word2Vec GloVe and FastText]]
