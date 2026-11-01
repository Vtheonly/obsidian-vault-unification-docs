---
title: Gradient Boosting
type: concept
aliases:
  - Gradient Boosted Trees
  - Gradient Boosted Decision Trees
  - GBT
tags:
  - machine-learning
  - supervised-learning
  - gradient-boosting
  - tree-based-models
  - ensembles
  - boosting
  - xgboost
  - lightgbm
  - catboost
  - tabular-data
sources:
  - "Gradient Boosting and XGBoost"
  - "03 - Decision Trees and Gradient Boosting"
created_index: 26
---

Gradient boosted trees are the state of the art for tabular data: XGBoost, LightGBM, and CatBoost — the three dominant implementations — win most Kaggle competitions on structured data and are the default choice in industry for tabular machine learning, and for tabular data gradient boosting is still SOTA, beating deep learning on most benchmarks. Where [[Random Forests and Bagging|random forests]] train many independent trees and average them, boosting trains trees sequentially, each correcting the errors of the previous ones. This note explains the core algorithm, the deep connection to [[Gradient Descent]] (boosting is gradient descent in function space), the hyperparameters that govern it, the practical differences between XGBoost, LightGBM, and CatBoost, and when to reach for boosting at all. It builds directly on [[Decision Trees]] and anchors the tree-based models area of the [[Machine Learning MOC]].

## Boosting versus bagging

The distinction between the two great tree-ensemble families is fundamental.

**Random Forests (bagging):** train many trees **independently** on bootstrap samples, then average. Each tree is a strong learner (low bias, high variance); averaging reduces the variance. For regression, the forest prediction is the average of its $N$ trees:

$$
\hat{f}_{\text{RF}}(\mathbf{x}) = \frac{1}{N} \sum_{i=1}^{N} T_i(\mathbf{x})
$$

**Gradient Boosting:** train many trees **sequentially**, where each tree corrects the errors of the previous ones. Each tree is a **weak learner** (high bias, low variance — typically a shallow tree); the sequence reduces the bias.

- Bagging: independent trees, strong learners, reduce variance.
- Boosting: sequential trees, weak learners, reduce bias.

This is the same [[Bias Variance Tradeoff]] seen from two directions: bagging attacks variance by averaging, boosting attacks bias by accumulating corrections. The two families even borrow from each other — boosting's stochastic sampling options (below) import bagging-style randomness into the sequential scheme.

## The gradient boosting algorithm

### The general algorithm (any differentiable loss)

Initialize the prediction $F_0(x)$ as a constant (the mean for regression, the log-odds for classification).

For $m = 1, 2, \ldots, M$:

1. **Compute the pseudo-residuals:** for each sample $i$, compute the negative gradient of the loss with respect to the current prediction:
   $$r_i = -\frac{\partial L(y_i, F_{m-1}(x_i))}{\partial F_{m-1}(x_i)}$$

   For MSE loss, this is just $r_i = y_i - F_{m-1}(x_i)$ — the ordinary residual. For other losses (logistic, etc.), it is the gradient of that loss.

2. **Fit a tree** to the pseudo-residuals: train a regression tree $h_m$ that predicts $r_i$ from $x_i$.

3. **Find the optimal step size:** for each leaf of $h_m$, find the value $\gamma$ that minimizes the loss when added to the current prediction:
   $$\gamma_{jm} = \arg\min_\gamma \sum_{x_i \in \text{leaf } j} L(y_i, F_{m-1}(x_i) + \gamma)$$

4. **Update the prediction:**
   $$F_m(x) = F_{m-1}(x) + \nu \cdot \gamma_{jm} \cdot h_m(x)$$

   where $\nu \in (0, 1]$ is the **learning rate** (typically 0.01–0.1) that shrinks each tree's contribution.

The final model is $F_M(x) = F_0(x) + \nu \sum_{m=1}^M \gamma_m h_m(x)$ — a sum of $M$ trees.

### The compact form for squared-error loss

For MSE loss the procedure collapses into the version most commonly written down:

