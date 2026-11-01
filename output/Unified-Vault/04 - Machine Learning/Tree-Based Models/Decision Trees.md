---
title: Decision Trees
type: concept
aliases:
  - Decision Tree
  - Classification and Regression Trees
  - CART
tags:
  - machine-learning
  - supervised-learning
  - decision-trees
  - tree-based-models
  - classification
  - regression
  - interpretability
sources:
  - "Decision Trees - Splitting Criteria and Tree Construction"
  - "03 - Decision Trees and Gradient Boosting"
created_index: 25
---

A decision tree recursively partitions the feature space into regions and assigns a prediction to each region — the majority class for classification, the mean of the target values for regression. Decision trees are the foundation of the most powerful algorithms for tabular data: random forests and gradient boosted trees (XGBoost, LightGBM, CatBoost) — the industry standard for structured data — are all built on decision trees, so understanding the tree is the prerequisite for understanding the ensembles. This note covers how a tree is built greedily from impurity measures, the splitting criteria for classification and regression, the strengths and weaknesses of single trees, and the pruning strategies that keep them from overfitting. It anchors the tree-based models area of the [[Machine Learning MOC]] together with [[Random Forests and Bagging]] and [[Gradient Boosting]].

## The core idea: recursive partitioning

A decision tree recursively partitions the feature space into regions, and assigns a prediction to each region. For classification, the prediction is the majority class in the region; for regression, it is the mean of the target values in the region.

**Example:** a tree for predicting "will the customer buy?" might be:

```text
                  Age > 30?
                 /         \
              Yes           No
              /              \
    Income > 50K?       Buy = No (90%)
      /        \
    Yes        No
    /           \
Buy = Yes (85%)  Buy = No (70%)
```

Each internal node tests a feature against a threshold; each leaf is a prediction. The tree partitions the feature space into rectangular regions (each leaf corresponds to one region).

A second example shows the same mechanism driving a three-way trading decision, with a categorical question ("is the customer a student?") sitting alongside numeric threshold tests:

```text
                       age > 35?
                      /         \
                  yes            no
                  /               \
            income > 60k?     student?
            /         \         /     \
         yes         no       yes     no
          |           |        |       |
       "buy"      "hold"   "buy"   "sell"
```

Reading either tree from the root downward, a prediction is just a sequence of if-then rules, which is exactly why trees remain the reference point for interpretable machine learning.

## How a tree is built: greedy recursive splitting

The tree is built top-down, greedily:

1. Start with all training data at the root.
2. For each possible split (each feature, each threshold), compute the **impurity reduction** (how much the split improves the purity of the children).
3. Choose the split with the highest impurity reduction.
4. Recurse on each child.
5. Stop when: all samples in a node have the same label (pure), or a stopping criterion is met (max depth, min samples per leaf, etc.).

Put differently: at each node, find the feature and threshold that best separates the classes (for classification) or reduces the variance of the target (for regression). Recursion stops when a maximum depth is reached, when too few samples remain in a node, or when the node is pure.

The key question: how do we measure **impurity**?

## Splitting criteria for classification

### Gini impurity

$$\text{Gini}(S) = 1 - \sum_{k=1}^K p_k^2$$

where $p_k$ is the fraction of class $k$ in set $S$.

- Gini = 0: all samples are the same class (pure).
- Gini = $1 - 1/K$: all classes equally represented (maximum impurity).

**Interpretation:** Gini is the probability that a randomly chosen sample is misclassified if labeled randomly according to the class distribution. Lower is better.

### Shannon entropy

$$\text{Entropy}(S) = -\sum_{k=1}^K p_k \log_2 p_k$$

- Entropy = 0: pure.
- Entropy = $\log_2 K$: maximum impurity (all classes equal).

**Interpretation:** Entropy is the average information (in bits) needed to encode the class of a randomly chosen sample. Lower is better.

### Information gain

The impurity reduction from a split is called **Information Gain** (for entropy) or **Gini decrease** (for Gini):

$$IG(S, A) = \text{Impurity}(S) - \sum_{v \in \text{values}(A)} \frac{|S_v|}{|S|} \text{Impurity}(S_v)$$

