---
title: Logistic Regression
type: concept
aliases:
  - Logit Regression
  - Binary Logistic Regression
  - Softmax Regression
tags:
  - machine-learning
  - supervised-learning
  - regression
  - classification
  - logistic-regression
sources:
  - "Logistic Regression"
  - "02 - Linear and Logistic Regression"
created_index: 16
---

Despite the name "regression," logistic regression is strictly a **classification** algorithm: it predicts the probability that an instance belongs to a class (fraud vs. not fraud, pneumothorax vs. healthy, spam vs. not spam, malignant vs. benign tumor). It is one of the most widely used algorithms in both machine learning and deep learning — neural networks are essentially stacked logistic regression units, and together with linear regression it forms the conceptual basis for every neural network layer, which is why understanding it deeply makes the rest of ML make sense. This note builds the model from first principles: why linear regression fails for classification, how the sigmoid function fixes it, why log loss replaces squared error, how the gradient falls out of the math, and how the whole construction generalizes to many classes. The shared $X$/$y$ supervised-learning framing is set up in [[Regression Fundamentals]], and the continuous-target counterpart is [[04 - Machine Learning/Regression/Linear Regression|Linear Regression]].

## Why linear regression fails for classification

The classification setting has a discrete target: **binary classification** uses $y \in \{0, 1\}$ (e.g., spam/not spam, malignant/benign tumor), while **multi-class** problems use $y \in \{0, 1, 2, 3\}$. If we try to fit a straight line to binary data (0s and 1s), we face three fundamental problems:

1. **Invalid predictions:** the line will eventually output values below 0 and above 1, which are invalid probabilities. A prediction of -0.3 or 1.7 makes no sense for a binary outcome.
2. **Poor fit:** binary data forms two distinct clusters (at 0 and 1), and a straight line is a poor representation of this step-like pattern.
3. **Non-convex loss:** using MSE on classification creates a non-convex loss curve, trapping gradient descent in local minima. The optimization landscape becomes treacherous.

The linear model itself — a weighted sum of the inputs plus a bias, fit by minimizing **mean squared error (MSE)** — remains the right tool when the target is continuous. Its full treatment, including the closed-form solution via the **normal equations** (exact for small problems, but the matrix inverse costs $O(d^3)$, which is why large problems use gradient descent or SGD instead), **ridge (L2)** and **lasso (L1)** regularization, multicollinearity and its singular-matrix troubles, and the interpretation of MSE as maximum likelihood estimation under Gaussian noise, is covered in [[04 - Machine Learning/Regression/Linear Regression|Linear Regression]] and [[Regularization Techniques]]. This note is about what must change when the target is a class label.

## The sigmoid model form

The solution is to make the hypothesis output a value between 0 and 1 — a probability. We do this by passing our linear equation ($\theta^T x$) through the **sigmoid (logistic) function**:

$$ g(z) = \frac{1}{1 + e^{-z}} $$
$$ h(x) = g(\theta^T x) = \frac{1}{1 + e^{-\theta^T x}} $$

This "squashes" any linear output into a probability between 0 and 1. No matter how large or small $z$ is, the sigmoid output is always in the range $(0, 1)$. In the weight-and-bias notation used for probabilistic models, the same hypothesis reads:

$$ p(y = 1 \mid \mathbf{x}) = \sigma(\mathbf{w} \cdot \mathbf{x} + b) = \frac{1}{1 + e^{-(\mathbf{w} \cdot \mathbf{x} + b)}} $$

**Key properties of the sigmoid:**

- If $z \to +\infty$, $g(z) \to 1$ (confident positive prediction).
- If $z \to -\infty$, $g(z) \to 0$ (confident negative prediction).
- If $z = 0$, $g(z) = 0.5$ (uncertain — on the decision boundary).
- The function is monotonically increasing — larger inputs always produce larger outputs.
- The derivative of the sigmoid has a beautiful property: $g'(z) = g(z)(1 - g(z))$. This will become crucially important in the chain rule derivation below.

## The decision boundary

The parameters $\theta$ define a line (or hyperplane) that separates the classes. The model predicts Class 1 if the probability is $\ge 0.5$. Looking at the sigmoid curve, $g(z) \ge 0.5$ whenever $z \ge 0$. Therefore, the decision boundary is the line where **$\theta^T x = 0$**:

