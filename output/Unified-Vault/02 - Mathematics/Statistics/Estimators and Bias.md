---
title: Estimators and Bias
type: concept
aliases:
  - Estimators
  - Maximum Likelihood Estimation
  - MLE
  - Maximum A Posteriori
  - MAP
  - Bias-Variance
tags:
  - mathematics
  - statistics
  - estimators
  - mle
  - map
  - bias-variance
  - bootstrap
  - robust-estimation
sources:
  - "16 - Estimators and Bias"
created_index: 17
---

Estimation theory studies how to infer population parameters from samples and when the resulting estimates deserve trust. Its two workhorses are **maximum likelihood estimation (MLE)**, which picks the parameters that make the observed data most probable, and **maximum a posteriori (MAP)** estimation, which folds a prior over the parameters into the objective and turns regularization into Bayesian inference. This note develops both methods together with the bias, variance and consistency properties of estimators, then surveys the modern extensions — James-Stein shrinkage, robust losses and the bootstrap — that explain why regularized estimators dominate machine learning practice.

> [!info] TL;DR
> Estimators are functions that produce estimates of population parameters from samples. The two main estimation methods are **Maximum Likelihood Estimation (MLE)** — find the parameters that make the observed data most probable — and **Maximum A Posteriori (MAP)** — find the parameters most probable given the data (incorporating a prior). An estimator is **unbiased** if its expected value equals the true parameter; **consistent** if it converges to the true parameter as sample size grows. Understanding estimators is foundational for understanding how LLMs are trained (cross-entropy loss is MLE).

## Why estimators matter for AI

Machine learning is fundamentally about estimation: we estimate model parameters from data. The loss functions we use (cross-entropy, MSE) are derived from estimation principles:

- **Cross-entropy loss** = negative log-likelihood (MLE for categorical distributions).
- **Mean squared error** = MLE for Gaussian-distributed errors.
- **L2 regularization** = MAP with a Gaussian prior.
- **L1 regularization** = MAP with a Laplacian prior.

Understanding estimators clarifies *why* we use these losses and *what* they're optimizing (the information-theoretic side of cross-entropy is covered in [[Entropy Cross-Entropy and KL Divergence]]).

## Maximum likelihood estimation

### The principle

Given observed data $X = \{x_1, \ldots, x_n\}$ assumed to come from a distribution $p(x \mid \theta)$ with unknown parameter $\theta$, MLE finds the $\theta$ that makes the observed data most probable:

```text
θ_MLE = argmax_θ p(X | θ) = argmax_θ Π_i p(x_i | θ)
```

### Log-likelihood

Products are hard to optimize, so we take the log:

```text
log p(X | θ) = Σ_i log p(x_i | θ)
```

The log-likelihood is a sum, which is easier to differentiate. Maximizing the log-likelihood is equivalent to maximizing the likelihood (log is monotonic).

### Example: Gaussian distribution

For data drawn from $\mathcal{N}(\mu, \sigma^2)$ (see [[Gaussian Distribution]]), the log-likelihood is:

```text
log L(μ, σ²) = -n/2 log(2π) - n/2 log(σ²) - Σ_i (x_i - μ)² / (2σ²)
```

Maximizing with respect to $\mu$ gives the sample mean:

```text
μ_MLE = (1/n) Σ_i x_i
```

Maximizing with respect to $\sigma^2$ gives:

```text
σ²_MLE = (1/n) Σ_i (x_i - μ_MLE)²
```

Note that $\sigma^2_{MLE}$ is biased (divides by $n$ instead of $n-1$). The `_unbiased` sample-variance estimator divides by $n-1$.

### MLE for categorical distributions (cross-entropy)

For categorical data (like token prediction), the likelihood is:

```text
L(p) = Π_i p(x_i)
log L(p) = Σ_i log p(x_i)
```

This is exactly the **cross-entropy loss** (negated). Applied to language modeling, the pieces line up as: **Data** — token sequences from a corpus; **Model** — the LLM, parameterized by `θ`; **Likelihood** — `p(tokens | θ) = Π p(token_i | token_<i, θ)`; **MLE** — maximize the log-likelihood, i.e. minimize the cross-entropy loss. Training an LLM with cross-entropy loss is MLE — we're finding the parameters that make the observed token sequence most probable.

## Maximum a posteriori estimation

