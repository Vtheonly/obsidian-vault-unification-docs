---
title: Entropy Cross-Entropy and KL Divergence
type: concept
aliases:
  - Entropy Cross-Entropy KL
  - Entropy, Cross-Entropy, and KL Divergence
  - Cross-Entropy
  - KL Divergence
tags:
  - mathematics
  - information-theory
  - entropy
  - cross-entropy
  - kl-divergence
sources:
  - Entropy, Cross-Entropy, and KL Divergence
created_index: 3
---

Information theory gives machine learning its fundamental bookkeeping for uncertainty. **Entropy** measures how uncertain a probability distribution is, **cross-entropy** measures the cost of encoding outcomes from one distribution with a code optimized for another, and **KL divergence** measures how different two distributions are. The three are tied together by the identity $D_{KL}(p \,\|\, q) = H(p, q) - H(p)$, which is why cross-entropy is the loss function for almost all classification and language modeling while KL divergence shows up everywhere as a regularizer and constraint.

> [!info] TL;DR
> **Entropy** measures uncertainty. **Cross-entropy** measures the cost of using one distribution to encode another. **KL divergence** measures how different two distributions are. Cross-entropy is the loss function for almost all classification and language modeling.

## Entropy

The **Shannon entropy** of a discrete distribution $p$ over outcomes $\{x_1, \ldots, x_n\}$ is:

$$
H(p) = -\sum_{i=1}^{n} p(x_i) \log p(x_i)
$$

(convention: $0 \log 0 = 0$.)

### Intuition

Entropy is the **average number of bits needed to encode an outcome from $p$**, using an optimal code for $p$. It measures uncertainty:

- A fair coin: $H = 1$ bit.
- A biased coin (99% heads): $H \approx 0.08$ bits — almost no uncertainty.
- A fair 8-sided die: $H = 3$ bits.

The maximum entropy distribution over $n$ outcomes is the **uniform distribution**, with $H = \log n$.

### Differential entropy

For a continuous distribution with density $p(x)$, the analogous quantity is the differential entropy:

$$
h(p) = -\int p(x) \log p(x) \, dx
$$

Differential entropy can be negative (unlike discrete entropy) and is less intuitive. It's used in theory but rarely directly in ML loss functions.

## Cross-entropy

The **cross-entropy** between two distributions $p$ and $q$ (over the same outcome space) is:

$$
H(p, q) = -\sum_{i=1}^{n} p(x_i) \log q(x_i)
$$

### Intuition

Cross-entropy is the **average number of bits needed to encode outcomes from $p$ using a code optimized for $q$**. If $q = p$, cross-entropy equals entropy — the optimal case. If $q \neq p$, you need more bits.

### Cross-entropy as a loss function

In supervised classification, $p$ is the **true** distribution (one-hot label) and $q$ is the **predicted** distribution (softmax output). For a single example with true class $y$ and predicted probabilities $\hat{q}$:

$$
H(p, q) = -\log \hat{q}_y
$$

This is the **negative log-likelihood (NLL)** of the true class. Averaging over a batch gives the standard **cross-entropy loss** — the classification workhorse within the broader family of [[Loss Functions]].

```python
import torch.nn.functional as F
loss = F.cross_entropy(logits, labels)  # logits are pre-softmax
```

### Why cross-entropy and not MSE

For classification, MSE on softmax outputs has vanishing gradients when predictions are very wrong (because softmax saturates). Cross-entropy with logits has clean gradients: $\nabla_{\text{logits}} \mathcal{L} = \text{softmax}(\text{logits}) - \text{onehot}(y)$. This is why cross-entropy is universal for classification and language modeling.

## KL divergence

The **Kullback-Leibler (KL) divergence** from $p$ to $q$ is:

$$
D_{KL}(p \,\|\, q) = \sum_{i} p(x_i) \log \frac{p(x_i)}{q(x_i)} = H(p, q) - H(p)
$$

### Properties

- **Non-negative**: $D_{KL}(p \,\|\, q) \geq 0$, with equality iff $p = q$.
- **Not symmetric**: $D_{KL}(p \,\|\, q) \neq D_{KL}(q \,\|\, p)$ in general. (For a symmetric version, see Jensen-Shannon divergence.)
- **Not a true metric** — doesn't satisfy the triangle inequality.

### Intuition

KL divergence measures the **extra bits** you need to encode outcomes from $p$ when using a code optimized for $q$ instead of $p$. Equivalently: how surprised you are by data from $p$ when you expected $q$.

