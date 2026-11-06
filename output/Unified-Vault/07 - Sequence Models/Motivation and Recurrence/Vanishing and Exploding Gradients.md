---
title: Vanishing and Exploding Gradients
type: concept
aliases:
  - "The Vanishing and Exploding Gradient Problem in RNNs"
  - Vanishing Gradients in RNNs
  - Exploding Gradients in RNNs
  - RNN Gradient Pathology
tags:
  - recurrent-neural-networks
  - sequence-models
  - gradient-flow
  - vanishing-gradients
  - exploding-gradients
  - gradient-clipping
  - weight-initialization
  - lstm
sources:
  - "04. The Vanishing and Exploding Gradient Problem in RNNs"
created_index: 7
---

When a recurrent network is trained, the gradient that reaches an early time step is multiplied by a long product of per-step Jacobians, and that product either decays to zero or blows up as the sequence grows. This note makes the two failure modes rigorous in terms of the spectral radius of the recurrent matrix, explains why the $\tanh$ nonlinearity is the culprit, surveys the two cheap engineering fixes (gradient clipping and near-orthogonal initialization) and their limits, and shows why the real cure is architectural: the LSTM's linear cell-state path. It is the recurrent counterpart of the same pathology in feedforward networks.

## The problem, stated precisely

[[Backpropagation Through Time]] derives the gradient of the loss at time $T$ with respect to the first hidden state $h_1$:

$$\frac{\partial \mathcal{L}_T}{\partial h_1} = \prod_{t=2}^{T} \underbrace{W_h^\top \, \mathrm{diag}(1 - h_t^2)}_{\text{per-step Jacobian}} \cdot \frac{\partial \ell_T}{\partial h_T}$$

This is a product of $T-1$ matrices. The behavior of that product as $T$ grows is the entire story of why vanilla RNNs fail.

## The two failure modes, made rigorous

Let $\sigma_{\max}(W_h)$ be the largest singular value of $W_h$ — informally, the "largest stretch factor" that $W_h$ applies to any vector. The per-step Jacobian $J_t = W_h^\top \mathrm{diag}(1 - h_t^2)$ has singular values bounded by $\sigma_{\max}(W_h) \cdot \max_t(1 - h_t^2)$.

Because $h_t = \tanh(\cdot) \in (-1, 1)$, the factor $(1 - h_t^2)$ lies in $[0, 1]$. So the spectral radius of $J_t$ is at most $\sigma_{\max}(W_h)$, and in practice it is smaller — often much smaller, because $\tanh$ saturates and $(1-h_t^2) \to 0$ for large $|h_t|$.

### Case 1 — vanishing gradients

If the effective spectral radius is less than 1, then multiplying $T-1$ such matrices produces something whose norm behaves like $\rho^{T-1}$, where $\rho < 1$. For $T = 100$ and $\rho = 0.9$, that is $0.9^{99} \approx 2.7 \times 10^{-5}$. For $T = 1000$ it is effectively zero.

The consequence is that the gradient signal from step $T$ cannot reach step 1. The network's early time steps receive almost no learning signal and never adjust their behavior. The RNN becomes a model that can remember the last ~10 tokens and nothing before that — functionally identical to a fixed-window MLP, which is exactly what [[Why Sequence Models]] was trying to escape.

### Case 2 — exploding gradients

If the effective spectral radius is greater than 1, the product grows like $\rho^{T-1}$ with $\rho > 1$. For $T = 100$ and $\rho = 1.1$, that is $1.1^{99} \approx 12500$. The gradient blows up to numerical infinity, weights get NaN, training crashes.

The consequence is loud: the loss curve suddenly spikes to `NaN`, weights become `NaN`, and the run is dead. This is the easier of the two to detect — and the easier to fix (gradient clipping; see below).

## Why vanishing is the dangerous one

Exploding gradients are loud: the loss explodes, the run dies, you know immediately. Vanishing gradients are silent: the loss decreases slowly, the model trains, but it only ever learns short-range dependencies. You can train a vanilla RNN for a week on a language modeling task and discover that it has learned to predict the next word from the previous 5 words — no better than an [[N-Gram Language Models|n-gram model]].

This is why vanishing is the pathology that motivated LSTMs. Exploding has a cheap engineering fix (clip the gradient); vanishing requires an architectural fix (change the recurrence so the gradient does not have to pass through a $\tanh$ at every step).

