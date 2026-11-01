---
title: Random Forests and Bagging
type: concept
aliases:
  - Random Forest
  - Bagging
  - Bootstrap Aggregating
  - RF
tags:
  - machine-learning
  - supervised-learning
  - random-forests
  - bagging
  - ensembles
  - tree-based-models
  - bootstrap
  - oob-error
  - feature-importance
sources:
  - "Random Forests and Bagging"
  - "03 - Decision Trees and Gradient Boosting"
created_index: 27
---

Random forests fix the defining weakness of a single [[Decision Trees|decision tree]] — high variance — by averaging many trees, each trained on a slightly different view of the data. The recipe combines bagging (bootstrap sampling plus aggregation) with feature randomness at every split, and it comes with two elegant byproducts: out-of-bag error, a free validation estimate computed during training, and feature importance, a built-in measure of which features matter. Random forests are robust, fast, and need little tuning, which makes them the strong baseline for tabular data — typically a bit less accurate than [[Gradient Boosting]] but easier to use and harder to mess up. This note covers the variance problem they solve, the bagging mechanics, the bias-variance accounting behind why they work, and their strengths, weaknesses, and evaluation tooling.

## The variance problem

A single decision tree has high variance — small changes in the training data produce very different trees. This is because each split is chosen greedily, and a slightly different dataset may make a different split look best, which then affects all subsequent splits. The result: the tree fits the noise in the training data, not just the signal. Deep trees make this worse, since they overfit easily, and on top of that a single tree cannot extrapolate — its predictions are constant within each leaf.

**Random Forests** (Breiman, 2001) fix this by **averaging many trees**, each trained on a slightly different view of the data. The averaging reduces variance without increasing bias, producing a model that is more accurate and more stable than any single tree.

## Bagging: bootstrap aggregating

The core technique is **bagging** (Bootstrap Aggregating):

1. **Bootstrap sample:** draw a random sample of size $n$ from the training data **with replacement**. Some samples appear multiple times; ~37% of samples are left out (the "out-of-bag" samples).
2. **Train a tree** on the bootstrap sample, **without pruning**. (We want each tree to have low bias; the averaging handles the variance.)
3. **Repeat** $B$ times (typically $B = 100$–$1000$), producing $B$ trees.
4. **Aggregate:** for classification, majority vote; for regression, average.

The deliberate choice *not* to prune is what makes the ensemble work: each tree is allowed to be a rich, low-bias model of its own bootstrap sample, and the variance that would otherwise wreck a single unpruned tree is washed out by the aggregation.

The key insight: averaging $B$ **independent** models with variance $\sigma^2$ each reduces the variance to $\sigma^2 / B$. But the trees are not fully independent (they all see similar data), so the reduction is less than $\sigma^2 / B$ — but still substantial.

## Random forests: adding feature randomness

Bagging alone is not enough because the trees are correlated — they all see similar data, so they make similar splits. **Random Forests** decorrelate the trees by adding **feature randomness**:

At each split, the tree is not allowed to consider all features. Instead, it considers only a **random subset** of features (typically $\sqrt{d}$ for classification, $d/3$ for regression, where $d$ is the total number of features). The best split is chosen from this random subset.

This forces different trees to split on different features, decorrelating them. The effect: when averaged, the trees provide more independent "votes," and the variance reduction is closer to the theoretical $\sigma^2 / B$.

Formally, the forest trains $N$ decision trees on bootstrap samples of the data, with random feature subsets at each split, and averages (regression) or majority-votes (classification) their outputs:

$$
\hat{f}_{\text{RF}}(\mathbf{x}) = \frac{1}{N} \sum_{i=1}^{N} T_i(\mathbf{x})
$$

### Why this works: the bias-variance decomposition

- **Bias:** unchanged (each tree is still an unpruned tree, with low bias).
- **Variance:** reduced (averaging decorrelated trees).
- **Result:** lower total error (which is bias + variance).

**Why it works**: averaging many high-variance, low-bias trees reduces variance without increasing bias. This is the [[Bias Variance Tradeoff]] in action — bagging reduces variance. Both randomness sources matter: the bootstrap gives each tree a different dataset, and the feature subsets give each split different candidate questions; neither changes how expressive a single tree is, so bias stays put while the averaging cancels noise across trees.

## Out-of-bag error

Each tree is trained on a bootstrap sample containing ~63% of the data. The remaining ~37% (the "out-of-bag" samples) can be used to evaluate that tree — without needing a separate validation set.

For each training sample, find the trees that did **not** train on it (the trees for which it is out-of-bag), and use those trees to predict it. Average their predictions, and compute the error. This is the **OOB error** — an unbiased estimate of the test error, computed for free during training.

OOB error is one of the most elegant features of Random Forests. It lets you tune hyperparameters (number of trees, max features, max depth) without a separate validation set or cross-validation — a built-in counterpart to the holdout and cross-validation protocols described in [[Model Evaluation Metrics]].

## Feature importance

Random Forests provide a natural **feature importance** measure: for each feature, sum the impurity reduction across all splits that use that feature, averaged over all trees. Features that are used often and produce large impurity reductions are deemed important.

This is a byproduct of training (no extra computation) and is one of the main reasons practitioners use Random Forests for exploratory data analysis — it tells you which features matter, even if you do not ultimately use the forest for prediction.

