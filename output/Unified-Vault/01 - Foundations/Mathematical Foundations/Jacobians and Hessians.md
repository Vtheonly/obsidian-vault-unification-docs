---
title: Jacobians and Hessians
type: concept
aliases:
  - Jacobian
  - Hessian
  - Jacobian matrix
  - Hessian matrix
  - Multivariate Calculus - Jacobians and Hessians
  - "08. Multivariate Calculus — Jacobians and Hessians"
tags:
  - multivariable-calculus
  - jacobian
  - hessian
  - optimization
  - backpropagation
  - curvature
  - loss-landscape
sources:
  - "08. Multivariate Calculus — Jacobians and Hessians"
created_index: 17
---

Multivariate calculus does not stop at the gradient: gradients are first derivatives of scalar functions, while deep learning is built out of vector-valued functions and curved loss surfaces that first derivatives alone cannot describe. The **Jacobian** is the matrix of first derivatives of a vector-valued function, and the **Hessian** is the matrix of second derivatives of a scalar function; together they are essential for understanding backpropagation through vector-valued layers (like RNNs and attention), second-order optimization, and the curvature of loss landscapes. This note develops both objects: the three levels of derivative, the Jacobian form of the chain rule that makes backpropagation rigorous, the places Jacobians appear in practice, and what the Hessian reveals about optimization. It builds on the derivative machinery of [[Derivatives and the Chain Rule]] and the matrix language of [[Linear Algebra Fundamentals]], and extends [[Gradients and Gradient Descent]]; a complementary treatment of the same objects from the calculus side is [[02 - Mathematics/Calculus/Jacobians and Hessians|Jacobians and Hessians]].

## The three levels of derivative

Derivatives come in a hierarchy determined by the shape of the function being differentiated:

| Function type | Derivative | Name | Shape |
| :--- | :--- | :--- | :--- |
| Scalar → scalar $f: \mathbb{R} \to \mathbb{R}$ | $f'(x)$ | Ordinary derivative | scalar |
| Vector → scalar $f: \mathbb{R}^n \to \mathbb{R}$ | $\nabla f(\mathbf{x})$ | Gradient | vector $\in \mathbb{R}^n$ |
| Vector → vector $f: \mathbb{R}^n \to \mathbb{R}^m$ | $J_f(\mathbf{x})$ | Jacobian | matrix $\in \mathbb{R}^{m \times n}$ |
| Scalar → vector (second derivative) | $H_f(\mathbf{x})$ | Hessian | matrix $\in \mathbb{R}^{n \times n}$ |

The ordinary derivative and the gradient are the subject of [[Derivatives and the Chain Rule]] and [[Gradients and Gradient Descent]]; this note is about the two remaining rows, and about how all four rows connect.

## The Jacobian

For a vector-valued function $\mathbf{f}: \mathbb{R}^n \to \mathbb{R}^m$, the **Jacobian** is the matrix of all first-order partial derivatives:

$$J_f(\mathbf{x}) = \begin{pmatrix} \frac{\partial f_1}{\partial x_1} & \cdots & \frac{\partial f_1}{\partial x_n} \\ \vdots & \ddots & \vdots \\ \frac{\partial f_m}{\partial x_1} & \cdots & \frac{\partial f_m}{\partial x_n} \end{pmatrix} \in \mathbb{R}^{m \times n}$$

Entry $(i, j)$ is $\partial f_i / \partial x_j$ — how the $i$-th output changes with the $j$-th input.

### The chain rule with Jacobians

The multivariate chain rule is **matrix multiplication of Jacobians**. If $\mathbf{h} = \mathbf{f} \circ \mathbf{g}$ (i.e., $\mathbf{h}(\mathbf{x}) = \mathbf{f}(\mathbf{g}(\mathbf{x}))$), then:

$$J_h(\mathbf{x}) = J_f(\mathbf{g}(\mathbf{x})) \cdot J_g(\mathbf{x})$$

This is the rigorous form of backpropagation (see [[Backpropagation]]). The "gradient" that flows backward through a layer is a vector; the layer's transformation has a Jacobian; the gradient flowing further backward is the Jacobian-transpose times the incoming gradient:

$$\frac{\partial L}{\partial \mathbf{x}} = J_f(\mathbf{x})^\top \frac{\partial L}{\partial \mathbf{f}(\mathbf{x})}$$

### Where Jacobians appear in deep learning

1. **RNN backpropagation (BPTT):** The gradient at the first hidden state of an RNN is a product of per-step Jacobians: $\frac{\partial L}{\partial h_1} = \prod_t J_t \cdot \frac{\partial L}{\partial h_T}$. The vanishing/exploding gradient problem is fundamentally about the eigenvalues of this Jacobian product. See [[Backpropagation Through Time]] and [[07 - Sequence Models/Motivation and Recurrence/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]].

2. **Attention:** The softmax in attention is a vector-to-vector function (logits → probabilities), with a Jacobian that is not diagonal (changing one logit affects all probabilities because they must sum to 1). The softmax Jacobian is $J_{ij} = p_i (\delta_{ij} - p_j)$ — used to derive the famous $\hat{y} - y$ gradient simplification for softmax + cross-entropy. See [[Scaled Dot-Product Attention]].

3. **BatchNorm backward:** The BatchNorm operation is a vector-to-vector function with a non-trivial Jacobian. Computing its gradient requires care (the "BatchNorm backward" derivation is notoriously fiddly). See [[05 - Neural Network Foundations/Training Dynamics and Stability/Batch Normalization|Batch Normalization]].

4. **Contractive autoencoders:** These penalize the Frobenius norm of the encoder's Jacobian, $\|J_f(\mathbf{x})\|_F^2$, to force the encoder to be locally insensitive to input perturbations. See [[The Autoencoder]].

5. **Reparameterization trick (VAE):** When $z = \mu + \sigma \odot \epsilon$, the Jacobian $\partial z / \partial (\mu, \sigma)$ is what lets gradients flow through the sampling step — the reparameterization backprops through a Jacobian. See [[The Reparameterization Trick]] and [[The KL Divergence Loss]].

## The Hessian

For a scalar function $f: \mathbb{R}^n \to \mathbb{R}$, the **Hessian** is the matrix of all second-order partial derivatives:

$$H_f(\mathbf{x}) = \begin{pmatrix} \frac{\partial^2 f}{\partial x_1^2} & \frac{\partial^2 f}{\partial x_1 \partial x_2} & \cdots \\ \frac{\partial^2 f}{\partial x_2 \partial x_1} & \frac{\partial^2 f}{\partial x_2^2} & \cdots \\ \vdots & & \ddots \end{pmatrix} \in \mathbb{R}^{n \times n}$$

