---
title: Data Preparation for Neural Networks
type: concept
aliases:
  - Data Preparation
  - Feature Scaling
  - Data Preprocessing for MLPs
  - MLP Implementation Strategy
tags:
  - neural-networks
  - data-preparation
  - feature-scaling
  - standardization
  - min-max-normalization
  - regularization
  - weight-initialization
  - overfitting
  - mlp
sources:
  - "08. Data Preparation and MLP Implementation"
created_index: 11
---

Neural networks are picky about their inputs: unscaled features, missing values, and carelessly split datasets can stall or silently corrupt training before any architecture choice matters. This note covers the practical guidelines for implementing an MLP, from data preparation to preventing overfitting: the cleaning and encoding checklist, the train/validation/test split, the mathematics of feature scaling, the mathematics of L1/L2 regularization, the mathematics of weight initialization, and a disciplined iterative strategy for growing a model that actually generalizes. It anchors the [[Neural Network Foundations MOC]] alongside [[Neural Network Architecture and Notation]] and [[Perceptrons and Multi-Layer Perceptrons]].

## The data preparation checklist

Three cleaning requirements come before anything else. **Missing values** must be imputed or dropped — handle them by imputing or deleting them. **Categorical variables** must be numericized using **one-hot encoding** — categorical text data cannot enter a network as raw strings (see [[Data Cleaning and Encoding Lab]] for the hands-on workflow).

**Scaling is not optional.** You **must** scale data (min-max or z-score): unscaled data will cause gradient descent to explode or stall, and scaling is crucial for convergence. The pairing matters:

- Use **standardization (z-score)** usually paired with **ReLU**.
- Use **min-max** paired with **sigmoid/tanh**.

The reason for the pairing is the shape of each activation's active region, developed in the next section.

## Structuring the data

Never train and test on the same data. Split your data into three parts, each with a distinct job:

- **Train set (70%):** used to update the weights — to learn the weights.
- **Validation set (15%):** used to evaluate hyperparameter choices (number of layers, learning rate) and prevent overfitting during training — to tune hyperparameters and trigger early stopping.
- **Test set (15%):** kept strictly isolated — used only once at the very end to evaluate final real-world performance. Untouched data for final evaluation.

**Data augmentation** — rotating, flipping, or zooming images — artificially creates more data to improve model generalization (see [[05 - Neural Network Foundations/Training Dynamics and Stability/Data Augmentation|Data Augmentation]]).

> [!TIP] Dataset splitting
> Never train and test on the same data. Split your data:
>
> - **Train (70%):** To learn the weights.
> - **Validation (15%):** To tune hyperparameters (number of layers, learning rate) and trigger Early Stopping.
> - **Test (15%):** Untouched data for final evaluation.

## Feature scaling mathematics

Neural networks are highly sensitive to the scale and distribution of input data. If Feature A ranges from 0–1 and Feature B ranges from 0–1,000,000, the gradient descent will create elongated contour plots, oscillating wildly and converging extremely slowly. Scaling creates circular contours, allowing gradient descent to take a direct path to the minimum. Preprocessing is not optional; it is mandatory for convergence.

### Standardization (z-score normalization)

Transforms the data to have a mean of 0 and a standard deviation of 1:

$$ x' = \frac{x - \mu}{\sigma} $$

- $\mu$ is the mean of the feature.
- $\sigma$ is the standard deviation of the feature.

Standardization is always preferred when using **ReLU** activation. It centers the data around zero, which helps gradient descent navigate efficiently. It also handles outliers better than min-max because it doesn't bound the data to a specific range — an outlier at 1000 will be mapped to a high z-score but won't compress all other values into a tiny range. As intuition for what the transform produces: after standardization, approximately 68% of values fall within $[-1, 1]$, 95% within $[-2, 2]$, and 99.7% within $[-3, 3]$.

### Normalization (min-max scaling)

Squeezes the data into a fixed range, typically $[0, 1]$:

$$ x' = \frac{x - x_{min}}{x_{max} - x_{min}} $$

Min-max scaling is preferred when using **sigmoid** or **tanh** activations, as their active, non-saturating regions are explicitly bounded between 0 and 1 (or -1 and 1).

Its vulnerability is outliers: a single extreme outlier will compress all other values into a tiny range. For example, if one house costs $10,000,000 while all others are under $500,000, min-max scaling would map 99% of the data to values between 0 and 0.05, losing most of the discriminative information.

> [!WARNING] Critical pitfall: data leakage
> You must fit the scaler (calculate $\mu, \sigma, x_{min}, x_{max}$) on the **training set only**. Then, use those exact parameters to transform the validation and test sets. If you calculate the min/max or mean/std on the entire dataset, you commit "data leakage" — giving the model hints about the test data during training. This results in artificially high performance that will not hold in production. The test set must remain completely unseen during all preprocessing decisions.