### Forward vs reverse KL

- **Forward KL** $D_{KL}(p \,\|\, q)$ — "mean-seeking" / "zero-avoiding". $q$ must cover everywhere $p$ is non-zero. Used in maximum likelihood (MLE).
- **Reverse KL** $D_{KL}(q \,\|\, p)$ — "mode-seeking". $q$ avoids regions where $p$ is small. Used in variational inference.

### KL as a regularizer

Many ML objectives can be written as:

$$
\mathcal{L} = -\log p(\text{data} \mid \theta) + \beta D_{KL}(q \,\|\, p)
$$

— a likelihood term plus a KL regularizer. Examples:
- **VAEs** — KL between the approximate posterior and the prior.
- **RLHF** — KL penalty between the policy and a reference model to prevent reward hacking. See [[RLHF with PPO]].
- **Knowledge distillation** — KL between student and teacher softmax outputs.

## Why this matters for AI

### Language modeling is cross-entropy minimization

An autoregressive language model $p_\theta$ predicts the next token $x_t$ given context. Training minimizes:

$$
\mathcal{L} = -\sum_t \log p_\theta(x_t \mid x_{<t})
$$

— the cross-entropy between the empirical next-token distribution (one-hot on the actual next token) and the model's predicted distribution. See [[Perplexity]] and [[Decoder-Only Architecture]].

### Softmax + cross-entropy is the standard output layer

For classification over $K$ classes, the model produces logits $z \in \mathbb{R}^K$, applies softmax to get probabilities $\hat{q}$, and minimizes cross-entropy against the true label. The fused `F.cross_entropy(logits, labels)` is numerically stable (uses log-sum-exp) and computationally efficient.

### KL divergence is everywhere in alignment

- **RLHF**: penalize deviation from the reference policy.
- **DPO**: implicitly optimizes a KL-constrained objective. See [[DPO Derivation]].
- **Constitutional AI / RLAIF**: similar KL constraints.

### Perplexity is exponentiated cross-entropy

$$
\text{Perplexity} = \exp\left(\frac{\mathcal{L}}{N}\right)
$$

— the "effective vocabulary size" of the model. Lower is better. See [[Perplexity]].

## Deriving the cross-entropy gradient

The clean gradient of cross-entropy + softmax is one of the most important derivations in ML. For logits $\mathbf{z}$, true class $y$, and softmax probabilities $\hat{q}_i = \frac{e^{z_i}}{\sum_j e^{z_j}}$:

$$
\mathcal{L} = -\log \hat{q}_y = -z_y + \log \sum_j e^{z_j}
$$

Taking the gradient w.r.t. $z_i$:

$$
\frac{\partial \mathcal{L}}{\partial z_i} = -\mathbb{1}[i = y] + \frac{e^{z_i}}{\sum_j e^{z_j}} = \hat{q}_i - \mathbb{1}[i = y]
$$

So $\nabla_{\mathbf{z}} \mathcal{L} = \hat{\mathbf{q}} - \text{onehot}(y)$ — the gradient is simply the difference between the predicted probability distribution and the true one-hot distribution.

### Why this is beautiful

1. **Linear gradient**: the gradient is linear in the prediction error — no saturation.
2. **No vanishing gradient**: even when the prediction is very wrong ($\hat{q}_y \approx 0$), the gradient is large (close to 1), driving learning.
3. **Numerically stable**: with log-sum-exp, no overflow.
4. **Fused implementation**: `F.cross_entropy` computes softmax + NLL in one kernel, avoiding the intermediate probability computation.

### Contrast with MSE on softmax

If you used MSE on softmax outputs, $\mathcal{L} = \sum_i (\hat{q}_i - y_i)^2$, the gradient involves $\hat{q}_i(1 - \hat{q}_i)$ — which vanishes when $\hat{q}_i \approx 0$ or $\hat{q}_i \approx 1$. When the prediction is very wrong, the gradient is ~0, so the model doesn't learn. This is why cross-entropy, not MSE, is universal for classification.

## Worked example: entropy, cross-entropy and KL by hand

Two distributions over $\{a, b, c\}$:
- $p = (0.5, 0.3, 0.2)$
- $q = (0.4, 0.4, 0.2)$

$$
H(p) = -(0.5 \log 0.5 + 0.3 \log 0.3 + 0.2 \log 0.2) \approx 1.03 \text{ bits}
$$

