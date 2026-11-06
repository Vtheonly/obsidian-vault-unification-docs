---
title: Regression Evaluation Metrics
type: reference
aliases:
  - Regression Metrics
  - MAE MSE RMSE R2 MAPE
  - Coefficient of Determination
  - RMSLE
tags:
  - machine-learning
  - model-evaluation
  - regression
  - evaluation-metrics
  - mean-absolute-error
  - mean-squared-error
  - root-mean-squared-error
  - root-mean-squared-logarithmic-error
  - r-squared
  - mape
  - huber-loss
sources:
  - "Regression Metrics - MAE, MSE, RMSE, R2, MAPE"
  - "05 - ML Evaluation Metrics"
created_index: 10
---

When the model's output is a continuous number rather than a label, the evaluation question shifts from "was it right?" to "how far off was it?", and a dedicated family of metrics takes over: MAE, MSE, RMSE, RMSLE, R², adjusted R², and MAPE, with Huber loss bridging the gap between the training objective and the evaluation metric. Each aggregates per-sample errors differently, so each answers a different question — how much outliers should count, whether errors should be read in the target's units or as percentages, and how much of the target's variance the model actually explains. Choosing among them is as important as choosing the model itself: most production machine-learning failures are evaluation failures, caused by optimizing the wrong quantity for the business objective. The modeling background lives in [[Regression Fundamentals]] and [[04 - Machine Learning/Regression/Linear Regression|Linear Regression]]; the classification, ranking, and calibration families are consolidated in [[Model Evaluation Metrics]], and the surrounding map is [[Machine Learning MOC]].

## The regression evaluation problem

In regression, the model predicts a continuous value $\hat{y}$ for each input, and the true value is $y$. The question is how to measure the error $\hat{y} - y$. There are many ways to aggregate per-sample errors into a single number, and each captures different aspects of model quality; the choice depends on the task. A delivery-time forecast, a drug-dosage calculation, and a house-price estimate all output numbers, but they disagree about whether one rare huge mistake is catastrophic or tolerable, whether "off by 500" means anything without knowing the target's scale, and whether the audience reasons in units or in percentages. The metrics below are the standard answers to those disagreements, and the classification side of evaluation — accuracy, precision, recall, F1 and their extensions — is summarized at the end of this note as context, with the consolidated treatment in [[Model Evaluation Metrics]].

## Mean absolute error (MAE)

$$\text{MAE} = \frac{1}{n} \sum_{i=1}^n |y_i - \hat{y}_i|$$

MAE is the average absolute deviation between predicted and true values, expressed in the same units as the target. Because the penalty is linear — every unit of error contributes exactly one unit to the sum — MAE is robust to outliers and easy to interpret: "the average error is \$5" on one scale, "the model is off by \$500 on average" on another.

It is the right choice in three situations:

- When you want a metric interpretable in the target's units.
- When the data has outliers and you do not want them to dominate — MAE is robust to outliers because each error contributes linearly, not quadratically.
- When the cost of an error is proportional to its magnitude (e.g., delivery time prediction: being off by 2 hours is twice as bad as 1 hour).

The main drawback is a training-time property rather than an evaluation-time one. MAE's gradient has constant magnitude regardless of error size, which can make training harder: the model gets the same "push" from a small error as from a large one. This is why MAE is rarely used as a training loss even when it is the evaluation metric — the mechanics of why gradient magnitude matters are covered in [[Gradient Descent]].

## Mean squared error (MSE)

$$\text{MSE} = \frac{1}{n} \sum_{i=1}^n (y_i - \hat{y}_i)^2$$

MSE is the average squared deviation. Errors enter quadratically, so large errors are penalized heavily — the metric grows quadratically as errors grow — and MSE is both the outlier-sensitive member of the family and the default loss for regression.

Use it in three situations:

- When large errors are disproportionately bad (e.g., predicting drug dosage: being off by 10x is far more than 10× worse than being off by 1×).
- When the noise is Gaussian — MSE is the maximum-likelihood estimator under Gaussian noise.
- As a training loss: the gradient grows with error size, so the model focuses on the worst predictions (see [[Loss Functions]] for the loss-side treatment).

The quadratic penalty has a price. MSE is sensitive to outliers — a single large error can dominate the metric — and its value is not interpretable in target units, because it carries squared units.

## Root mean squared error (RMSE)

$$\text{RMSE} = \sqrt{\text{MSE}} = \sqrt{\frac{1}{n} \sum_{i=1}^n (y_i - \hat{y}_i)^2}$$

RMSE is the square root of MSE, which puts the number back in the target's units — the same units as the target, and easier to interpret than MSE itself. It is the standard metric for reporting regression model quality in most scientific and industry contexts.

