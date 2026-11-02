---
title: Backpropagation Through Time
type: derivation
aliases:
  - BPTT
  - Backprop Through Time
  - Truncated BPTT
  - "Backpropagation Through Time (BPTT)"
tags:
  - recurrent-neural-networks
  - sequence-models
  - backpropagation
  - chain-rule
  - gradient-flow
  - training
  - truncated-bptt
sources:
  - "03. Backpropagation Through Time (BPTT)"
created_index: 5
---

Training an RNN is ordinary backpropagation applied to the unrolled computational graph — that is the entire trick, and the name "Backpropagation Through Time" makes it sound more novel than it is. It is not a new algorithm; it is just backprop on a graph that happens to be very deep, because it has one layer per time step. This derivation makes the chain-rule bookkeeping explicit, step by step, so that the analysis of [[07 - Sequence Models/Motivation and Recurrence/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]] has a product formula to refer back to.

## The setup

Consider a vanilla RNN cell producing an output at every step:

$$h_t = \tanh(W_h h_{t-1} + W_x x_t + b)$$
$$y_t = W_y h_t + c$$
$$\hat{p}_t = \mathrm{softmax}(y_t)$$
$$\mathcal{L} = \sum_{t=1}^{T} \ell_t(\hat{p}_t, \text{target}_t)$$

The total loss is the sum of per-step losses. (Other choices — like averaging, or only computing loss at the final step — work the same way; only the bookkeeping changes.)

We want $\partial \mathcal{L} / \partial W_h$, $\partial \mathcal{L} / \partial W_x$, and $\partial \mathcal{L} / \partial W_y$. We focus on $W_h$, because the recurrent weight matrix is where the interesting behavior lives.

## Step 1 — gradients flow into each $h_t$

Each hidden state $h_t$ influences the loss through two paths:

1. **Directly**, through $y_t$ and $\ell_t$ at the same time step. Call this contribution $\partial \ell_t / \partial h_t$.
2. **Indirectly**, through $h_{t+1}$, which depends on $h_t$ through the recurrence. Call this contribution $(\partial h_{t+1} / \partial h_t) \cdot (\partial \mathcal{L}_{t+1:T} / \partial h_{t+1})$.

Combining, the total gradient at $h_t$ is:

$$\frac{\partial \mathcal{L}}{\partial h_t} = \frac{\partial \ell_t}{\partial h_t} + \frac{\partial h_{t+1}}{\partial h_t}^\top \frac{\partial \mathcal{L}}{\partial h_{t+1}}$$

The second term is the recursion: the gradient at $h_t$ depends on the gradient at $h_{t+1}$, which depends on $h_{t+2}$, and so on. This is exactly the chain rule — there is nothing new here, just a recursive definition that walks backward through the unrolled graph.

The local derivative $\partial h_{t+1} / \partial h_t$ is:

$$\frac{\partial h_{t+1}}{\partial h_t} = \mathrm{diag}(1 - h_{t+1}^2) \cdot W_h$$

because $\tanh'(z) = 1 - \tanh^2(z)$ and $h_{t+1}$ depends on $h_t$ linearly through $W_h$.

## Step 2 — the gradient at $W_h$ collects contributions from every time step

$W_h$ appears in the computation of $h_1, h_2, \ldots, h_T$ — once per time step. So the total gradient is the sum over all of them:

$$\frac{\partial \mathcal{L}}{\partial W_h} = \sum_{t=1}^{T} \frac{\partial \mathcal{L}}{\partial h_t} \cdot \frac{\partial h_t}{\partial W_h}$$

This is just the multivariate chain rule, applied carefully. The unrolled graph has $T$ copies of $W_h$ (one per time step), and the autodiff system accumulates gradients into a single buffer.

## Step 3 — unrolling the recursion reveals the product

Here is the moment that everything clicks. Expand the recursion for $\partial \mathcal{L} / \partial h_1$ — the gradient at the first hidden state, which must pass through every subsequent step:

$$\frac{\partial \mathcal{L}}{\partial h_1} = \frac{\partial \ell_1}{\partial h_1} + \left(\frac{\partial h_2}{\partial h_1}\right)^\top \left[ \frac{\partial \ell_2}{\partial h_2} + \left(\frac{\partial h_3}{\partial h_2}\right)^\top \left[ \frac{\partial \ell_3}{\partial h_3} + \cdots \right] \right]$$