- If $h(x) \ge 0.5$ (which means $z \ge 0$), predict Class 1.
- If $h(x) < 0.5$ (which means $z < 0$), predict Class 0.

_Note: The decision boundary can be linear, or if we use polynomial features (like $x_1^2 + x_2^2$), the boundary can be a complex curve (like a circle). This is a powerful technique: by transforming the input features, we can create non-linear decision boundaries while still using the same logistic regression algorithm._

### A worked boundary example

A concrete example shows how the parameters define a boundary. Suppose the model learned the parameters $\theta_0 = -3$, $\theta_1 = 1$, $\theta_2 = 1$. The hypothesis predicts $y=1$ if $\theta^T x \ge 0$. Substituting the parameters:

$$ -3 + x_1 + x_2 \ge 0 $$
$$ x_1 + x_2 \ge 3 $$

This equation ($x_1 + x_2 = 3$) represents a straight, diagonal line on a 2D graph. Any data point falling above this line is classified as Class 1; anything below is Class 0. The bias term $\theta_0 = -3$ shifts the boundary away from the origin — without it, the boundary would pass through $(0,0)$.

## Odds, log-odds, and the logit

Understanding the mathematical foundation of logistic regression requires understanding **odds** and **log-odds**, which provide the theoretical bridge between linear regression and logistic regression.

### Odds

The **odds** of an event is the ratio of the probability of the event happening to the probability of it not happening:

$$ \text{Odds} = \frac{p}{1 - p} $$

For example:

- If $p = 0.5$, the odds are $\frac{0.5}{0.5} = 1$ (even odds — the event is equally likely to happen or not).
- If $p = 0.9$, the odds are $\frac{0.9}{0.1} = 9$ (9-to-1 odds — the event is 9 times more likely to happen than not).
- If $p = 0.01$, the odds are $\frac{0.01}{0.99} \approx 0.01$ (1-to-99 odds — the event is very unlikely).

Odds range from 0 to $+\infty$, making them useful for representing relative likelihoods but difficult to model directly with a linear equation.

### Log-odds (the logit)

The **logit** is the natural logarithm of the odds:

$$ \text{Logit}(p) = \log\left(\frac{p}{1 - p}\right) $$

The logit transforms the probability $p \in (0, 1)$ into a value that ranges from $-\infty$ to $+\infty$. This is crucial because it maps the bounded probability space onto the entire real number line, making it compatible with linear models.

### The key insight: logistic regression models linear log-odds

If we substitute $p = \sigma(z) = \frac{1}{1 + e^{-z}}$ into the logit equation and simplify:

$$ \text{Logit}(p) = \log\left(\frac{\sigma(z)}{1 - \sigma(z)}\right) = \log\left(\frac{\frac{1}{1+e^{-z}}}{\frac{e^{-z}}{1+e^{-z}}}\right) = \log\left(\frac{1}{e^{-z}}\right) = \log(e^z) = z $$

Therefore, logistic regression is actually modeling the **linear relationship between the features and the log-odds of the target class**, not the probabilities directly. The probability interpretation comes from applying the sigmoid function to this linear log-odds relationship. This means: $\text{Logit}(P(Y=1|X)) = w_1 x_1 + w_2 x_2 + \dots + w_m x_m + b = \theta^T x$.

**Why this matters:** each weight $w_j$ in logistic regression represents the change in log-odds associated with a one-unit increase in feature $x_j$, holding all other features constant. A positive weight increases the log-odds (making the positive class more likely), while a negative weight decreases the log-odds. This provides a direct, interpretable relationship between features and the outcome — one of the reasons logistic regression remains popular in domains where interpretability is important (medicine, finance, social sciences).

## Why mean squared error fails

If we substitute $h(x) = \frac{1}{1 + e^{-\theta^T x}}$ into the standard MSE cost function:

$$ J(\theta) = \frac{1}{2m} \sum \left(\frac{1}{1 + e^{-\theta^T x}} - y\right)^2 $$

