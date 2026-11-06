---
title: Activation Functions
type: concept
aliases:
  - Activation Function
  - activations
  - nonlinearity functions
  - ReLU family
  - GELU
  - SwiGLU
tags:
  - neural-networks
  - deep-learning
  - activation-functions
  - relu
  - gelu
  - swiglu
  - sigmoid
  - tanh
  - softmax
  - leaky-relu
  - vanishing-gradient
sources:
  - "06. Activation Functions in Deep Learning"
  - "02 - Activation Functions"
created_index: 9
---

Activation functions are the heart of neural networks: they introduce the non-linearity that allows networks to learn complex patterns — without them, no amount of layer stacking could produce anything beyond a simple linear model. This note is a comprehensive reference to the activations that matter in practice: the classical sigmoid, tanh, and softmax; the ReLU family and its fixes for dying neurons; the smooth modern variants Swish and GELU; and the gated variants SwiGLU and GEGLU that dominate modern Transformers. It anchors the [[Neural Network Foundations MOC]] alongside [[Forward Propagation]] and [[Perceptrons and Multi-Layer Perceptrons]], and also covers the mathematical properties (differentiability, boundedness, sparsity), the vanishing-gradient story that explains why ReLU was revolutionary, and practical guidance for choosing, mixing, and deploying activations — including how they interact with initialization, normalization, and quantization.

## Why nonlinearity matters

A linear composition of linear functions is still linear:

$$
\mathbf{W}_2 (\mathbf{W}_1 \mathbf{x}) = (\mathbf{W}_2 \mathbf{W}_1) \mathbf{x} = \mathbf{W} \mathbf{x}
$$

So no matter how deep a stack of linear layers is, it is equivalent to a single linear layer. Nonlinear activations break this collapse and give neural networks their expressive power — this is the single reason every layer in a network is followed by an activation (the architectural context is developed in [[Perceptrons and Multi-Layer Perceptrons]], and the mechanics of where activations sit in the computation in [[Forward Propagation]]).

## Quick reference

The table below condenses the activation functions most used in practice, their formulas, output ranges, and the situations in which each is the right choice. Each function is then treated in full detail in the sections that follow.

| Function       | Formula                           | Range | Characteristics & Usage                                                                                                     |
| :------------- | :-------------------------------- | :---- | :-------------------------------------------------------------------------------------------------------------------------- |
| **Sigmoid**    | $1 / (1 + e^{-x})$                | (0,1) | Squashes to [0,1]. Used **only** in the Output layer for binary classification. Causes Vanishing Gradient in hidden layers. |
| **Tanh**       | $(e^x - e^{-x}) / (e^x + e^{-x})$ | (-1,1)| Squashes to [-1, 1]. Better than sigmoid for hidden layers as it centers data around zero, aiding convergence.              |
| **Softmax**    | $e^{z_i} / \sum e^{z_j}$          | (0,1) | Used **only** in the Output layer for multi-class classification. Turns outputs into probabilities that sum to 1.           |
| **ReLU**       | $\max(0, x)$                      | [0,∞) | **The Industry Standard for Hidden Layers.** Extremely fast to compute. Solves the vanishing gradient problem.              |
| **Leaky ReLU** | $\max(0.01x, x)$                  | (-∞,∞)| Fixes the "Dying ReLU" problem (where neurons get stuck at 0) by allowing a slight negative slope.                          |
| **GELU**       | $x \cdot \Phi(x)$                 | (-∞,∞)| Used heavily in Transformers (BERT, GPT). A smoother, probabilistic version of ReLU.                                        |

## Classical activations

### Sigmoid (logistic function)

$$ \sigma(x) = \frac{1}{1 + e^{-x}} $$

Equivalently written with its range made explicit:

$$
\sigma(x) = \frac{1}{1 + e^{-x}} \in (0, 1)
$$

The sigmoid's output is always between 0 and 1, making it a natural probability. It is smooth and differentiable everywhere, and its output can be directly interpreted as a probability — which is why its remaining role is as the output layer for **binary classification**. Historically it was the popular default, but it is now rarely used in hidden layers.