where $S_v$ is the subset of $S$ where feature $A$ has value $v$. The weighted sum charges each child node only for the fraction of samples it receives, so a split only looks good if it genuinely purifies a large share of the data. The greedy construction picks the feature and threshold that maximize this quantity at every node.

### Gini versus entropy: which to use

In practice, they give nearly identical trees. Gini is slightly faster to compute (no logarithm) and is the default in scikit-learn. Entropy is more theoretically motivated (information theory). The choice rarely matters.

## Splitting criteria for regression

For regression trees, the impurity is the **variance** of the target values in the node:

$$\text{Var}(S) = \frac{1}{|S|} \sum_{i \in S} (y_i - \bar{y}_S)^2$$

A split is chosen to minimize the weighted variance of the children. The prediction at each leaf is the mean of the target values in that leaf.

This is equivalent to minimizing **MSE** — regression trees minimize MSE, just like [[04 - Machine Learning/Regression/Linear Regression|Linear Regression]], but by partitioning the feature space rather than fitting a global linear function. Where linear regression commits to a single functional form over the whole input space, the tree carves the space into rectangles and fits a local constant in each one; the regression criterion (squared error) is the same, and the machinery of [[Regression Fundamentals]] carries over. The quality of the resulting predictions is assessed with the usual [[Regression Evaluation Metrics]].

## The strengths of decision trees

1. **Interpretability:** a tree is a sequence of if-then rules that a human can read. This is invaluable in domains where explainability is required (medicine, finance, law) — you can trace any single prediction through the tree, node by node.
2. **Handles mixed data types:** numerical and categorical features, no scaling needed.
3. **Captures nonlinearities and interactions:** a tree can learn "if Age > 30 AND Income > 50K then ..." — interactions are automatic.
4. **No distributional assumptions:** works regardless of the data's statistical properties.
5. **Robust to outliers:** splits are based on order, not magnitude, so an extreme value never distorts a threshold the way it can distort a fitted coefficient.

Together these properties make the single tree a genuinely useful model class, not merely a building block: it is often the fastest way to get a readable, defensible baseline on mixed tabular data.

## The weaknesses: why single trees need ensembles

1. **High variance:** a small change in the data can produce a completely different tree. Trees overfit easily, and deep trees overfit badly.
2. **Low accuracy on most tasks:** a single tree is rarely competitive with linear models or neural networks.
3. **Instability:** greedy splits compound — a bad split early affects all subsequent splits.
4. **Cannot extrapolate:** predictions are constant within each leaf; the tree cannot predict values outside the training range.

The high-variance failure is the deepest of these: each split is chosen greedily from the data at hand, so a slightly different dataset can make a different split look best, and that single different choice cascades down the whole subtree. The result is a model that fits the noise in the training data, not just the signal — a textbook manifestation of the [[Bias Variance Tradeoff]]. These weaknesses are why **ensembles of trees** — random forests and gradient boosting — dominate tabular ML. They keep the tree's strengths (interpretability, mixed data handling, non-linearity) while fixing the variance and accuracy problems.

## Pruning: preventing overfitting

A tree built without constraints will keep splitting until every leaf has one sample — perfectly fitting the training data, badly overfitting. **Pruning** prevents this:

- **Pre-pruning (stopping criteria):** stop splitting when max depth is reached, when a node has fewer than `min_samples_split` samples, or when the impurity reduction is below a threshold.
- **Post-pruning (cost-complexity pruning):** build the full tree, then prune back branches that do not improve validation performance. The classic CART algorithm uses this.

scikit-learn's `DecisionTreeClassifier` supports pre-pruning via `max_depth`, `min_samples_split`, `min_samples_leaf`, `max_leaf_nodes`. Use these — an unpruned tree is almost always overfit. Pruning plays the same role for trees that shrinkage penalties play for parametric models (see [[Regularization Techniques]]), and deciding how aggressively to prune is ultimately a validation question, so the evaluation protocols in [[Model Evaluation Metrics]] apply directly.

## The tree-model family: from single trees to ensembles

The three tree-based model families form a single progression: decision trees recursively split the feature space; random forests average many trees; gradient boosting builds trees sequentially, each correcting the previous. For tabular data, gradient boosting is still the state of the art — beating deep learning on most benchmarks.