Use RMSE when you want MSE's outlier sensitivity but interpretability in target units. The pitfall is inherited unchanged: RMSE has the same outlier sensitivity as MSE.

## Root mean squared logarithmic error (RMSLE)

$$\text{RMSLE} = \sqrt{\frac{1}{n} \sum_{i=1}^n (\log(1 + y_i) - \log(1 + \hat{y}_i))^2}$$

RMSLE is RMSE in log space — errors are measured on $\log(1+y)$ rather than on $y$ — which means it penalizes relative errors rather than absolute errors.

It shines for targets spanning multiple orders of magnitude: house prices from $10K to $10M, or counts from 1 to 10000.
Being off by $1000 on a $10K house is bad; on a ten-million-dollar house it is fine — RMSLE captures this. It also fits whenever you care about percentage errors rather than absolute ones, which is why it is common in Kaggle competitions with skewed targets such as store sales or ticket counts.

Two caveats. RMSLE requires non-negative targets, since the log of a negative number is undefined. And it is asymmetric: under-prediction is penalized more than over-prediction, because $\log(1+y) - \log(1+\hat{y})$ is larger when $\hat{y} < y$. Depending on the task, that asymmetry can be a feature or a bug.

## R², the coefficient of determination

### R²

$$R^2 = 1 - \frac{\sum_i (y_i - \hat{y}_i)^2}{\sum_i (y_i - \bar{y})^2} = 1 - \frac{\text{SS}_{res}}{\text{SS}_{tot}}$$

R² is the proportion of variance in $y$ explained by the model. The formula compares the model's MSE to the MSE of a trivial "always predict the mean" model — the fraction of variance explained. The reading of values:

- $R^2 = 1$: perfect predictions.
- $R^2 = 0$: the model is no better than predicting the mean.
- $R^2 < 0$: the model is worse than predicting the mean, which is possible for bad models on test data.

R² is the right choice when you want a unitless, bounded measure of "how much of the variation does the model explain," and it doubles as a quick sanity check: an $R^2 < 0.5$ on a simple task suggests the model is missing something fundamental.

Two pitfalls matter in practice. First, **adding features always increases R²** (or keeps it the same), even if the features are noise, because more features give the model more capacity to fit the training data — the overfitting dynamics of [[Bias Variance Tradeoff]] showing up inside the metric itself. Use adjusted R² to correct for this. Second, R² is only meaningful for in-distribution evaluation: on out-of-distribution data, R² can be arbitrarily negative.

### Adjusted R²

$$R^2_{adj} = 1 - \frac{(1 - R^2)(n - 1)}{n - p - 1}$$

where $p$ is the number of features. Adjusted R² is R² penalized for the number of features: adding a feature increases $R^2_{adj}$ only if the feature improves the model more than would be expected by chance.

Use it when comparing models with different numbers of features, and to guard against overfitting from adding irrelevant features — the modeling-side remedy for that problem is [[Regularization Techniques]]. The caveat: the formula assumes linear regression specifically, and it is less meaningful for other model types.

## Mean absolute percentage error (MAPE)

$$\text{MAPE} = \frac{100\%}{n} \sum_{i=1}^n \left| \frac{y_i - \hat{y}_i}{y_i} \right|$$

MAPE is the average percentage error — unitless, which is exactly its appeal. Use it when you want to compare error rates across datasets with different scales, and when stakeholders think in percentages ("we're off by 5% on average").

Three pitfalls, all rooted in the denominator:

- **Undefined when $y_i = 0$** — division by zero, so all targets must be non-zero.
- **Asymmetric** — over-predictions are penalized less than under-predictions, because the denominator is $y_i$, so errors when $y_i$ is small produce large percentages.
- **Infinite** if any $y_i$ is very small relative to the error.

> [!warning] MAPE and small targets
> MAPE's percentage framing collapses when targets approach zero. A \$1 error on a \$2 actual value is a 50% error; the same \$1 error on a \$2,000 actual value is negligible. If the target distribution has mass near zero — or contains zeros — prefer MAE, RMSE, or RMSLE.

## Losses versus metrics: where Huber fits

MSE and MAE are both loss functions (used in training) and metrics (used in evaluation), but the two roles do not have to be played by the same formula. A common and healthy split: train with MSE for smooth gradients, evaluate with MAE for interpretability and robustness. This is fine — the loss determines what the model optimizes; the metric determines how you judge it. The full loss-side treatment is in [[Loss Functions]].

The most popular bridge between the two roles is **Huber loss** — smooth like MSE near zero, robust like MAE for large errors — with the pattern: train with Huber, evaluate with MAE or RMSE. Huber is:

$$L_\delta(y, \hat{y}) = \begin{cases} \frac{1}{2}(y - \hat{y})^2 & \text{if } |y - \hat{y}| \leq \delta \\ \delta(|y - \hat{y}| - \frac{1}{2}\delta) & \text{otherwise} \end{cases}$$

This combines MSE's smooth gradients (for well-predicted samples) with MAE's robustness (for outliers): a smooth combination of MSE for small errors and MAE for large errors that remains differentiable, which is why it is often used as the regression loss in deep learning.

## Choosing a regression metric

| Situation | Recommended metric |
| :--- | :--- |
| Interpretable error in target units, outliers present | MAE |
| Outliers matter heavily, training loss | MSE |
| Reporting quality in target units, outliers matter | RMSE |
| Target spans multiple orders of magnitude | RMSLE |
| "How much variance is explained?" | R² (or Adjusted R²) |
| Comparing across datasets/scales, stakeholder communication | MAPE |
| Skewed count targets (sales, clicks) | RMSLE or log-transform + MSE |

The rows trace back to three questions. Outlier sensitivity: should a rare large error dominate the verdict (MSE, RMSE) or contribute only its own magnitude (MAE)? Target scale: is the target homogeneous, so absolute errors make sense, or spread over orders of magnitude, so relative errors do (RMSLE, or a log-transform plus MSE for skewed counts)? Interpretation: does the audience need target units (MAE, RMSE), explained variance (R², adjusted when feature counts differ), or percentages (MAPE, with its zero-target caveat)?

In compressed form: MAE is the robust, interpretable baseline; MSE is the outlier-sensitive default training loss and the maximum-likelihood choice under Gaussian noise; RMSE is MSE in reportable units and the standard for reporting; RMSLE scores relative errors for multi-magnitude targets; R² explains variance but inflates as features are added, so adjust it when comparing feature sets; MAPE speaks percentages but is undefined at zero and asymmetric. And the training loss and evaluation metric need not match — train with MSE for smooth gradients, evaluate with MAE for robustness.

## Classification metrics as context

Regression metrics judge distance from the truth; classification metrics judge the kind of mistake made. Both families descend from the same discipline — the metric must mirror the business objective — and the classification vocabulary recurs throughout evaluation work, so the core concepts are summarized here for orientation. The full treatment, including worked examples, threshold analysis, and decision frameworks, is consolidated in [[Model Evaluation Metrics]].

### Accuracy

$$
\text{Accuracy} = \frac{\text{correct predictions}}{\text{total predictions}}
$$

Accuracy is simple and intuitive, but **misleading on imbalanced data**. A spam filter that always says "not spam" gets 99% accuracy if 1% of emails are spam — and is useless. The same degenerate majority-prediction pattern reappears wherever a single aggregate is dominated by the most frequent label, most famously as pixel accuracy in image segmentation.

### Precision and recall

All finer-grained classification metrics are derived from the four counts of the confusion matrix:

|                 | Predicted Positive | Predicted Negative |
|-----------------|---------------------|--------------------|
| Actual Positive | TP (true positive)  | FN (false negative)|
| Actual Negative | FP (false positive) | TN (true negative) |

$$
\text{Precision} = \frac{TP}{TP + FP} \quad \text{(of predicted positives, how many are actually positive)}
$$

$$
\text{Recall} = \frac{TP}{TP + FN} \quad \text{(of actual positives, how many did we catch)}
$$

The two trade off against each other: high precision means few false positives; high recall means few false negatives. Which matters more depends on the cost of each error type. For a **spam filter**, precision matters more, because false positives mean real email landing in the spam folder. For **cancer screening**, recall matters more, because false negatives mean missed cancer.

### F1 score

$$
F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}
$$

F1 is the harmonic mean of precision and recall, and it favors balanced precision/recall. Use **F-beta** to weight recall (beta > 1) or precision (beta < 1) when the error costs are asymmetric.

### The wider metric landscape

Beyond the basics, a few names recur and are worth recognizing. The **ROC curve** plots true positive rate (recall) versus false positive rate as the decision threshold varies; its **AUC** is the probability that the model ranks a random positive above a random negative, with 0.5 meaning random and 1.0 meaning perfect. AUC is threshold-independent — useful when no threshold has been picked yet — and insensitive to class imbalance, which makes it useful for comparing models on imbalanced data; but it can be misleading on highly imbalanced data, where PR-AUC is the better choice. **Log loss** (cross-entropy) penalizes confident wrong predictions heavily and is the standard loss for classification; lower is better.