The sigmoid has two serious problems. The first is the **vanishing gradient**: the derivative of sigmoid is $\sigma'(x) = \sigma(x)(1-\sigma(x))$, which has a maximum value of only $0.25$ (at $x=0$). This means every time we multiply backward through a layer during backpropagation, we multiply by a number smaller than $0.25$ — by the time the gradient reaches the first layer of a deep network, it is effectively zero, and the first layer never learns. The function also **saturates**: gradients vanish for large $|x|$. The second problem is that it is **not zero-centered**: the outputs are always positive (between 0 and 1), which causes the gradients for weights to always be the same sign during backpropagation, leading to inefficient zigzagging during optimization. Together with its proneness to producing "dead" neurons, these issues explain why hidden-layer use has disappeared.

### Tanh (hyperbolic tangent)

$$ \tanh(x) = \frac{e^x - e^{-x}}{e^x + e^{-x}} $$

or, with the range explicit:

$$
\tanh(x) = \frac{e^x - e^{-x}}{e^x + e^{-x}} \in (-1, 1)
$$

The tanh squashes to $[-1, 1]$ and its output is centered around zero: negative inputs produce negative outputs, and positive inputs produce positive outputs. This zero-centering is its advantage over sigmoid — the gradients for weights can be both positive and negative, which facilitates faster convergence and more efficient optimization paths — which is why tanh was historically preferred for hidden layers and became the tradition in RNN gates (LSTM, GRU).

The problem is that tanh still suffers from vanishing gradients: the derivative maximum is 1.0 at $x=0$, but it drops rapidly for large $|x|$. This is not as severe as sigmoid, but it is still problematic for very deep networks, and tanh has largely been replaced by the ReLU family in modern architectures.

### Softmax

$$ Softmax(z_i) = \frac{e^{z_i}}{\sum_{j} e^{z_j}} $$

Softmax produces a value in $(0, 1)$ for each output, and all outputs sum to exactly 1. It is used **only** in the output layer for multi-class classification, transforming raw scores into a valid probability distribution. Its key property is that it **amplifies differences** — the largest input gets a disproportionately large share of the output probability. If one $z_i$ is significantly larger than the others, its softmax output will be close to 1 while the others are close to 0. Softmax is always paired with **Categorical Cross-Entropy** loss. Putting softmax in hidden layers is a mistake — it saturates and kills gradients (see the pitfalls section below).

## The ReLU family

### ReLU (rectified linear unit)

$$ f(x) = \max(0, x) $$

that is,

$$
\text{ReLU}(x) = \max(0, x)
$$

The output range is $[0, \infty)$ — zero for negative inputs, identity for positive inputs. ReLU is **the standard for hidden layers**, and its advantages are decisive:

- **No vanishing gradient.** The gradient is exactly 1 for all positive inputs, so the gradient passes through unchanged during backpropagation, even in very deep networks. This single property revolutionized deep learning.
- **Computational simplicity.** ReLU requires only a comparison and a max operation — no exponentials or divisions. This makes it orders of magnitude faster to compute than Sigmoid or Tanh; it is cheap precisely because there is no `exp`.
- **Sparsity.** For any input $\le 0$, the output is exactly 0. This creates sparse activations (many neurons outputting zero), which is computationally efficient and acts as a natural regularizer. ReLU is non-saturating for positive inputs, which is what removes the vanishing-gradient failure mode.

Historically, ReLU was introduced to deep learning by Nair & Hinton (2010) and popularized by AlexNet (2012).

The one problem is the **"Dying ReLU"**: neurons can output 0 permanently and "die" because the gradient is 0 for all negative inputs. If a neuron's weights are updated such that it always receives negative inputs, it will output 0 forever, its gradient will be 0, and it will never recover. With a high learning rate, up to 40% of neurons can "die" during training. The variants below exist to address this.

### Leaky ReLU and PReLU

$$ f(x) = \max(\alpha x, x) $$ where $\alpha$ is a small constant (e.g., 0.01).

In piecewise form:

$$
\text{LeakyReLU}(x) = \begin{cases} x & x \geq 0 \\ \alpha x & x < 0 \end{cases}
$$

The range is $(-\infty, \infty)$ — a slight negative slope for negative inputs. Leaky ReLU fixes the "Dying ReLU" problem by allowing this slight negative slope, so neurons never have a gradient of exactly zero: even when the input is negative, there is still a small but non-zero gradient flowing through, allowing the neuron to recover. The constant $\alpha$ is typically set to 0.01, which means negative inputs produce outputs that are 1% of the input value — small enough not to dominate, but large enough to keep the gradient alive. The trade-off is that Leaky ReLU avoids dead units but adds a hyperparameter.

**PReLU (Parametric ReLU)** uses the same formula,