### The principle

MAP extends MLE by incorporating a **prior** over the parameters:

```text
θ_MAP = argmax_θ p(θ | X) = argmax_θ p(X | θ) p(θ)
```

Using Bayes' theorem (see [[Bayes Theorem]]):

```text
p(θ | X) = p(X | θ) p(θ) / p(X)
```

Since $p(X)$ doesn't depend on $\theta$, we maximize $p(X \mid \theta) p(\theta)$ — the likelihood times the prior.

### Log form

```text
log p(θ | X) = log p(X | θ) + log p(θ) + const
             = log-likelihood + log-prior
```

MAP maximizes log-likelihood plus log-prior. The prior acts as a regularizer.

### Example: Gaussian prior = L2 regularization

If the prior is $p(\theta) = \mathcal{N}(0, \tau^2)$, then:

```text
log p(θ) = -θ² / (2τ²) + const
```

MAP becomes:

```text
θ_MAP = argmax_θ [log L(θ) - θ² / (2τ²)]
      = argmin_θ [-log L(θ) + θ² / (2τ²)]
```

This is **L2-regularized loss** — the likelihood term plus a penalty on large parameter values. The regularization strength $1/(2\tau^2)$ corresponds to $\lambda$ in standard L2 regularization.

### Example: Laplacian prior = L1 regularization

If the prior is $p(\theta) = \text{Laplace}(0, b)$, then:

```text
log p(θ) = -|θ| / b + const
```

MAP becomes L1-regularized loss. This is why L1 regularization produces sparse solutions — the Laplacian prior puts more probability mass at zero.

### MLE vs MAP

The three estimation philosophies differ in how much of the posterior they use:

- **MLE**: no prior, just fit the data. Can overfit with limited data.
- **MAP**: incorporates prior knowledge, regularizes. Less prone to overfitting.
- **Bayesian**: compute the full posterior $p(\theta \mid X)$, not just the mode. Most informative but most expensive.

MLE is a special case of MAP with a uniform prior (no preference for any parameter value).

## Bias and variance

### Bias

An estimator $\hat{\theta}$ is **unbiased** if:

```text
E[θ̂] = θ  (the true parameter)
```

If $\mathbb{E}[\hat{\theta}] \neq \theta$, the estimator is biased, with bias $\mathbb{E}[\hat{\theta}] - \theta$.

**Example**: the sample variance $s^2 = \frac{1}{n} \sum (x_i - \bar{x})^2$ is biased — it underestimates the true variance because it uses the sample mean (which fits the data) rather than the true mean. The unbiased estimator divides by $n-1$:

```text
s²_unbiased = (1/(n-1)) Σ (x_i - x̄)²
```

### Variance

The variance of an estimator measures how much it varies across different samples:

```text
Var(θ̂) = E[(θ̂ - E[θ̂])²]
```

High variance means the estimate changes a lot depending on which sample you draw.

### The bias-variance tradeoff

There's often a tradeoff:

- **Low bias, high variance**: complex models fit the data closely but vary across samples (overfitting).
- **High bias, low variance**: simple models are stable but don't fit well (underfitting).

See [[Bias Variance Tradeoff]] for the full treatment.

### Consistency

An estimator is **consistent** if it converges to the true parameter as sample size grows:

```text
θ̂_n → θ  as n → ∞
```

Consistency requires both low bias (asymptotically unbiased) and low variance (concentrates as $n$ grows). MLE is consistent under regularity conditions.

## Properties of MLE

### Asymptotic properties

Under regularity conditions, MLE has desirable properties as $n \to \infty$:

1. **Consistency**: $\hat{\theta}_{MLE} \to \theta$ as $n \to \infty$.
2. **Asymptotic normality**: $\sqrt{n} (\hat{\theta}_{MLE} - \theta) \to \mathcal{N}(0, I(\theta)^{-1})$, where $I(\theta)$ is the Fisher information.
3. **Asymptotic efficiency**: MLE achieves the Cramér-Rao lower bound asymptotically — no consistent estimator has lower asymptotic variance.

These properties make MLE the default choice when you have enough data.

### Limitations

- **Small samples**: MLE can overfit with limited data. MAP (regularization) helps.
- **Misspecified models**: if the model family doesn't include the true distribution, MLE converges to the closest model (in KL divergence), which may not be desirable.
- **Computational cost**: for complex models (LLMs), computing MLE exactly is infeasible — we use stochastic gradient descent.