## Preventing overfitting (surapprentissage)

Deep learning models are so powerful they can easily memorize the training data, failing on new data. Overfitting occurs when a model memorizes the training data but fails on new data — in French, *surapprentissage*. Three defenses are used in practice, all developed in depth in [[05 - Neural Network Foundations/Training Dynamics and Stability/Dropout and Regularization|Dropout and Regularization]]:

- **Regularization (L1/L2)** adds a penalty to the loss function for having overly large weights — it penalizes large weights.
- **Dropout** randomly deactivates a percentage of neurons during training. This prevents the network from becoming overly reliant on any specific feature or neuron — it randomly turns off a percentage of neurons during training, forcing the network to not rely on any single neuron.
- **Early stopping** (*arrêt précoce*): continuously monitor the validation loss. If the training loss continues to drop, but the validation loss suddenly starts to rise, the model is beginning to overfit — stop training immediately.

## Regularization mathematics

When an MLP has too many parameters relative to the data, it memorizes the training set (overfitting): the model achieves near-zero training loss but performs poorly on new, unseen data. Regularization adds a penalty to the cost function to force the network to keep weights small and simple, preventing it from fitting the noise in the training data.

### L2 regularization (Ridge / weight decay)

We add the squared magnitude of the weights to the loss function:

$$ J_{regularized} = J_{original} + \lambda \sum_{j=1}^{m} w_j^2 $$

Here $\lambda$ (lambda) is the regularization strength hyperparameter. A larger $\lambda$ forces the weights to be smaller; a smaller $\lambda$ allows them to grow freely.

The effect is to force weights to be small but rarely exactly zero — it smooths the model by preventing any single weight from becoming too large and dominating the prediction. This is the most common form of regularization in deep learning, where it is often called **weight decay**. It works because large weights indicate that the model is relying heavily on specific features, which is a sign of overfitting; by penalizing large weights, L2 regularization forces the model to spread importance across many features, leading to more robust predictions.

The gradient of the regularization term is $2\lambda w_j$, which is added to the gradient of the original loss. This means the regularization effect is proportional to the current weight value — larger weights are penalized more.

### L1 regularization (Lasso)

We add the absolute magnitude of the weights to the loss function:

$$ J_{regularized} = J_{original} + \lambda \sum_{j=1}^{m} |w_j| $$

The effect follows from the derivative: the absolute value derivative is constant (either +1 or -1), which causes many weights to be pushed exactly to zero. This creates a **sparse** model, effectively performing feature selection — the network learns to ignore useless features by setting their weights to exactly 0.

The reason it works this way: unlike L2, where the penalty decreases as the weight approaches zero (proportional to $w$), L1 applies a constant force toward zero regardless of the weight's current value. This means even very small weights are pushed all the way to zero. The use case is when you suspect many features are irrelevant and want the model to automatically identify and discard them — L1 is popular in interpretability-critical applications where you need to know which features matter.

### Choosing between L1 and L2

- **L2 (Ridge):** Use when you believe all features contribute somewhat and you want to prevent any one from dominating. This is the default choice in most deep learning applications.
- **L1 (Lasso):** Use when you want feature selection — a sparse model where many weights are exactly zero. Useful when interpretability is important.
- **Elastic net (L1 + L2):** Combines both penalties: $J_{reg} = J_{original} + \lambda_1 \sum |w_j| + \lambda_2 \sum w_j^2$. Gets the sparsity of L1 with the stability of L2.

## Weight initialization mathematics

If all weights start at 0, every neuron in a layer computes the same output, receives the same gradient, and updates identically. The layer acts as a single neuron — a phenomenon called **symmetry breaking failure**. We must initialize weights randomly, but carefully: the initialization must ensure that the variance of activations and gradients remains stable as they pass through the network.

### The problem with naive random initialization

If weights are initialized with too-large values, activations grow exponentially through the layers (exploding gradients). If weights are initialized with too-small values, activations shrink to zero through the layers (vanishing gradients). Both scenarios prevent the network from learning (see [[05 - Neural Network Foundations/Training Dynamics and Stability/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]]).

### Xavier initialization (Glorot)

Designed for sigmoid and tanh activations, Xavier initialization ensures the variance of the outputs of a layer is roughly equal to the variance of its inputs:

$$ W \sim \mathcal{N}\left(0, \sqrt{\frac{1}{n_{in}}}\right) $$

Or using a uniform distribution:

$$ W \sim \mathcal{U}\left(-\sqrt{\frac{6}{n_{in} + n_{out}}}, +\sqrt{\frac{6}{n_{in} + n_{out}}}\right) $$

- $n_{in}$: Number of input neurons to the layer.
- $n_{out}$: Number of output neurons from the layer.

