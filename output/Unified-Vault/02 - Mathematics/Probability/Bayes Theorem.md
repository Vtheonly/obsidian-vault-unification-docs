---
title: Bayes Theorem
type: concept
aliases: ["Bayes' Theorem", "Bayes' Rule", "Bayes Rule", "Bayes Theorem Deep Dive"]
tags: [mathematics, probability, bayes-theorem, bayesian-inference, naive-bayes, conjugate-priors, variational-inference]
sources: ["Bayes Theorem Deep Dive"]
created_index: 14
---

Bayes' theorem is the single most important formula in probability for machine learning: it tells you how to update beliefs in light of evidence. It underlies Bayesian inference, naive Bayes classifiers, MAP estimation, and the conceptual basis of generative modeling. This note derives the theorem, works through canonical examples — medical testing, spam filtering, Bayesian linear regression — and develops the machinery built on top of it: conjugate priors, MAP-as-regularization, Bayesian model comparison, variational inference, and Bayesian A/B testing.

> [!info] TL;DR
> Bayes' theorem is the single most important formula in probability for ML. It tells you how to update beliefs in light of evidence. It underlies Bayesian inference, naive Bayes, MAP estimation, and the conceptual basis of generative modeling.

## The theorem

$$
P(A \mid B) = \frac{P(B \mid A) \, P(A)}{P(B)}
$$

In Bayesian-interpretation language:

$$
\text{posterior} = \frac{\text{likelihood} \times \text{prior}}{\text{evidence}}
$$

Each term has a precise role:

- **Prior** $P(A)$: belief about $A$ before seeing evidence.
- **Likelihood** $P(B \mid A)$: how likely the evidence is if $A$ is true.
- **Evidence** $P(B)$: total probability of the evidence, marginalized over all $A$.
- **Posterior** $P(A \mid B)$: updated belief about $A$ after seeing evidence.

## Derivation

From the definition of conditional probability:

$$
P(A, B) = P(A \mid B) P(B) = P(B \mid A) P(A)
$$

Divide both sides by $P(B)$:

$$
P(A \mid B) = \frac{P(B \mid A) P(A)}{P(B)}
$$

That's it. Bayes' theorem is just a rearrangement of the conditional probability definition.

## Why the theorem matters

### It is the rule for updating beliefs

Bayes tells you how to revise your belief in $A$ when you observe $B$. The prior encodes what you knew; the likelihood encodes what the new evidence says; the posterior is your new belief.

### It connects generative and discriminative models

A **discriminative** model learns $P(y \mid x)$ directly. A **generative** model learns $P(x \mid y)$ and $P(y)$, then uses Bayes:

$$
P(y \mid x) = \frac{P(x \mid y) P(y)}{P(x)}
$$

Naive Bayes classifiers work this way. Generative models (VAEs, diffusion models, autoregressive LMs) model $P(x)$ or $P(x \mid y)$; using Bayes to invert gives $P(y \mid x)$.

### It is the basis of MAP and Bayesian inference

- **MAP** (Maximum A Posteriori): pick $\hat\theta = \arg\max_\theta P(\theta \mid \text{data}) = \arg\max_\theta P(\text{data} \mid \theta) P(\theta)$.
- **Bayesian inference**: maintain the full posterior $P(\theta \mid \text{data})$ and average predictions over it.

L2 regularization = Gaussian prior on weights. L1 = Laplace prior. See [[Probability Essentials]] for the surrounding probability machinery.

### It is how RAG should work (conceptually)

In RAG, you have a prior over answers (from the LLM) and you observe evidence (retrieved documents). Bayesian reasoning suggests: weight answers that are consistent with the evidence higher. RAG doesn't literally compute Bayes, but the conceptual structure is the same.

## Worked examples

### Medical test

A disease affects 1 in 1000 people. A test is 99% sensitive (true positive rate) and 95% specific (true negative rate). You test positive. What's the probability you have the disease?

- $P(D) = 0.001$ (prior)
- $P(\neg D) = 0.999$
- $P(+ \mid D) = 0.99$
- $P(+ \mid \neg D) = 0.05$ (false positive rate)

$$
P(D \mid +) = \frac{P(+ \mid D) P(D)}{P(+)} = \frac{0.99 \times 0.001}{0.99 \times 0.001 + 0.05 \times 0.999} \approx 0.0194
$$

Only ~2% probability! Despite the "good" test, the low base rate means most positives are false positives. This is the **base rate fallacy** — humans (and naive ML models) consistently get this wrong.

### Spam classification (naive Bayes)

For each word $w_i$ in an email, compute $P(\text{spam} \mid w_i)$. Naive Bayes assumes words are conditionally independent given the label:

