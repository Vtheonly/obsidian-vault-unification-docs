---
title: From Basic Convolution to Learned Weights
type: concept
aliases:
  - The Bridge - From Basic Convolution to Learned Weights
  - Classical-to-Deep Bridge
  - From Hand-Crafted Filters to Learned Kernels
  - Learned Convolution Kernels
tags:
  - cnn
  - convolutional-neural-networks
  - computer-vision
  - deep-learning
  - feature-learning
  - sobel
  - gabor
  - backpropagation
  - gradient-descent
  - unsharp-masking
  - transferable-features
sources:
  - "03. The Bridge - From Basic Convolution to Learned Weights"
  - "5.6 The Classical-to-Deep Bridge"
created_index: 15
---

Classical image processing and deep learning are usually presented as separate worlds, yet the convolution at the heart of a CNN is mechanically the same sliding-window operation every hand-crafted kernel performs. The single conceptual shift — from human-designed feature extractors to machine-learned feature extractors — is that in a CNN the numbers inside the kernel are learnable weights, discovered by optimization rather than designed by a human — the engine that powered the computer vision revolution of the 2010s and beyond. This note traces the shift in full: why manual feature engineering was brittle and unscalable, the five-step lifecycle by which a random filter becomes a specialized feature extractor — iterating until the filters converge on task-optimal feature extractors, the empirical fact that trained CNNs rediscover the classical filters, and practical guidance on when classical pipelines still win. It anchors the [[CNN Course Overview]] alongside [[06 - Computer Vision/CNN Foundations and Philosophy/Core Architecture and Philosophy|Core Architecture and Philosophy]] and [[Processing 3D Volumes, Depth Summation, and Biases]].

## The same operation, decided two different ways

You already understand the mechanical process of basic convolution from classic image processing: taking a small matrix (a filter or kernel), sliding it across an input image, performing element-wise multiplication at every stop, and summing the results to create an output feature map. In classical computer vision, experts manually crafted these filters. A **Sobel filter** was built with specific hand-picked numbers (e.g., `[-1, 0, 1]` arrays) explicitly to detect vertical or horizontal edges. A **Gaussian blur** filter was designed with a specific bell-curve distribution of values to smooth images. A **Laplacian filter** was constructed to detect regions of rapid intensity change. Every single one of these was a product of human engineering — a domain expert sat down, reasoned about the mathematics of the visual feature they wanted to extract, and hard-coded the numbers.

**The fundamental leap from basic image filtering to Deep Convolutional Neural Networks (CNNs) is this:** In a CNN, we **do not hand-craft the filters**. The numbers inside the matrix are the **learnable weights** of the neural network itself. The network discovers, through iterative mathematical optimization, exactly what values those filters should contain in order to minimize a task-specific error function.

A classical image filter (Sobel, Laplacian, Gaussian, Gabor) is a **convolution** — a small kernel is slid across the image, and at each position, the kernel weights are multiplied with the corresponding pixels and summed. This is exactly what a CNN's first layer does. The only difference: **in classical image processing, the kernel is designed by a human (based on mathematical principles). In a CNN, the kernel is learned from data (via backpropagation).**

| | Classical filter | CNN filter |
| :--- | :--- | :--- |
| Operation | Convolution | Convolution |
| Kernel source | Designed by human | Learned from data |
| Kernel values | Fixed (e.g., Sobel = $[[-1,0,1],[-2,0,2],[-1,0,1]]$) | Initialized randomly, updated by gradient descent |
| Number of kernels | One per filter type (you choose which to apply) | Dozens to hundreds per layer (all learned) |
| Purpose | Detect specific features (edges, textures) | Detect whatever features minimize the loss |

**The convolution operation is identical.** The difference is entirely in how the kernel is determined.

## The flaw of manual feature engineering

Before deep learning, if you wanted to detect a cat in a photograph, the process was painstaking and brittle. Experts had to sit down and write algorithms to extract lines, calculate fur textures, and find shapes that looked like ears. They might design a Sobel filter for edges, a Gabor filter for textures, and a Hough transform for geometric shapes, then chain all of these hand-crafted features together into a pipeline that fed a classifier like a Support Vector Machine (SVM). If the lighting changed, or the cat turned around, or the image was slightly rotated, the hand-crafted filters usually failed — because they were designed for a narrow set of visual conditions. Scaling this approach to thousands of object categories was effectively impossible; you would need human experts to engineer custom feature extractors for every single object you ever wanted to detect.

