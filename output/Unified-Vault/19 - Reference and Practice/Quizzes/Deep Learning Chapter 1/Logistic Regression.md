---
title: Logistic Regression
type: example
aliases:
  - "Q8 - Logistic Regression"
  - "Logistic Regression Quiz"
  - "Sigmoid and Log Loss Quiz"
tags:
  - deep-learning
  - quiz
  - practice
  - logistic-regression
  - classification
  - sigmoid
  - binary-cross-entropy
  - log-loss
  - logit
  - odds
  - decision-boundary
sources:
  - "Q8 - Logistic Regression"
created_index: 16
---

This quiz bank practices logistic regression, the classification algorithm that hides behind a regression name. Its thirty questions cover why linear regression fails on binary targets, the sigmoid and the decision boundary it induces, the non-convexity that rules out MSE and the convexity that makes binary cross-entropy the standard loss, the gradient's resemblance to the linear regression gradient, and the odds and logit transformations that connect probabilities to a linear model. The concepts are developed in [[04 - Machine Learning/Regression/Logistic Regression|Logistic Regression]] and [[04 - Machine Learning/Regression/Linear Regression|Linear Regression]]; unfold each answer only after committing.

## True or false

Ten statements open the quiz: two on the algorithm's true nature, three on the sigmoid and the boundary it creates, three on loss landscape geometry, and two on odds and logits. Several false statements describe the right object with the wrong property — a sigmoid value of zero at the origin, a logit range of [0, 1] — which are exactly the slips this round is built to catch.

### A classifier in regression clothing

Two statements on what the algorithm actually does and what goes wrong when linear regression is pressed into classification duty.

> [!question] Despite its name, Logistic Regression is a classification algorithm, not a regression algorithm.
>> [!success]- Answer
>> True

> [!question] Linear regression can output invalid probabilities (below 0 or above 1) for classification.
>> [!success]- Answer
>> True

### The sigmoid and the decision boundary

Three statements on the squashing function, its value at zero, and the line where the classes change.

> [!question] The Sigmoid function squashes any input into a value between 0 and 1.
>> [!success]- Answer
>> True

> [!question] When z = 0, the Sigmoid function outputs 0.
>> [!success]- Answer
>> False

> [!question] The decision boundary in logistic regression is defined by theta^T * x = 0.
>> [!success]- Answer
>> True

### Loss landscape geometry

Three statements on what MSE does to the landscape, what cross-entropy guarantees, and how the gradient formula compares to linear regression's.

> [!question] Using MSE with a Sigmoid activation produces a convex loss landscape.
>> [!success]- Answer
>> False

> [!question] Binary Cross-Entropy (Log Loss) guarantees a convex landscape for logistic regression.
>> [!success]- Answer
>> True

> [!question] The gradient formula for Logistic Regression with Log Loss looks identical to the Linear Regression gradient formula.
>> [!success]- Answer
>> True

### Odds and logits

Two statements on the range of the odds ratio and the logit's output space.

> [!question] The Odds ratio can range from 0 to +infinity.
>> [!success]- Answer
>> True

> [!question] The Logit function maps probabilities to the range [0, 1].
>> [!success]- Answer
>> False

## Multiple choice

Ten questions trace the causal chain: the sigmoid formula and its limits, the three-fold failure of linear regression for classification, the cross-entropy loss and its penalty for confident mistakes, and the odds and logit functions that linearize probability. Read the formula options closely — one sign or one parenthesis separates several of them.

### The sigmoid function

Two questions on the formula and the limit as z approaches +infinity.

> [!question] What is the Sigmoid function formula?
> a) g(z) = max(0, z)
> b) g(z) = 1 / (1 + e^{-z})
> c) g(z) = z^2
> d) g(z) = tanh(z)
>> [!success]- Answer
>> b) g(z) = 1 / (1 + e^{-z})