$$ f(x) = \max(\alpha x, x) $$ where $\alpha$ is a **learned parameter**.

The difference is that $\alpha$ is not a fixed constant; it is a parameter learned by the network during training through backpropagation. The advantage is that the network learns the optimal negative slope for each neuron, rather than requiring the practitioner to guess a good value, which makes PReLU more flexible and often more effective than Leaky ReLU. The disadvantage is that it adds a small number of additional parameters to the model.

### ELU (exponential linear unit)

$$ f(x) = \begin{cases} x & \text{if } x > 0 \\ \alpha(e^x - 1) & \text{if } x \le 0 \end{cases} $$

The range is $(-\alpha, \infty)$ — a smooth transition to negative values. ELU tends to converge faster and produces activations closer to zero. Its advantage over ReLU is that the negative portion is smooth (not a sharp corner like ReLU/Leaky ReLU), which can help gradient-based optimization; it also pushes the mean activation closer to zero, which speeds up learning. The disadvantage is that it requires computing an exponential for negative inputs, which is slower than ReLU.

## Smooth modern activations

### Swish (SiLU)

$$ f(x) = x \cdot \sigma(x) $$

The range is approximately $(-0.28, \infty)$ — slightly negative for some inputs. Swish was discovered by Google through automated search and often outperforms ReLU in extremely deep networks (40+ layers). Unlike ReLU, which is a hard threshold, Swish is a smooth, **non-monotonic** function: it dips slightly below zero for inputs around -1.25 before rising again, and this smoothness appears to help optimization in very deep networks. It is also **self-gating**: the sigmoid $\sigma(x)$ acts as a gate that controls how much of $x$ passes through — the network learns to automatically modulate the flow of information.

### GELU (Gaussian error linear unit)

$$ f(x) = x \cdot \Phi(x) $$

where $\Phi(x)$ is the cumulative distribution function of the standard normal distribution. In the other common notation:

$$
\text{GELU}(x) = x \cdot \Phi(x)
$$

The range is approximately $(-0.17, \infty)$. GELU is massively used in **Transformer architectures** (BERT, GPT, Gemini) due to its probabilistic nature — it is a smoother, probabilistic version of ReLU, and is the standard in BERT, GPT-2/3, and most Transformer variants. It is smooth (infinitely differentiable), which gives smoother gradients than ReLU — part of why GELU trains slightly better in some settings — and it is stochastically motivated: it multiplies the input by a probability derived from its own value.

The intuition is: "How likely is $x$ to be greater than a random value drawn from a standard normal distribution?" If $x$ is very large, $\Phi(x) \approx 1$ and the output is approximately $x$. If $x$ is very negative, $\Phi(x) \approx 0$ and the output is approximately 0. In between, the transition is smooth and probabilistic. In practice, GELU is often approximated as $0.5x(1 + \tanh[\sqrt{2/\pi}(x + 0.044715x^3)])$ for computational efficiency; the same approximation in display form:

$$
\text{GELU}(x) \approx 0.5 x \left[ 1 + \tanh\left(\sqrt{2/\pi} (x + 0.044715 x^3)\right) \right]
$$

### The GELU probabilistic interpretation

GELU is $x \cdot \Phi(x)$ where $\Phi$ is the standard normal CDF, and this has a clean probabilistic interpretation: GELU multiplies the input by the probability that a Gaussian random variable is less than the input. Equivalently, GELU is the expected value of $x \cdot \mathbb{1}[X \leq x]$ where $X \sim \mathcal{N}(0, 1)$.

This is a smoother version of ReLU's "pass through if positive, zero if negative" — GELU passes through with probability $\Phi(x)$, which is smooth around $x = 0$. For large positive $x$, $\Phi(x) \to 1$ (full pass-through). For large negative $x$, $\Phi(x) \to 0$ (full suppression). Near $x = 0$, there is a smooth transition. The probabilistic motivation comes from **dropout** thinking: ReLU deterministically masks, while GELU stochastic-masks with a probability depending on the input value. This connects to the Bayesian interpretation of dropout as approximate variational inference (see [[05 - Neural Network Foundations/Training Dynamics and Stability/Dropout and Regularization|Dropout and Regularization]]).

## Gated linear units and their variants

**GLU** (Dauphin et al., 2017) introduces a multiplicative gate:

$$
\text{GLU}(\mathbf{x}) = (\mathbf{W}\mathbf{x} + \mathbf{b}) \otimes \sigma(\mathbf{V}\mathbf{x} + \mathbf{c})
$$

where $\sigma$ is a sigmoid and $\otimes$ is element-wise. The first linear transformation is "gated" by the second — instead of applying a fixed nonlinearity to one projection, the network learns a second projection that decides, element by element, how much of the first one survives.

### SwiGLU

**SwiGLU** (Shazeer, 2020) replaces the sigmoid with Swish (= SiLU = $x \cdot \sigma(x)$):

$$
\text{SwiGLU}(\mathbf{x}) = \text{Swish}(\mathbf{W}\mathbf{x}) \otimes (\mathbf{V}\mathbf{x})
$$

SwiGLU is used in **Llama, Mistral, PaLM, Gemma, Qwen, and most modern LLMs**, and it empirically outperforms GELU in large-scale Transformer training. The cost is that it requires an extra linear layer (3 weight matrices instead of 2). To keep the parameter count comparable, the hidden dimension is reduced by a factor of 2/3 — a detail that trips up many implementations (see the failure-modes table below).

### GEGLU

The same idea but with GELU as the gate:

$$
\text{GEGLU}(\mathbf{x}) = \text{GELU}(\mathbf{W}\mathbf{x}) \otimes (\mathbf{V}\mathbf{x})
$$

GEGLU is used in some models and has performance comparable to SwiGLU.

## Mathematical properties

### Continuity and differentiability

Backpropagation requires the activation to be differentiable (or sub-differentiable) almost everywhere. The properties that matter:

- **ReLU**: continuous everywhere, differentiable except at $x = 0$ (where the derivative is undefined). The sub-gradient at $x = 0$ is conventionally taken as 0. This works in practice — the probability of hitting exactly $x = 0$ is measure zero for continuous inputs.
- **GELU**: smooth (infinitely differentiable), which gives smoother gradients than ReLU. This is part of why GELU trains slightly better in some settings.
- **Swish/SiLU**: smooth, with a small negative region for $x < 0$ (unlike ReLU which is exactly 0). This allows the network to learn "mostly linear with occasional negative" patterns.
- **Sigmoid/tanh**: smooth but saturating — gradients vanish for large $|x|$.

### Boundedness

- **Sigmoid**: bounded in $(0, 1)$. Outputs are interpretable as probabilities.
- **Tanh**: bounded in $(-1, 1)$. Zero-centered, which helps optimization.
- **ReLU/GELU/SwiGLU**: unbounded above. Allows the network to produce large activations when needed.
- **Softmax**: bounded (each output in $(0, 1)$, sums to 1). Used for output, not hidden layers.

Bounded activations prevent activation explosion but can cause vanishing gradients. Modern LLMs use unbounded activations (ReLU, GELU, SwiGLU) and rely on normalization (LayerNorm/RMSNorm) to keep activations in check — see [[05 - Neural Network Foundations/Training Dynamics and Stability/Batch Normalization|Batch Normalization]] for the normalization machinery.

### Sparsity

- **ReLU**: produces exact zeros for $x < 0$, creating sparse activations. This is computationally beneficial (sparse matrix ops) and may have regularization effects.
- **GELU**: produces near-zero but not exact zero for $x < 0$. Less sparse than ReLU.
- **SwiGLU**: the gating mechanism produces sparse-like behavior (gate near 0 suppresses the output) but without exact zeros.

## The vanishing gradient problem in depth

If we use the Sigmoid activation function, every time we multiply backward through a layer during backpropagation, we multiply by a number smaller than $0.25$. After just 10 layers, the gradient is multiplied by $0.25^{10} \approx 0.00000095$ — effectively zero. The first layer of the network receives almost no gradient signal and cannot learn.

This is why **ReLU** was such a revolutionary invention: its gradient is either 0 or 1 for positive inputs. For the positive pathway (which is the active portion of the network), the gradient passes through completely unchanged, even through hundreds of layers. This single change enabled the training of deep networks with dozens or even hundreds of layers, unlocking the era of modern deep learning. The full treatment of gradient pathologies is in [[05 - Neural Network Foundations/Training Dynamics and Stability/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]].

## Choosing an activation

For a quick decision:

> [!TIP] Quick decision guide
>
> - **Hidden Layers:** Always start with **ReLU**. If you have dead neurons (many neurons outputting 0 consistently), switch to Leaky ReLU. If you are building Transformers, use GELU.
> - **Output Layer (Binary Classification):** Sigmoid — outputs a single probability.
> - **Output Layer (Multi-class Classification):** Softmax — outputs a probability distribution over all classes.
> - **Output Layer (Regression):** Linear (no activation) — output can be any real number.

Layer by layer, the defaults look like this:

| Layer type            | Default choice                | Notes                                            |
|-----------------------|-------------------------------|--------------------------------------------------|
| Hidden layer (CNN/MLP)| ReLU or GELU                  | ReLU if you need speed; GELU for smoother grads. |
| Transformer FFN       | SwiGLU or GELU                | SwiGLU is the modern default for LLMs.           |
| Output (classification)| Softmax (multiclass) / Sigmoid (multilabel) | Always paired with cross-entropy.     |
| Output (regression)   | Linear (no activation)        |                                                  |
| RNN/LSTM gates        | Sigmoid / tanh                | Tradition; gating requires (0, 1) range.         |

Note the multilabel case: sigmoid handles it (one probability per class), while softmax is for multiclass (one probability distribution over mutually exclusive classes). RNN/LSTM gating keeps sigmoid and tanh not out of habit alone — gating requires the $(0, 1)$ range that sigmoid provides.

## Worked examples

First, a concrete numeric pass over the three most common activations, plus SwiGLU implemented as a feed-forward layer:

```python
import torch
import torch.nn.functional as F

x = torch.tensor([-2.0, -1.0, 0.0, 1.0, 2.0])

F.relu(x)       # tensor([0., 0., 0., 1., 2.])
F.gelu(x)       # tensor([-0.0454, -0.1588, 0.0000, 0.8412, 1.9546])
F.silu(x)       # tensor([-0.2384, -0.2689, 0.0000, 0.7311, 1.7616]) — Swish

# SwiGLU as a feed-forward layer
class SwiGLUFFN(nn.Module):
    def __init__(self, dim, hidden_dim):
        super().__init__()
        self.w_gate = nn.Linear(dim, hidden_dim)
        self.w_up   = nn.Linear(dim, hidden_dim)
        self.w_down = nn.Linear(hidden_dim, dim)
    def forward(self, x):
        return self.w_down(F.silu(self.w_gate(x)) * self.w_up(x))
```

Reading the numbers: ReLU is exactly zero on the negative side; GELU dips slightly negative (down to about $-0.17$) before rising; Swish/SiLU dips a bit deeper (about $-0.28$). The SwiGLU class shows the three-matrix structure explicitly — gate, up, and down projections — with the gate passed through SiLU before the element-wise multiply.

The second example plots the activation functions themselves, their numerical derivatives, and their sparsity on Gaussian input, which is the fastest way to see the differences discussed above:

```python
import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
import numpy as np

x = torch.linspace(-5, 5, 200)

# Activation values
plt.figure(figsize=(12, 4))
plt.subplot(1, 3, 1)
plt.plot(x, F.relu(x), label='ReLU')
plt.plot(x, F.gelu(x), label='GELU')
plt.plot(x, F.silu(x), label='Swish/SiLU')
plt.plot(x, torch.tanh(x), label='tanh')
plt.plot(x, torch.sigmoid(x), label='sigmoid')
plt.axhline(0, color='gray', linestyle='--', alpha=0.5)
plt.axvline(0, color='gray', linestyle='--', alpha=0.5)
plt.legend(); plt.title('Activation functions')

# Derivatives
plt.subplot(1, 3, 2)
plt.plot(x[1:], torch.diff(F.relu(x)) / (x[1] - x[0]).item(), label='ReLU')
plt.plot(x[1:], torch.diff(F.gelu(x)) / (x[1] - x[0]).item(), label='GELU')
plt.plot(x[1:], torch.diff(F.silu(x)) / (x[1] - x[0]).item(), label='Swish')
plt.axhline(0, color='gray', linestyle='--', alpha=0.5)
plt.legend(); plt.title('Derivatives')

# Sparsity: fraction of near-zero outputs for Gaussian inputs
gaussian_input = torch.randn(10000)
plt.subplot(1, 3, 3)
activations = {
    'ReLU': F.relu(gaussian_input),
    'GELU': F.gelu(gaussian_input),
    'Swish': F.silu(gaussian_input),
}
sparsity = {name: (act.abs() < 0.01).float().mean().item() for name, act in activations.items()}
plt.bar(sparsity.keys(), sparsity.values())
plt.ylabel('Fraction near zero')
plt.title('Sparsity (Gaussian input)')
```