## Estimators in LLM training

### Cross-entropy = MLE

Training an LLM with cross-entropy loss is MLE:

- **Data**: token sequences from a corpus.
- **Model**: the LLM, parameterized by $\theta$.
- **Likelihood**: $p(\text{tokens} \mid \theta) = \prod p(\text{token}_i \mid \text{token}_{<i}, \theta)$.
- **MLE**: maximize the log-likelihood = minimize the cross-entropy loss.

### Weight decay = MAP with Gaussian prior

Adding L2 regularization (weight decay) to cross-entropy loss makes it MAP:

- **Prior**: $\theta \sim \mathcal{N}(0, \tau^2)$.
- **MAP**: maximize log-likelihood + log-prior = minimize cross-entropy + $\lambda \|\theta\|^2$.

### Dropout as approximate Bayesian inference

Dropout (randomly zeroing activations during training) can be interpreted as approximate Bayesian inference — the dropout distribution acts like a prior over the weights. This provides a Bayesian justification for dropout as regularization.

### LoRA as MAP

LoRA (Low-Rank Adaptation) constrains the parameter updates to a low-rank subspace. This is equivalent to a MAP estimate with a prior that prefers low-rank updates — the prior encodes the belief that "good updates are low-rank."

## The James-Stein estimator — when MLE is suboptimal

A surprising result from classical statistics: for estimating the mean of a multivariate Gaussian (dim ≥ 3), the MLE (sample mean) is **inadmissible** — there's always an estimator with lower mean squared error. The James-Stein estimator shrinks the sample mean toward zero (or any other point):

$$
\hat{\theta}_{JS} = \left(1 - \frac{d - 2}{\|\bar{x}\|^2}\right) \bar{x}
$$

where $d$ is the dimension and $\bar{x}$ is the sample mean. This dominates MLE in MSE for $d \geq 3$. The intuition: in high dimensions, shrinking toward a point reduces variance more than it adds bias.

### Why this matters for ML

The James-Stein phenomenon generalizes: in high dimensions, **regularization works**. Ridge regression, Lasso, weight decay — they're all forms of shrinkage that exploit this. The fact that MLE is suboptimal in high dimensions is why we use MAP (regularized) estimators almost universally in ML. L2 weight decay is the James-Stein estimator applied to neural network weights.

## Robust estimators — when the model is wrong

MLE assumes the model is correctly specified. If the data has outliers or the true distribution has heavier tails than the model, MLE can be arbitrarily bad. Robust estimators trade some efficiency for robustness:

| Estimator              | Loss function            | Robust to outliers | Efficiency (Gaussian) |
|------------------------|--------------------------|--------------------|----------------------|
| MLE (Gaussian)         | Squared error $\|y - f\|^2$ |               | 100% (optimal)       |
| MLE (Laplacian)        | Absolute error $\|y - f\|$  |               | 64% (less efficient) |
| Huber                  | Quadratic near 0, linear far |               | ~95%                 |
| Tukey biweight         | Bounded influence        |                | ~90%                 |

### Huber loss for RLHF reward models

Reward models in RLHF are often trained with Huber loss instead of squared error. This is because preference data is noisy — some labels are wrong, and squared error would over-weight them. Huber is quadratic for small residuals (efficient when the model is right) and linear for large residuals (robust to outliers). See [[RLHF with PPO]].

## The bootstrap — estimating uncertainty without theory

The bootstrap is a computationally expensive but theory-free way to estimate the variance of any estimator:

1. Sample $B$ bootstrap datasets by resampling the original data with replacement.
2. Compute the estimator $\hat{\theta}_b$ on each bootstrap dataset.
3. Estimate variance as $\text{Var}(\hat{\theta}) \approx \text{Var}(\{\hat{\theta}_1, \ldots, \hat{\theta}_B\})$.

This works for any estimator, no formulas needed. The cost: $B$ × the original computation. For neural networks, $B = 10$–$100$ is typical for uncertainty estimation.