$$
P(\text{spam} \mid w_1, \ldots, w_n) \propto P(\text{spam}) \prod_i P(w_i \mid \text{spam})
$$

The "naive" independence assumption is wrong (words are correlated), but the classifier still works well in practice — Naive Bayes was the dominant spam filter for years.

### Bayesian linear regression

Standard linear regression: minimize $\|y - X\beta\|^2$.

Bayesian version: assume a Gaussian prior $\beta \sim \mathcal{N}(0, \tau^2 I)$ and Gaussian likelihood $y \sim \mathcal{N}(X\beta, \sigma^2 I)$. The MAP estimate is:

$$
\hat\beta = \arg\max_\beta P(\beta \mid y, X) = \arg\min_\beta \left[ \|y - X\beta\|^2 + \frac{\sigma^2}{\tau^2} \|\beta\|^2 \right]
$$

This is just ridge regression! L2 regularization = Gaussian prior. The Bayesian view gives regularization a principled interpretation. See [[04 - Machine Learning/Regression/Linear Regression|Linear Regression]].

## Marginalization (computing the evidence)

The denominator $P(B)$ is often the hard part:

$$
P(B) = \sum_A P(B \mid A) P(A)
$$

For continuous parameters, this is an integral:

$$
P(\text{data}) = \int P(\text{data} \mid \theta) P(\theta) d\theta
$$

This integral is usually intractable for complex models — the **marginal likelihood problem**. Bayesian inference methods (MCMC, variational inference) approximate it.

## Conjugate priors

A **conjugate prior** is a prior distribution that, when combined with a particular likelihood, gives a posterior in the same family. Conjugate priors make Bayesian inference tractable — the posterior has closed form.

### Common conjugate pairs

| Likelihood                  | Conjugate Prior           | Posterior                 | Use Case                          |
|-----------------------------|---------------------------|---------------------------|-----------------------------------|
| Bernoulli / Binomial        | Beta                      | Beta                      | Coin flip, click-through rate     |
| Categorical / Multinomial   | Dirichlet                 | Dirichlet                 | Naive Bayes, topic models (LDA)   |
| Gaussian (known variance)   | Gaussian                  | Gaussian                  | Bayesian linear regression        |
| Gaussian (unknown variance) | Inverse-Gamma             | Inverse-Gamma             | Variance estimation               |
| Poisson                     | Gamma                     | Gamma                     | Count data, event rates           |
| Exponential                 | Gamma                     | Gamma                     | Waiting times                     |
| Multivariate Gaussian       | Wishart / Inverse-Wishart | Wishart / Inverse-Wishart | Covariance estimation             |

### Beta-Bernoulli conjugacy

For a Bernoulli likelihood with $n$ trials and $k$ successes, and a Beta($\alpha, \beta$) prior:

$$
\text{posterior} = \text{Beta}(\alpha + k, \beta + n - k)
$$

The posterior mean is $\frac{\alpha + k}{\alpha + \beta + n}$, which interpolates between the prior mean and the empirical mean. As $n \to \infty$, the posterior concentrates on the empirical mean — the prior is "washed out" by data.

The hyperparameters $\alpha, \beta$ act as "pseudo-counts" — a Beta(1, 1) prior (uniform) is like having seen 1 success and 1 failure before any data. This gives a principled way to encode prior beliefs.

### Why conjugate priors matter

1. **Closed-form inference** — no MCMC needed; posterior is computed analytically.
2. **Online updating** — new data updates the posterior parameters; no need to store all data.
3. **Interpretable hyperparameters** — pseudo-counts make priors easy to reason about.
4. **Foundation for variational inference** — VAEs use mean-field Gaussian (conjugate) variational families.

For complex models (deep neural networks), conjugate priors don't exist — the likelihood is too complex. This is why Bayesian deep learning requires approximation (MCMC, variational inference, MC dropout).

## MAP estimation and regularization

MAP estimation is the Bayesian analogue of MLE — instead of $\arg\max_\theta P(\text{data} \mid \theta)$, we compute $\arg\max_\theta P(\theta \mid \text{data}) = \arg\max_\theta P(\text{data} \mid \theta) P(\theta)$.

### L2 regularization is a Gaussian prior

With a Gaussian prior $\theta \sim \mathcal{N}(0, \tau^2 I)$ and Gaussian likelihood:

$$
\log P(\theta \mid \text{data}) = \log P(\text{data} \mid \theta) + \log P(\theta) = -\text{loss}(\theta) - \frac{1}{2\tau^2} \|\theta\|^2 + \text{const}
$$