## Activations in production LLMs

The choice of activation function in the FFN is a **visible architectural choice** that distinguishes model generations — GPT-2 used GELU; Llama uses SwiGLU. Activations also interact with initialization, normalization, and learning rate: a bad combination leads to training instability. And quantization can change the effective activation — INT8 quantization of GELU requires careful implementation, and SwiGLU's element-wise multiply can amplify quantization noise.

| Model            | FFN Activation | Notes                                          |
|------------------|----------------|------------------------------------------------|
| GPT-2/3          | GELU           | Original Transformer default                   |
| BERT             | GELU           | Same                                           |
| Llama 1/2/3      | SwiGLU         | $\text{Swish}(xW_1) \otimes (xW_2)$, 3 matrices |
| Mistral 7B       | SwiGLU         | Same as Llama                                  |
| Qwen 2/2.5       | SwiGLU         | Same                                           |
| Gemma            | GELU           | Uses approximate GELU for speed                |
| DeepSeek-V3      | SwiGLU         | Same                                           |
| T5               | GELU           | Original                                       |
| Claude (inferred)| GELU or SwiGLU | Not publicly disclosed                         |

The shift from GELU (GPT-2/3 era) to SwiGLU (Llama era) reflects the empirical finding that gated activations train better at scale. The cost (extra weight matrix) is offset by reducing the hidden dimension by 2/3. For historical perspective, the original Transformer (Vaswani 2017, "Attention Is All You Need") used ReLU in its FFN — the lineage ReLU → GELU → SwiGLU tracks three generations of architecture design, each step justified empirically at the scales where it was tested. Beyond training and serving, activation patterns are themselves an object of study: mechanistic interpretability works by examining what individual activations and circuits respond to, so the choice of activation shapes what can be read out of a trained model.

## Common pitfalls and failure modes

The recurring mistakes are few but expensive. **Using sigmoid in hidden layers** causes vanishing gradients in deep networks. **Forgetting that softmax is for outputs** — softmax in hidden layers saturates and kills gradients. **Mixing activations carelessly** is dangerous because different activations have different scales; mixing can destabilize training. And **not scaling the hidden dimension for GLU variants** breaks parameter budgets — SwiGLU has 3 weight matrices, so the standard 4x expansion becomes 8/3 x to keep the parameter count comparable.

When something goes wrong in training, the symptom usually points back to one of these causes:

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Dead ReLUs (neurons always output 0) | Bad init; or LR too high | Lower LR; use He init; switch to LeakyReLU or GELU |
| Activations explode (NaN) | No normalization; unbounded activation | Add LayerNorm; use bounded activation; gradient clipping |
| Activations vanish (all near 0) | Sigmoid/tanh saturation; deep net | Use ReLU/GELU; add residual connections; proper init |
| SwiGLU dimension mismatch | Forgot to scale hidden dim by 2/3 | Use `hidden_dim = (2/3) * 4 * d_model` |
| INT8 quantization breaks SwiGLU | Element-wise multiply amplifies noise | Use per-channel quantization; or keep activation in fp16 |
| Model is too sparse (low activation density) | Too much ReLU; or high sparsity init | Switch to GELU/SwiGLU; check init scale |

## Production implications

SwiGLU and GELU require **fused kernels** for performance. PyTorch's eager mode is slow; use `torch.compile` or library-provided fused ops. For **inference at low precision** (INT8/INT4), activation functions need lookup tables or polynomial approximations. Most serving frameworks (vLLM, TensorRT-LLM) handle this; custom implementations may not. Finally, **activation checkpointing** trades compute for memory by recomputing activations during the backward pass — a memory technique that is independent of which activation function you choose.

## Interview-grade distinctions

- **Q: Why does SwiGLU outperform GELU in modern LLMs?**
  A: Three reasons. (1) **Gating mechanism** — the element-wise multiply with a sigmoid/Swish gate lets the model selectively suppress information, which is more expressive than a simple nonlinearity. (2) **Empirical at scale** — Shazeer (2020) showed SwiGLU beats GELU on large-scale Transformer training, and the advantage grows with model size. (3) **Compatibility with normalization** — SwiGLU works well with RMSNorm (used in Llama), while GELU was paired with LayerNorm. The cost: SwiGLU uses 3 weight matrices instead of 2, so the hidden dim is reduced by 2/3 to keep the parameter count comparable.