```python
import numpy as np

# Bootstrap estimate of standard error for the mean
data = np.random.randn(100) + 2.0  # True mean = 2.0
B = 1000
bootstrap_means = [np.mean(np.random.choice(data, len(data), replace=True)) for _ in range(B)]
print(f"MLE mean: {np.mean(data):.4f}")
print(f"Bootstrap std error: {np.std(bootstrap_means):.4f}")
print(f"95% CI: [{np.percentile(bootstrap_means, 2.5):.4f}, {np.percentile(bootstrap_means, 97.5):.4f}]")
```

### Bootstrap for neural networks (deep ensembles)

Training $B$ neural networks on bootstrap datasets gives a **deep ensemble**. The ensemble's predictions are averaged for inference, and the variance across ensemble members estimates uncertainty. This is the most reliable uncertainty estimate for neural networks, but the cost ($B$ × training) is high. For uncertainty-related interpretability, see the probing notes in the interpretability area.

## Estimators in modern AI: a survey

### In LoRA fine-tuning

LoRA adds low-rank updates $\Delta W = BA$ to a frozen weight $W$. The MAP interpretation: $\Delta W$ has a low-rank prior (the rank $r$). Training minimizes the negative log-likelihood plus a low-rank-inducing regularizer. This is why LoRA generalizes well from limited data — the prior is strong. See [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]].

### In reasoning model training (GRPO)

GRPO estimates the policy gradient using group-relative advantages: $A_i = (r_i - \bar{r}) / \sigma_r$. The estimator is unbiased (the group mean is an unbiased estimate of the expected reward) but has high variance for small groups. Larger groups (more samples per prompt) reduce variance.

### In RLHF reward modeling

The reward model is trained with the Bradley-Terry likelihood: $\max_\phi \sum \log \sigma(r_\phi(x, y_w) - r_\phi(x, y_l))$. This is MLE for the Bradley-Terry model. The reward estimate is biased if the preference data is biased (e.g., labelers prefer verbose answers). See [[RLHF with PPO]] and [[DPO Derivation]].

### In DPO

DPO derives a closed-form estimator for the optimal policy given preference data. The DPO loss is a maximum-likelihood estimator on a transformed objective. The key insight: by eliminating the reward model, DPO reduces variance (no reward model noise) at the cost of stronger assumptions (the reference policy must be the true MLE). See [[DPO Derivation]].

### In LLM-as-judge

LLM-as-judge estimates human preference by asking an LLM to rate or compare outputs. The estimator is biased by the judge LLM's preferences (e.g., GPT-4 prefers GPT-4-style writing). Mitigations: ensemble multiple judges, calibrate against human labels, use position-swapping to reduce order bias. See [[LLM-as-Judge Evaluation]].

## Common pitfalls

### Statistical bias is not fairness bias

"Bias" in estimation theory ($\mathbb{E}[\hat{\theta}] \neq \theta$) is different from "bias" in fairness (demographic bias). They share a name but are distinct concepts.

### Using biased estimators unknowingly

Many common estimators are biased (sample variance with $1/n$, MLE for variance). For large samples, the bias is small, but for small samples, it matters. Know which estimators are biased and when to use corrections.

### Ignoring the prior in MAP

MAP results depend on the prior. Different priors give different estimates. Always specify the prior when discussing MAP estimates.

### Assuming MLE is always best

MLE is asymptotically efficient but can be poor with small samples. MAP (regularization) often performs better in practice, especially for high-dimensional models.

### Confusing consistency with unbiasedness

An estimator can be biased but consistent (bias → 0 as $n \to \infty$). Consistency is about asymptotic behavior; unbiasedness is about finite-sample behavior.

## Common failure modes

| Symptom | Likely cause | Fix |
|--------|--------------|-----|
| MLE overfits | No prior, high-capacity model | Add regularization (L2 = Gaussian prior) |
| Reward model biased | Preference data biased | Balance data; use Huber loss; ensemble |
| Bootstrap is too slow | $B$ × training cost is high | Use cheaper uncertainty (MC dropout, deep ensembles with $B=5$) |
| MAP estimate is wrong | Wrong prior | Choose prior based on domain knowledge; or use hierarchical Bayes |
| Confidence intervals too narrow | Assuming Gaussianity when data is heavy-tailed | Use bootstrap; or robust estimators |
| LLM-as-judge inconsistent | Judge bias; prompt ambiguity | Ensemble multiple judges; calibrate against humans |

## Interview questions

