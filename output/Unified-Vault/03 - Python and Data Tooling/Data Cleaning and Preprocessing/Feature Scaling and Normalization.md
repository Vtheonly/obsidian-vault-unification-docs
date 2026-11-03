---
title: Feature Scaling and Normalization
type: concept
aliases:
  - Feature Scaling
  - Standardization
  - Z-Score Normalization
  - Min-Max Normalization
  - Feature Scaling Methods
tags:
  - python
  - data-cleaning
  - preprocessing
  - feature-scaling
  - scikit-learn
  - data-leakage
sources:
  - "04. Feature Scaling and Normalization"
created_index: 4
---

Many machine learning algorithms quietly assume that all features live on comparable scales: anything that calculates **distance** (KNN, K-Means, SVM) or uses **gradient descent** (neural networks, logistic regression) performs poorly if features have different scales. Feature scaling fixes this by rescaling each numeric column with a shared, model-appropriate transformation. This note tours the six scalers of the scikit-learn preprocessing toolbox, compares them side by side, and covers the fitting discipline that keeps scaling from leaking test information into training.

## Why feature scaling matters

The classic illustration mixes two features of very different magnitude: **Age (0-100)** vs. **Salary (20,000 - 100,000)**. Without scaling, Salary will dominate every distance calculation simply because the numbers are bigger — even if Age is more predictive. The bias is inherited by every distance-based learner ([[K-Nearest Neighbors]], the K-Means algorithm covered in [[Clustering]], SVMs) and by every gradient-descent model (neural networks, logistic regression); [[Principal Component Analysis]] belongs on the same list of methods for which scaling is essential. Several of the scalers below are built on the z-score and the IQR — the same statistics used in [[Outlier Detection and Treatment]].

## Standardization (z-score normalization)

Standardization rescales the data to have **mean = 0** and **standard deviation = 1**:

$$z = \frac{x - \mu}{\sigma}$$

It is the default choice when the downstream algorithm assumes a Gaussian distribution — logistic regression, SVMs and neural networks are the usual examples. Outliers are preserved: they remain far from the mean, just on a standardized scale rather than their original units. Tree-based models are the exception and do not benefit, as discussed below under when scaling is unnecessary.

```python
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
df_scaled = scaler.fit_transform(df[['Age', 'Salary']])
```

## Min-max normalization

Min-max normalization rescales the data to a fixed range, usually **[0, 1]**:

$$x_{norm} = \frac{x - x_{min}}{x_{max} - x_{min}}$$

Typical use cases are image processing (pixels 0-255) and neural-network input layers, where sigmoid/tanh activations work best with [0,1] or [-1,1] inputs. The method is sensitive to outliers: a single extreme value compresses the rest of the data into a narrow band. As with standardization, tree-based models do not need it.

```python
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
df_norm = scaler.fit_transform(df[['Age', 'Salary']])
```

## Robust scaling

The RobustScaler scales data using the **median** and the **IQR** (interquartile range) instead of the mean and standard deviation:

$$x_{robust} = \frac{x - \text{median}}{Q3 - Q1}$$

Use it when the data contains significant outliers that you don't want to remove but also don't want influencing the scale: the median and IQR are robust to outliers, unlike the mean and std.

```python
from sklearn.preprocessing import RobustScaler
scaler = RobustScaler()
df_robust = scaler.fit_transform(df[['Age', 'Salary']])
```

## MaxAbs scaling

The MaxAbsScaler rescales data to **[-1, 1]** by dividing by the maximum absolute value, and it does not shift or center the data:

$$x_{maxabs} = \frac{x}{\max(|x|)}$$

That no-centering property makes it the scaler of choice for **sparse data** (CSR matrices): zeros stay zeros, so sparsity is preserved, whereas centering would destroy it.

```python
from sklearn.preprocessing import MaxAbsScaler
scaler = MaxAbsScaler()
df_maxabs = scaler.fit_transform(df[['Age', 'Salary']])
```

## Power transformation (Box-Cox and Yeo-Johnson)

The PowerTransformer applies a parametric transformation to make the data **more Gaussian-like**, which is useful for skewed features. It comes in two variants: **Box-Cox** requires strictly positive data, while **Yeo-Johnson** handles both positive and negative data. Reach for it when a feature is highly skewed and the downstream algorithm assumes Gaussianity (linear models, Gaussian processes).