**Random forests** (Breiman, 2001) train $N$ decision trees on bootstrap samples of the data, with random feature subsets at each split, and then average the predictions (regression) or take a majority vote (classification):

$$
\hat{f}_{\text{RF}}(\mathbf{x}) = \frac{1}{N} \sum_{i=1}^{N} T_i(\mathbf{x})
$$

Averaging many high-variance, low-bias trees reduces variance without increasing bias — the bias-variance tradeoff in action, with bagging attacking the variance term. Random forests are robust, fast, and need little tuning, which makes them a great baseline for tabular data; the full treatment, including out-of-bag error and feature importance, is in [[Random Forests and Bagging]].

**Gradient boosting** takes the opposite route: instead of averaging independent trees, it trains trees sequentially, each correcting the errors of the previous ones. It starts from a constant prediction (for example, the mean of $y$), and each new tree is fit to the current model's residuals and added with a learning rate. Each tree learns the gradient direction — boosting is functional gradient descent in function space, with each tree taking a step in the direction that reduces the loss. The trees are deliberately shallow weak learners (depth 3–8) that accumulate into a strong one, and the key hyperparameters (`n_estimators` for the number of trees, `learning_rate`, `max_depth` for per-tree depth, `subsample`, `colsample_bytree`, plus L1/L2 regularization) govern that accumulation — with early stopping on a validation set halting training when the loss stops improving, since training to a fixed number of trees overfits badly. The full algorithm and its modern implementations are developed in [[Gradient Boosting]].

Those modern implementations are the reason trees dominate industrial tabular ML. **XGBoost** (2014) is the original major library — it introduced regularization, second-order gradients, and native handling of missing values (the widely cited Chen and Guestrin paper followed in 2016, which is why both dates appear). **LightGBM** (2017, Microsoft) uses histogram-based splits and is faster on large data. **CatBoost** (2018, Yandex) handles categorical features natively and is often the best out of the box. All three are widely used in production and in Kaggle competitions. Empirical studies (for example, Grinsztajn et al. 2022) consistently show that tree-based models beat deep learning on tabular data because trees handle irregular target functions and non-smooth features naturally, need no feature scaling, perform implicit feature selection, are robust to irrelevant features, and work well in smaller data regimes — while deep learning dominates unstructured data (text, images, audio) and very large tabular datasets.

Because most enterprise ML is tabular ML, these ensembles are the practitioner's bread and butter. Tree-based models also come with interpretability tooling — feature importance, SHAP values, and individual tree traces — which is one of their main advantages in regulated industries. For a deeper treatment, Hastie, Tibshirani, and Friedman's *Elements of Statistical Learning* covers additive models and trees in Chapter 9 and boosting in Chapter 10.

## What to walk away with

1. A decision tree recursively splits the feature space into regions, predicting the majority class (classification) or mean (regression) in each region.
2. **Gini impurity** and **entropy** measure node purity; splits are chosen to maximize impurity reduction (information gain).
3. For regression, the impurity is the variance of the target — equivalent to minimizing MSE.
4. Trees are interpretable, handle mixed data, capture non-linearities and interactions, and are robust to outliers.
5. Trees overfit easily (high variance) — pruning (max depth, min samples per leaf) is essential.
6. Single trees are weak; ensembles (Random Forest, Gradient Boosting) fix the variance problem and dominate tabular ML.

## See also

- [[Machine Learning MOC]] — the map of machine learning topics.
- [[Random Forests and Bagging]] — the variance-fixing ensemble built from these trees.
- [[Gradient Boosting]] — the sequential ensemble that turns weak trees into the tabular state of the art.
- [[Bias Variance Tradeoff]] — the theory behind tree variance and why averaging helps.
- [[Model Evaluation Metrics]] — validation protocols for pruning decisions and model comparison.
- [[Regularization Techniques]] — the parametric counterpart of pruning.
- [[04 - Machine Learning/Regression/Linear Regression|Linear Regression]] — the global-linear contrast to the tree's local-constant partitioning.
- [[Regression Fundamentals]] — background for regression trees and MSE minimization.
- [[Regression Evaluation Metrics]] — how regression-tree predictions are scored.
- [[Support Vector Machines]] — another classical classifier for structured data.
- [[K-Nearest Neighbors]] — a non-parametric alternative with similar distribution-free spirit.