This creates a **non-convex** function. The combination of the sigmoid's non-linearity with the squared error produces a loss surface with numerous hills and valleys (local minima). Gradient descent cannot be trusted on this landscape — it will likely converge to a suboptimal point that is not the best possible solution.

The same conclusion follows in the per-sample notation: applying the MSE cost $J = \frac{1}{n} \sum (y - \hat{y})^2$ to a logistic regression model, substituting $\hat{y} = \sigma(wX + b)$, yields a function that is **highly non-convex** — full of bumps, local minima, and plateaus. The non-linear sigmoid function combined with the quadratic penalty creates a complex landscape that is treacherous for gradient descent, which will almost certainly get stuck in a suboptimal local minimum.

This is a deep mathematical problem, not just an implementation detail. The squared error function was designed for linear relationships, and plugging a non-linear sigmoid into it breaks the convexity guarantee.

## Log loss (binary cross-entropy)

To restore a perfect, convex "bowl" shape, we redefine the cost function using logarithms. We define the cost piecewise to force convexity:

- Cost if $y=1$: $-\log(h(x))$
- Cost if $y=0$: $-\log(1 - h(x))$

### Deriving the piecewise loss from first principles

Each branch is built to punish confident mistakes without bound. **If $y = 1$**, we want $\hat{y}$ to be close to 1, so we define the loss as $-\log(\hat{y})$:

- As $\hat{y} \to 1$, loss $\to 0$ (correct prediction, no penalty).
- As $\hat{y} \to 0$, loss $\to \infty$ (confidently wrong, infinite penalty).

**If $y = 0$**, we want $\hat{y}$ to be close to 0, so we define the loss as $-\log(1 - \hat{y})$:

- As $\hat{y} \to 0$, loss $\to 0$ (correct prediction, no penalty).
- As $\hat{y} \to 1$, loss $\to \infty$ (confidently wrong, infinite penalty).

We combine these into a single, elegant equation by using the indicator function trick — multiplying each branch by $y$ or $(1-y)$ ensures only the correct branch contributes:

$$ \text{Loss} = -[y \log(\hat{y}) + (1-y) \log(1-\hat{y})] $$

Averaging over $n$ samples gives the full binary cross-entropy formula. This function is **strictly convex** for logistic models, guaranteeing that gradient descent will find the single global minimum regardless of the starting point.

### The combined cost function

In vectorized form over the training set, the cost is the **binary cross-entropy**:

$$ J(\theta) = -\frac{1}{m} \sum_{i=1}^{m} [y^{(i)} \log(h_\theta(x^{(i)})) + (1 - y^{(i)}) \log(1 - h_\theta(x^{(i)}))] $$

**Why this works:** the logarithm is a strictly concave function, and the negative log of the sigmoid output is convex. This combination guarantees that the overall loss surface is a smooth, convex bowl with a single global minimum — exactly what gradient descent needs to find the optimal solution reliably. This is why we _must_ use **binary cross-entropy (log loss)** for logistic regression, which mathematically guarantees a perfect, convex, single-minimum bowl.

In the $\hat{p}$ notation of probabilistic modeling, the same loss appears at two granularities. For one example:

$$ L = -[y \log \hat{p} + (1-y) \log(1 - \hat{p})] $$

For a batch:

$$ L = -\frac{1}{N} \sum_i [y_i \log \hat{p}_i + (1-y_i) \log(1 - \hat{p}_i)] $$

Both are the same object as the $J(\theta)$ above — the per-sample and averaged views of binary cross-entropy, the classification counterpart of the MSE role surveyed in [[Loss Functions]].

## The maximum likelihood connection

Logistic regression is maximum likelihood estimation (MLE) for a Bernoulli model: $y_i \sim \text{Bernoulli}(\sigma(\mathbf{w} \cdot \mathbf{x}_i))$. The negative log-likelihood of this model is exactly the binary cross-entropy loss — the loss function was not an arbitrary choice but the unique consequence of modeling the labels as coin flips whose success probability is the sigmoid of a linear score. This mirrors linear regression, where MSE is the MLE under Gaussian noise. Once you understand the chain from "model the data distribution" to "loss function" to "gradient descent" — MLE → cross-entropy → backprop — you understand the conceptual core of all supervised learning; the optimization itself is the province of [[Gradient Descent]].

