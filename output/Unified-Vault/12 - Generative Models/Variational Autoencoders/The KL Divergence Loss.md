---
title: The KL Divergence Loss
type: derivation
aliases:
  - KL divergence loss
  - KL divergence
  - Kullback-Leibler divergence
  - KL regularizer
  - "03. The KL Divergence Loss"
tags:
  - variational-autoencoder
  - kl-divergence
  - generative-models
  - regularization
  - latent-space
sources:
  - "03. The KL Divergence Loss"
created_index: 11
---

The KL divergence term is the regularizer that shapes a variational autoencoder's latent space: it penalizes the gap between the encoder's Gaussian posterior and the standard-normal prior, pulling latent means to zero and latent variances to one. Because both distributions are Gaussian, the penalty collapses to a closed form that is cheap to compute and differentiable in the encoder's outputs — no integration required. This note derives that closed form from the general definition of KL divergence, interprets each term of the result, explains why KL in particular is the mathematically justified penalty rather than an arbitrary prior-matching term, and examines the price it exacts — the notorious blurriness of VAE samples. It completes the objective assembled in [[From Autoencoder to VAE]] and pairs with [[The Reparameterization Trick]], the mechanism that makes the sampled latent trainable.

## What KL divergence measures

The **Kullback-Leibler (KL) divergence** $D_{KL}(p \| q)$ measures how much one distribution $p$ differs from another $q$:

$$D_{KL}(p \| q) = \int p(x) \log \frac{p(x)}{q(x)} dx$$

Four properties matter here:

- $D_{KL} \geq 0$ always.
- $D_{KL} = 0$ if and only if $p = q$.
- **Not symmetric:** $D_{KL}(p \| q) \neq D_{KL}(q \| p)$ in general.
- Not a true distance (no triangle inequality), but often used as one informally.

In the VAE, the KL term measures how far the encoder's approximate posterior $q_\phi(z|x) = \mathcal{N}(\mu(x), \sigma(x)^2)$ is from the prior $p(z) = \mathcal{N}(0, I)$. Minimizing the KL pushes the encoder's distributions toward the prior.

## The closed-form for Gaussians

### The general two-Gaussian case

For two Gaussians $p = \mathcal{N}(\mu_1, \sigma_1^2)$ and $q = \mathcal{N}(\mu_2, \sigma_2^2)$, the KL divergence has a closed form:

$$D_{KL}(p \| q) = \log \frac{\sigma_2}{\sigma_1} + \frac{\sigma_1^2 + (\mu_1 - \mu_2)^2}{2 \sigma_2^2} - \frac{1}{2}$$

This is the stepping stone for the VAE: everything that follows is substitution into this formula.

### Specializing to the standard-normal prior

In the VAE, $q = \mathcal{N}(0, 1)$ (so $\mu_2 = 0$, $\sigma_2 = 1$). Substituting these values into the closed form: the scale term $\log \frac{\sigma_2}{\sigma_1}$ becomes $\log \frac{1}{\sigma}$, that is, $-\log \sigma$; the middle term $\frac{\sigma_1^2 + (\mu_1 - \mu_2)^2}{2 \sigma_2^2}$ becomes $\frac{\sigma^2 + \mu^2}{2}$; and the constant $-\frac{1}{2}$ is unchanged. Writing $-\log \sigma$ as $-\frac{1}{2} \log \sigma^2$ and pulling out the common factor $\frac{1}{2}$ collects the three pieces into the familiar bracketed form:

$$D_{KL}(\mathcal{N}(\mu, \sigma^2) \| \mathcal{N}(0, 1)) = \frac{1}{2} \left(\mu^2 + \sigma^2 - \log \sigma^2 - 1\right)$$

### Summing over the latent dimensions

For a $k$-dimensional latent (independent dimensions), this sums:

$$\mathcal{L}_{KL} = \frac{1}{2} \sum_{i=1}^k \left(\mu_i^2 + \sigma_i^2 - \log \sigma_i^2 - 1\right)$$

This is the KL loss used in VAE training. It is cheap to compute (no integration needed — the closed form is evaluated directly) and differentiable in $\mu$ and $\sigma$.

## What each term does

Let's interpret the three terms in the per-dimension KL: $\frac{1}{2}(\mu_i^2 + \sigma_i^2 - \log \sigma_i^2 - 1)$.

### Pulling the mean to zero

