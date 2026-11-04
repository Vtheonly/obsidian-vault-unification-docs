---
title: Linear Regression
type: example
aliases:
  - "Q7 - Linear Regression"
  - "Linear Regression Quiz"
  - "Simple Linear Regression Quiz"
tags:
  - deep-learning
  - quiz
  - practice
  - linear-regression
  - mean-squared-error
  - gradient-descent
  - normal-equation
  - ols
  - vectorization
  - feature-scaling
  - z-score
  - min-max-normalization
sources:
  - "Q7 - Linear Regression"
created_index: 15
---

This quiz bank practices linear regression, the first trainable model in most deep learning courses and the template for everything that follows. Its thirty questions cover the hypothesis and its parameters, the Mean Squared Error cost and the 1/2m factor that cleans its derivative, simultaneous gradient updates, the Normal Equation and when iterative optimization beats it, vectorized batch predictions, and the two feature scaling methods with their outlier behavior. The full treatment lives in [[04 - Machine Learning/Regression/Linear Regression|Linear Regression]] and [[Regression Fundamentals]], with the metrics that judge the fit in [[Regression Evaluation Metrics]]; commit to an answer before unfolding it.

## True or false

Ten statements open the quiz: three on the model and its hypothesis, two on the cost function and how its parameters must be updated, two on vectorization and the Normal Equation, and three on feature scaling and the analytical solver. The false statements assign the wrong role to a parameter or the wrong property to a method — the bias wearing the slope's job, the Normal Equation called iterative — so check each claim against the definitions before deciding.

### The model and its hypothesis

Three statements on what linear regression predicts, the form of the hypothesis in the simple case, and which parameter actually carries the slope.

> [!question] Linear regression predicts a continuous output Y based on input X.
>> [!success]- Answer
>> True

> [!question] In simple linear regression, the hypothesis function is Y = wX + b.
>> [!success]- Answer
>> True

> [!question] The bias term (theta_0) represents the slope of the regression line.
>> [!success]- Answer
>> False

### Cost and updates

Two statements on the cost function being minimized and how the two parameters must be treated during each gradient descent step.

> [!question] The cost function for linear regression is the Mean Squared Error (MSE).
>> [!success]- Answer
>> True

> [!question] In gradient descent for linear regression, theta_0 and theta_1 must be updated simultaneously.
>> [!success]- Answer
>> True

### Vectorization and the Normal Equation

Two statements on matrix operations replacing loops, and on what kind of solution the Normal Equation actually delivers.

> [!question] Vectorization replaces slow for-loops with fast matrix operations.
>> [!success]- Answer
>> True

> [!question] The Normal Equation gives an approximate solution that requires iteration.
>> [!success]- Answer
>> False

### Scaling and solvers

Three statements on why feature scaling rounds the loss landscape, which scaling method tolerates outliers better, and what kind of solution OLS provides.

> [!question] Feature scaling helps gradient descent converge faster by making the loss landscape more circular.
>> [!success]- Answer
>> True

> [!question] Min-Max Normalization is more robust to outliers than Z-score Standardization.
>> [!success]- Answer
>> False

> [!question] OLS (Ordinary Least Squares) is the analytical solution for linear regression.
>> [!success]- Answer
>> True

## Multiple choice

Ten questions walk through the mechanics: the vectorized hypothesis, the reason updates must be simultaneous, the 1/2m trick, the Normal Equation and its cubic price, the two scaling methods, and the matrix formulation for batch predictions. Several formula options differ by a single transpose or inverse, so read them closely.

### Hypothesis, updates, and the cost's constants

Three questions on the vectorized form of the hypothesis, why both parameters must move together, and the purpose of the 1/2m factor in the MSE cost.

> [!question] What is the vectorized form of the hypothesis function?
> a) h(x) = theta_0 + theta_1 * x
> b) h(x) = theta^T * x
> c) h(x) = sigmoid(theta^T * x)
> d) h(x) = max(0, theta^T * x)
>> [!success]- Answer
>> b) h(x) = theta^T * x

> [!question] Why must theta_0 and theta_1 be updated simultaneously?
> a) It is faster computationally
> b) Sequential updates use a different point on the loss surface, leading to incorrect gradient
> c) It reduces the learning rate
> d) It makes the loss function convex
>> [!success]- Answer
>> b) Sequential updates use a different point on the loss surface, leading to incorrect gradient

> [!question] What does the 1/2m trick in the MSE cost function accomplish?
> a) It makes the loss larger
> b) It simplifies the derivative by canceling the exponent 2
> c) It handles outliers
> d) It changes the minimum
>> [!success]- Answer
>> b) It simplifies the derivative by canceling the exponent 2

### The Normal Equation and its price

Three questions on the closed-form solution itself, when gradient descent is the better choice, and the complexity of the matrix inverse it requires.

> [!question] What is the Normal Equation?
> a) W = X^T Y
> b) W = (X^T X)^{-1} X^T Y
> c) W = X Y^{-1}
> d) W = gradient * alpha
>> [!success]- Answer
>> b) W = (X^T X)^{-1} X^T Y

> [!question] When should you use Gradient Descent instead of OLS?
> a) When the dataset is small
> b) When you need the exact solution
> c) When the dataset is large or the model is non-linear
> d) When features are few
>> [!success]- Answer
>> c) When the dataset is large or the model is non-linear

> [!question] What is the complexity of computing the Normal Equation inverse?
> a) O(n)
> b) O(m^3) where m is the number of features
> c) O(1)
> d) O(log n)
>> [!success]- Answer
>> b) O(m^3) where m is the number of features

### Scaling the features