- **Q: What is the GELU probabilistic interpretation?**
  A: GELU is $x \cdot \Phi(x)$ where $\Phi$ is the standard normal CDF. This multiplies the input by the probability that a Gaussian random variable is less than the input — equivalently, GELU is the expected value of $x \cdot \mathbb{1}[X \leq x]$ where $X \sim \mathcal{N}(0, 1)$. It is a smoother version of ReLU's "pass through if positive, zero if negative": GELU passes through with probability $\Phi(x)$, smooth around $x = 0$. The probabilistic motivation comes from dropout thinking — ReLU deterministically masks, while GELU stochastic-masks with a probability depending on the input value.

- **Q: Why don't we use sigmoid in hidden layers anymore?**
  A: Three problems. (1) **Saturation** — for large $|x|$, the gradient is near zero, so deep networks can't learn (vanishing gradients). (2) **Not zero-centered** — the output is in $(0, 1)$, so gradients are always positive, causing zigzag optimization. (3) **No sparsity** — every neuron produces a non-zero output, wasting capacity. ReLU/GELU/SwiGLU solve all three: non-saturating for positive inputs, zero-centered (mostly), and sparse. Sigmoid is still used for output (binary classification) and gating (LSTM gates) where the $(0, 1)$ range is desired.

- **Q: How does the choice of activation interact with initialization?**
  A: The activation's derivative at init determines the right scale. For ReLU (derivative 0 or 1, expected 0.5 for symmetric inputs), He init uses variance $2/n$ to compensate for the 50% zeroing. For GELU (similar to ReLU but smoother), He init works. For tanh (derivative $\leq 1$), Xavier init uses variance $1/n$. Mismatching activation and init causes activation explosion or vanishing at init, which destabilizes training. Modern LLMs use SwiGLU with He init scaled by $\sqrt{2/n}$ — the gating adds variance, so the scale is adjusted. See [[05 - Neural Network Foundations/Training Dynamics and Stability/Weight Initialization|Weight Initialization]].

- **Q: Why is SwiGLU's hidden dimension $\frac{8}{3} d$ instead of $4d$?**
  A: SwiGLU has 3 weight matrices (gate, up, down) instead of GELU's 2 (up, down). To keep the parameter count comparable, the hidden dimension is reduced by a factor of $2/3$: $4d \times 2/3 = 8d/3$. Without this reduction, SwiGLU would have 1.5× the parameters of GELU for the same $d_{model}$, which would be an unfair comparison. The $8/3$ factor is empirical; some models use slightly different values (e.g., Llama uses $\lfloor 8d/3 / 256 \rfloor \times 256$ to align with Tensor Core sizes).

- **Q: How does activation choice affect quantization?**
  A: Two issues. (1) **Range** — unbounded activations (ReLU, GELU, SwiGLU) can produce large values that exceed INT8's range. Per-channel quantization handles this by giving each channel its own scale. (2) **Element-wise multiply** — SwiGLU's gate multiply amplifies quantization noise; the product of two INT8 values has higher relative error than the inputs. Mitigations: keep SwiGLU in fp16 (quantize only the linear layers), or use INT8 with careful per-channel scales. Most production INT8 LLMs (vLLM, TensorRT-LLM) handle this automatically, but custom implementations need care.

## Further reading

The primary sources behind the results above are worth reading directly:

- Nair & Hinton (2010), *Rectified Linear Units Improve Restricted Boltzmann Machines*.
- Hendrycks & Gimpel (2016), *Gaussian Error Linear Units (GELUs)*.
- Shazeer (2020), *GLU Variants Improve Transformer*.
- Ramachandran et al. (2017), *Searching for Activation Functions* (Swish).

## See also

- [[Neural Network Foundations MOC]]
- [[Forward Propagation]]
- [[Neural Network Architecture and Notation]]
- [[Perceptrons and Multi-Layer Perceptrons]]
- [[Artificial Neural Networks]]
- [[Backpropagation]]
- [[Matrix Implementation of Backpropagation]]
- [[Data Preparation for Neural Networks]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Weight Initialization|Weight Initialization]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Batch Normalization|Batch Normalization]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Dropout and Regularization|Dropout and Regularization]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Hyperparameters and Network Configuration|Hyperparameters and Network Configuration]]
- [[Normalization Layers]]
- [[Transformer Block]]