```python
from sklearn.preprocessing import PowerTransformer
scaler = PowerTransformer(method='yeo-johnson')  # or 'box-cox'
df_power = scaler.fit_transform(df[['Age', 'Salary']])
```

## Quantile transformation

The QuantileTransformer transforms features to follow a **uniform** or **normal** distribution by mapping each value to its quantile. Use it when you want to remove all distributional structure — heavy tails, skewness — and produce a uniform/normal output; the mapping is robust to outliers. The caveat: the transformation is non-linear and **distorts correlations and distances**, so downstream geometry should be interpreted with care.

```python
from sklearn.preprocessing import QuantileTransformer
scaler = QuantileTransformer(output_distribution='normal')
df_quant = scaler.fit_transform(df[['Age', 'Salary']])
```

## Choosing a scaler

The six scalers trade off output range, outlier robustness and sparsity preservation:

| Scaler | Output Range | Robust to Outliers? | Preserves Sparsity? | When to Use |
| :--- | :--- | :--- | :--- | :--- |
| StandardScaler | Unbounded (mean 0, std 1) | No | No | Default for most ML; Gaussian-assuming models |
| MinMaxScaler | [0, 1] | No | No | NN inputs, image pixels |
| RobustScaler | Unbounded | **Yes** | No | Data with significant outliers |
| MaxAbsScaler | [-1, 1] | No | **Yes** | Sparse data |
| PowerTransformer | Unbounded | Partially | No | Skewed data, Gaussian-assuming models |
| QuantileTransformer | [0, 1] or unbounded | **Yes** | No | Heavy-tailed data, want uniform/normal output |

## Fit on train, transform both

> [!DANGER] Data Leakage Warning
> **Never fit the scaler on the full dataset.** If you fit on train + test together, the scaler's statistics (mean, std, min, max) are influenced by the test data — this is **data leakage**, and it inflates your test performance.

The correct pattern fits the scaler on the training split only and reuses those statistics for the test split:

```python
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)  # Fit on train ONLY
X_test_scaled = scaler.transform(X_test)        # Transform test with train's statistics
```

Or, better, use a **Pipeline** to guarantee no leakage:

```python
from sklearn.pipeline import Pipeline
pipe = Pipeline([
    ('scaler', StandardScaler()),
    ('model', LogisticRegression())
])
pipe.fit(X_train, y_train)  # Scaler fits on train only, automatically
pipe.score(X_test, y_test)
```

This is the single most important preprocessing practice. The same fit-on-train discipline applies to encoders and imputers — see [[Categorical Encoding and Text Normalization]] and [[Missing Data and Imputation]] — and it is exercised end-to-end in [[Exercise - Medical Dataset Pipeline]].

## When scaling is unnecessary

**Tree-based models** — Decision Trees, Random Forests, XGBoost, LightGBM, CatBoost — are **scale-invariant**. They split on feature values directly (`if Age > 30`), and the threshold is chosen from the data, so the scale does not matter; scaling before tree-based models is wasted computation. **Naive Bayes** is also largely scale-invariant, since it works on probabilities, not distances.

For all other models — KNN, K-Means, SVM, logistic regression, neural networks, PCA — scaling is essential.

## Key takeaways

1. **StandardScaler** (Z-score): default for most ML; mean 0, std 1; not robust to outliers.
2. **MinMaxScaler**: [0, 1] range; for NN inputs and image pixels; sensitive to outliers.
3. **RobustScaler**: median + IQR; robust to outliers.
4. **MaxAbsScaler**: [-1, 1]; preserves sparsity.
5. **PowerTransformer / QuantileTransformer**: for skewed or heavy-tailed data.
6. **Always fit on train, transform both** — or use a Pipeline to guarantee no leakage.
7. **Tree-based models do not need scaling** — they are scale-invariant.

## See also

- [[Python Language Overview]]
- [[Categorical Encoding and Text Normalization]]
- [[Missing Data and Imputation]]
- [[Outlier Detection and Treatment]]
- [[Duplicate Detection and Record Linkage]]
- [[Exercise - Medical Dataset Pipeline]]
- [[Pandas]]
- [[K-Nearest Neighbors]]
- [[Clustering]]
- [[Principal Component Analysis]]
- [[04 - Machine Learning/Regression/Logistic Regression|Logistic Regression]]
- [[Decision Trees]]
- [[Random Forests and Bagging]]
- [[Gradient Boosting]]
- [[Artificial Neural Networks]]
- [[Data Preparation for Neural Networks]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Batch Normalization|Batch Normalization]]