## The gradient derivation and the beautiful coincidence

When you take the derivative of this log loss function, the complex derivative of the sigmoid mathematically cancels out elements of the log derivative. When you calculate the partial derivative of the cost function for linear regression, and the partial derivative of the cost function for logistic regression, the final resulting formulas look **exactly the same**:

$$ \frac{\partial J(\theta)}{\partial \theta_j} = \frac{1}{m} \sum_{i=1}^{m} (h_\theta(x^{(i)}) - y^{(i)}) x_j^{(i)} $$

**Why does this happen?** Because the derivative of the log loss with respect to the sigmoid output produces a term $\frac{1}{h_\theta(x)}$ or $\frac{1}{1-h_\theta(x)}$, and the derivative of the sigmoid itself produces a term $h_\theta(x)(1-h_\theta(x))$. These perfectly cancel each other, leaving the highly elegant, simple update rule.

### Are the gradient formulas identical? A deeper look

The same calculation in the $w_j$ notation makes the structure explicit — a fascinating mathematical coincidence: a fascinating mathematical coincidence: a fascinating mathematical coincidence: the gradient for updating the weights in linear regression (using MSE) and logistic regression (using log loss) yields the **exact same final formulaic structure**:

$$ \frac{\partial J}{\partial w_j} = \frac{1}{n} \sum_{i=1}^{n} (\hat{y}_i - y_i) x_{ij} $$

**However, they are NOT the same algorithm!** The definition of $\hat{y}$ is fundamentally different. In linear regression, $\hat{y} = wX + b$ (a straight line). In logistic regression, $\hat{y} = \sigma(wX + b)$ (an S-curve squashed between 0 and 1). The non-linear squashing of the sigmoid changes the loss landscape entirely, even though the final derivative formula looks similar. The identical formula arises because the derivative of the log loss with respect to the sigmoid output produces terms that perfectly cancel the derivative of the sigmoid function itself. This mathematical cancellation is not accidental — it is the reason why cross-entropy loss is the natural pairing for sigmoid activation. The two functions were mathematically designed to simplify each other's derivatives.

> [!WARNING] Important reminder
> Even though the formula looks the same, $h_\theta(x)$ is entirely different (linear vs. sigmoid). In linear regression, $h_\theta(x) = \theta^T x$ (a straight line). In logistic regression, $h_\theta(x) = \frac{1}{1+e^{-\theta^T x}}$ (an S-curve squashed between 0 and 1). The algorithms are not the same; their loss landscapes are fundamentally different. Linear regression with MSE gives a convex bowl; logistic regression with log loss also gives a convex bowl, but the shape and interpretation are completely different.

## Multiclass: softmax regression

For $K$ classes, the binary sigmoid generalizes to:

$$ p(y = k \mid \mathbf{x}) = \frac{\exp(\mathbf{w}_k \cdot \mathbf{x})}{\sum_j \exp(\mathbf{w}_j \cdot \mathbf{x})} $$

This is **softmax** — and softmax regression is exactly the output layer of every modern LLM. The loss is categorical cross-entropy, the multi-class analogue of the binary cross-entropy derived above. Where binary problems have $y \in \{0, 1\}$, multi-class problems have $y \in \{0, 1, 2, 3\}$, and the softmax form assigns a probability to every class at once while keeping the whole distribution summing to one.

## Imbalanced classes and decision thresholds

The model's native output is a probability; the class decision comes from comparing that probability to a threshold, conventionally $0.5$ — a rule inherited directly from the boundary mathematics, since $g(z) = 0.5$ exactly when $z = 0$, the "uncertain" point on the decision boundary. The prediction rule "Class 1 if $h(x) \ge 0.5$" is therefore a property of the sigmoid, not a free parameter of the model.

When the training classes are imbalanced, the model will be biased toward the majority class, because the loss is dominated by the more frequent label. The standard remedies are class weighting or resampling. Judging the resulting classifier well — rather than staring at raw accuracy — is the job of the metric families in [[Model Evaluation Metrics]].

## Why these models matter