By scaling the initial weights inversely with the number of inputs, the variance of each neuron's output is approximately equal to the variance of its input. This prevents activations from growing or shrinking as they pass through the network, maintaining a stable signal throughout the forward pass.

### He initialization

Designed specifically for ReLU and its variants. Since ReLU zeros out half of the inputs (the negative ones), the variance of the output is effectively halved compared to the input. He initialization compensates by doubling the variance:

$$ W \sim \mathcal{N}\left(0, \sqrt{\frac{2}{n_{in}}}\right) $$

This prevents the signal from dying out (vanishing) or exploding as it passes through dozens of deep layers — the factor of 2 compensates for the fact that ReLU discards approximately half of the activations.

> [!WARNING] _Never initialize weights to zero_
> If all weights start at 0, every neuron in a layer computes the same output $z = 0 \cdot x_1 + 0 \cdot x_2 + \dots + b = b$, receives the same gradient during backpropagation (because the gradient depends on the same inputs and same errors), and updates by the same amount. After one update, all neurons still have identical weights. The layer effectively acts as a single neuron regardless of how many neurons it contains. This symmetry must be broken by random initialization.

The rule of thumb that falls out of the two schemes: always use He initialization with ReLU/Leaky ReLU/PReLU/ELU, and always use Xavier initialization with sigmoid/tanh. Using the wrong initialization can cause the network to fail to converge entirely. The broader design space is covered in [[05 - Neural Network Foundations/Training Dynamics and Stability/Weight Initialization|Weight Initialization]].

## MLP implementation strategy

Building an effective MLP requires a disciplined, iterative approach. Throwing a massive network at a problem and hoping for the best is a recipe for wasted time and poor results.

### Start simple

Build a network with just 1 hidden layer, and see how it performs before adding complexity. A simple model that works is always preferable to a complex model that might work. If a single hidden layer achieves 95% accuracy, adding more layers might only improve it to 95.5% while making training slower and more prone to overfitting.

### Adapt to the task

Complex tasks (high-dimensional images, natural language) need deeper/wider networks; simple tabular data might only need 1–2 layers. The architecture should be proportional to the complexity of the problem:

- **Simple problems** (tabular data with few features): 1–2 hidden layers with 32–128 neurons each.
- **Medium problems** (small images, short text): 2–4 hidden layers with 128–512 neurons each.
- **Complex problems** (large images, long sequences): deep architectures (CNNs, RNNs, Transformers) rather than simple MLPs — raw MLPs are rarely used for these tasks.

### Track metrics

Always plot training loss and validation loss together. The relationship between these two curves tells you exactly what is happening:

- **If both are high:** the model is **underfitting** — it hasn't learned the patterns in the data. Solution: increase model capacity (more layers, more neurons), train longer, or reduce regularization.
- **If training loss is low but validation loss is high:** the model is **overfitting** — it has memorized the training data but can't generalize. Solution: add regularization (L2, dropout), get more data, use data augmentation, or reduce model capacity.
- **If both are low and close together:** the model is well-fit — it has learned the patterns without memorizing the noise. This is the ideal scenario.

### Iterate: change one hyperparameter at a time

Deep learning is highly empirical. If you change the learning rate, batch size, and number of layers all at once and the model improves, you won't know which change caused the improvement. Follow a systematic approach:

1. Start with a baseline architecture and default hyperparameters.
2. Change ONE hyperparameter (e.g., learning rate from 0.01 to 0.001).
3. Train and evaluate.
4. If improvement, keep the change; if worse, revert.
5. Move to the next hyperparameter.

**Hyperparameter search order (by importance):**

1. **Learning rate** — the most impactful. Start with 0.001 (Adam default) and try log-scale variations.
2. **Batch size** — affects generalization and training speed. Try 32, 64, 128, 256.
3. **Number of hidden layers and neurons** — determines model capacity. Start small and grow.
4. **Regularization strength** ($\lambda$, dropout rate) — prevents overfitting. Add only if overfitting is observed.
5. **Activation function** — ReLU is the default; try Leaky ReLU or GELU only if ReLU underperforms.

More on the tuning landscape in [[05 - Neural Network Foundations/Training Dynamics and Stability/Hyperparameters and Network Configuration|Hyperparameters and Network Configuration]].

## See also

- [[Neural Network Foundations MOC]]
- [[Neural Network Architecture and Notation]]
- [[Perceptrons and Multi-Layer Perceptrons]]
- [[Forward Propagation]]
- [[Activation Functions]]
- [[Artificial Neural Networks]]
- [[Data Cleaning and Encoding Lab]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Dropout and Regularization|Dropout and Regularization]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Data Augmentation|Data Augmentation]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Weight Initialization|Weight Initialization]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Hyperparameters and Network Configuration|Hyperparameters and Network Configuration]]