## Why the $\tanh$ is the villain

Look again at the per-step Jacobian: $W_h^\top \mathrm{diag}(1 - h_t^2)$. The factor $(1 - h_t^2)$ is the derivative of $\tanh$, and it is the multiplier that pushes the spectral radius below 1. If we could remove the $\tanh$ — if the hidden state could update linearly — the gradient would flow through undiminished.

But removing the $\tanh$ entirely destroys the nonlinearity, which makes the whole network a linear autoregressive model. The trick that LSTMs use is more subtle: keep a separate path through the cell — the cell state $C_t$ — that updates linearly, while a different path — the hidden state $h_t$ — goes through the nonlinearity. The linear path lets gradients flow; the nonlinear path does the actual computation. This is the deep insight behind [[LSTM]].

## The two cheap engineering fixes (and their limits)

### Fix 1 — gradient clipping (handles exploding, not vanishing)

Clipping rescales the gradient when its norm exceeds a threshold:

$$\text{if } \|\nabla\| > \tau, \quad \nabla \leftarrow \tau \cdot \frac{\nabla}{\|\nabla\|}$$

This is the standard defense against exploding gradients in RNNs and Transformers. It does nothing for vanishing — the gradient is still tiny, you just clip the giant ones.

> [!NOTE] Clip by norm, not by value.
> Clipping each component to $[-\tau, \tau]$ ("clip by value") distorts the gradient direction. Clipping the whole vector's norm to $\tau$ ("clip by norm") preserves direction and only rescales magnitude. Always use norm clipping.

### Fix 2 — better initialization (delays vanishing, does not prevent it)

Initializing $W_h$ to be near-orthogonal makes $\sigma_{\max}(W_h) \approx 1$ at the start of training, which keeps the spectral radius near 1 for as long as possible. This helps — the network trains for longer before vanishing sets in — but it does not change the asymptotic behavior. Eventually, training drifts $W_h$ away from orthogonality and vanishing returns.

## Why the fixes are not enough — and what is

Clipping and initialization are band-aids. The disease is structural: the gradient must pass through a $\tanh$ at every time step, and that multiplication pushes it toward zero. No amount of clipping or initialization changes the algebraic structure of the recurrence.

The cure is to redesign the cell so that there exists a path through it along which the gradient is multiplied by exactly 1 at every time step. That is what an LSTM does. The key is the cell state $C_t$, which updates as:

$$C_t = f_t \odot C_{t-1} + i_t \odot \tilde{C}_t$$

The gradient $\partial C_t / \partial C_{t-1} = f_t$ (a vector of forget-gate values). When the forget gate is near 1, the gradient passes through unchanged — like a residual connection, but learned and time-varying. This single design choice is what lets LSTMs learn dependencies across hundreds of time steps where vanilla RNNs fail at tens. [[LSTM]] builds the cell from this insight up, gate by gate; [[GRU]] simplifies it.

## What to walk away with

The RNN gradient contains a product of $T-1$ Jacobians, each of which has a $\tanh$ derivative factor in $[0,1]$. If the spectral radius of the product is less than 1, gradients vanish — early time steps never learn; if it is greater than 1, gradients explode — training crashes. Vanishing is the dangerous case because it is silent: the model trains but only learns short-range patterns. Gradient clipping fixes exploding; better initialization delays vanishing; neither cures vanishing. The cure is architectural: redesign the cell so a gradient path exists that multiplies by ~1 at every step. That is the LSTM.

## See also

- [[07 - Sequence Models/Chapter Overview|Chapter Overview]]
- [[Backpropagation Through Time]] — the derivation of the gradient product analyzed here
- [[The Recurrent Neuron]] — the recurrence whose Jacobians are under the microscope
- [[Why Sequence Models]] — the fixed-window failure that vanishing silently recreates
- [[LSTM]] — the architectural cure; [[GRU]] and [[LSTM vs GRU]] — its simplification
- [[Long-Range Dependencies]] — what vanishing gradients stop RNNs from learning
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]] — the feedforward version of the same problem
- [[06 - Computer Vision/Architecture and Connectivity/The Degradation Problem and Residual Connections|The Degradation Problem and Residual Connections]] — the "additive path preserves gradient" idea that LSTMs anticipate by 20 years
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Weight Initialization|Weight Initialization]] — background for the near-orthogonal fix
