---
title: Gradient Descent Optimization
type: example
aliases:
  - "Q5 - Gradient Descent Optimization"
  - "Gradient Descent Optimization Quiz"
  - "Gradient Descent Quiz"
tags:
  - deep-learning
  - quiz
  - practice
  - gradient-descent
  - optimization
  - learning-rate
  - convexity
  - saddle-points
  - sgd
  - mini-batch
  - adaptive-optimizers
sources:
  - "Q5 - Gradient Descent Optimization"
created_index: 14
---

This quiz bank practices gradient descent, the iterative algorithm that underlies virtually all neural network training. Its thirty questions cover the update rule and the learning rate, convex and non-convex loss landscapes, saddle points and why they dominate high-dimensional spaces, the batch, stochastic, and mini-batch variants, and the schedulers and adaptive optimizers built to tame the learning rate. The full treatment lives in [[Gradient Descent]] and [[Optimization Essentials]], with the optimizer side of the story in [[Optimizers and Learning Rate Schedulers]]; decide on an answer before unfolding it.

## True or false

Ten statements open the quiz: two on the algorithm and the gradient's direction, two on learning rate extremes, three on landscapes and their stationary points, and three on the data-per-update variants. The false statements reverse well-known facts — the gradient's direction, convexity's single-minimum guarantee — so check each claim against the definitions before deciding.

### The algorithm and the gradient

Two statements on what gradient descent is and which way the gradient points.

> [!question] Gradient Descent is an iterative optimization algorithm used to minimize a differentiable function.
>> [!success]- Answer
>> True

> [!question] The gradient points in the direction of the steepest descent.
>> [!success]- Answer
>> False

### Learning rate extremes

Two statements on the two ways a mis-set learning rate fails: too small and too large.

> [!question] If the learning rate is too small, gradient descent will converge very slowly.
>> [!success]- Answer
>> True

> [!question] If the learning rate is too large, gradient descent may overshoot and diverge.
>> [!success]- Answer
>> True

### Landscapes: convexity and saddle points

Three statements on bowl-shaped versus multi-valley landscapes, the shape of neural network losses, and points that are minima in some directions and maxima in others.

> [!question] A convex function has multiple local minima.
>> [!success]- Answer
>> False

> [!question] Neural network loss functions are typically convex.
>> [!success]- Answer
>> False

> [!question] A saddle point is a point that is a minimum in some directions but a maximum in others.
>> [!success]- Answer
>> True

### Batch, stochastic, and mini-batch

Three statements on how much data each variant uses per update and which one the industry trains with.

> [!question] Batch Gradient Descent computes the gradient using the entire dataset for each update.
>> [!success]- Answer
>> True

> [!question] Stochastic Gradient Descent (SGD) uses all training data for each weight update.
>> [!success]- Answer
>> False

> [!question] Mini-Batch Gradient Descent is the industry standard for training deep learning models.
>> [!success]- Answer
>> True

## Multiple choice

Ten questions cover the update mechanics, why deep learning needs iteration at all, how to read a loss landscape, and the tooling built around the variants. The options are drawn from neighboring concepts — schedulers and adaptive optimizers swap roles, and the three variants trade data-per-update — so be precise about which does what.

### The update rule, learning rate, and stopping

Three questions on what the learning rate controls, the formula every step follows, and when the algorithm knows to stop.

> [!question] What does the learning rate (alpha) control in gradient descent?
> a) The number of features
> b) The size of the step taken in the opposite direction of the gradient
> c) The number of layers
> d) The batch size
>> [!success]- Answer
>> b) The size of the step taken in the opposite direction of the gradient

> [!question] What is the update rule for gradient descent?
> a) x = x + alpha * gradient
> b) x = x - alpha * gradient
> c) x = alpha * gradient
> d) x = x / gradient
>> [!success]- Answer
>> b) x = x - alpha * gradient

> [!question] What is the stopping criterion for gradient descent?
> a) When the gradient is zero or very close to zero
> b) When the learning rate reaches 1
> c) When all weights are zero
> d) When the dataset is empty
>> [!success]- Answer
>> a) When the gradient is zero or very close to zero

### Why deep learning optimizes iteratively

One question on why closed-form solutions are off the table for neural network losses.

> [!question] Why cannot we solve deep learning optimization analytically?
> a) The functions are too simple
> b) There are millions of non-linear parameters making analytical solutions impossible
> c) Computers cannot do math
> d) The loss is always zero
>> [!success]- Answer
>> b) There are millions of non-linear parameters making analytical solutions impossible

### Reading the loss landscape

Three questions on the convex bowl, the cost of stopping in a local minimum, and why saddle points outnumber true minima in high dimensions.

> [!question] What is a convex function?
> a) A function with multiple local minima
> b) A function with a single global minimum shaped like a bowl
> c) A function that is always flat
> d) A function that has no minimum
>> [!success]- Answer
>> b) A function with a single global minimum shaped like a bowl

> [!question] What happens when gradient descent gets stuck in a local minimum on a non-convex landscape?
> a) It always finds the global minimum anyway
> b) It converges prematurely to a suboptimal solution
> c) It automatically switches to a convex function
> d) It crashes
>> [!success]- Answer
>> b) It converges prematurely to a suboptimal solution

> [!question] Why are saddle points more common than true local minima in high-dimensional spaces?
> a) Because all dimensions have the same minimum
> b) Because a local minimum in one dimension is rarely a local minimum in all other dimensions
> c) Because saddle points do not exist
> d) Because neural networks are always convex
>> [!success]- Answer
>> b) Because a local minimum in one dimension is rarely a local minimum in all other dimensions