This approach suffered from three crippling weaknesses. First, it was **brittle**: small changes in viewpoint, illumination, or occlusion would cause the carefully engineered features to produce unreliable outputs. Second, it was **non-scalable**: each new visual category required a fresh round of expert engineering. Third, it was **suboptimal**: hand-crafted features were designed based on human intuition about what visual patterns matter, but human intuition is a poor substitute for mathematical optimization across millions of data points.

A CNN bypasses all of these problems completely by *learning its own optimal features* directly from the raw pixel data. Instead of a human deciding what patterns to look for, the network discovers the patterns that are most useful for minimizing prediction error across the training dataset. The features that emerge are often ones that no human would have thought to engineer — complex, multi-scale patterns that are statistically optimal for the task at hand.

> [!important] The paradigm shift
> Classical vision: **"Tell me what features to look for, and I will design a filter for each one."**
> Deep learning: **"Give me data and a loss function, and I will discover the features myself."**

## From fixed to learned kernels

To make the transition concrete, consider the direct comparison between the classical and deep learning paradigms:

| Aspect | Classical Vision | Deep Learning (CNNs) |
|---|---|---|
| **Filter Design** | Human expert manually selects every number in the kernel | Network initializes random numbers and learns optimal values through training |
| **Feature Discovery** | You must know in advance what features matter (edges, corners, textures) | The network discovers which features matter by minimizing a loss function |
| **Adaptability** | Fixed once designed — cannot adapt to new data distributions | Continuously adaptive — retraining on new data shifts the filter values |
| **Example Workflow** | You want to detect edges → Apply a pre-defined $3 \times 3$ Sobel filter | You tell the network: "Here is an image. Here are 32 empty $3 \times 3$ filters. Adjust the numbers until you can classify this." |
| **Output** | Filters are static and hand-designed; they detect exactly one thing | The network might learn one filter that acts like an edge detector, another that detects specific color gradients, and another that detects textures — all from the same training process |
| **Scalability** | Each new visual category requires new hand-crafted features | The same training loop scales to any number of categories |

The deep learning approach does not discard the mathematical machinery of convolution — it still slides a small matrix across the image, performs element-wise multiplication, and sums the results. What changes is *who decides what numbers go in the matrix*. In classical vision, a human decides. In a CNN, the optimization algorithm decides.

## The lifecycle of a learnable filter

How does a network figure out what numbers belong inside the filter to make it act like an edge-detector or a fur-detector? It uses the same fundamental deep learning loop used by a standard multi-layer perceptron (MLP). Each step is explained in full detail below, because understanding this loop is the key to understanding how CNNs learn.

### Step 1: initialization

The network starts with algorithmically generated, very small random numbers inside its kernel matrices. This is not arbitrary — the initialization strategy matters enormously for training stability and convergence speed. Two common techniques dominate modern practice:

- **Xavier (Glorot) Initialization:** Draws weights from a distribution with variance $\frac{2}{n_{in} + n_{out}}$, where $n_{in}$ is the number of input units and $n_{out}$ is the number of output units. This keeps the variance of activations roughly constant across layers, preventing early layers from producing values that are either vanishingly small or explosively large.
- **Kaiming (He) Initialization:** Draws weights from a distribution with variance $\frac{2}{n_{in}}$. This variant is specifically designed for networks using ReLU activations, which zero out half the values and thus require a compensating factor of 2 in the variance to maintain signal magnitude through the network.

At this point, the filter does absolutely nothing useful. The random numbers bear no resemblance to an edge detector, a texture extractor, or any other meaningful feature. The output they produce when convolved with an input image is essentially structured noise.

### Step 2: the forward pass

These randomly initialized filters slide over the raw input image according to the convolution operation. Because the numbers are random, the initial output feature maps are essentially mathematical noise — there is no meaningful spatial structure in the activations. This noise passes all the way through the network's subsequent layers, through any pooling operations, and ultimately to the classification head (typically a set of fully connected layers followed by a softmax). The classification head inevitably makes a completely random guess — for example, it might predict with 90% confidence that the image is a dog, when the image actually contains a car. This is expected and correct behavior for the first forward pass; the network has not yet learned anything.

### Step 3: loss calculation

The network uses an objective **loss function** to measure exactly the magnitude and direction of how incorrect its final prediction was. For classification tasks, the standard choice is **cross-entropy loss** (also called log loss), which is defined as:

$$\mathcal{L} = -\sum_{c=1}^{C} y_c \log(\hat{y}_c)$$

where $C$ is the number of classes, $y_c$ is the true label (1 for the correct class, 0 for all others), and $\hat{y}_c$ is the predicted probability for class $c$. Cross-entropy loss is zero when the prediction is perfect and increases without bound as the prediction gets worse. This scalar value — a single number quantifying the total error — is the compass that guides all subsequent learning.