The Hessian captures the **curvature** of $f$ — how the gradient itself changes. For smooth $f$, the Hessian is symmetric (Clairaut's theorem: mixed partials are equal).

### Why the Hessian matters for optimization

The gradient tells you the **direction** of steepest descent. The Hessian tells you the **shape** of the loss surface in that direction:

- **Positive definite Hessian** (all eigenvalues > 0): local minimum (bowl shape).
- **Negative definite Hessian** (all eigenvalues < 0): local maximum (inverted bowl).
- **Mixed signs**: saddle point (the surface curves up in some directions, down in others).
- **Zero eigenvalues**: flat direction (no curvature).

In high dimensions, saddle points vastly outnumber local minima (Dauphin et al. 2014). This is why deep learning optimization is "stuck at saddle points" rather than local minima — the gradient is zero, but the Hessian has both positive and negative eigenvalues.

### Second-order optimization: Newton's method

Gradient descent uses only first-order information (the gradient):

$$\mathbf{x}_{t+1} = \mathbf{x}_t - \alpha \nabla f(\mathbf{x}_t)$$

**Newton's method** uses second-order information (the Hessian) to take a more direct step:

$$\mathbf{x}_{t+1} = \mathbf{x}_t - H_f(\mathbf{x}_t)^{-1} \nabla f(\mathbf{x}_t)$$

This "divides out" the curvature, taking a step that would reach the minimum in one shot if $f$ were quadratic. Newton's method converges much faster than gradient descent on well-conditioned problems.

Why we do not use Newton's method in deep learning:

1. The Hessian is $n \times n$ where $n$ is the number of parameters (millions to billions). Storing and inverting it is infeasible.
2. The Hessian can be ill-conditioned (negative or near-zero eigenvalues), causing Newton's method to step in the wrong direction.
3. Stochastic gradients (from mini-batches) make the Hessian estimate noisy.

**Quasi-Newton methods** (BFGS, L-BFGS) approximate the Hessian from gradient evaluations, avoiding the storage cost. They are used in classical optimization but rarely in deep learning, where the per-step cost is still too high.

### Hessian-free insights

Even when we do not compute the Hessian, its properties inform deep learning design:

1. **Momentum** (Adam, SGD+momentum) approximates curvature by accumulating gradient directions — a cheap substitute for Hessian information (see [[Adam Optimizer Derivation]]).
2. **Preconditioning** (RMSprop, Adam's per-parameter learning rates) approximates the Hessian's diagonal — scaling each parameter's step by its local curvature.
3. **Saddle points** are the reason "the loss plateaus and then suddenly drops" — the optimizer is slowly escaping a saddle.
4. **Sharp vs. flat minima** (Hessian eigenvalues at the minimum) correlate with generalization — flat minima (small eigenvalues) generalize better than sharp minima (large eigenvalues).

## The gradient-Jacobian relationship

The gradient $\nabla f$ is the **transpose of the Jacobian of a scalar function**: for $f: \mathbb{R}^n \to \mathbb{R}$, $J_f \in \mathbb{R}^{1 \times n}$ is a row vector, and $\nabla f = J_f^\top \in \mathbb{R}^{n \times 1}$ is a column vector. They are the same object, just oriented differently.

This is why backpropagation works: the chain rule through a vector-valued layer is $J^\top \cdot \text{incoming gradient}$, which is the transpose of the Jacobian times a vector — equivalent to "how does each input change given how each output should change."

## What you should walk away with

1. **Jacobians** are the multivariate generalization of derivatives — matrices of partial derivatives for vector-valued functions.
2. The **multivariate chain rule** is Jacobian matrix multiplication — backpropagation is Jacobian products.
3. Jacobians appear in RNN BPTT (the per-step Jacobian product causes vanishing/exploding gradients), attention (softmax Jacobian), BatchNorm backward, and VAE reparameterization.
4. **Hessians** are matrices of second derivatives — they capture the curvature of the loss surface.
5. Hessian eigenvalues classify critical points: minima (all positive), maxima (all negative), saddle points (mixed).
6. **Newton's method** uses the Hessian for faster convergence, but is infeasible in DL due to the Hessian's $O(n^2)$ size.
7. Momentum and Adam are cheap approximations of Hessian information — they use gradient history to estimate curvature.
8. Saddle points, not local minima, are the main obstacle in high-dimensional DL optimization.

Together with notation, derivatives and the chain rule, gradients and gradient descent, linear algebra, and probability and statistics, Jacobians and Hessians complete the mathematical machinery of modern ML.

## See also

- [[Foundations MOC]]
- [[Linear Algebra Fundamentals]]
- [[Gradients and Gradient Descent]]
- [[Derivatives and the Chain Rule]]
- [[Mathematical Notation]]
- [[Probability and Statistics for ML]]
- [[02 - Mathematics/Calculus/Jacobians and Hessians|Jacobians and Hessians]]
- [[Gradient and Chain Rule]]
- [[Backpropagation]]
- [[Backpropagation Through Time]]
- [[07 - Sequence Models/Motivation and Recurrence/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Batch Normalization|Batch Normalization]]
- [[Scaled Dot-Product Attention]]
- [[The Autoencoder]]
- [[The Reparameterization Trick]]
- [[The KL Divergence Loss]]
- [[Adam Optimizer Derivation]]
- [[Optimization Essentials]]
- [[Loss Functions]]