> [!WARNING] Impurity-based importance is biased toward high-cardinality features.
> Features with many possible split points (continuous features, high-cardinality categoricals) get more chances to produce a good split by chance, inflating their importance. Use **permutation importance** (shuffle each feature and measure the accuracy drop) for an unbiased measure.

The same caution extends to how importance is interpreted rather than just estimated: treating feature importance as causation is a mistake — it is not causal, and SHAP values are closer but still correlational.

## Strengths of random forests

1. **Strong default:** works well out-of-the-box with minimal tuning. Often the first algorithm to try on tabular data.
2. **Handles mixed data types:** numerical and categorical, no scaling needed.
3. **Robust to outliers:** trees split on order, not magnitude.
4. **OOB error:** free validation, no need for a separate holdout.
5. **Feature importance:** built-in interpretability.
6. **Parallelizable:** each tree is independent, so training parallelizes perfectly.

That last point is a genuine architectural advantage over sequential methods: because the $B$ trees never depend on one another, adding cores scales training almost linearly.

## Weaknesses

1. **Cannot extrapolate:** like single trees, the forest predicts constant values within leaves. It cannot predict values outside the training range.
2. **Large model:** 500 trees of depth 20 is a lot of memory. Slower inference than a single tree or a linear model.
3. **Less accurate than gradient boosting:** on most tabular benchmarks, XGBoost/LightGBM beat Random Forests. RFs are the "strong baseline"; boosting is the "state of the art."
4. **Less interpretable than a single tree:** you can no longer trace a single decision path; you have 500 trees voting.

## Random forests in the tree-model family

The forest sits in the middle of the tree-model progression: single trees (high variance) → Random Forests (bagging, reduce variance) → Gradient Boosting (sequential, reduce bias). The base learner is a [[Decision Trees|decision tree]] that recursively splits the feature space, choosing at each node the feature and threshold that best separate the classes (Gini impurity or information gain) or reduce target variance (MSE); the forest inherits the tree's love of mixed data, non-linearities, and interactions, and cures its variance. At each node the forest still searches only a random feature subset for the best split — the same impurity criteria, restricted candidates.

The other branch of the family, [[Gradient Boosting|gradient boosting]], trains trees **sequentially**, each correcting the previous one's errors: it starts from a constant prediction, fits each new tree to the current model's residuals, and adds it with a learning rate, so the final model is the base prediction plus a shrunken sum of trees. Boosting is functional gradient descent in function space, and it uses shallow weak learners (depth 3–8) that accumulate, governed by hyperparameters such as `n_estimators`, `learning_rate`, `subsample`, and `colsample_bytree` (the latter two adding bagging-style randomness to the sequential scheme) and trained with early stopping, which halts boosting when validation loss stops improving. Its dominant implementations — XGBoost (the original, from 2014, with the Chen and Guestrin paper in 2016), LightGBM (2017, Microsoft, histogram-based splits, faster on large data), and CatBoost (Yandex, native categorical handling, often best out-of-the-box) — are all widely used in production and Kaggle competitions, and on most tabular benchmarks they beat random forests, which is why the forest is the strong baseline and boosting the state of the art.

The forest more than holds its own in the broader landscape, though: empirical studies (for example, Grinsztajn et al. 2022) consistently show tree-based models as a whole beat deep learning on tabular data — trees handle irregular target functions and non-smooth features, need no feature scaling, perform implicit feature selection, tolerate irrelevant features, and work in smaller data regimes — while deep learning dominates unstructured data (text, images, audio) and very large tabular datasets. Tree-based models also offer interpretability tooling — feature importance, SHAP values, individual tree traces — which matters in regulated industries, and in production their feature distributions should be monitored, since tree-based models fail silently when those distributions shift. For deeper background, Hastie, Tibshirani, and Friedman's *ESL* covers trees in Chapter 9 and boosting in Chapter 10, alongside Breiman's original 2001 random forests paper.

## What to walk away with

1. Random Forests fix decision trees' high variance by **averaging many trees**, each trained on a bootstrap sample.
2. **Feature randomness** (considering only a random subset of features at each split) decorrelates the trees, improving the variance reduction.
3. **Out-of-bag error** provides a free, unbiased validation estimate during training.
4. **Feature importance** is a useful byproduct, but use permutation importance for unbiased estimates.
5. Random Forests are a strong default for tabular data — minimal tuning, robust, parallelizable.
6. They are typically less accurate than gradient boosting but easier to use and harder to mess up.

## See also

- [[Machine Learning MOC]] — the map of machine learning topics.
- [[Decision Trees]] — the base learner whose variance the forest averages away.
- [[Gradient Boosting]] — the sequential, bias-reducing sibling ensemble.
- [[Bias Variance Tradeoff]] — the decomposition that explains why averaging unpruned trees works.
- [[Model Evaluation Metrics]] — the validation framework OOB error replaces.
- [[Regularization Techniques]] — contrast: forests control variance by averaging rather than by penalizing.
- [[Regression Fundamentals]] — background for the averaging (regression) mode of the forest.
- [[04 - Machine Learning/Regression/Linear Regression|Linear Regression]] — the low-variance, high-bias counterpoint to the unpruned tree.
- [[Support Vector Machines]] — another strong classical baseline for structured data.
- [[K-Nearest Neighbors]] — a comparably tuning-light, non-parametric baseline.