1. Start with a constant prediction $F_0(\mathbf{x})$ (e.g., mean of $y$).
2. For $m = 1, \ldots, M$:
   - Compute residuals $r_i = y_i - F_{m-1}(\mathbf{x}_i)$.
   - Train a tree $T_m$ to predict the residuals.
   - Update: $F_m(\mathbf{x}) = F_{m-1}(\mathbf{x}) + \nu \cdot T_m(\mathbf{x})$, where $\nu$ is the learning rate.

The final model: $F_M(\mathbf{x}) = F_0(\mathbf{x}) + \nu \sum_{m=1}^M T_m(\mathbf{x})$ — a base prediction plus a shrunken sum of trees. More trees means lower bias but higher variance, which is why the count of trees is itself a regularization knob.

## Why this is gradient descent in function space

Look at step 1: the pseudo-residuals are the negative gradient of the loss with respect to the prediction. Step 4 adds a tree (fit to the gradient) to the current prediction, scaled by a learning rate. This is exactly **gradient descent**, but instead of descending in parameter space, we descend in **function space** — the space of possible prediction functions.

This is the deep insight: **gradient boosting is gradient descent where each "parameter" is a tree, and the gradient tells us what tree to add next.** The tree fits the gradient; adding it moves the prediction in the direction that reduces the loss.

This is why boosting can use any differentiable loss: MSE, logistic, Huber, custom losses. The algorithm just needs the gradient, which any differentiable loss provides — the same property that powers the parametric methods discussed in [[Loss Functions]] and [[Gradient Descent]], transferred from weight vectors to whole functions.

## Key hyperparameters

| Hyperparameter | Effect | Typical range |
| :--- | :--- | :--- |
| `n_estimators` ($M$) | Number of trees | 100–10000 |
| `learning_rate` ($\nu$) | Shrinkage per tree | 0.01–0.3 |
| `max_depth` | Depth of each tree | 3–8 (shallow!) |
| `subsample` | Fraction of data per tree | 0.5–1.0 |
| `colsample_bytree` | Fraction of features per tree | 0.5–1.0 |
| `min_child_weight` | Min samples per leaf | 1–10 |
| `reg_alpha`, `reg_lambda` | L1/L2 regularization | 0–10 |

**The learning rate / n_estimators tradeoff:** lower learning rate with more trees usually gives better performance (but slower training). A common pattern: start with $\nu = 0.1$, $M = 100$, then lower $\nu$ and increase $M$ with early stopping. A lower learning rate needs more trees but often yields better generalization; typical values sit in 0.01–0.1.

**Shallow trees:** unlike Random Forests (deep trees), boosting uses shallow trees (depth 3–8). This is because each tree is a weak learner — it should capture a small pattern, not fit the data fully. The sequence of weak learners composes into a strong learner: each tree is weak but they accumulate.

