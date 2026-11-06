---
title: Loss Functions and Cost Optimization
type: example
aliases:
  - "Q6 - Loss Functions and Cost Optimization"
  - "Loss Functions and Cost Optimization Quiz"
  - "Loss Functions Quiz"
tags:
  - deep-learning
  - quiz
  - practice
  - loss-functions
  - mean-squared-error
  - mean-absolute-error
  - huber-loss
  - binary-cross-entropy
  - categorical-cross-entropy
  - hinge-loss
  - log-loss
  - outliers
sources:
  - "Q6 - Loss Functions and Cost Optimization"
created_index: 17
---

This quiz bank practices loss functions and cost optimization, the machinery that turns a network's raw outputs into a single number worth minimizing. Its thirty questions cover the regression losses — MSE, MAE, and the Huber compromise between them — the classification losses from binary and categorical cross-entropy to hinge loss, and the practical details that decide between them: outlier sensitivity, gradient behavior near zero, landscape convexity, and the activation each loss expects at the output layer. The concepts are developed in [[Loss Functions]] and [[Entropy Cross-Entropy and KL Divergence]], with the regression side of the story in [[04 - Machine Learning/Regression/Linear Regression|Linear Regression]]; commit to an answer before unfolding it.

## True or false

Ten statements open the quiz: three on the regression family of MSE, MAE, and Huber loss, five on the classification losses and what happens when they are misused, and two on gradient behavior and activation pairings. The false statements swap a property between neighbors — MAE wearing MSE's outlier sensitivity, MAE claiming MSE's shrinking gradient — which is exactly the confusion this round is built to catch.

### The regression losses

Three statements on the workhorses of regression: what MSE stands for, which of MSE and MAE is the outlier-sensitive one, and how Huber loss splits the difference between them.

> [!question] MSE stands for Mean Squared Error and is used for regression problems.
>> [!success]- Answer
>> True

> [!question] MAE is more sensitive to outliers than MSE.
>> [!success]- Answer
>> False

> [!question] Huber Loss behaves like MSE for small errors and like MAE for large errors.
>> [!success]- Answer
>> True

### Classification losses

Five statements on the classification family: the number of classes binary cross-entropy handles, what happens when MSE is pressed into classification duty, the label encoding categorical cross-entropy expects, hinge loss's home turf, and what the logarithm does to confident wrong predictions.

> [!question] Binary Cross-Entropy is used for multi-class classification with 5+ classes.
>> [!success]- Answer
>> False

> [!question] Using MSE for classification results in a non-convex loss landscape.
>> [!success]- Answer
>> True

> [!question] Categorical Cross-Entropy uses one-hot encoded labels.
>> [!success]- Answer
>> True

> [!question] Hinge Loss is primarily used for Support Vector Machines.
>> [!success]- Answer
>> True

> [!question] The logarithm in classification loss punishes confident wrong predictions exponentially.
>> [!success]- Answer
>> True

### Gradients and pairings

Two statements closing the round: how MAE's gradient behaves as the error approaches zero, and the activation that categorical cross-entropy is always paired with.

> [!question] MAE has a gradient that naturally decreases as the error approaches zero.
>> [!success]- Answer
>> False

> [!question] Categorical Cross-Entropy is always paired with the Softmax activation.
>> [!success]- Answer
>> True

## Multiple choice

Ten questions trace the decision chain: which loss fits which problem, what each one computes, why MSE is barred from classification, and how sharply each loss penalizes a confidently wrong prediction. Read the formula options closely — a single logarithm or exponent separates several of them.

### Choosing a regression loss

Three questions on picking between MSE and MAE under severe outliers, what MSE actually computes, and why a single outlier can dominate the squared loss.

> [!question] Which loss function is most appropriate for a regression problem with severe outliers?
> a) MSE
> b) MAE
> c) Binary Cross-Entropy
> d) Hinge Loss
>> [!success]- Answer
>> b) MAE