### Step 4: backpropagation

Using the **chain rule of calculus**, the gradient of the loss is calculated backwards through every layer of the network. This is the most computationally intensive and mathematically sophisticated step. For every single weight in every single filter, the network asks and answers the question: *"If I increase this weight by a tiny fraction $\epsilon$, does my overall classification error go up or down, and by exactly how much?"*

Mathematically, for a filter weight $w_{i,j,d}$ (where $i$ and $j$ are spatial positions and $d$ is the depth index), the network computes:

$$\frac{\partial \mathcal{L}}{\partial w_{i,j,d}}$$

This partial derivative tells us the slope of the loss surface with respect to that specific weight. A positive gradient means increasing the weight will increase the loss (bad), and a negative gradient means increasing the weight will decrease the loss (good). The chain rule allows this gradient to be computed efficiently by propagating error signals backward from the loss, through each layer's activation function, all the way to the individual filter weights.

> [!tip] Why backpropagation is revolutionary
> Without the chain rule, computing the gradient for each weight would require a separate perturbation experiment for every single parameter — an astronomically expensive process. The chain rule allows all gradients to be computed in a single backward pass, making training deep networks with millions of parameters computationally feasible.

### Step 5: gradient descent optimization

The optimizer takes these gradients and slightly adjusts the filter values in the direction that reduces the error. The most fundamental update rule is:

$$W_{new} = W_{old} - \eta \cdot \frac{\partial \mathcal{L}}{\partial W}$$

where $\eta$ is the **learning rate** — a hyperparameter that controls the step size of each update. Set it too large and the updates overshoot minima, causing the loss to oscillate or diverge. Set it too small and training takes impractically long to converge.

Two dominant optimizer families are used in practice:

- **Stochastic Gradient Descent (SGD):** The simplest optimizer. It updates weights using the gradient computed from a single mini-batch, with an optional momentum term that accumulates a velocity vector to smooth out oscillations and accelerate convergence along consistent gradient directions. SGD with momentum is still widely used in production training of large vision models.
- **Adam (Adaptive Moment Estimation):** Maintains per-parameter adaptive learning rates by computing running averages of both the gradients (first moment) and the squared gradients (second moment). Adam converges faster than SGD on many problems and requires less manual learning rate tuning, though the final converged solution may sometimes be slightly worse than well-tuned SGD with momentum.

## The training loop visualized

The entire lifecycle forms a closed loop that iterates until convergence:

```mermaid
graph TD
    A["Step 1: Random Initialization<br/>Filters contain small random numbers"] --> B["Step 2: Forward Pass<br/>Filters slide over image → noisy output"]
    B --> C["Step 3: Loss Calculation<br/>Cross-Entropy measures prediction error"]
    C --> D["Step 4: Backpropagation<br/>Chain Rule computes ∂L/∂w for every weight"]
    D --> E["Step 5: Gradient Descent<br/>Optimizer updates: w = w - η·∂L/∂w"]
    E --> F{"Converged?"}
    F -->|"No"| B
    F -->|"Yes"| G["Trained Filters<br/>Random numbers → specialized feature extractors"]
```

By iterating this loop millions of times over a large dataset, those completely random initial numbers morph precisely into highly specialized feature extractors. The network mathematically proves to itself that having a specific arrangement of numbers (like an edge detector) minimizes its loss. No human ever explicitly programmed the network to detect edges — the optimization process discovered that edge-like filters are useful for reducing classification error, and it converged on those filter values automatically.

> [!warning] A common misconception
> Beginners sometimes assume that the network learns a Sobel filter or a Gabor filter. In reality, the learned filters often resemble these classical filters in early layers (because edges and gradients are universally useful for visual tasks), but they are not identical to them. The network learns *task-specific* features that are optimal for minimizing its particular loss function on its particular dataset. Later layers learn features that have no classical analogue — abstract patterns that combine lower-level features in ways that are meaningful only to the network.

## CNNs rediscover the classical filters

When you train a CNN on natural images (ImageNet) and visualize the first-layer filters, you find that they look like **classical filters**:

- Some filters look like **Sobel operators** (oriented edge detectors) — they compute differences in one direction, detecting edges.
- Some filters look like **Gabor filters** (Gaussian-windowed sinusoids) — they detect oriented bars and gratings at specific frequencies.
- Some filters look like **Laplacian operators** (center-surround) — they detect blobs and spots.
- Some filters look like **Gaussian smoothing** — they low-pass filter the image.

This is not a coincidence. The classical filters were designed to capture the **statistics of natural images** — edges, orientations, textures — and those are exactly the features that a CNN learns to extract when trained on natural images. The CNN *discovers* the classical filters from data.