For $K$-class problems, **macro F1** averages F1 across classes and treats all classes equally, **micro F1** aggregates TP/FP/FN across classes before computing F1 and favors larger classes, and **top-k accuracy** is the fraction of examples where the true class is in the top-k predictions — common for ImageNet-style evaluation (top-5). Search, recommendation, and retrieval problems bring a ranking family: **NDCG** rewards relevant items at the top of a ranking and discounts by rank, **MRR** takes the reciprocal of the rank of the first relevant item, **MAP** averages precision across all relevant items, and **Hit Rate@K** is the fraction of queries where any relevant item is in the top K. One terminology warning: ranking MAP collides by name with the detection metric mAP@IoU used in computer vision — the two are different constructions that happen to share a name, so check which family is meant whenever "mean average precision" appears.

Finally, **calibration** asks whether predicted probabilities match empirical frequencies: if the model says "80% chance of spam" 100 times, about 80 should actually be spam. The **reliability diagram** bins predictions by predicted probability and plots predicted versus empirical frequency — a calibrated model's curve lies on the diagonal — and **Expected Calibration Error (ECE)** is the average distance from that diagonal. Miscalibration has standard fixes: temperature scaling (divide the logits by a learned scalar $T$ — cheap and effective), Platt scaling (fit a logistic regression on the logits), and isotonic regression (nonparametric). Modern neural networks are notoriously miscalibrated — overconfident, as shown by Guo et al. (2017) — and temperature scaling is almost always worth applying.

## Evaluation practice

### Why the metric choice matters

Choosing the right metric is the difference between shipping a useful model and shipping a useless one: a model with 99% accuracy can be worthless if the 1% errors are catastrophic. Most machine-learning mistakes are evaluation mistakes — leaking test data, optimizing the wrong metric, ignoring calibration, evaluating on a non-representative sample. The same concepts carry into LLM evaluation as well, which inherits precision/recall for classification benchmarks, log loss for perplexity, and calibration for probability outputs.

### Production guidance

Pick the metric before the model: if you cannot articulate what "good" looks like in business terms, you are not ready to train. Track multiple metrics, because accuracy alone hides precision/recall tradeoffs and F1 alone hides calibration. Always evaluate on held-out data, and use cross-validation when data is small. For imbalanced data, prefer PR-AUC and macro F1 over accuracy. Calibrate before deploying — temperature scaling takes five minutes and prevents overconfident wrong predictions. For high-stakes decisions, track the cost matrix (FP and FN have different costs) rather than aggregate metrics.

### Common pitfalls

The recurring evaluation mistakes cut across families: using accuracy on imbalanced data, which is almost always misleading; optimizing ROC-AUC when you actually need precision at a fixed recall, which is a different objective; forgetting that probabilities need calibration, so the model's "90%" might mean "70%"; test set leakage through feature engineering on the whole dataset or ignored time-based splits; and reporting only the best metric across hyperparameters, which overstates performance — use nested cross-validation instead.

### Computing metrics in practice

`sklearn.metrics` is the standard tool for computing evaluation metrics, and the same module serves both the classification and regression families — the imports below pull the classification metrics alongside the regression pair `mean_squared_error` and `r2_score`. The minimal worked example shows the classification toolkit in a few lines, with expected outputs as comments; note how the headline number (accuracy 0.8) would hide the recall of 0.667:

```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, log_loss, mean_squared_error, r2_score
)

# Binary classification
y_true = [1, 0, 1, 1, 0]
y_pred = [1, 0, 1, 0, 0]
y_prob = [0.9, 0.1, 0.8, 0.4, 0.2]  # predicted probabilities

print(accuracy_score(y_true, y_pred))   # 0.8
print(precision_score(y_true, y_pred))  # 1.0
print(recall_score(y_true, y_pred))     # 0.667
print(f1_score(y_true, y_pred))         # 0.8
print(roc_auc_score(y_true, y_prob))    # 1.0
print(log_loss(y_true, y_prob))         # 0.36
```

For regression, the same module's `mean_squared_error` and `r2_score` (plus MAE and the others discussed above) plug into the identical workflow: run the model on held-out data, collect predictions, and hand them to the metric functions.

### Further reading

For deeper study, three references stand out: Hastie, Tibshirani, and Friedman, *The Elements of Statistical Learning*, Chapter 7 (model assessment); Guo et al. (2017), *On Calibration of Modern Neural Networks*; and Washburn et al. (2023), *A Note on ML Evaluation Metrics*, a good survey.

## See also

- [[Machine Learning MOC]]
- [[Model Evaluation Metrics]]
- [[Regression Fundamentals]]
- [[04 - Machine Learning/Regression/Linear Regression|Linear Regression]]
- [[04 - Machine Learning/Regression/Logistic Regression|Logistic Regression]]
- [[Loss Functions]]
- [[Gradient Descent]]
- [[Bias Variance Tradeoff]]
- [[Regularization Techniques]]
- [[Entropy Cross-Entropy and KL Divergence]]
- [[Agents and Tooling MOC]]