**They're the building blocks of neural networks.** A dense layer is a linear regression plus an activation. A classification head is softmax regression. Every Transformer is built from these primitives, which is why the stacked-sigmoid view ("neural networks are essentially stacked logistic regression units") is more than a slogan.

**Strong baselines.** For many problems, logistic regression is a perfectly good model — and it's interpretable, fast, and easy to deploy. Don't reach for a neural network before trying logistic regression.

**Calibration.** Logistic regression produces **calibrated probabilities** by construction (when the model is correctly specified). Neural networks often need post-hoc temperature scaling to calibrate.

**The math generalizes.** MLE → cross-entropy → backprop. Once you understand the chain from "model the data distribution" to "loss function" to "gradient descent," you understand the conceptual core of all supervised learning.

## Practice

### Worked example

The following scikit-learn workflow fits all three members of the family on the same random feature matrix — a continuous target for linear regression and ridge, and a thresholded binary target for logistic regression:

```python
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge
import numpy as np

X = np.random.randn(100, 5)
y_reg = X @ np.array([1, -2, 0.5, 0, 3]) + 0.1 * np.random.randn(100)
y_cls = (X @ np.array([1, -2, 0.5, 0, 3]) > 0).astype(int)

# Linear regression
lr = LinearRegression().fit(X, y_reg)
print(lr.coef_)  # ≈ [1, -2, 0.5, 0, 3]

# Ridge (L2)
ridge = Ridge(alpha=1.0).fit(X, y_reg)

# Logistic regression
logr = LogisticRegression(C=1.0).fit(X, y_cls)  # C = 1/lambda
print(logr.coef_)  # ≈ direction separating classes
```

The linear regression recovers the true coefficients; the logistic regression recovers the direction separating the classes. Note the `C = 1/lambda` convention: scikit-learn parameterizes regularization by its inverse, so larger `C` means less regularization — the same L1/L2 machinery discussed in [[Regularization Techniques]]. The linear and ridge portions of the example are unpacked in [[04 - Machine Learning/Regression/Linear Regression|Linear Regression]].

### When to use classical regression vs neural networks

| Use classical regression when...            | Use neural networks when...                     |
|---------------------------------------------|-------------------------------------------------|
| Tabular data, small dataset (<10k rows)     | Unstructured data (text, images, audio)         |
| Interpretability is required                | Pure predictive accuracy matters                |
| Linear relationships are plausible          | Nonlinear relationships expected                 |
| Fast iteration / deployment needed          | You have lots of data and compute               |
| Need calibrated probabilities out of the box| Willing to add temperature scaling              |

For tabular data, **gradient boosting** (see [[Gradient Boosting]]) is often a better choice than both.

### Production implications

Always start with a simple baseline — logistic regression with feature engineering beats jumping straight to deep learning. For high-stakes probability estimates (credit risk, medical diagnosis), logistic regression's calibration is a real advantage. For tabular data, use XGBoost — it typically outperforms both logistic regression and deep learning. Finally, feature scaling matters for regularized linear models: standardize features before applying L1/L2.

### Common pitfalls

**Multicollinearity** — correlated features produce unstable coefficients in unregularized regression; use ridge. **Extrapolation** — linear models extrapolate linearly, which can be wildly wrong outside the training range. **Imbalanced classes in logistic regression** — the model will be biased toward the majority class; use class weighting or resampling, as discussed above. **Forgetting that logistic regression is linear** — the decision boundary is a hyperplane, so if classes aren't linearly separable (even in feature space), it won't work well; that is the regime where kernel-based classifiers such as [[Support Vector Machines]] with the [[Kernel Trick]] earn their keep.

### Further reading

- Hastie, Tibshirani, Friedman, *The Elements of Statistical Learning*, Chapter 3 (regression) and 4 (classification).
- Murphy, *Probabilistic Machine Learning*, Chapter 10–11.

## See also

- [[Machine Learning MOC]]
- [[04 - Machine Learning/Regression/Linear Regression|Linear Regression]]
- [[Regression Fundamentals]]
- [[Loss Functions]]
- [[Gradient Descent]]
- [[Model Evaluation Metrics]]
- [[Regularization Techniques]]
- [[Bias Variance Tradeoff]]
- [[Gradient Boosting]]
- [[Support Vector Machines]]