So MAP with Gaussian prior = minimize loss + L2 regularization. The regularization strength $\lambda = 1/(2\tau^2)$ — stronger prior (smaller $\tau$) = stronger regularization.

### L1 regularization is a Laplace prior

With a Laplace prior $\theta \sim \text{Laplace}(0, b)$:

$$
\log P(\theta) = -\frac{1}{b} \|\theta\|_1 + \text{const}
$$

So MAP with Laplace prior = minimize loss + L1 regularization. L1 induces sparsity (many $\theta_i = 0$) because the Laplace prior has a sharp peak at 0.

### Implications

This connection means:

- **Regularization is not a hack** — it has a principled Bayesian interpretation as a prior.
- **The regularization strength is a prior belief** about parameter scale.
- **Different regularizers correspond to different priors** — L2 (Gaussian) assumes parameters are small; L1 (Laplace) assumes many are exactly zero.
- **Dropout** has a Bayesian interpretation (variational approximation with Bernoulli priors) — Gal & Ghahramani 2016.

See [[Regularization Techniques]] for the regularization toolkit and [[05 - Neural Network Foundations/Training Dynamics and Stability/Dropout and Regularization|Dropout and Regularization]] for dropout's Bayesian reading.

## Bayesian model comparison

Bayes' theorem extends to model comparison. Given models $M_1, M_2, \ldots$ and data $\mathcal{D}$:

$$
P(M_i \mid \mathcal{D}) = \frac{P(\mathcal{D} \mid M_i) P(M_i)}{P(\mathcal{D})}
$$

The term $P(\mathcal{D} \mid M_i)$ is the **marginal likelihood** (evidence), computed by integrating over parameters:

$$
P(\mathcal{D} \mid M_i) = \int P(\mathcal{D} \mid \theta, M_i) P(\theta \mid M_i) d\theta
$$

The marginal likelihood automatically balances fit and complexity — more complex models can fit any data, but they spread probability mass over more outcomes, so $P(\mathcal{D} \mid M_i)$ can be lower for a complex model even if it fits better. This is **Occam's razor** made mathematically precise.

In practice, the marginal likelihood is intractable for complex models (deep nets). Approximations: BIC (Bayesian Information Criterion), variational lower bounds, or cross-validation (frequentist alternative).

## Variational inference

When the posterior $P(\theta \mid \mathcal{D})$ is intractable (complex models), **variational inference** approximates it with a simpler distribution $q(\theta)$ from a tractable family:

$$
q^* = \arg\min_q D_{KL}(q(\theta) \| P(\theta \mid \mathcal{D}))
$$

This is equivalent to maximizing the **ELBO** (Evidence Lower BOund):

$$
\mathcal{L}(q) = \mathbb{E}_q[\log P(\mathcal{D}, \theta)] - \mathbb{E}_q[\log q(\theta)] = \mathbb{E}_q[\log P(\mathcal{D} \mid \theta)] - D_{KL}(q \| P(\text{prior}))
$$

The ELBO trades off:

1. **Reconstruction** — $q$ should make the data likely ($\mathbb{E}_q[\log P(\mathcal{D} \mid \theta)]$).
2. **Regularization** — $q$ should stay close to the prior ($D_{KL}(q \| P)$).

VAEs optimize the ELBO with $q$ being a Gaussian (mean and variance from encoder network). See [[From Autoencoder to VAE]] for the architecture, [[The KL Divergence Loss]] for the divergence term, and [[Entropy Cross-Entropy and KL Divergence]] for the underlying information theory.

## Worked example: Bayesian A/B testing

```python
import numpy as np
from scipy.stats import beta

class BayesianABTest:
    def __init__(self, alpha_prior=1, beta_prior=1):
        """Beta(alpha, beta) prior for conversion rate."""
        self.alpha_A, self.beta_A = alpha_prior, beta_prior
        self.alpha_B, self.beta_B = alpha_prior, beta_prior

    def update(self, variant: str, trials: int, successes: int):
        if variant == "A":
            self.alpha_A += successes
            self.beta_A += trials - successes
        else:
            self.alpha_B += successes
            self.beta_B += trials - successes

    def probability_B_better(self, n_samples=100_000):
        """P(conversion_B > conversion_A) estimated by sampling."""
        samples_A = beta.rvs(self.alpha_A, self.beta_B, size=n_samples)
        samples_B = beta.rvs(self.alpha_B, self.beta_B, size=n_samples)
        return (samples_B > samples_A).mean()

    def expected_loss(self, variant: str, n_samples=100_000):
        """Expected loss if we pick `variant` and the other is actually better."""
        samples_A = beta.rvs(self.alpha_A, self.beta_A, size=n_samples)
        samples_B = beta.rvs(self.alpha_B, self.beta_B, size=n_samples)
        if variant == "A":
            loss = np.maximum(samples_B - samples_A, 0)
        else:
            loss = np.maximum(samples_A - samples_B, 0)
        return loss.mean()

# Usage
test = BayesianABTest(alpha_prior=1, beta_prior=1)  # uniform prior
test.update("A", trials=1000, successes=120)  # 12% conversion
test.update("B", trials=1000, successes=150)  # 15% conversion
print(f"P(B > A) = {test.probability_B_better():.3f}")
print(f"Expected loss if pick A: {test.expected_loss('A'):.4f}")
print(f"Expected loss if pick B: {test.expected_loss('B'):.4f}")
```