$$
H(p, q) = -(0.5 \log 0.4 + 0.3 \log 0.4 + 0.2 \log 0.2) \approx 1.07 \text{ bits}
$$

$$
D_{KL}(p \,\|\, q) = H(p, q) - H(p) \approx 0.04 \text{ bits}
$$

The distributions are close, so the KL is small.

## Worked example: computing cross-entropy in PyTorch

The same computation in code, including the manual version that shows why the fused op is equivalent, and the gradient check that confirms the softmax-minus-onehot form:

```python
import torch
import torch.nn.functional as F

# Logits for 3 classes, batch of 4
logits = torch.tensor([
    [2.0, 1.0, 0.1],  # class 0 likely
    [0.1, 2.0, 1.0],  # class 1 likely
    [1.0, 0.1, 2.0],  # class 2 likely
    [0.5, 0.5, 0.5],  # uncertain
])
labels = torch.tensor([0, 1, 2, 1])

# Fused cross-entropy (numerically stable, recommended)
loss = F.cross_entropy(logits, labels)
print(f"Cross-entropy loss: {loss.item():.4f}")

# Manual computation (for understanding)
log_probs = F.log_softmax(logits, dim=-1)
nll = -log_probs[range(4), labels]
manual_loss = nll.mean()
print(f"Manual loss: {manual_loss.item():.4f}")
# Should match

# Gradient (beautiful: softmax - onehot)
probs = F.softmax(logits, dim=-1)
grad = probs.clone()
grad[range(4), labels] -= 1
grad /= 4  # batch mean
print(f"Gradient:\n{grad}")
# Each row is (predicted_probs - onehot_label) / batch_size
```

## Forward vs reverse KL in detail

The asymmetry of KL divergence has profound implications:

### Forward KL: $D_{KL}(p \| q)$

- **Mean-seeking / zero-avoiding**: $q$ must cover everywhere $p$ is non-zero (otherwise KL = ∞).
- **Mass-covering**: $q$ spreads out to cover all modes of $p$.
- **Used in MLE**: maximizing likelihood = minimizing $D_{KL}(\hat{p}_{\text{data}} \| q_\theta)$.
- **Behavior**: $q$ avoids being small where $p$ is large.

### Reverse KL: $D_{KL}(q \| p)$

- **Mode-seeking / zero-forcing**: $q$ avoids regions where $p$ is small (otherwise KL = ∞).
- **Mass-concentrating**: $q$ collapses to one mode of $p$.
- **Used in variational inference**: ELBO optimization minimizes $D_{KL}(q \| p_{\text{posterior}})$.
- **Behavior**: $q$ avoids being large where $p$ is small.

### Practical implication

- **MLE** (forward KL) gives a model that covers all data modes — but may put probability mass in "empty" regions between modes.
- **Variational inference** (reverse KL) gives a model that focuses on one mode — but may miss other modes entirely.

This is why VAEs (reverse KL) tend to produce blurry samples (they average over modes), while GANs (different objective) produce sharp samples (they focus on modes).

## KL in modern AI

### RLHF KL penalty

In RLHF, the policy $\pi_\theta$ is trained to maximize reward while staying close to a reference policy $\pi_{\text{ref}}$:

$$
\mathcal{L} = -\mathbb{E}_{\pi_\theta}[r(x, y)] + \beta D_{KL}(\pi_\theta \| \pi_{\text{ref}})
$$

The KL coefficient $\beta$ controls the trade-off:
- $\beta$ too low: reward hacking — the policy exploits reward model imperfections.
- $\beta$ too high: no learning — the policy stays identical to the reference.
- Typical $\beta$: 0.01 to 0.5, tuned per task.

### DPO's implicit KL

DPO (Direct Preference Optimization) rewrites the RLHF objective to eliminate the reward model. The DPO loss implicitly optimizes a KL-constrained objective:

$$
\mathcal{L}_{\text{DPO}} = -\log \sigma\left(\beta \log \frac{\pi_\theta(y_w | x)}{\pi_{\text{ref}}(y_w | x)} - \beta \log \frac{\pi_\theta(y_l | x)}{\pi_{\text{ref}}(y_l | x)}\right)
$$

where $y_w$ is the preferred response and $y_l$ is the dispreferred. The KL constraint is baked in — no separate penalty needed.

### Knowledge distillation

Distillation trains a student model to match a teacher's output distribution:

$$
\mathcal{L} = (1 - \alpha) H(p, q_{\text{student}}) + \alpha T^2 D_{KL}(q_{\text{teacher}}^T \| q_{\text{student}}^T)
$$

where $T$ is temperature (softens the distributions) and $\alpha$ balances hard-label and soft-label losses. The KL term transfers the teacher's "dark knowledge" — the relative probabilities between non-target classes.

### VAEs

VAEs maximize the ELBO, which includes a KL term:

$$
\mathcal{L} = \mathbb{E}_q[\log p(x | z)] - D_{KL}(q(z | x) \| p(z))
$$

The KL term regularizes the latent space toward the prior $p(z) = \mathcal{N}(0, I)$. Without it, the encoder could collapse to a delta function (no information in the latent). See [[From Autoencoder to VAE]] and [[The KL Divergence Loss]] for how this term arises in practice.

### Constitutional AI and RLAIF

RLAIF (Reinforcement Learning from AI Feedback) uses an AI judge instead of human raters. The same KL-constrained objective applies — the KL penalty prevents the policy from drifting too far from the reference, ensuring stability.

## Entropy in practice

### Entropy as a quality metric

- **High entropy** outputs: the model is uncertain — common in open-ended generation.
- **Low entropy** outputs: the model is confident — common in factual Q&A, code.
- **Entropy collapse** during training: the model becomes overconfident — a sign of overfitting or mode collapse.

### Temperature scaling

Softmax with temperature $T$: $\hat{q}_i = \frac{e^{z_i / T}}{\sum_j e^{z_j / T}}$.
- $T = 1$: normal softmax.
- $T > 1$: softer (higher entropy) — more diverse, less confident.
- $T < 1$: sharper (lower entropy) — more confident, less diverse.
- $T \to 0$: argmax (greedy decoding).

Temperature is also the main dial for diversity at generation time — see [[Sampling Strategies]].

### Calibration

A well-calibrated model's confidence matches its accuracy: if it says "90% confident", it should be right 90% of the time. Modern neural networks are often miscalibrated (overconfident). **Temperature scaling** on a validation set can fix this — find $T$ that minimizes NLL on validation data.

## Common pitfalls

- **Forgetting to use log-softmax** — computing `log(softmax(logits))` directly is numerically unstable. Use `F.log_softmax` or `F.cross_entropy` which use log-sum-exp internally.
- **Confusing nats and bits** — using natural log gives entropy in **nats**; using $\log_2$ gives entropy in **bits**. ML uses nats by default.
- **Interpreting KL as a distance** — KL is not symmetric and not a metric. Don't say "the distance between $p$ and $q$".
- **KL with zero probabilities** — if $p(x) > 0$ but $q(x) = 0$, $D_{KL}(p \,\|\, q) = \infty$. Always smooth $q$ or use a prior.

## Production implications

- **Loss monitoring**: track cross-entropy on a held-out set. An upward trend indicates overfitting or distribution shift.
- **KL in RLHF**: too low → reward hacking; too high → no learning. The KL coefficient is one of the most important hyperparameters in RLHF. Typical values: 0.01–0.5.
- **Quantifying hallucination**: KL between the model's output distribution and a grounded distribution (from retrieval) can flag [[Hallucination]].

## Common failure modes

The recurring symptoms below trace back to the numerical and optimization properties discussed above:

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| NaN in cross-entropy | log(0) from softmax underflow | Use `F.cross_entropy` (log-sum-exp); avoid manual log(softmax) |
| Loss not decreasing | Learning rate too high/low; gradient vanishing | Check gradient norms; tune LR |
| Model overconfident | Poor calibration; entropy collapse | Temperature scaling; label smoothing |
| RLHF reward hacking | KL coefficient too low | Increase $\beta$; monitor KL divergence |
| VAE blurry samples | KL weight too high | Decrease KL weight; use β-VAE scheduling |
| Distillation doesn't transfer | Temperature too low | Increase $T$ (typical: 4-20); check $\alpha$ |
| KL = ∞ | $q(x) = 0$ where $p(x) > 0$ | Smooth $q$ (add epsilon); use Laplace smoothing |

For loss spikes and broader training instability connected to cross-entropy, see [[Loss Spikes and Stability]].

## Interview questions