Unwinding fully, the contribution from $\ell_T$ to $h_1$ is a product of $T-1$ Jacobians:

$$\frac{\partial \mathcal{L}_{T}}{\partial h_1} = \left(\frac{\partial h_T}{\partial h_{T-1}}\right)^\top \left(\frac{\partial h_{T-1}}{\partial h_{T-2}}\right)^\top \cdots \left(\frac{\partial h_2}{\partial h_1}\right)^\top \frac{\partial \ell_T}{\partial h_T}$$

Substituting the per-step Jacobian from above:

$$\frac{\partial \mathcal{L}_{T}}{\partial h_1} = \prod_{t=2}^{T} \left[ W_h^\top \, \mathrm{diag}(1 - h_t^2) \right] \cdot \frac{\partial \ell_T}{\partial h_T}$$

That product of $T-1$ matrices is the source of all RNN training pathology. It is a product of:

- $W_h^\top$ — a fixed matrix, repeated $T-1$ times.
- $\mathrm{diag}(1 - h_t^2)$ — a diagonal matrix whose entries lie in $[0, 1]$ because $h_t \in (-1, 1)$.

When you multiply $T-1$ such terms together, two failure modes are possible:

1. If the largest singular value of $W_h$ is less than 1, the product shrinks exponentially with $T$. Gradient signal from step $T$ reaches step 1 multiplied by something like $\sigma^{T-1}$, which goes to zero alarmingly fast.
2. If the largest singular value of $W_h$ is greater than 1, the product grows exponentially, blowing up to numerical infinity.

Both are catastrophic, and both are the subject of [[07 - Sequence Models/Motivation and Recurrence/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]].

## Truncated BPTT — the practical compromise

For sequences of thousands of steps (audio, very long documents), full BPTT is impractical: the unrolled graph is huge, memory grows linearly in $T$, and the vanishing-gradient pathology makes the long-range contributions numerically irrelevant anyway.

The standard fix is truncated BPTT: split the sequence into chunks of length $K$ (typically 20–100) and run BPTT only within each chunk. The hidden state is carried across chunk boundaries during the forward pass, but gradients are not propagated backward across them.

```
full sequence:  x_1 x_2 ... x_K | x_{K+1} ... x_{2K} | x_{2K+1} ...
BPTT windows:    [─── window 1 ───] [─── window 2 ───] [─── window 3 ───]
                (gradients stop at chunk boundaries)
```

This is a bias-variance tradeoff: truncation biases the gradient (it ignores long-range dependencies longer than $K$) but massively reduces variance in the estimate (the chunks are shorter, the gradients are well-conditioned, training is stable).

> [!NOTE] Truncation is not free.
> Truncated BPTT is a tacit admission that vanilla RNNs cannot learn dependencies longer than the truncation window. This is one of the empirical facts that motivated the move to LSTMs (which extend the effective range) and ultimately to Transformers (which remove the temporal bottleneck entirely).

## What to walk away with

BPTT is ordinary backprop on the unrolled RNN graph — no new algorithm, just careful chain rule. The gradient at the first hidden state contains a product of $T-1$ Jacobians, one per time step. Each Jacobian has a factor of $W_h^\top$ and a factor of $\mathrm{diag}(1 - h_t^2)$ whose entries are in $[0, 1]$. Multiplying many such factors either decays to zero (vanishing) or blows up (exploding) depending on the singular values of $W_h$. Truncated BPTT is the engineering compromise that makes RNNs trainable on long sequences at the cost of ignoring dependencies longer than the truncation window.

Why the vanishing case is the dangerous one in practice — and why it forces the architectural change from vanilla RNNs to LSTMs — is the subject of [[07 - Sequence Models/Motivation and Recurrence/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]].

## See also

- [[07 - Sequence Models/Chapter Overview|Chapter Overview]]
- [[The Recurrent Neuron]] — the cell and the unrolled graph this derivation differentiates
- [[07 - Sequence Models/Motivation and Recurrence/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]] — the pathology this product formula predicts
- [[Why Sequence Models]] — why the network carries state at all
- [[Long-Range Dependencies]] — what the truncation window and the Jacobian product cut off
- [[From RNNs to Attention]] — removing the temporal bottleneck entirely
- [[Backpropagation]] — the underlying chain-rule machinery
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]] — the feedforward version of the same problem
