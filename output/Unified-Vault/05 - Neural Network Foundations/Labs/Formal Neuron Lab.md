---
title: Formal Neuron Lab
type: tutorial
aliases:
  - Lab 2 Formal Neuron
  - "Lab 2: Formal Neuron"
  - TP2
  - Formal Neuron
tags:
  - neural-networks
  - formal-neuron
  - activation-functions
  - numpy
  - matplotlib
  - tutorial
sources:
  - "01. TP2"
created_index: 8
---

This lab implements the formal neuron — the single computational unit that every neural network stacks into layers — and puts its two core components to work in Python. It is organized as two jobs: Job 1 visualizes the five classic activation functions (binary step, linear, ReLU, sigmoid, and tanh) on one matplotlib plot, and Job 2 computes a single neuron's output from given inputs, weights, and a bias, first by hand and then in code. The goal is to understand and implement the two core components of a single artificial neuron: its activation function and its computation process. It is the hands-on companion to [[Activation Functions]] and [[Perceptrons and Multi-Layer Perceptrons]], and it anchors the lab track of the [[Neural Network Foundations MOC]] alongside [[Data Cleaning and Encoding Lab]].

## Environment setup

For this lab, you'll need `numpy` for efficient numerical calculations and `matplotlib` for plotting the graphs. The first two steps are to create and activate your virtual environment; if you are continuing from the previous lab and the `venv` is already active, you can skip this part. The commands differ slightly between platforms.

*On macOS or Linux:*

```bash
python3 -m venv venv
source venv/bin/activate
```

*On Windows:*

```bash
python -m venv venv
venv\Scripts\activate
```

**Step 3: install the required packages.** With your environment active (`(venv)` showing in the prompt), run the install command below. We use the `python -m pip` method to avoid any potential `externally-managed-environment` errors. You are now ready to write the code.

```bash
python -m pip install numpy matplotlib
```

## The two jobs of the lab

Job 1 asks you to visualize the activation functions so that their shapes — a hard threshold, a straight line, a rectified line, and two S-curves — become familiar at a glance. Job 2 asks you to compute a neuron's output for a concrete input vector, weight vector, and bias, which exercises the two-step computation every formal neuron performs. Keeping a `README.md` file in your project folder that explains the concepts behind both jobs is part of the lab, and the next two sections provide exactly that background.

## What an activation function does

In a neural network, a neuron computes a "weighted sum" of its inputs. The **activation function** then takes this sum and performs a transformation on it to produce the neuron's final output. It is the only ingredient that can bend the network away from plain linear behavior.

Its primary purpose is to introduce **non-linearity** into the network. Without non-linearity, no matter how many layers a neural network has, it would behave just like a single linear regression model, which cannot learn complex patterns in data. This is why the choice of activation matters so much in practice — see [[Activation Functions]] for the full conceptual treatment, and [[Artificial Neural Networks]] for how these units are wired into complete networks.

## The functions we will visualize

The lab plots five activations, chosen to span the space from the original threshold of the formal neuron to the modern default. For each one it records the formula, the behavior, and the use case.

### Binary step

The binary step is a simple threshold function: $f(x) = 1$ if $x > 0$ else $0$. If the input is positive, it "fires" (output 1); otherwise, it doesn't (output 0). It is rarely used in modern deep learning because its derivative is zero almost everywhere, which makes it impossible to train using gradient-based methods like [[Backpropagation]].

### Linear

The linear activation is the identity, $f(x) = x$. The output is simply equal to the input, so it does not introduce non-linearity. It is primarily used in the output layer of a network for regression tasks, where you want to predict a continuous value, like a price.

### ReLU

ReLU (Rectified Linear Unit) is $f(x) = max(0, x)$. If the input is positive, the output is the input itself; if the input is negative, the output is zero. It is the most popular activation function in deep learning — computationally very efficient, and it helps mitigate the "vanishing gradient" problem that afflicts the two saturating S-curves below.

### Sigmoid

The sigmoid, $f(x) = 1 / (1 + e^-x)$, is an "S"-shaped curve that squashes any input value into a range between 0 and 1. It is very common in the output layer for binary classification problems, where the output can be interpreted as a probability. It suffers from the vanishing gradient problem in deep networks.

### Tanh