> [!question] What is the formula for MSE?
> a) Average of absolute differences
> b) Average of squared differences between predicted and actual values
> c) Sum of logarithms
> d) Max of differences
>> [!success]- Answer
>> b) Average of squared differences between predicted and actual values

> [!question] Why is MSE sensitive to outliers?
> a) It uses absolute values
> b) Errors are squared, so an outlier with error 10 contributes 100 to the loss
> c) It ignores outliers completely
> d) It uses logarithms
>> [!success]- Answer
>> b) Errors are squared, so an outlier with error 10 contributes 100 to the loss

### Huber, cross-entropy, and a warning about MSE

Three questions on Huber loss below its threshold, the standard loss for binary classification, and why MSE must never be used for it.

> [!question] What does Huber Loss do when the error is below the threshold delta?
> a) It acts like MAE
> b) It acts like MSE (quadratic)
> c) It acts like Cross-Entropy
> d) It becomes zero
>> [!success]- Answer
>> b) It acts like MSE (quadratic)

> [!question] Which loss function is used for binary classification?
> a) MSE
> b) MAE
> c) Binary Cross-Entropy (Log Loss)
> d) Huber Loss
>> [!success]- Answer
>> c) Binary Cross-Entropy (Log Loss)

> [!question] Why should you never use MSE for classification?
> a) It is too fast
> b) It produces a non-convex landscape with many local minima
> c) It only works with images
> d) It requires too much memory
>> [!success]- Answer
>> b) It produces a non-convex landscape with many local minima

### Penalty sizes and loss mechanics

Four questions on the size of the penalty when a model predicts 0.001 for a true label of 1, the margin that hinge loss enforces, the terms that actually contribute to categorical cross-entropy, and the reason for the 1/2m factor in the MSE cost.

> [!question] What happens to the penalty in Log Loss when the model predicts 0.001 for a true label of 1?
> a) The penalty is 0.001
> b) The penalty is approximately 0.99
> c) The penalty is very large (approximately 6.9)
> d) There is no penalty
>> [!success]- Answer
>> c) The penalty is very large (approximately 6.9)

> [!question] What is the key property of Hinge Loss?
> a) It always produces zero loss
> b) It forces predictions to be correct by a margin, not just correct
> c) It uses logarithms
> d) It only works for regression
>> [!success]- Answer
>> b) It forces predictions to be correct by a margin, not just correct

> [!question] In Categorical Cross-Entropy, which terms contribute to the loss?
> a) All class terms equally
> b) Only the term for the true class (because other y_ij are 0)
> c) Only the predicted class
> d) No terms contribute
>> [!success]- Answer
>> b) Only the term for the true class (because other y_ij are 0)

> [!question] Why does the 1/2m trick in MSE exist?
> a) To make MSE larger
> b) To make the derivative cleaner by canceling the exponent 2
> c) To change the optimization result
> d) To handle outliers
>> [!success]- Answer
>> b) To make the derivative cleaner by canceling the exponent 2

## Matching

Ten matching questions assign each loss to the problem it fits, rank the regression losses by outlier sensitivity, pair the classification losses with their class counts and activations, and probe behavior at the extremes — penalty sizes, gradients near zero, Huber's two regimes, and the outcome of each hinge condition. The groups are shuffled independently, so match on meaning rather than position.

### Use cases, classes, and outliers

Three questions assigning each loss to the use case it fits, ranking MSE, MAE, and Huber by outlier sensitivity, and separating binary from multi-class cross-entropy by class count.

> [!question] Match the loss function with its use case.
>> [!example] Group A
>> a) MSE
>> b) Binary Cross-Entropy
>> c) Categorical Cross-Entropy
>> d) Huber Loss
>
>> [!example] Group B
>> n) Multi-class classification
>> o) Regression with occasional outliers
>> p) Binary classification
>> q) Standard regression without severe outliers
>
>> [!success]- Answer
>> a) -> q)
>> b) -> p)
>> c) -> n)
>> d) -> o)