This is one of the most beautiful results in deep learning: **decades of human-designed filter engineering (Sobel 1968, Gabor 1946, Canny 1986) are rediscovered automatically by a CNN trained on natural images.** The classical filters were correct — they were the right features for natural images. The CNN just learns them from data rather than from human insight. It is also the strongest evidence that the two traditions are one: the hand-crafted kernels of classical image processing and the first layer of a CNN are the same machinery, differing only in how the coefficients are chosen.

## The dimension of depth (channels)

In standard 2D image filtering, you typically deal with grayscale images — flat $X \times Y$ grids. In CNNs, data exists in **volumes**. An RGB image is not just an $X \times Y$ grid; it is $X \times Y \times 3$ (Height $\times$ Width $\times$ Channels). Therefore, a filter in a CNN must also be 3-dimensional. If you use a $3 \times 3$ filter on an RGB image, the actual filter size is $3 \times 3 \times 3$. It slides across the height and width dimensions, but it always extends through the *full depth* of the input volume. This critical concept is explored in full detail in [[Processing 3D Volumes, Depth Summation, and Biases]], and the tensor perspective on volumes, depths, and data formats is laid out in [[Demystifying Tensors - Volumes, Depth, and Data Formats]].

## Multiple filters produce multiple output channels

If one 3D filter produces a single 2D output feature map, what happens when we use 32 different filters? We stack their 2D output maps on top of each other along a new channel dimension. The new output becomes a volume with a depth of 32. This volume then becomes the input for the next layer, where each filter will now have a depth of 32 to match. This cascading process is what gives deep CNNs their representational power — each layer builds increasingly abstract feature representations by combining the outputs of the previous layer's filters.

```mermaid
graph TD
    A["Input Image: 64×64×3"] -->|"Apply 32 Filters<br/>each of size 3×3×3"| B["Output Feature Map: 62×62×32"]
    B -->|"Apply 64 Filters<br/>each of size 3×3×32"| C["Output Feature Map: 60×60×64"]
    C -->|"Apply 128 Filters<br/>each of size 3×3×64"| D["Output Feature Map: 58×58×128"]
```

> [!tip] Common student trap
> Students often confuse the number of channels in the input image with the number of filters. These are two completely independent quantities. Remember:
> - The **depth of each filter** must mathematically match the **depth of the input volume** (this is a hard constraint — the element-wise multiplication requires matching dimensions).
> - The **number of filters** you choose is a free design decision, and it dictates the **depth of the output volume**.
> - These two numbers are only related in that the *next* layer's filter depth will equal the *current* layer's number of filters (because the current output becomes the next input).

## The unsharp masking and ResNet connection

A deeper connection: classical **unsharp masking** and the **ResNet residual block** are the same idea, applied in different contexts.

### Unsharp masking (classical)

$$\text{output} = \text{input} + \lambda \cdot (\text{input} - \text{blur}(\text{input}))$$

The image is sharpened by adding a fraction of the **high-frequency detail** (the difference between the image and its blurred version). The blur removes detail; subtracting it from the original extracts the detail; adding the detail back sharpens.

### The ResNet residual block

$$\text{output} = \text{input} + F(\text{input})$$

where $F$ is a learned function (two conv layers + ReLU). The block learns the **residual** — the difference between the desired output and the input — rather than the full transformation.

### The connection

Both compute **output = input + correction**, where the correction is a function of the input. Unsharp masking uses a fixed correction (high-pass filter); ResNet learns the correction. The ResNet block is a **learned generalization of unsharp masking** — and this is why ResNet's residual connections work: they make it easy for the network to learn the identity (correction = 0) when no transformation is needed, just as unsharp masking with $\lambda = 0$ is the identity. The additive-correction idea is the same one that leads to the remark that "LSTMs anticipated ResNets by 20 years" — the idea appears in classical image processing (unsharp masking) before it appears in deep learning (LSTMs, ResNets); see [[06 - Computer Vision/Architecture and Connectivity/The Degradation Problem and Residual Connections|The Degradation Problem and Residual Connections]].

## The convolution theorem connection

Classical image processing uses the **convolution theorem**: convolution in the spatial domain is multiplication in the frequency domain. This lets you design filters in the frequency domain (where it is easier to specify "remove high frequencies") and transform them to the spatial domain — the toolkit developed in [[Introduction to the Frequency Domain]] and [[Frequency Domain Filtering]].

CNNs do not use the convolution theorem explicitly — they perform spatial-domain convolution directly. But the underlying operation is the same, and the frequency-domain perspective is still useful for understanding what a CNN filter does:

- A filter with small kernel size is a **low-order** frequency selector — it captures local patterns.
- A filter with large kernel size captures lower frequencies (broader patterns).
- Stacking layers (deeper network) lets the model compose frequency-domain operations, building complex filters from simple ones.

The classical frequency-domain toolkit (Fourier transform, frequency filtering) and the CNN's learned spatial filters are two views of the same underlying mathematics.

## When to use classical and when to use learned

The classical-to-deep bridge is not just theoretical — it has practical consequences for when to use classical image processing versus CNNs.

### Use classical image processing when

The classical toolkit remains the right tool whenever the task is well-defined, data is scarce, or determinism matters. Concretely:

- **You have no training data.** A Sobel filter works without any data; a CNN needs thousands of labeled examples.
- **The task is simple and well-defined.** Edge detection, noise removal, geometric transforms — these are solved problems with optimal classical algorithms.
- **You need exact, reproducible results.** Classical filters are deterministic and have no learned parameters. A CNN's output depends on its training, which may vary.
- **You need interpretability.** A Sobel filter computes a specific, understandable quantity (horizontal gradient). A CNN filter's exact computation is opaque.
- **Compute is constrained.** Classical filters are fast and cheap; CNNs are expensive.

### Use CNNs when

The learned approach wins wherever semantics and data are present:

- **The task requires semantic understanding.** "Find cats" is not a classical filter — it requires learned features.
- **You have training data.** The CNN will learn better features than you could design by hand.
- **The task is end-to-end.** If you are already training a model, let it learn the low-level features rather than fixing them with classical filters.
- **You need to handle variability.** Classical filters are rigid; CNNs adapt to the data's statistics.

### Hybrid approaches

In practice, many computer vision pipelines combine classical and learned components:

- **Preprocessing:** classical filters (Gaussian blur, normalization) before a CNN.
- **Postprocessing:** classical morphology (NMS, connected components) after a CNN.
- **Feature extraction:** classical features (SIFT, ORB) for matching, combined with CNN features for recognition.
- **Data augmentation:** classical transforms (rotation, color jitter) to augment CNN training data.

The classical and deep worlds are not opposed — they are complementary, and the best systems use both.

## Key takeaways

The classical-to-deep transition compresses into five statements, each developed in full above. Together they explain why deep learning displaced hand-crafted pipelines without invalidating the mathematics underneath them.

1. **Classical filters and CNN filters are the same operation** (convolution) — they differ only in how the kernel is determined (designed vs. learned).
2. **CNNs discover classical filters** when trained on natural images: first-layer filters look like Sobel, Gabor, Laplacian, Gaussian filters. Decades of filter engineering are rediscovered automatically.
3. **Unsharp masking and ResNet:** both compute `output = input + correction`; unsharp uses a fixed correction, ResNet learns it. ResNet is a learned generalization of unsharp masking.
4. **The convolution theorem** connects classical frequency-domain filtering to CNN spatial filtering — two views of the same mathematics.
5. **Practical guidance:** use classical image processing for simple, well-defined, no-data tasks; use CNNs for semantic, end-to-end, data-rich tasks. The best systems combine both.

## See also

- [[CNN Course Overview]]
- [[Image Processing Global Index]]
- [[06 - Computer Vision/CNN Foundations and Philosophy/Introduction and Foundations of CNNs|Introduction and Foundations of CNNs]]
- [[06 - Computer Vision/CNN Foundations and Philosophy/Core Architecture and Philosophy|Core Architecture and Philosophy]]
- [[Processing 3D Volumes, Depth Summation, and Biases]]
- [[Demystifying Tensors - Volumes, Depth, and Data Formats]]
- [[Foundations and Philosophy Summary]]
- [[The Convolution Operation]]
- [[The Mechanics of Spatial Filtering]]
- [[Sharpening and Edge Detection]]
- [[Gabor Filters]]
- [[The Hough Transform]]
- [[Feature Descriptors - SIFT, SURF, ORB, HOG]]
- [[Introduction to the Frequency Domain]]
- [[Frequency Domain Filtering]]
- [[The Fourier Transform]]
- [[Connected Components and Region Properties]]
- [[06 - Computer Vision/Architecture and Connectivity/The Degradation Problem and Residual Connections|The Degradation Problem and Residual Connections]]
- [[Hierarchical Feature Extraction]]
- [[Local Connectivity and Parameter Sharing]]
- [[Deep Learning for Imaging]]
- [[06 - Computer Vision/Training and Transfer Learning/Transfer Learning and Fine-Tuning|Transfer Learning and Fine-Tuning]]