Two questions on what Z-score standardization produces and why a single outlier can ruin Min-Max normalization.

> [!question] What does Z-score standardization do?
> a) Scales data to [0, 1]
> b) Centers data to mean 0 and standard deviation 1
> c) Removes all outliers
> d) Converts data to integers
>> [!success]- Answer
>> b) Centers data to mean 0 and standard deviation 1

> [!question] Why is Min-Max Normalization vulnerable to outliers?
> a) It uses the mean
> b) A single extreme outlier compresses all other values into a tiny range
> c) It removes outliers
> d) It squares the values
>> [!success]- Answer
>> b) A single extreme outlier compresses all other values into a tiny range

### Matrices and variables

Two questions closing the round: the matrix formulation for batch predictions and the name for the variable being predicted.

> [!question] What is the matrix formulation for batch predictions in linear regression?
> a) Y_hat = X + W + b
> b) Y_hat = XW + b
> c) Y_hat = X * W * b
> d) Y_hat = X / W
>> [!success]- Answer
>> b) Y_hat = XW + b

> [!question] What is the endogenous variable in linear regression?
> a) The independent variable X
> b) The dependent variable Y being predicted
> c) The weight theta_1
> d) The bias theta_0
>> [!success]- Answer
>> b) The dependent variable Y being predicted

## Matching

Ten matching questions pair the model's parameters and variables with their meanings, the scaling methods with their formulas, robustness, and output ranges, the two solvers with their characteristics and their ideal regimes, and the update rules and partial derivatives with their consequences. The groups are shuffled independently, so match on meaning rather than position.

### Vocabulary and formulas

One question on the model's parameters and variables, and one pairing each scaling method with its formula.

> [!question] Match the term with its meaning in linear regression.
>> [!example] Group A
>> a) theta_0 (bias)
>> b) theta_1 (weight)
>> c) Endogenous variable
>> d) Exogenous variable
>
>> [!example] Group B
>> n) Independent variable X
>> o) Dependent variable Y
>> p) Slope — how much Y changes per unit of X
>> q) Y-intercept — prediction when all inputs are zero
>
>> [!success]- Answer
>> a) -> q)
>> b) -> p)
>> c) -> o)
>> d) -> n)

> [!question] Match the scaling method with its formula.
>> [!example] Group A
>> a) Min-Max Normalization
>> b) Z-score Standardization
>
>> [!example] Group B
>> n) (x - mu) / sigma
>> o) (x - x_min) / (x_max - x_min)
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

### Solvers and robustness

One question on what each solution method delivers, and one on which scaling method survives an extreme outlier.

> [!question] Match the solution method with its characteristic.
>> [!example] Group A
>> a) OLS (Normal Equation)
>> b) Gradient Descent
>
>> [!example] Group B
>> n) Iterative approximation, scales to large datasets
>> o) Exact analytical solution, O(m^3) complexity
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

> [!question] Match the scaling method with its outlier robustness.
>> [!example] Group A
>> a) Min-Max Normalization
>> b) Z-score Standardization
>
>> [!example] Group B
>> n) More robust — does not compress range
>> o) Vulnerable — extreme outlier compresses all values
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

### Updates and gradients

One question on why simultaneous updates are the correct procedure, and one on which partial derivative updates which parameter.

> [!question] Match the update approach with its correctness.
>> [!example] Group A
>> a) Simultaneous update
>> b) Sequential update
>
>> [!example] Group B
>> n) Incorrect — uses different point on loss surface
>> o) Correct — all gradients computed at the same point
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

> [!question] Match the partial derivative with the parameter it updates.
>> [!example] Group A
>> a) Average error (no x weighting)
>> b) Error weighted by x_i
>
>> [!example] Group B
>> n) Derivative for theta_1 (weight)
>> o) Derivative for theta_0 (bias)
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

### Benefits and choices

One question on what vectorization and feature scaling each buy you, and one on when to reach for OLS versus gradient descent.

> [!question] Match the concept with its benefit.
>> [!example] Group A
>> a) Vectorization
>> b) Feature Scaling
>
>> [!example] Group B
>> n) Makes the loss landscape more circular for faster convergence
>> o) Replaces for-loops with fast matrix operations
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

> [!question] Match the approach with when to use it.
>> [!example] Group A
>> a) OLS / Normal Equation
>> b) Gradient Descent
>
>> [!example] Group B
>> n) Large dataset or many features or non-linear model
>> o) Small dataset with few features
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

### Dimensions and ranges

One question on the shapes of X, W, and Y_hat, and one on the output range each scaling method produces.

> [!question] Match the matrix dimension with the variable.
>> [!example] Group A
>> a) n x m matrix
>> b) m x 1 vector
>> c) n x 1 vector
>
>> [!example] Group B
>> n) Y_hat (predictions)
>> o) X (feature matrix)
>> p) W (weights)
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> n)

> [!question] Match the scaling method with its output range.
>> [!example] Group A
>> a) Min-Max Normalization
>> b) Z-score Standardization
>
>> [!example] Group B
>> n) Mean 0, standard deviation 1
>> o) Strictly [0, 1]
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

## See also

- [[04 - Machine Learning/Regression/Linear Regression|Linear Regression]]
- [[Regression Fundamentals]]
- [[Regression Evaluation Metrics]]
- [[Gradient Descent]]
- [[Feature Scaling and Normalization]]
- [[Outlier Detection and Treatment]]
- [[Matrix Multiplication]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 1/Logistic Regression|Logistic Regression]]
- [[Loss Functions and Cost Optimization]]
- [[Gradient Descent Optimization]]
- [[Multi-Layer Perceptron and Backpropagation]]
- [[Glossary MOC]]