> [!question] What does the Sigmoid output when z approaches +infinity?
> a) 0
> b) 0.5
> c) 1
> d) -1
>> [!success]- Answer
>> c) 1

### From linear failure to logistic fix

Three questions on why linear regression fails, where the decision boundary sits, and why MSE is the wrong loss.

> [!question] Why does linear regression fail for classification?
> a) It is too slow
> b) It can output values outside [0,1], provides poor fit to binary data, and creates non-convex loss
> c) It requires too many features
> d) It only works with images
>> [!success]- Answer
>> b) It can output values outside [0,1], provides poor fit to binary data, and creates non-convex loss

> [!question] What is the decision boundary in logistic regression?
> a) The point where the prediction equals the true label
> b) The line where theta^T * x = 0, separating class 0 and class 1
> c) The maximum probability
> d) The training data mean
>> [!success]- Answer
>> b) The line where theta^T * x = 0, separating class 0 and class 1

> [!question] Why is MSE bad for logistic regression?
> a) It is too fast
> b) Combining sigmoid non-linearity with squared error creates a non-convex landscape with local minima
> c) It produces only integer outputs
> d) It works only for regression
>> [!success]- Answer
>> b) Combining sigmoid non-linearity with squared error creates a non-convex landscape with local minima

### Binary cross-entropy

Two questions on the loss formula and its behavior when a confident wrong prediction meets a true label of 1.

> [!question] What is the Binary Cross-Entropy formula?
> a) Average of squared errors
> b) -1/n * sum[y*log(y_hat) + (1-y)*log(1-y_hat)]
> c) sum of |y - y_hat|
> d) max(0, 1 - y*y_hat)
>> [!success]- Answer
>> b) -1/n * sum[y*log(y_hat) + (1-y)*log(1-y_hat)]

> [!question] What happens to Log Loss when the true label is 1 and the model predicts 0?
> a) Loss is 0
> b) Loss is 1
> c) Loss approaches infinity
> d) Loss is -1
>> [!success]- Answer
>> c) Loss approaches infinity

### Odds, logit, and linear log-odds

Three questions on the odds ratio, the logit's mapping, and why the model linearizes log-odds rather than probabilities.

> [!question] What is the Odds ratio formula?
> a) p / (1 - p)
> b) log(p)
> c) p * (1 - p)
> d) 1 / p
>> [!success]- Answer
>> a) p / (1 - p)

> [!question] What does the Logit (log-odds) function do?
> a) Maps [0,1] probabilities to the full real number line (-inf to +inf)
> b) Maps real numbers to [0,1]
> c) Computes the squared error
> d) Calculates the gradient
>> [!success]- Answer
>> a) Maps [0,1] probabilities to the full real number line (-inf to +inf)

> [!question] Why does Logistic Regression model linear log-odds instead of linear probabilities?
> a) Because probabilities are always negative
> b) Because log-odds map bounded probabilities to the full real line, making them compatible with linear models
> c) Because log-odds are easier to visualize
> d) Because probabilities do not exist
>> [!success]- Answer
>> b) Because log-odds map bounded probabilities to the full real line, making them compatible with linear models

## Matching

Ten matching questions pair sigmoid inputs with outputs, cost functions with the landscapes they produce, log loss pieces with labels, formulas with concepts, and prediction scenarios with their penalties. The groups are shuffled independently, so match on meaning rather than position.

### Sigmoid inputs, outputs, and derivatives

Two questions on the function's limiting values and the derivative formula with its peak.

> [!question] Match the Sigmoid input with its output.
>> [!example] Group A
>> a) z -> +infinity
>> b) z = 0
>> c) z -> -infinity
>
>> [!example] Group B
>> n) 0 (confident negative prediction)
>> o) 0.5 (uncertain — decision boundary)
>> p) 1 (confident positive prediction)
>
>> [!success]- Answer
>> a) -> p)
>> b) -> o)
>> c) -> n)