1. **Q: Derive the gradient of cross-entropy + softmax.**
   A: $\mathcal{L} = -\log \hat{q}_y = -z_y + \log \sum_j e^{z_j}$. Taking gradient: $\frac{\partial \mathcal{L}}{\partial z_i} = -\mathbb{1}[i=y] + \frac{e^{z_i}}{\sum_j e^{z_j}} = \hat{q}_i - \mathbb{1}[i=y]$. So $\nabla_{\mathbf{z}} \mathcal{L} = \hat{\mathbf{q}} - \text{onehot}(y)$ — the gradient is the difference between predicted and true distributions. This is why cross-entropy has no vanishing gradient (unlike MSE on softmax).

2. **Q: Why is cross-entropy preferred over MSE for classification?**
   A: MSE on softmax has gradient $\propto \hat{q}_i(1 - \hat{q}_i)$, which vanishes when $\hat{q}_i \approx 0$ or $\approx 1$. When the prediction is very wrong ($\hat{q}_y \approx 0$), the gradient is ~0, so the model doesn't learn. Cross-entropy's gradient is $\hat{q} - \text{onehot}$ — large when the prediction is wrong, driving learning. This is why cross-entropy is universal for classification.

3. **Q: What's the difference between forward and reverse KL?**
   A: Forward KL $D_{KL}(p \| q)$ is mean-seeking (zero-avoiding) — $q$ must cover everywhere $p$ is non-zero. Used in MLE. Reverse KL $D_{KL}(q \| p)$ is mode-seeking (zero-forcing) — $q$ avoids regions where $p$ is small. Used in variational inference. The asymmetry explains why VAEs (reverse KL) produce blurry samples (averaging modes) while GANs produce sharp samples (focusing on modes).

4. **Q: How is KL used in RLHF?**
   A: RLHF objective: maximize reward minus $\beta D_{KL}(\pi_\theta \| \pi_{\text{ref}})$. The KL penalty keeps the policy close to the reference, preventing reward hacking. $\beta$ too low → reward hacking; too high → no learning. Typical $\beta$: 0.01-0.5. DPO eliminates the explicit KL by rewriting the objective — the KL constraint is baked into the loss.

5. **Q: What is temperature scaling, and why is it used?**
   A: Softmax with temperature $T$: $\hat{q}_i \propto e^{z_i / T}$. $T > 1$ softens (higher entropy, more diverse); $T < 1$ sharpens (lower entropy, more confident). Used for: (1) calibration — find $T$ on validation set to fix overconfidence, (2) knowledge distillation — high $T$ reveals "dark knowledge" (relative probabilities between non-target classes), (3) sampling — control diversity of generation.

6. **Q: Why does $D_{KL}(p \| q) = \infty$ when $q(x) = 0$ but $p(x) > 0$?**
   A: The KL term $p(x) \log(p(x)/q(x))$ has $q(x) = 0$ in the denominator of the log. $\log(p(x)/0) = \log(\infty) = \infty$. So if $p$ has mass where $q$ has none, the KL is infinite. This is why forward KL is "zero-avoiding" — $q$ must cover everywhere $p$ is non-zero. In practice, smooth $q$ (add epsilon) or use a prior to avoid infinities.

## Further reading

- Cover & Thomas, *Elements of Information Theory* — the canonical reference.
- MacKay, *Information Theory, Inference, and Learning Algorithms* — free online, excellent intuition.
- Goodfellow et al., *Deep Learning* — Chapter 3.

## See also

- [[Mathematics MOC]] — the area hub.
- [[Probability Essentials]] — distributions, expectation.
- [[Bayes Theorem]] — variational inference uses KL.
- [[Gaussian Distribution]] — closed-form Gaussian KL.
- [[Gradient and Chain Rule]] — cross-entropy gradient derivation.
- [[Optimization Essentials]] — how the loss enters optimization.
- [[Perplexity]] — exponentiated cross-entropy.
- [[BPE]] — tokenization affects entropy.
- [[Decoder-Only Architecture]] — cross-entropy as training objective.
- [[DPO Derivation]] — implicit KL in DPO.
- [[RLHF with PPO]] — KL penalty.
- [[From Autoencoder to VAE]] — KL in the ELBO.
- [[The KL Divergence Loss]] — the VAE KL term in depth.
- [[Loss Functions]] — the broader loss-function family.
- [[Loss Spikes and Stability]] — cross-entropy instability.
- [[Hallucination]] — KL as a hallucination signal.
- [[Sampling Strategies]] — temperature at generation time.