This is the foundation of Bayesian A/B testing — you can stop the test as soon as the expected loss of the worse variant is below a threshold. No need for fixed sample sizes or p-value corrections. [[A-B Testing and Shadow Deployment]] covers the production-side view.

## Bayes in modern AI

### Naive Bayes (still relevant)

Despite being "naive", Naive Bayes remains a strong baseline for:

- **Text classification** (spam, sentiment) — fast, interpretable, works with small data.
- **Recommendation** — collaborative filtering has a Bayesian formulation.
- **Anomaly detection** — model normal behavior, flag low-probability events.

### Bayesian optimization

Hyperparameter tuning (Optuna, Hyperopt, BoTorch) uses Gaussian processes + Bayes:

- Prior: GP over the objective function.
- Likelihood: observations (hyperparameter settings + validation score).
- Posterior: updated GP, with uncertainty.
- Acquisition function: pick next hyperparameters to maximize expected improvement.

This is sample-efficient — 10-50 evaluations often suffice, vs. 100s for grid/random search.

### Bayesian deep learning

Maintain posteriors over neural network weights:

- **MC Dropout**: dropout at inference, average predictions — approximate Bayesian posterior.
- **Bayesian neural networks**: weights are distributions, not point estimates.
- **Ensembles**: train multiple models, average — approximates Bayesian model averaging.

Use cases: uncertainty quantification (medical, autonomous driving), out-of-distribution detection, active learning.

### RLHF (Bayesian flavor)

The reward model in RLHF produces a distribution over rewards (not a point estimate). The policy update (PPO) can be seen as Bayesian-ish: the reward posterior informs the policy update. Full Bayesian RLHF is an active research area. See [[RLHF with PPO]].

The Bayesian lens reaches further: the low-rank constraint in [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]] admits a Bayesian interpretation, as does the confidence produced by probing classifiers in interpretability work.

## Why this matters for AI

- **Bayesian deep learning** promises uncertainty estimates by maintaining posteriors over weights. Critical for high-stakes applications (medicine, autonomous driving).
- **Naive Bayes** is still a strong baseline for text classification — fast, simple, interpretable.
- **Bayesian optimization** (hyperparameter tuning, black-box optimization) uses Gaussian processes + Bayes' theorem.
- **Variational inference** (VAEs, Bayesian neural nets) is approximate Bayesian inference at scale.
- **RLHF** has a Bayesian flavor: the reward model produces a posterior over rewards; the policy is updated accordingly.

## Production implications

- For most production ML, **MAP estimation** is enough — full Bayesian inference is too expensive.
- **Uncertainty quantification** via Bayesian methods is valuable for high-stakes decisions (medical, financial) but adds significant complexity.
- **Calibration**: a model's predicted probabilities should match empirical frequencies. Bayesian methods tend to be better calibrated, but aren't guaranteed.

## Common pitfalls

- **Base rate neglect** — forgetting the prior $P(A)$. Even strong evidence for a rare event doesn't make the event likely.
- **Confusing $P(A \mid B)$ with $P(B \mid A)$** — the **prosecutor's fallacy**. "If the defendant is guilty, the DNA match probability is 1 in a million" ≠ "If the DNA matches, the defendant is guilty with probability 999999/1000000".
- **Forgetting to normalize** — the posterior must sum (or integrate) to 1. Compute the evidence $P(B)$.
- **Treating priors as objective** — priors encode assumptions. Different priors give different posteriors. Be transparent about prior choices.