The $\mu_i^2$ term penalizes the mean being far from zero. It pushes each latent dimension's mean toward 0, which is the mean of the prior $\mathcal{N}(0, 1)$. Without this, the encoder could shift all distributions to some non-zero mean, and sampling from $\mathcal{N}(0, 1)$ would miss them.

### Pulling the variance to one

The $\sigma_i^2 - \log \sigma_i^2 - 1$ term is minimized at $\sigma_i^2 = 1$ (where it equals 0). It penalizes the variance being either too small (overfitting — the distribution becomes a delta function at the best encoding) or too large (underfitting — the distribution is too broad to be useful). The $\log \sigma^2$ term makes the penalty asymmetric: it grows faster for small $\sigma$ than for large, which prevents the encoder from collapsing to deterministic mappings.

### The balance

The KL term is in tension with the reconstruction term:

- **Reconstruction** wants $\sigma \to 0$ (deterministic encoding — the latent is exactly the best encoding of the input).
- **KL** wants $\sigma \to 1$ (matching the prior — the latent is a broad distribution).

The balance determines the "bluriness" of the VAE. High KL weight → broad distributions → blurry samples (the decoder must handle a wide range of latents, so it averages). Low KL weight → narrow distributions → sharp samples but the latent space is less Gaussian (sampling becomes unreliable). The $\beta$-VAE framework explicitly tunes this tradeoff via a coefficient $\beta$ on the KL term.

## Why KL and not just "match the prior"?

You might wonder: why use KL divergence specifically? Why not just penalize $|\mu|$ and $|\sigma - 1|$ directly?

The answer is the **probabilistic interpretation** from [[From Autoencoder to VAE]]. The VAE maximizes the ELBO, which is a lower bound on the data likelihood $\log p(x)$. The KL term in the ELBO is exactly the KL divergence between the approximate posterior and the prior — it falls out of the variational inference derivation, not arbitrarily chosen.

Using a different penalty (like $L_2$ on $\mu$ and $\sigma$) would not correspond to a principled probabilistic objective. The KL divergence is the "right" measure of distributional distance for the variational inference framework, and using it ensures the VAE is optimizing a well-defined probabilistic objective (the ELBO), not just a heuristic reconstruction-plus-regularization loss.

## The practical impact: blurriness

VAE samples are notoriously **blurry**. This is the price of the KL regularization: by forcing the latent distributions to be broad (close to the prior), the decoder must handle a range of latents for each input, and it learns to produce the "average" reconstruction over that range — which is blurry.

> [!warning] Blurriness is the price of the prior-matching term
> Forcing the latent distributions to be broad means the decoder must handle a range of latents for each input; it learns to produce the "average" reconstruction over that range, and an average over many plausible reconstructions is blurry.

This blurriness is the main reason GANs overtook VAEs for image generation: GANs do not have the KL regularization and can produce sharp samples — they replace the KL term with an adversarial loss (see [[The Adversarial Game]]). But GANs have their own problems (training instability, mode collapse), and diffusion models have since surpassed both. The VAE remains important as a conceptual foundation and as a component of modern systems (Stable Diffusion uses a VAE to encode/decode between pixel space and latent space — see [[Score-Based and Latent Diffusion]]).

## What you should walk away with

1. KL divergence measures how far one distribution is from another; it is non-negative and zero iff the distributions match.
2. For Gaussians, the KL has a closed form: $D_{KL}(\mathcal{N}(\mu, \sigma^2) \| \mathcal{N}(0, 1)) = \frac{1}{2}(\mu^2 + \sigma^2 - \log \sigma^2 - 1)$.
3. The $\mu^2$ term pulls means to zero; the $\sigma^2 - \log \sigma^2 - 1$ term pulls variances to one.
4. KL is in tension with reconstruction: reconstruction wants narrow distributions (sharp encoding), KL wants broad distributions (matching the prior).
5. The blurriness of VAE samples is the price of this regularization — the decoder averages over the broad latent distribution.
6. KL is the "right" penalty because it falls out of the variational inference framework (maximizing the ELBO), not an arbitrary choice.

## See also

- [[12 - Generative Models/Chapter Overview|Chapter Overview]] — where the VAE objective sits among the generative families
- [[From Autoencoder to VAE]] — the two-part loss and the ELBO this regularizer completes
- [[The Reparameterization Trick]] — making the sampled latent differentiable
- [[The Adversarial Game]] — GANs replace the KL term with an adversarial loss
- [[Training Dynamics and Mode Collapse]] — the instability GANs trade for sharp samples
- [[Score-Based and Latent Diffusion]] — diffusion models surpassing both, and the VAE inside Stable Diffusion