1. **Q: What is the James-Stein estimator and why does it matter for ML?**
   A: For estimating the mean of a multivariate Gaussian (dim ≥ 3), the sample mean (MLE) is **inadmissible** — the James-Stein estimator $\hat{\theta}_{JS} = (1 - (d-2)/\|\bar{x}\|^2) \bar{x}$ always has lower MSE. It shrinks the sample mean toward zero. The generalization for ML: in high dimensions, regularization works. Ridge regression, Lasso, and weight decay are all forms of shrinkage that exploit this. This is why we use MAP (regularized) estimators almost universally in ML — MLE is suboptimal in high dimensions.

2. **Q: Why does the Huber loss make reward models more robust?**
   A: Squared error (Gaussian MLE) penalizes large residuals quadratically, so outliers dominate the loss. Preference data is noisy — some labels are wrong. Squared error would over-weight these wrong labels, biasing the reward model. Huber loss is quadratic for small residuals (efficient when the model is right) and linear for large residuals (robust to outliers). The transition point $\delta$ controls the robustness/efficiency tradeoff. For RLHF reward models, $\delta = 1$ is common.

3. **Q: Explain the bootstrap and when it's preferred over closed-form variance estimates.**
   A: The bootstrap resamples the data with replacement $B$ times, computes the estimator on each resample, and estimates variance from the spread. It's preferred when: (1) the estimator's variance has no closed-form (e.g., median, quantiles, complex neural network metrics); (2) the data distribution is unknown or non-Gaussian; (3) the sample size is small and asymptotic theory doesn't apply. The cost: $B$ × the original computation. For neural networks, deep ensembles ($B$ = 5–10 separately trained models) are the bootstrap equivalent and the most reliable uncertainty estimate.

4. **Q: How does DPO eliminate the reward model, and what's the estimator?**
   A: DPO derives that the optimal RLHF policy satisfies $\pi^*(y \mid x) \propto \pi_{\text{ref}}(y \mid x) \exp(r(x, y) / \beta)$. Substituting into the Bradley-Terry preference likelihood gives a loss directly in terms of $\pi_\theta$ and $\pi_{\text{ref}}$ — no reward model needed. The DPO loss is a maximum-likelihood estimator on this transformed objective. The advantage: lower variance (no reward model noise), simpler training (no RL). The cost: stronger assumptions (the reference policy must be the true MLE; if it's not, DPO is biased).

5. **Q: Why is LLM-as-judge a biased estimator of human preference, and how do you mitigate it?**
   A: Biases include: (1) **verbosity bias** — judges prefer longer answers; (2) **position bias** — judges prefer the first/last option; (3) **self-preference** — GPT-4 prefers GPT-4-style writing; (4) **calibration drift** — judges rate on different scales. Mitigations: (a) ensemble multiple judges (GPT-4, Claude, Llama); (b) calibrate against a small human-labeled set; (c) use position-swapping and average; (d) use structured rubrics instead of open-ended rating. For production, always have a human-labeled eval set to catch judge bias.

6. **Q: When is MLE the right choice over MAP?**
   A: Use MLE when: (1) you have lots of data (the prior is dominated by the likelihood); (2) you have no prior knowledge; (3) you're doing pure maximum-likelihood inference (e.g., language model pretraining — cross-entropy loss is NLL). Use MAP when: (1) data is limited (regularization prevents overfitting); (2) you have genuine prior knowledge (e.g., weights should be small); (3) you're in high dimensions (James-Stein shows MLE is suboptimal). For LLMs: pretraining uses MLE; fine-tuning with weight decay uses MAP (Gaussian prior = L2); LoRA uses MAP with a low-rank prior.

## See also

- [[Mathematics MOC]]
- [[Probability Essentials]]
- [[Bayes Theorem]]
- [[Gaussian Distribution]]
- [[Entropy Cross-Entropy and KL Divergence]]
- [[Optimization Essentials]]
- [[Adam Optimizer Derivation]]
- [[Hypothesis Testing]]
- [[Probability and Statistics for ML]]
- [[Bias Variance Tradeoff]]
- [[Regularization Techniques]]
- [[04 - Machine Learning/Regression/Linear Regression|Linear Regression]]
- [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]]
- [[RLHF with PPO]]
- [[DPO Derivation]]
- [[LLM-as-Judge Evaluation]]
- [[A-B Testing and Shadow Deployment]]