> [!question] Match the property with the Sigmoid derivative.
>> [!example] Group A
>> a) Maximum derivative value
>> b) Derivative formula
>
>> [!example] Group B
>> n) sigma(x) * (1 - sigma(x))
>> o) 0.25 (at x = 0)
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

### Cost functions and their landscapes

Three questions on MSE versus log loss, which piece of the loss applies to which label, and how confident mistakes are punished.

> [!question] Match the cost function with the landscape it produces for logistic regression.
>> [!example] Group A
>> a) MSE
>> b) Log Loss (BCE)
>
>> [!example] Group B
>> n) Convex — guaranteed global minimum
>> o) Non-convex — many local minima
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

> [!question] Match the Log Loss piece with the true label.
>> [!example] Group A
>> a) -log(h(x))
>> b) -log(1 - h(x))
>
>> [!example] Group B
>> n) When y = 0
>> o) When y = 1
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

> [!question] Match the prediction scenario with its Log Loss penalty.
>> [!example] Group A
>> a) y=1, y_hat=0.99
>> b) y=1, y_hat=0.01
>> c) y=0, y_hat=0.01
>
>> [!example] Group B
>> n) Very large penalty (confidently wrong)
>> o) Minimal penalty (correct and confident)
>> p) Minimal penalty (correct — prediction near 0)
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)

### Formulas, failures, and definitions

Three questions matching odds, logit, and sigmoid to their formulas, the three problems with linear regression to their descriptions, and the model's core concepts to their meanings.

> [!question] Match the concept with its formula.
>> [!example] Group A
>> a) Odds
>> b) Logit (Log-Odds)
>> c) Sigmoid
>
>> [!example] Group B
>> n) 1 / (1 + e^{-z})
>> o) p / (1 - p)
>> p) log(p / (1 - p))
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> n)

> [!question] Match the problem with linear regression for classification.
>> [!example] Group A
>> a) Invalid predictions
>> b) Poor fit
>> c) Non-convex loss
>
>> [!example] Group B
>> n) Binary data forms two clusters, not a line
>> o) Sigmoid + MSE creates hills and valleys
>> p) Line outputs values below 0 and above 1
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

> [!question] Match the logistic regression concept with its meaning.
>> [!example] Group A
>> a) Decision boundary
>> b) h(x) >= 0.5
>> c) h(x) < 0.5
>
>> [!example] Group B
>> n) Predict Class 0
>> o) Predict Class 1
>> p) The line theta^T * x = 0 separating classes
>
>> [!success]- Answer
>> a) -> p)
>> b) -> o)
>> c) -> n)

### The gradient connection to linear regression

One question separating what is true and what is false about the gradient formulas of linear and logistic regression.

> [!question] Match the statement about gradient formulas with its correctness.
>> [!example] Group A
>> a) LR and LogReg have identical gradient formulas
>> b) h_theta(x) is the same in both
>
>> [!example] Group B
>> n) False — h(x) is linear in LR and sigmoid in LogReg
>> o) True — the final formula structure is identical, but h(x) differs
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

### Logit properties

One question tying the logit's two properties — its unbounded range and its linear model — to their implications.

> [!question] Match the Logit property with its implication.
>> [!example] Group A
>> a) Logit maps p to (-inf, +inf)
>> b) Logit(P(Y=1|X)) = theta^T * x
>
>> [!example] Group B
>> n) Compatible with linear models — each weight represents change in log-odds per unit feature
>> o) Probabilities can be modeled with a linear function
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

## See also

- [[04 - Machine Learning/Regression/Logistic Regression|Logistic Regression]]
- [[04 - Machine Learning/Regression/Linear Regression|Linear Regression]]
- [[Activation Functions]]
- [[Loss Functions]]
- [[Entropy Cross-Entropy and KL Divergence]]
- [[Gradient Descent]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 1/Linear Regression|Linear Regression]]
- [[Gradient Descent Optimization]]
- [[Loss Functions and Cost Optimization]]
- [[Glossary MOC]]