## Common failure modes

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Posterior collapses to prior | Likelihood too weak; data insufficient | Collect more data; check likelihood specification |
| Posterior overconfident | Prior too informative; model mis-specified | Use weaker prior; check model assumptions |
| Posterior too diffuse | Prior too weak; data noisy | Use informative prior from domain knowledge |
| MCMC doesn't converge | Posterior is multi-modal | Use better initialization; try HMC/NUTS; reparameterize |
| Variational inference underestimates uncertainty | $q$ family too simple | Use richer variational family (normalizing flows) |
| Base rate neglect in evaluation | Confusing $P(A \mid B)$ with $P(B \mid A)$ | Always compute the full Bayes formula; check with confusion matrix |

## Interview questions

1. **Q: Derive Bayes' theorem from the definition of conditional probability.**
   A: From $P(A, B) = P(A \mid B) P(B) = P(B \mid A) P(A)$, divide both sides by $P(B)$: $P(A \mid B) = \frac{P(B \mid A) P(A)}{P(B)}$. That's it — Bayes' theorem is just a rearrangement of the conditional probability definition.

2. **Q: A disease affects 1 in 1000 people. A test is 99% sensitive, 95% specific. You test positive. What's the probability you have the disease?**
   A: $P(D \mid +) = \frac{P(+ \mid D) P(D)}{P(+)} = \frac{0.99 \times 0.001}{0.99 \times 0.001 + 0.05 \times 0.999} \approx 0.0194$ (about 2%). Despite the "good" test, the low base rate means most positives are false positives. This is the **base rate fallacy** — humans consistently get this wrong because they confuse $P(+ \mid D)$ with $P(D \mid +)$.

3. **Q: How does L2 regularization relate to Bayes' theorem?**
   A: L2 regularization = MAP estimation with a Gaussian prior. With prior $\theta \sim \mathcal{N}(0, \tau^2 I)$ and Gaussian likelihood, $\log P(\theta \mid \text{data}) = -\text{loss}(\theta) - \frac{1}{2\tau^2}\|\theta\|^2 + \text{const}$. Maximizing the posterior = minimizing loss + L2 regularization, with $\lambda = 1/(2\tau^2)$. L1 regularization corresponds to a Laplace prior. This gives regularization a principled Bayesian interpretation.

4. **Q: What is a conjugate prior, and why does it matter?**
   A: A conjugate prior is one where the posterior is in the same family as the prior. Example: Beta prior + Bernoulli likelihood → Beta posterior. Conjugate priors matter because they give closed-form posteriors — no MCMC needed. Common pairs: Beta-Bernoulli, Dirichlet-Categorical, Gaussian-Gaussian, Gamma-Poisson. For complex models (deep nets), conjugate priors don't exist, requiring approximate inference (variational, MCMC).

5. **Q: What is variational inference, and how does it relate to Bayes?**
   A: Variational inference approximates an intractable posterior $P(\theta \mid \mathcal{D})$ with a simpler distribution $q(\theta)$ by minimizing $D_{KL}(q \| P)$. This is equivalent to maximizing the ELBO: $\mathcal{L}(q) = \mathbb{E}_q[\log P(\mathcal{D} \mid \theta)] - D_{KL}(q \| \text{prior})$. The ELBO trades off reconstruction (data fit) and regularization (closeness to prior). VAEs use this with Gaussian $q$ — the encoder outputs the Gaussian parameters.

6. **Q: How would you design a Bayesian A/B test?**
   A: Use a Beta prior on each variant's conversion rate (Beta(1,1) = uniform, or Beta-informed by historical data). Update with observed trials/successes: posterior is Beta($\alpha + k$, $\beta + n - k$). Compute $P(B > A)$ by sampling from both posteriors. Stop the test when the expected loss of choosing the wrong variant falls below a threshold. This is more flexible than frequentist A/B testing — no fixed sample size, can stop early, gives direct probability of superiority.

## Further reading

- Wasserman, *All of Statistics*, Chapter 1–2.
- Efron & Hastie, *Computer Age Statistical Inference* — modern treatment.
- Bishop, *Pattern Recognition and Machine Learning*, Chapter 2.

## See also

- [[Mathematics MOC]]
- [[Probability Essentials]]
- [[Gaussian Distribution]]
- [[Entropy Cross-Entropy and KL Divergence]]
- [[Estimators and Bias]]
- [[Hypothesis Testing]]
- [[Probability and Statistics for ML]]
- [[04 - Machine Learning/Regression/Linear Regression|Linear Regression]]
- [[04 - Machine Learning/Regression/Logistic Regression|Logistic Regression]]
- [[Regularization Techniques]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Dropout and Regularization|Dropout and Regularization]]
- [[From Autoencoder to VAE]]
- [[The KL Divergence Loss]]
- [[A-B Testing and Shadow Deployment]]
- [[RLHF with PPO]]
- [[Pretraining Objectives and Scaling Laws]]
- [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]]