The hyperbolic tangent, $f(x) = (e^x - e^-x) / (e^x + e^-x)$, is similar to sigmoid but squashes values into a range between -1 and 1. It is often preferred over sigmoid in hidden layers because its output is zero-centered, which can help in learning. It also suffers from the vanishing gradient problem.

The table condenses the five profiles for quick comparison while you read the plot:

| Function | Formula | Output range | Typical use |
| --- | --- | --- | --- |
| Binary step | $f(x) = 1$ if $x > 0$ else $0$ | 0 or 1 | rarely used; untrainable by gradient methods |
| Linear | $f(x) = x$ | unbounded | output layer for regression |
| ReLU | $f(x) = max(0, x)$ | $[0, +\infty)$ | most popular choice overall |
| Sigmoid | $f(x) = 1 / (1 + e^-x)$ | between 0 and 1 | output layer for binary classification |
| Tanh | $f(x) = (e^x - e^-x) / (e^x + e^-x)$ | between -1 and 1 | hidden layers; zero-centered |

> [!note] Edge case at zero
> The README formula fires only for strictly positive input ($x > 0$), while the solution script implements `np.where(x >= 0, 1, 0)`, which returns 1 at exactly $x = 0$. The two definitions differ only at that single point, which is invisible on the plot.

## How a formal neuron computes its output

A formal neuron's computation is a two-step process. **Step 1: calculate the potential** (also called the net input or the weighted sum). The neuron takes all its inputs, multiplies each by its corresponding weight, sums them all up, and then adds a bias term:

$$z = (w₁x₁ + w₂x₂ + ... + wₙxₙ) + b$$

In vector form, this is much simpler — where `·` is the dot product:

$$z = W · X + b$$

**Step 2: apply the activation function.** The potential $z$ is then passed through an activation function (`f`) to produce the final output $y$:

$$y = f(z)$$

That is the whole machinery: one dot product, one bias, one transform. [[Forward Propagation]] develops what happens when this two-step unit is stacked across layers and vectorized.

## Worked example: one neuron by hand

The lab fixes a concrete example and asks you to work it through before trusting the code. The givens are:

- Inputs (X): `[3, -2, 0, -1.5]`
- Weights (W): `[1, 2, 3, 4]`
- Bias (b): `1`
- Activation function (f): `TanH`

**Step 1 — calculate the potential:**

$$z = (3 * 1) + (-2 * 2) + (0 * 3) + (-1.5 * 4) + 1$$

$$z = 3 - 4 + 0 - 6 + 1$$

$$z = -6$$

**Step 2 — apply the activation:**

$$y = tanh(-6)$$

The `tanh` of a large negative number is very close to -1, so:

$$y ≈ -0.9999877$$

The potential is strongly negative, so the neuron sits deep in tanh's saturated regime and its output is pinned near the floor of -1; making $z$ even more negative would barely move the output. This saturation is the same mechanism behind the vanishing gradient problem that sigmoid and tanh suffer from in deep networks.

## The complete solution script

This single script solves both Job 1 and Job 2. You can save it as `lab2_solution.py` and run it from your terminal.