> [!question] Match the loss function with its sensitivity to outliers.
>> [!example] Group A
>> a) MSE
>> b) MAE
>> c) Huber Loss
>
>> [!example] Group B
>> n) Moderate — switches behavior at threshold delta
>> o) Low — each outlier contributes linearly
>> p) High — errors are squared
>
>> [!success]- Answer
>> a) -> p)
>> b) -> o)
>> c) -> n)

> [!question] Match the classification loss with the number of classes it handles.
>> [!example] Group A
>> a) Binary Cross-Entropy
>> b) Categorical Cross-Entropy
>
>> [!example] Group B
>> n) 3+ classes (multi-class)
>> o) 2 classes (binary)
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

### Penalty and gradient behavior

Two questions on the penalty log loss assigns to confident predictions and the way MSE and MAE gradients behave near zero.

> [!question] Match the loss behavior with the scenario.
>> [!example] Group A
>> a) Log Loss when y=1 and prediction=0.99
>> b) Log Loss when y=1 and prediction=0.01
>
>> [!example] Group B
>> n) Huge penalty (confidently wrong)
>> o) Minimal penalty (correct and confident)
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

> [!question] Match the loss function with its gradient behavior near zero.
>> [!example] Group A
>> a) MSE
>> b) MAE
>
>> [!example] Group B
>> n) Constant gradient (oscillates around minimum)
>> o) Gradient naturally decreases (smooth convergence)
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

### Regions, operations, and conditions

Three questions on Huber loss's two regimes, the raw mathematical operation behind each loss, and the outcome of each hinge loss condition.

> [!question] Match the Huber Loss region with its behavior.
>> [!example] Group A
>> a) Error <= delta
>> b) Error > delta
>
>> [!example] Group B
>> n) Linear (MAE-like, robust to outliers)
>> o) Quadratic (MSE-like, smooth convergence)
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

> [!question] Match the loss function with its mathematical operation.
>> [!example] Group A
>> a) MSE
>> b) MAE
>> c) Log Loss
>
>> [!example] Group B
>> n) Negative logarithm of predicted probability
>> o) Average of absolute differences
>> p) Average of squared differences
>
>> [!success]- Answer
>> a) -> p)
>> b) -> o)
>> c) -> n)

> [!question] Match the Hinge Loss condition with the outcome.
>> [!example] Group A
>> a) y * y_hat >= 1
>> b) 0 < y * y_hat < 1
>> c) y * y_hat < 0
>
>> [!example] Group B
>> n) Loss = 0 (correct with margin)
>> o) Loss > 1 (wrong prediction)
>> p) Loss > 0 (correct but too close to boundary)
>
>> [!success]- Answer
>> a) -> n)
>> b) -> p)
>> c) -> o)

### Pairings and penalty shapes

Two questions closing the round: the activation each cross-entropy variant expects, and which loss penalizes errors quadratically, linearly, or exponentially.

> [!question] Match the loss function with the paired activation.
>> [!example] Group A
>> a) BCE
>> b) CCE
>
>> [!example] Group B
>> n) Softmax
>> o) Sigmoid
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

> [!question] Match the property with the loss function.
>> [!example] Group A
>> a) Quadratic penalty on errors
>> b) Linear penalty on errors
>> c) Exponentially increasing penalty for confident wrong predictions
>
>> [!example] Group B
>> n) MAE
>> o) Log Loss / Cross-Entropy
>> p) MSE
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

## See also

- [[Loss Functions]]
- [[Entropy Cross-Entropy and KL Divergence]]
- [[04 - Machine Learning/Regression/Linear Regression|Linear Regression]]
- [[04 - Machine Learning/Regression/Logistic Regression|Logistic Regression]]
- [[Regression Evaluation Metrics]]
- [[Activation Functions]]
- [[Gradient Descent]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 1/Linear Regression|Linear Regression]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 1/Logistic Regression|Logistic Regression]]
- [[Gradient Descent Optimization]]
- [[Loss Functions and Optimizers Deep Dive]]
- [[Glossary MOC]]