### Variants and adaptive optimizers

Three questions on the single-sample variant, the hidden benefit of mini-batch noise, and the optimizers that adjust the learning rate per parameter.

> [!question] Which variant of gradient descent uses a single random data point per update?
> a) Batch GD
> b) Mini-Batch GD
> c) Stochastic GD
> d) Full GD
>> [!success]- Answer
>> c) Stochastic GD

> [!question] What is a key benefit of mini-batch noise?
> a) It makes training slower
> b) It can help escape shallow local minima or saddle points
> c) It increases the learning rate
> d) It removes the need for a loss function
>> [!success]- Answer
>> b) It can help escape shallow local minima or saddle points

> [!question] Which adaptive optimizer automatically adjusts the learning rate per parameter?
> a) Only vanilla SGD
> b) Adam, RMSProp, or Adagrad
> c) Batch GD
> d) No optimizer does this
>> [!success]- Answer
>> b) Adam, RMSProp, or Adagrad

## Matching

Ten matching questions sort the three variants by data, stability, and memory, match learning rate scenarios with behaviors and remedies, pair landscape types with convergence guarantees, and tie the update rule's symbols to their meanings. The groups are shuffled independently, so work from definitions rather than positions.

### Variants by data, stability, and memory

Three questions profiling batch, stochastic, and mini-batch gradient descent from three angles.

> [!question] Match the GD variant with the amount of data used per update.
>> [!example] Group A
>> a) Batch GD
>> b) Stochastic GD
>> c) Mini-Batch GD
>
>> [!example] Group B
>> n) A small group (e.g., 32-512 samples)
>> o) The entire dataset
>> p) A single random sample
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> n)

> [!question] Match the GD variant with its stability.
>> [!example] Group A
>> a) Batch GD
>> b) Stochastic GD
>> c) Mini-Batch GD
>
>> [!example] Group B
>> n) Very stable, smooth path
>> o) Noisy/chaotic, seismograph-like
>> p) Stable enough, slight noise
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the GD variant with its memory usage.
>> [!example] Group A
>> a) Batch GD
>> b) SGD
>> c) Mini-Batch GD
>
>> [!example] Group B
>> n) Low
>> o) Medium
>> p) Very High
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

### Learning rate scenarios and remedies

Two questions on what too-small and too-large rates do, and the two families of fixes: schedulers and adaptive optimizers.

> [!question] Match the learning rate scenario with the behavior.
>> [!example] Group A
>> a) Learning rate too small
>> b) Learning rate too large
>
>> [!example] Group B
>> n) Overshoots, bounces, may diverge
>> o) Tiny steps, very slow convergence
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

> [!question] Match the solution to the learning rate problem.
>> [!example] Group A
>> a) Learning Rate Schedulers
>> b) Adaptive Optimizers
>
>> [!example] Group B
>> n) Automatically adjust learning rate per parameter (Adam, RMSProp)
>> o) Start high then gradually reduce the rate
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

### Landscape shapes and guarantees

Two questions connecting convexity, or its absence, to what gradient descent can promise.

> [!question] Match the function type with its landscape shape.
>> [!example] Group A
>> a) Convex function
>> b) Non-convex function
>
>> [!example] Group B
>> n) Single bowl, one global minimum
>> o) Multiple valleys, local and global minima
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)

> [!question] Match the convexity property with the implication for GD.
>> [!example] Group A
>> a) Convex landscape
>> b) Non-convex landscape
>
>> [!example] Group B
>> n) GD may get stuck in local minima
>> o) GD guaranteed to find the global minimum
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

### Definitions and formula components

Two questions defining the gradient, learning rate, and saddle point, then naming each piece of the update rule.

> [!question] Match the concept with its definition.
>> [!example] Group A
>> a) Gradient
>> b) Learning Rate
>> c) Saddle Point
>
>> [!example] Group B
>> n) Step size hyperparameter
>> o) Minimum in some directions, maximum in others
>> p) Direction of steepest ascent
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

> [!question] Match the term with the formula component.
>> [!example] Group A
>> a) x_t
>> b) alpha
>> c) nabla f(x_t)
>
>> [!example] Group B
>> n) The gradient (slope) at the current point
>> o) Current parameter value
>> p) Learning rate (step size)
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> n)

### The mini-batch case

One question assembling the three arguments for the industry-standard variant: escaping shallow valleys, fitting in GPU VRAM, and updating many times per epoch.

> [!question] Match the mini-batch benefit with its description.
>> [!example] Group A
>> a) Escape from local minima
>> b) RAM management
>> c) Faster convergence
>
>> [!example] Group B
>> n) Stochastic noise shakes the algorithm out of shallow valleys
>> o) Updates weights many times per epoch instead of once
>> p) Fits in GPU VRAM — cannot load millions of images at once
>
>> [!success]- Answer
>> a) -> n)
>> b) -> p)
>> c) -> o)

## See also

- [[Gradient Descent]]
- [[Optimization Essentials]]
- [[Optimizers and Learning Rate Schedulers]]
- [[Learning Rate Schedules]]
- [[Adam Optimizer Derivation]]
- [[Loss Functions]]
- [[Loss Functions and Cost Optimization]]
- [[The Perceptron and the Chain Rule]]
- [[Multi-Layer Perceptron and Backpropagation]]
- [[19 - Reference and Practice/Quizzes/Deep Learning Chapter 1/Linear Regression|Linear Regression]]
- [[Glossary MOC]]
