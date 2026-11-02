---
title: The Reparameterization Trick
type: derivation
aliases:
  - reparameterization trick
  - reparametrization trick
  - reparameterization
  - "02. The Reparameterization Trick"
tags:
  - variational-autoencoder
  - reparameterization
  - backpropagation
  - generative-models
  - gradient-estimators
sources:
  - "02. The Reparameterization Trick"
created_index: 12
---

The reparameterization trick is what makes variational autoencoders trainable: the latent code is a random sample, sampling has no derivative, and yet the encoder must receive gradients through it. The trick rewrites the sample as a deterministic, differentiable function of the distribution's parameters plus an independent noise variable, so that backpropagation flows through the parameters while the randomness is treated as a constant. This note states the problem, derives the rewrite and its gradients, explains it through the graphical-model view, and generalizes the principle beyond Gaussians to the whole class of reparameterizable gradient estimators. It resolves the sampling problem raised in [[From Autoencoder to VAE]] and works alongside [[The KL Divergence Loss]], the other half of the VAE objective.

## The problem

In a VAE, the latent $z$ is sampled from the encoder's output distribution:

$$z \sim \mathcal{N}(\mu, \sigma^2)$$

We need to backpropagate the reconstruction loss through $z$ to train the encoder (which produces $\mu$ and $\sigma$). But **sampling is a stochastic operation** — it is not differentiable. You cannot compute $\partial z / \partial \mu$ or $\partial z / \partial \sigma$ because the sampling operation has no derivative.

This is the **reparameterization problem**: how do you backpropagate through a sampled random variable?

## The trick

The insight: rewrite the sampling so that the randomness is **independent** of the parameters, and the parameters enter through a differentiable operation.

Instead of sampling $z \sim \mathcal{N}(\mu, \sigma^2)$ directly, sample a noise variable $\epsilon \sim \mathcal{N}(0, 1)$ (which does not depend on any parameters), then compute $z$ as a deterministic function of $\mu$, $\sigma$, and $\epsilon$:

$$z = \mu + \sigma \odot \epsilon$$

where $\odot$ is element-wise multiplication.

This is mathematically equivalent — $z = \mu + \sigma \epsilon$ is also distributed as $\mathcal{N}(\mu, \sigma^2)$ — but the randomness is now in $\epsilon$, which is treated as a constant for backpropagation. The parameters $\mu$ and $\sigma$ enter through addition and multiplication, which **are** differentiable:

$$\frac{\partial z}{\partial \mu} = 1, \quad \frac{\partial z}{\partial \sigma} = \epsilon$$

Both partial derivatives are now well-defined: the mean enters through addition, so its gradient is the constant 1; the standard deviation enters through multiplication by the noise, so its gradient is the noise itself. Backpropagation can now flow through $z$ to $\mu$ and $\sigma$, and from there to the encoder's weights. The trick works because we have **separated the randomness from the parameters**.

## Why this works — the graphical model view

The original sampling $z \sim \mathcal{N}(\mu, \sigma^2)$ is a single stochastic node that depends on $\mu$ and $\sigma$. Gradients cannot flow through stochastic nodes.

The reparameterized version splits this into two nodes:

1. A **stochastic** node $\epsilon \sim \mathcal{N}(0, 1)$, which has no parameters (and no gradients needed).
2. A **deterministic** node $z = \mu + \sigma \cdot \epsilon$, which depends on $\mu$, $\sigma$, and $\epsilon$ through differentiable operations.

Gradients flow through the deterministic node to $\mu$ and $\sigma$. The stochastic node $\epsilon$ is treated as a constant (like the input $x$).

```text
Original:               Reparameterized:
                        
  μ, σ                     μ, σ        ε ~ N(0,1)
   │                       │  │           │
   ▼                       ▼  ▼           │
  z ~ N(μ, σ²)            z = μ + σ·ε ──┘ (deterministic)
   │                       │
   ▼                       ▼
  decoder                 decoder
```

The reparameterization moves the randomness "outside" the computational graph that depends on parameters, so backpropagation can reach the parameters.

## Generalization

The reparameterization trick is not specific to Gaussians. Any distribution whose samples can be written as a deterministic function of parameters and an independent noise source can be reparameterized:

- **Gaussian:** $z = \mu + \sigma \epsilon$, $\epsilon \sim \mathcal{N}(0, 1)$.
- **Bernoulli:** use the Gumbel-Softmax trick (Jang et al. 2017).
- **Categorical:** same Gumbel-Softmax trick.
- **Many others:** any distribution with a tractable inverse-CDF can be reparameterized via $z = F^{-1}(u; \theta)$ where $u \sim \text{Uniform}(0, 1)$.

The general principle: **if you can express sampling as $z = g(\theta, \epsilon)$ where $\epsilon$ is parameter-free noise and $g$ is differentiable in $\theta$, you can backpropagate through $z$.**

This principle underlies modern probabilistic deep learning frameworks (Pyro, TensorFlow Probability, PyTorch distributions) and is used in VAEs, Bayesian neural networks, and many other models.

## Why this matters beyond VAEs

The reparameterization trick is the enabling technical innovation for a whole class of models called **"reparameterizable" or "reparametrized" gradients**. Anytime you want to train a model with a stochastic intermediate layer, you face the same problem: how do you backprop through the sampling? The reparameterization trick is the general answer (when it applies).

Specific applications:

- **VAEs:** $z = \mu + \sigma \epsilon$ (this note).
- **Gumbel-Softmax for discrete VAEs:** reparameterizes categorical sampling.
- **Reinforcement learning (policy gradient methods):** the REINFORCE estimator is an alternative when reparameterization is not possible (e.g., for discrete actions), but it has higher variance. When reparameterization is possible, it is preferred.
- **Stochastic neural networks:** any network with a stochastic layer benefits from reparameterization.

In every case the pattern is the same: isolate the randomness in a parameter-free noise source, let the parameters enter through differentiable operations, and ordinary gradient machinery — [[Backpropagation]] — can reach the model's weights. The policy-gradient family, where the REINFORCE estimator is the standard alternative, is covered in [[Policy Gradients and Actor Critic]].

## What you should walk away with

1. The problem: sampling $z \sim \mathcal{N}(\mu, \sigma^2)$ is stochastic and not differentiable — you cannot backprop through it.
2. The trick: rewrite as $z = \mu + \sigma \odot \epsilon$ where $\epsilon \sim \mathcal{N}(0, 1)$ is parameter-free. The parameters enter through differentiable operations; the randomness is in $\epsilon$ (treated as a constant).
3. This is mathematically equivalent (same distribution) but allows backpropagation.
4. The general principle: if sampling can be written as $z = g(\theta, \epsilon)$ with $\epsilon$ parameter-free and $g$ differentiable, you can backprop through $z$.
5. This principle underlies VAEs, Gumbel-Softmax, and many probabilistic deep learning models.

## See also

- [[12 - Generative Models/Chapter Overview|Chapter Overview]] — where the VAE machinery sits among the generative families
- [[From Autoencoder to VAE]] — the sampling problem this trick solves
- [[The KL Divergence Loss]] — the other half of the VAE objective
- [[Backpropagation]] — the gradient machinery the trick feeds into
- [[Policy Gradients and Actor Critic]] — the policy-gradient world of the REINFORCE estimator