**Stochastic gradient boosting:** using `subsample < 1` and `colsample_bytree < 1` (like Random Forests' bootstrap and feature sampling) decorrelates the trees and improves generalization. This is standard practice — `subsample` is the fraction of data per tree (adding randomness, like bagging) and `colsample_bytree` the fraction of features per tree.

Beyond these, the implementations expose explicit regularization — L1, L2, `min_child_weight`, and `gamma` — which connect boosting to the general shrinkage ideas covered in [[Regularization Techniques]].

## XGBoost, LightGBM, CatBoost: the three implementations

### XGBoost (Chen and Guestrin, 2016)

The original major gradient boosting library. Key innovations:

- **Regularized learning objective:** explicit L1/L2 regularization on the tree weights.
- **Second-order gradients:** uses both the gradient and the Hessian (second derivative) of the loss, for better split decisions.
- **Sparsity-aware:** handles missing values and sparse features natively.
- **Approximate split finding:** for large datasets, uses approximate (histogram-based) split finding instead of exact.
- **System optimization:** cache-aware access, out-of-core computation, parallelization.

XGBoost was the dominant library from 2016 to 2019 and remains widely used. One dating subtlety worth knowing (it shows up in interviews): the library itself first appeared in **2014**, while the famous Chen and Guestrin paper — *"XGBoost: A Scalable Tree Boosting System"* — was published in **2016**, so both dates circulate for "when XGBoost arrived."

### LightGBM (Ke et al., 2017)

Microsoft's implementation, focused on **speed and memory efficiency**. Key innovations:

- **Histogram-based splitting:** bins continuous features into histograms, reducing split-finding cost from $O(n \cdot d)$ to $O(\text{bins} \cdot d)$.
- **Leaf-wise growth:** grows trees leaf-by-leaf (the leaf with the highest delta loss) rather than level-by-level. This can produce deeper, more asymmetric trees that are more accurate for the same number of leaves — but more prone to overfitting on small data.
- **Gradient-based One-Side Sampling (GOSS):** keeps all samples with large gradients and randomly samples those with small gradients, reducing computation without losing much information.
- **Exclusive Feature Bundling (EFB):** bundles mutually exclusive sparse features (one-hot encoded) into a single dense feature, reducing dimensionality.

LightGBM is typically 3–10× faster than XGBoost with similar accuracy, making it the default for large datasets.

### CatBoost (Yandex, 2017)

Focused on **categorical features**. Key innovations:

- **Native categorical handling:** encodes categoricals using target statistics (with careful ordering to avoid leakage), eliminating the need for one-hot encoding.
- **Ordered boosting:** each tree is trained on residuals computed from a model that did not see that sample, reducing the prediction shift caused by using the same data for residual computation and tree fitting.
- **Symmetric trees:** all nodes at the same depth use the same split condition, making inference very fast (a single comparison per level).

CatBoost is the best choice when the data has many categorical features, and is competitive in general — often the best out-of-the-box. A compact summary of the timeline: XGBoost is the original (2014 library, 2016 paper), LightGBM followed in 2017, and CatBoost appeared from Yandex in 2017–2018.

## A worked example (XGBoost)

```python
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = xgb.XGBClassifier(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    eval_metric='logloss',
    early_stopping_rounds=20,
)
model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)
preds = model.predict(X_test)
print(accuracy_score(y_test, preds))
```

Early stopping is essential — it halts training when validation loss stops improving, preventing overfitting. Never train to a fixed number of trees when a validation set is available; accuracy is then scored exactly as in [[Model Evaluation Metrics]].

## When to use gradient boosting

**Use GBT when:**

- The data is tabular (structured).
- You want maximum accuracy.
- You have enough data (1000+ samples; boosting can overfit on very small datasets).
- You can afford the training time (boosting is slower than Random Forests).

**Do not use GBT when:**

- The data is unstructured (images, text, audio) — use neural networks.
- The dataset is very small (< 100 samples) — overfitting risk.
- You need real-time inference on resource-constrained devices — the model is large.

**Which implementation?**

- **LightGBM** for speed and large datasets (the default for most applications).
- **CatBoost** for data with many categoricals.
- **XGBoost** if you need the original, well-tested implementation (or are following a specific tutorial).

## Why gradient boosting beats deep learning on tabular data

Empirical studies (e.g., Grinsztajn et al. 2022) consistently show tree-based models beat deep learning on tabular data. Reasons:

1. **Trees handle irregular target functions and non-smooth features** naturally. Neural networks assume some smoothness.
2. **No feature scaling needed**. Neural networks are sensitive to feature scale.
3. **Implicit feature selection**. Trees pick the most informative splits; NNs use all features.
4. **Robust to irrelevant features**. Trees ignore them; NNs can overfit to noise.
5. **Smaller data regimes**. Trees work well with thousands of samples; NNs need more.

Deep learning dominates **unstructured data** (text, images, audio) and **very large tabular datasets** (millions of rows). For typical enterprise tabular data, gradient boosting is the right choice.

## Why this matters for AI

- **Most enterprise ML is tabular ML.** If you work in industry, gradient boosting will be your bread and butter, not LLMs.
- **Feature engineering is still alive.** Trees can't invent features; they need good inputs. Domain knowledge + gradient boosting often beats raw-data + deep learning.
- **Interpretability**: tree-based models offer feature importance, SHAP values, individual tree traces. Useful for regulated industries.
- **Ensembling for production**: stacking XGBoost + a neural network often gives the best of both worlds.

## Production implications

- **Default to gradient boosting for tabular classification/regression.** Don't reach for deep learning first.
- **Use early stopping** — never train to a fixed number of trees.
- **Tune hyperparameters via Bayesian optimization** (Optuna, Hyperopt) — better than grid search for high-dim hyperparameter spaces.
- **SHAP for explanations** — gives per-prediction feature attributions. Critical for compliance.
- **Monitor feature distributions in production** — tree-based models fail silently when feature distributions shift.
- **CatBoost for categorical features** — if your data has many categoricals, CatBoost saves you from one-hot encoding headaches.

## Common pitfalls

- **Too-deep trees** — high variance. Keep max_depth in 3–8.
- **Forgetting early stopping** — overfits badly.
- **Target leakage** — features that include future information. Always split by time for temporal data.
- **Class imbalance** — use `scale_pos_weight` or sampling.
- **Treating "feature importance" as causation** — it's not. SHAP is closer but still correlational.

## The tree-model family: single trees and random forests

Boosting completes a progression through tree-based models: single trees (high variance) → Random Forests (bagging, reduce variance) → Gradient Boosting (sequential, reduce bias). A single [[Decision Trees|decision tree]] recursively splits the feature space but has high variance — small data changes produce very different trees — which is the problem both ensembles solve. Random forests train $N$ trees independently on bootstrap samples with random feature subsets at each split and average or majority-vote the results; averaging many high-variance, low-bias trees reduces variance without increasing bias, and the result is a robust, fast, little-tuning baseline — easier to use and harder to mess up than boosting, if usually a bit less accurate. These three families are the foundation of tabular ML and belong in every practitioner's toolkit; the bagging side of the family is treated in [[Random Forests and Bagging]].

## What to walk away with

1. Gradient boosting trains trees **sequentially**, each fitting the **pseudo-residuals** (negative gradient of the loss) of the current model.
2. It is **gradient descent in function space** — each tree is a step in the direction that reduces the loss.
3. Key hyperparameters: many shallow trees (depth 3–8), low learning rate (0.01–0.3), stochastic sampling.
4. **XGBoost**: regularized, second-order, sparsity-aware. The original major library.
5. **LightGBM**: histogram-based, leaf-wise growth, fastest. The default for large data.
6. **CatBoost**: native categorical handling, ordered boosting. Best for categorical-heavy data.
7. GBT is the state of the art for tabular data — use it as the default for structured ML tasks.

## Further reading

- Hastie, Tibshirani, Friedman, *ESL*, Chapter 9 (additive models, trees), Chapter 10 (boosting).
- Chen & Guestrin (2016), *XGBoost: A Scalable Tree Boosting System*.
- Grinsztajn et al. (2022), *Why do tree-based models still outperform deep learning on tabular data?*

## See also

- [[Machine Learning MOC]] — the map of machine learning topics.
- [[Decision Trees]] — the base learner every boosted model is built from.
- [[Random Forests and Bagging]] — the parallel, variance-reduction branch of tree ensembles.
- [[Gradient Descent]] — the parameter-space ancestor of function-space gradient descent.
- [[Loss Functions]] — the differentiable losses boosting can optimize.
- [[Bias Variance Tradeoff]] — boosting reduces bias; bagging reduces variance.
- [[Model Evaluation Metrics]] — validation protocols behind early stopping and model comparison.
- [[Regularization Techniques]] — the shrinkage ideas behind learning rate, L1/L2 and tree constraints.
- [[04 - Machine Learning/Regression/Logistic Regression|Logistic Regression]] — the logistic loss whose gradient drives classification boosting.
- [[04 - Machine Learning/Regression/Linear Regression|Linear Regression]] — the squared-error loss behind the residual-fitting picture.
