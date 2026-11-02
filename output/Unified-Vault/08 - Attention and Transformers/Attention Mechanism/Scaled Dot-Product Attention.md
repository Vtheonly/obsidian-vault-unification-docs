---
title: Scaled Dot-Product Attention
type: derivation
aliases:
  - "Scaled Dot-Product Attention — Why the Square Root"
  - "Why the Square Root"
  - "sqrt(d_k) scaling"
  - Scaled dot product
tags:
  - attention
  - transformers
  - softmax
  - variance
  - numerical-conditioning
  - gradient-flow
sources:
  - "03. Scaled Dot-Product Attention — Why the Square Root"
created_index: 9
---

Scaled dot-product attention is the scoring rule at the heart of the Transformer: queries and keys are compared with dot products, and the scores are divided by $\sqrt{d_k}$ before the softmax. That division looks like a minor bookkeeping detail, yet it is what keeps attention trainable. This note derives the scaling from first principles — a central-limit argument about how dot-product magnitudes grow with dimension — and shows numerically what goes wrong without it.

## The formula

$$\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{Q K^\top}{\sqrt{d_k}}\right) V$$

The definitions of $Q$, $K$, $V$, and the softmax are covered in [[Queries Keys and Values]]; the only unexplained piece of the formula is the division by $\sqrt{d_k}$. It looks like a minor detail, but removing it causes training to fail, and the reason is a clean piece of probability theory that every deep learning practitioner should know.

## The problem: dot products grow with dimension

Suppose $q$ and $k$ are $d_k$-dimensional vectors whose entries are independent, mean-zero, unit-variance random variables. Then their dot product $q^\top k = \sum_{i=1}^{d_k} q_i k_i$ is a sum of $d_k$ independent, mean-zero terms, each with variance 1. By the central limit theorem, $q^\top k$ has:

- Mean 0
- Variance $d_k$
- Standard deviation $\sqrt{d_k}$

So the **typical magnitude** of a dot product grows like $\sqrt{d_k}$. For $d_k = 64$ (a typical Transformer dimension), dot products are around $\pm 8$. For $d_k = 512$, they are around $\pm 23$.

This is not a problem in itself — the issue is what happens when these large-magnitude scores enter the softmax.

## The softmax saturation problem

The softmax function $\text{softmax}(z)_i = e^{z_i} / \sum_j e^{z_j}$ has a critical property: **when the inputs $z_i$ have large magnitude, the output approaches a one-hot vector.** If one $z_i$ is much larger than the others, $e^{z_i}$ dominates the sum and the softmax puts almost all probability mass on position $i$.

Concretely, if $z = [10, 1, 1, 1]$ (one large entry), the softmax is approximately $[0.999, 0.0003, 0.0003, 0.0003]$ — essentially one-hot. The gradient of the softmax is also near zero in this regime, because the output is already saturated and small changes to $z$ barely affect it.

In attention, this means: **if the dot products $q^\top k_i$ have large magnitude, the attention weights become nearly one-hot, and the gradient through the softmax vanishes.** The model cannot learn because the attention pattern is "stuck" attending to one position, and the gradient telling it to adjust is zero.

## The fix: divide by $\sqrt{d_k}$

If the dot product has standard deviation $\sqrt{d_k}$, dividing by $\sqrt{d_k}$ gives a quantity with standard deviation 1, regardless of $d_k$. This keeps the softmax inputs in a moderate range where:

- The softmax output is not saturated (so gradients flow).
- The attention distribution can be peaked (when the query strongly matches one key) or flat (when the query weakly matches all keys), as the data demands.

The scaling factor is **not learned** — it is a fixed constant determined by $d_k$. It is a piece of statistical bookkeeping that keeps the math well-conditioned.

## A numerical illustration

Suppose $d_k = 512$ and the "true" attention should be roughly uniform over 10 keys (each gets ~0.1). Without scaling, the dot products might be:

$$q^\top k = [22, -15, 8, 3, -5, 19, -2, 11, -8, 14]$$

The softmax of this is approximately $[0.99, 0.00, 0.01, 0.00, 0.00, 0.05, 0.00, 0.01, 0.00, 0.01]$ — almost all mass on the first key, not uniform at all. The gradient is near zero.

With scaling by $\sqrt{512} \approx 22.6$:

$$q^\top k / \sqrt{d_k} = [0.97, -0.66, 0.35, 0.13, -0.22, 0.84, -0.09, 0.49, -0.35, 0.62]$$

The softmax is approximately $[0.18, 0.04, 0.10, 0.08, 0.06, 0.17, 0.07, 0.12, 0.05, 0.13]$ — much closer to uniform, with meaningful gradients.

## Why not just use smaller $d_k$

You could — and in practice $d_k$ is much smaller than the model dimension $d$ (typically $d_k = d / h$ where $h$ is the number of heads; see [[Multi-Head Attention]]). But even at $d_k = 64$, the unscaled dot product has standard deviation 8, which is large enough to saturate the softmax. The scaling is necessary for any reasonable $d_k$.

## The deeper lesson: numerical conditioning matters

The $\sqrt{d_k}$ scaling is a specific instance of a general deep-learning principle: **every time you have a sum of many terms entering a nonlinear function, check the variance.** This is the same principle behind Xavier/He initialization, which keeps activation variance stable across layers ([[05 - Neural Network Foundations/Training Dynamics and Stability/Weight Initialization|Weight Initialization]]); BatchNorm/LayerNorm, which normalizes activations before nonlinearities ([[05 - Neural Network Foundations/Training Dynamics and Stability/Batch Normalization|Batch Normalization]], [[Normalization Layers]]); and residual connections, whose additive paths keep gradient magnitude stable ([[06 - Computer Vision/Architecture and Connectivity/The Degradation Problem and Residual Connections|The Degradation Problem and Residual Connections]], [[Residual Connections]]).

In all cases, the goal is to keep the network's internal magnitudes in a range where nonlinearities are neither saturated (gradient vanishes) nor in their linear region (nonlinearity is wasted). The $\sqrt{d_k}$ scaling is the attention-specific instance of this principle.

## What to walk away with

Five points summarize the derivation. Dot products of $d_k$-dimensional vectors have standard deviation $\sqrt{d_k}$ — they grow with dimension. Large-magnitude dot products saturate the softmax, making attention one-hot and gradients zero. Dividing by $\sqrt{d_k}$ keeps the softmax inputs at unit variance, preserving gradient flow. The scaling is fixed (not learned) — it is statistical bookkeeping, not a hyperparameter. And the whole argument is an instance of the general principle: check variance whenever a sum enters a nonlinearity.

## See also

- [[Attention and Transformers MOC]]
- [[Queries Keys and Values]] — the Q/K/V projections and the matrix form being scaled
- [[Multi-Head Attention]] — parallel relationship patterns, and why $d_k = d/h$
- [[Self-Attention]] — where every token queries every other token
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Weight Initialization|Weight Initialization]] — Xavier/He variance control
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Batch Normalization|Batch Normalization]] — normalization before nonlinearities
- [[06 - Computer Vision/Architecture and Connectivity/The Degradation Problem and Residual Connections|The Degradation Problem and Residual Connections]] — additive paths and gradient stability
- [[Normalization Layers]] — LayerNorm in Transformers
- [[Residual Connections]] — residual paths in the Transformer block