```python
import numpy as np
import matplotlib.pyplot as plt

# =============================================================================
# Job 1: Visualize Activation Functions
# =============================================================================
print("--- Starting Job 1: Visualizing Activation Functions ---")

# Define the input range from -10 to 10 with a step of 0.1
x = np.arange(-10, 10.1, 0.1)

# --- Define the activation functions ---

def binary_step(x):
    """Returns 1 if x > 0, else 0."""
    return np.where(x >= 0, 1, 0)

def linear(x):
    """Returns the input value itself."""
    return x

def relu(x):
    """Returns max(0, x)."""
    return np.maximum(0, x)

def sigmoid(x):
    """Sigmoid function: 1 / (1 + e^-x)"""
    return 1 / (1 + np.exp(-x))

def tanh(x):
    """Hyperbolic tangent function."""
    return np.tanh(x)

# --- Calculate the outputs for each function ---
y_step = binary_step(x)
y_linear = linear(x)
y_relu = relu(x)
y_sigmoid = sigmoid(x)
y_tanh = tanh(x)

# --- Plotting the functions ---
plt.figure(figsize=(12, 8))
plt.title('Common Activation Functions', fontsize=16)

plt.plot(x, y_step, label='Binary Step', linestyle='--')
plt.plot(x, y_linear, label='Linear', linestyle='--')
plt.plot(x, y_relu, label='ReLU', linewidth=2)
plt.plot(x, y_sigmoid, label='Sigmoid', linewidth=2)
plt.plot(x, y_tanh, label='Tanh', linewidth=2)

# Add grid, axis lines, labels, and legend for clarity
plt.grid(True, which='both', linestyle='--', linewidth=0.5)
plt.axhline(y=0, color='k', linewidth=0.8)
plt.axvline(x=0, color='k', linewidth=0.8)
plt.xlabel('Input (z)', fontsize=12)
plt.ylabel('Output (f(z))', fontsize=12)
plt.legend(fontsize=12)
plt.ylim(-1.5, 2.0) # Set y-axis limits for better visualization

# Show the plot
print("Displaying the plot for Job 1. Please close the plot window to continue to Job 2.")
plt.show()


# =============================================================================
# Job 2: Compute the Output of a Formal Neuron
# =============================================================================
print("\n--- Starting Job 2: Computing Neuron Output ---")

# Given values from the example
inputs = np.array([3, -2, 0, -1.5])
weights = np.array([1, 2, 3, 4])
bias = 1

# Step 1: Compute the potential (net input), z = W · X + b
# np.dot() performs the dot product (w1*x1 + w2*x2 + ...)
potential = np.dot(weights, inputs) + bias

# Step 2: Compute the output by applying the TanH activation function
output = np.tanh(potential)

# Display the results in a clear, readable format
print("\n--- Neuron Calculation ---")
print(f"Inputs (X):  {inputs}")
print(f"Weights (W): {weights}")
print(f"Bias (b):    {bias}")
print("-" * 25)
print(f"1. Potential (z = W.X + b): {potential:.4f}")
print(f"2. Output (y = tanh(z)):    {output:.4f}")
print("\nLab successfully completed!")

```

### Job 1 in the script

The script opens by defining the input range from -10 to 10 with a step of 0.1 as `x = np.arange(-10, 10.1, 0.1)` — the stop value 10.1 is what makes the range actually reach +10, since `np.arange` excludes its endpoint. The five functions are then defined exactly as in the README: `binary_step` via `np.where`, `linear` as the identity, `relu` via `np.maximum(0, x)`, `sigmoid` as `1 / (1 + np.exp(-x))`, and `tanh` via `np.tanh`. All five are evaluated on the same `x` and drawn on one figure, with the step and linear curves in dashed lines and ReLU, sigmoid, and tanh in solid lines of width 2. The plot adds a grid, black zero-lines on both axes, axis labels (`Input (z)` and `Output (f(z))`), a legend, and y-limits of -1.5 to 2.0 for better visualization. Because `plt.show()` blocks the program until the window is dismissed, the script prints a reminder first: close the plot window to continue to Job 2.

### Job 2 in the script

Job 2 encodes the hand calculation almost line for line. `np.dot(weights, inputs) + bias` computes the potential — the code's comment notes that `np.dot()` performs the dot product (`w1*x1 + w2*x2 + ...`) — and `np.tanh(potential)` applies the activation. The results are then displayed in a clear, readable format, with the potential and output printed to four decimal places under the labels `1. Potential (z = W.X + b)` and `2. Output (y = tanh(z))`: the console reports the potential as `-6.0000` and the output as `-1.0000`, the latter being the four-decimal rounding of the true value ≈ -0.9999877. The script signs off with "Lab successfully completed!".

## See also

- [[Neural Network Foundations MOC]]
- [[Activation Functions]] — the full conceptual treatment of the five functions plotted here
- [[Perceptrons and Multi-Layer Perceptrons]] — the single formal neuron formalized as the perceptron
- [[Artificial Neural Networks]] — stacking these units into complete networks
- [[Forward Propagation]] — the two-step computation, vectorized across layers
- [[Backpropagation]] — why the binary step's zero-almost-everywhere derivative is fatal for training
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]] — the problem ReLU mitigates and sigmoid and tanh suffer from
- [[Data Cleaning and Encoding Lab]] — the sibling lab on the data side
