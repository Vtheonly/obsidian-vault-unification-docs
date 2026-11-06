---
title: SVM Lagrangian Dual
type: derivation
aliases:
  - SVM Dual Problem
  - SVM Dual Form
  - Dual Representation of SVM
tags:
  - machine-learning
  - support-vector-machines
  - optimization
  - lagrange-multipliers
  - duality
  - convex-optimization
  - dot-products
  - support-vectors
sources:
  - "The Lagrangian Optimization"
  - "The Dual Representation and Dot Products"
created_index: 23
---

This note is the mathematical heart of [[Support Vector Machines]]: the step-by-step derivation that turns the "widest street" objective into its dual form. Starting from the canonical constrained problem — minimize $\frac{1}{2} ||\vec{w}||^2$ subject to every sample lying on the correct side of the street — we build the Lagrangian with multipliers $\alpha_i$, take its derivatives with respect to $\vec{w}$ and $b$, and plug the results back in to eliminate the primal variables. The payoff is twofold: the optimization and even the classification rule turn out to depend exclusively on dot products between data vectors, and the problem is convex, so a single global optimum is guaranteed. The dot-product structure is exactly what the [[Kernel Trick]] later exploits; together the SVM notes anchor one area of the [[Machine Learning MOC]].

## The starting point: a constrained optimization problem

From the mathematics of separation we now have a classic constrained optimization problem:

1. **Minimize:** $\frac{1}{2} ||\vec{w}||^2$ (Minimize magnitude of w to maximize width).
2. **Subject to:** $y_i (\vec{w} \cdot \vec{x}_i + b) - 1 \geq 0$ (Every sample must be on the correct side of the street).

The objective is the canonical one inherited from the width calculation — minimizing the squared magnitude of $\vec{w}$ is what maximizes the street's width — and the constraint is the unified margin condition built from the labels $y_i$. Neither piece can be handled by unconstrained minimization alone; the constraints must enter the objective itself, which is precisely what Lagrange multipliers achieve.

## Lagrange multipliers

In calculus, when we want to find a minimum subject to constraints, we use **Lagrange Multipliers** ($\alpha$). We subtract the sum of the constraints from the objective function to create the **Lagrangian ($L$)**:

$$ L = \frac{1}{2}||\vec{w}||^2 - \sum_{i} \alpha_i [y_i(\vec{w} \cdot \vec{x}_i + b) - 1] $$

- **$\alpha_i$**: The Lagrange multiplier for the $i$-th data point.
- **Intuition**: We are looking for an extremum (minimum/maximum) of this new function $L$.

Each sample gets its own multiplier, weighted by how strongly its constraint participates in the solution — a weighting that will turn out to be zero for every point except the support vectors.

## Taking the derivatives

To find the extremum, we take the partial derivatives of $L$ with respect to the variables we want to find ($\vec{w}$ and $b$) and set them to zero.

### Derivative with respect to $\vec{w}$

$$ \frac{\partial L}{\partial \vec{w}} = \vec{w} - \sum \alpha_i y_i \vec{x}_i = 0 $$

$$ \implies \vec{w} = \sum_{i} \alpha_i y_i \vec{x}_i $$

**Major Insight #1:** The vector $\vec{w}$ is simply a **linear sum of the sample vectors**.

Note: Most $\alpha_i$ will be zero. Only the Support Vectors (points in the gutter) have non-zero $\alpha$. Thus, $\vec{w}$ is a linear sum of the *Support Vectors*.

### Derivative with respect to $b$

$$ \frac{\partial L}{\partial b} = - \sum \alpha_i y_i = 0 $$

$$ \implies \sum_{i} \alpha_i y_i = 0 $$

**Major Insight #2:** The sum of the alphas times their labels must be zero. This provides a constraint on the optimization variables.

## Plugging back in (the transformation)

We substitute these results back into the original Lagrangian equation to simplify it. This effectively removes the primal variables ($\vec{w}$ and $b$) and leaves us with only the dual variables ($\alpha$).

After a significant amount of algebra (substituting $\vec{w}$ and grouping terms), we arrive at the **Dual Form**:

$$ L = \sum_{i} \alpha_i - \frac{1}{2} \sum_{i} \sum_{j} \alpha_i \alpha_j y_i y_j (\vec{x}_i \cdot \vec{x}_j) $$

**Why is this amazing?** Look closely at the equation. The optimization depends **ONLY** on the **dot product** of pairs of samples:

$$ (\vec{x}_i \cdot \vec{x}_j) $$

This realization leads us to the "Miracle" of SVMs.

## The dual decision rule

The previous derivation left us with the Dual Form of the Lagrangian, written compactly:

$$ L = \sum \alpha_i - \frac{1}{2} \sum_{i} \sum_{j} \alpha_i \alpha_j y_i y_j (\vec{x}_i \cdot \vec{x}_j) $$

Furthermore, look at the decision rule for a new unknown point $\vec{u}$, inherited from the primal problem:

$$ \vec{w} \cdot \vec{u} + b \geq 0 $$

Since we know that $\vec{w} = \sum \alpha_i y_i \vec{x}_i$, we can substitute that into the decision rule:

$$ (\sum \alpha_i y_i \vec{x}_i) \cdot \vec{u} + b \geq 0 $$

$$ \sum \alpha_i y_i (\vec{x}_i \cdot \vec{u}) + b \geq 0 $$

The decision rule, too, has become a weighted sum of dot products — no explicit weight vector required.

## The "miracle"

Both the **training** (optimization of $L$) and the **classification** (decision rule) depend **exclusively** on the dot products of data vectors.

- Optimization uses: $\vec{x}_i \cdot \vec{x}_j$
- Decision uses: $\vec{x}_i \cdot \vec{u}$

We never actually need to know the vectors themselves in isolation, nor do we need to calculate $\vec{w}$ explicitly if we calculate these products. This is precisely the observation the [[Kernel Trick]] exploits: since only dot products enter the equations, any function that equals a dot product in some higher-dimensional space can be substituted for them, yielding non-linear boundaries without the cost of computing the mapping.

## Convexity

Because of the squared term in the minimization ($\frac{1}{2}||\vec{w}||^2$) and linear constraints, this is a **Convex Optimization Problem**.

- **Neural Nets:** The error landscape is rugged with many local minima. You might get stuck.
- **SVMs:** The landscape is a bowl. There is **one global minimum**. You cannot get stuck in a local minimum.
- The solution is guaranteed to be the optimal solution for the given constraints.

This guarantee is why the kernel-expanded SVM of [[Kernel Trick]] can produce highly complex, non-linear boundaries while still finding the global optimum — unlike training procedures that descend a rugged error surface with [[Gradient Descent]] and may settle somewhere suboptimal.

## See also

- [[Machine Learning MOC]] — the map of machine learning topics.
- [[Support Vector Machines]] — the primal story: the widest street, the decision rule, the constraints, and the width calculation.
- [[Kernel Trick]] — what the dot-product-only formulation makes possible: kernel functions, polynomial and RBF kernels, Mercer's theorem.
- [[Gradient Descent]] — iterative optimization of unconstrained objectives; the SVM dual is instead a convex program with a guaranteed global optimum.
- [[Loss Functions]] — error-based training objectives, for contrast with the margin-constrained SVM objective.
- [[Regularization Techniques]] — the $\frac{1}{2}||\vec{w}||^2$ objective penalizes weight magnitude, the same quantity controlled by L2-style penalties.
