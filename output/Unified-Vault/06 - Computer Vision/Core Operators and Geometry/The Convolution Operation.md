---
title: The Convolution Operation
type: concept
aliases:
  - Convolution Operation
  - Image Convolution
  - Convolution Deep Dive
  - CNN Convolution
  - In-Depth Image Convolution
tags:
  - cnn
  - convolution
  - filter
  - kernel
  - feature-map
  - sliding-dot-product
  - weight-sharing
  - translation-equivariance
  - stride
  - padding
  - output-dimensions
  - cross-correlation
  - separable-kernel
  - bias
sources:
  - "01. The Convolution Operation Deep Dive"
  - "01. Convolution"
created_index: 25
---

Convolution is the operation at the heart of every convolutional neural network: a small matrix of weights slides across an input, computing a weighted sum at every position and thereby producing a map of where a particular local pattern appears. This note develops the operation from the ground up — the precise vocabulary of filters, kernels, and feature maps; the sliding dot-product mathematics with a fully worked numerical example; the weight-sharing principle and its consequences for translation equivariance and parameter counts; and the spatial geometry controlled by stride and padding, culminating in the output-dimension formula. It then extends the operation to multi-channel inputs, draws the careful distinction between true convolution and the cross-correlation that frameworks actually implement, and closes with the bias term and its relationship to normalization. The note anchors the [[CNN Course Overview]] alongside the other Core Operators and Geometry notes, especially [[Strides - Skipping Pixels and Downsampling]], [[Padding - Mathematics, Edge Effects, and Valid vs Same]], and [[The Output Spatial Dimension Formula]].

## Filters, kernels, and feature maps

Before we can understand the mathematics of convolution, we must establish precise definitions for the key terms that are used throughout the CNN literature. These terms are sometimes used interchangeably or inconsistently across different textbooks and frameworks, so it is essential to pin down their exact meanings.

### Filter (kernel)

A **filter** (also called a **kernel**) is a small matrix of learnable weights that is used to extract a specific type of feature from the input. The terms "filter" and "kernel" are used interchangeably in most deep learning contexts, though in signal processing they have slightly different connotations. A filter is typically square (e.g., 3×3, 5×5, 7×7) and has a depth that matches the number of channels in the input it is applied to. For example, a filter applied to an RGB image with 3 color channels would have dimensions 3×3×3 (width × height × depth).

Each filter learns to detect one specific type of local pattern in the input. During the forward pass, the filter slides across the entire input, computing a dot product at each position. The values in the filter determine what pattern it detects. For instance, consider the following 3×3 filter:

$$\mathbf{K} = \begin{pmatrix} -1 & 0 & 1 \\ -1 & 0 & 1 \\ -1 & 0 & 1 \end{pmatrix}$$

This is a vertical edge detection filter. When this filter is convolved with an image, it produces high positive values where there is a vertical transition from dark (left) to bright (right), and high negative values where there is a transition from bright (left) to dark (right). Regions with no vertical transition produce values near zero. The specific values $(-1, 0, 1)$ were hand-crafted in classical image processing, but in a CNN, the filter values are learned from data during training — the network discovers for itself what patterns are useful, which is the step from fixed kernels to learned ones explored in [[From Basic Convolution to Learned Weights]].

> [!note] Filter vs. Kernel: A Subtle Distinction
> In some deep learning frameworks and texts, "kernel" refers to the 2D weight matrix (e.g., 3×3), while "filter" refers to the full 3D weight tensor (e.g., 3×3×3 for an RGB input). Under this convention, a filter contains one kernel per input channel, and the outputs of all kernels are summed to produce a single output value. However, in practice, most practitioners use the terms interchangeably to refer to the entire weight tensor.

### Kernel properties in classical image processing

In the classical image-processing tradition, the kernel (also called a **mask**) is the small matrix of weights that defines the effect of the convolution, and its values and size determine the outcome of the filtering operation. Three properties of kernels matter there and carry over to an understanding of CNN filters.

**Size:** Kernels typically have odd dimensions (e.g., 3×3, 5×5, 7×7). This ensures that the kernel has a clear center, which aligns with the current pixel being processed in the input image — the same reason CNNs almost exclusively use odd filter sizes, as discussed below in the context of "same" padding.

**Symmetry:** Many common kernels are symmetric, meaning the weights are balanced around the center.

**Sum of elements:** The sum of the kernel's elements often has significance. For example, in blurring filters, the elements typically sum to 1 to preserve the overall brightness of the image.

This sliding-window mechanism allows the kernel to systematically modify the image based on local pixel information, making it the primary method for tasks like blurring, sharpening, edge detection, and noise reduction — the classical applications catalogued in [[The Mechanics of Spatial Filtering]].

### Feature map (activation map)

A **feature map** (also called an **activation map**) is the output produced by applying a single filter to the entire input. It is a 2D array where each element represents the strength of the filter's response at that spatial location. If a vertical edge filter is applied to an image, the resulting feature map will have high values at locations where vertical edges are present in the image and low values elsewhere. In this sense, the feature map "maps out" where a particular feature is present in the input.

When we apply $K$ different filters to the same input, we produce $K$ feature maps, which are stacked along the channel dimension to form a 3D output tensor. This 3D output then becomes the input to the next layer, where a new set of filters (now with depth matching $K$) will extract higher-level features from it — the stacking that underpins [[Hierarchical Feature Extraction]].

> [!tip] Physical Interpretation of Feature Maps
> Think of a feature map as a "heat map" that highlights where a specific pattern appears in the input. Bright regions (high values) indicate strong detection of the pattern, while dark regions (low values) indicate absence. Visualizing feature maps is one of the most powerful techniques for understanding what a CNN has learned — you can literally see which parts of the image activate each filter.

## The mathematics of convolution

Convolution in the context of CNNs is best understood as a **sliding dot product**. The filter is placed at every possible position on the input, and at each position, the element-wise product of the filter weights and the corresponding input patch is computed, then all these products are summed to produce a single output value. This operation is repeated for every spatial position, producing the complete feature map.

The same idea is stated in the classical image-processing notation as follows: each output pixel's value is calculated as a weighted sum of the corresponding input pixel and its neighbors. The convolution operation is denoted by the $\otimes$ symbol, and for an input image $f(x,y)$ and a filter $h(x,y)$, the resulting image $g(x,y)$ is:

$$g(x,y) = f(x,y) \otimes h(x,y)$$

In discrete terms, this is calculated using a double summation. For a pixel at $(x,y)$, the value is computed as:

$$g(x, y) = \sum \sum f(x + i, y + j) \cdot h(i, j)$$

where $i$ and $j$ are the indices iterating over the dimensions of the kernel $h$. Expressed as an explicit procedure, the computation proceeds in six steps:

1. **Select an output pixel:** choose a coordinate $(x,y)$ in the output image to calculate.
2. **Center the kernel:** place the center of the kernel over the corresponding coordinate $(x,y)$ in the input image.
3. **Element-wise multiplication:** multiply each element of the kernel by the value of the underlying pixel in the input image.
4. **Summation:** sum all the products from the previous step.
5. **Assign value:** the resulting sum is the new value for the output pixel at $(x,y)$.
6. **Repeat:** repeat this process for every pixel in the image.

### Step-by-step with a full numerical example

Let us work through a complete example. Consider a 5×5 input matrix $\mathbf{I}$ and a 3×3 filter $\mathbf{K}$:

**Input** ($\mathbf{I}$, size 5×5):

$$\mathbf{I} = \begin{pmatrix} 1 & 2 & 0 & 1 & 3 \\ 0 & 1 & 2 & 3 & 1 \\ 1 & 3 & 1 & 0 & 2 \\ 2 & 0 & 2 & 1 & 0 \\ 1 & 2 & 3 & 1 & 1 \end{pmatrix}$$

**Filter** ($\mathbf{K}$, size 3×3):

$$\mathbf{K} = \begin{pmatrix} 1 & 0 & -1 \\ 1 & 0 & -1 \\ 1 & 0 & -1 \end{pmatrix}$$

This is a vertical edge detection filter. We will use stride $S = 1$ and no padding ($P = 0$).

**Step 1: Position (0,0).** Place the filter at the top-left corner, aligned with the input patch covering rows 0–2 and columns 0–2:

$$\text{Patch} = \begin{pmatrix} 1 & 2 & 0 \\ 0 & 1 & 2 \\ 1 & 3 & 1 \end{pmatrix}$$

Compute the element-wise product and sum:

$$\text{Output}[0,0] = (1)(1) + (2)(0) + (0)(-1) + (0)(1) + (1)(0) + (2)(-1) + (1)(1) + (3)(0) + (1)(-1)$$
$$= 1 + 0 + 0 + 0 + 0 - 2 + 1 + 0 - 1 = -1$$

**Step 2: Position (0,1).** Slide the filter one column to the right (stride = 1), covering rows 0–2 and columns 1–3:

$$\text{Patch} = \begin{pmatrix} 2 & 0 & 1 \\ 1 & 2 & 3 \\ 3 & 1 & 0 \end{pmatrix}$$

$$\text{Output}[0,1] = (2)(1) + (0)(0) + (1)(-1) + (1)(1) + (2)(0) + (3)(-1) + (3)(1) + (1)(0) + (0)(-1)$$
$$= 2 + 0 - 1 + 1 + 0 - 3 + 3 + 0 + 0 = 2$$

**Step 3: Position (0,2).** Slide right again, covering rows 0–2 and columns 2–4:

$$\text{Patch} = \begin{pmatrix} 0 & 1 & 3 \\ 2 & 3 & 1 \\ 1 & 0 & 2 \end{pmatrix}$$

$$\text{Output}[0,2] = (0)(1) + (1)(0) + (3)(-1) + (2)(1) + (3)(0) + (1)(-1) + (1)(1) + (0)(0) + (2)(-1)$$
$$= 0 + 0 - 3 + 2 + 0 - 1 + 1 + 0 - 2 = -3$$

Continuing this process for all positions, we obtain the complete output feature map:

$$\text{Output} = \begin{pmatrix} -1 & 2 & -3 \\ 2 & -2 & -1 \\ 2 & 4 & 0 \end{pmatrix}$$

The output size is $3 \times 3$, which we can verify using the formula $O = \lfloor\frac{5-3+2 \times 0}{1}\rfloor + 1 = 3$. Notice that the value 4 at position (2,1) indicates a strong vertical edge at that location in the input — this is exactly what the vertical edge filter is designed to detect.

The entire computation is short enough to implement from scratch, which makes the sliding-window mechanism concrete:

```python
import numpy as np

# Define the 5x5 input matrix
input_matrix = np.array([
    [1, 2, 0, 1, 3],
    [0, 1, 2, 3, 1],
    [1, 3, 1, 0, 2],
    [2, 0, 2, 1, 0],
    [1, 2, 3, 1, 1]
])

# Define the 3x3 vertical edge detection filter
kernel = np.array([
    [1,  0, -1],
    [1,  0, -1],
    [1,  0, -1]
])

# Get dimensions
input_h, input_w = input_matrix.shape  # 5, 5
kernel_h, kernel_w = kernel.shape       # 3, 3
stride = 1

# Calculate output dimensions using the golden formula
output_h = (input_h - kernel_h) // stride + 1  # (5-3)//1 + 1 = 3
output_w = (input_w - kernel_w) // stride + 1  # (5-3)//1 + 1 = 3

# Initialize the output feature map with zeros
output = np.zeros((output_h, output_w))

# Perform the convolution by sliding the kernel across the input
for i in range(output_h):           # Iterate over output rows
    for j in range(output_w):       # Iterate over output columns
        # Extract the input patch corresponding to this output position
        # The patch starts at (i*stride, j*stride) and has size (kernel_h, kernel_w)
        patch = input_matrix[i*stride:i*stride+kernel_h, 
                             j*stride:j*stride+kernel_w]
        # Compute the dot product (element-wise multiply and sum)
        output[i, j] = np.sum(patch * kernel)

print("Output feature map:")
print(output)
# Expected output:
# [[-1.  2. -3.]
#  [ 2. -2. -1.]
#  [ 2.  4.  0.]]
```

## Weight sharing, translation equivariance, and parameter savings

### What weight sharing means

Weight sharing is the principle that the same filter (the same set of weights) is applied at every spatial position of the input. Instead of learning a different set of weights for every possible position of a feature, we learn one set of weights and apply it everywhere. This is a direct consequence of the assumption that a feature (like an edge) looks the same regardless of where it appears in the image — a vertical edge in the top-left corner has the same visual structure as a vertical edge in the bottom-right corner. The architectural consequences of this principle are developed in [[Local Connectivity and Parameter Sharing]].

### Why it works: translation equivariance

Weight sharing gives CNNs the property of **translation equivariance**. Formally, if we denote the convolution operation as $\ast$ and a spatial translation as $T$, then:

$$T(\mathbf{I}) \ast \mathbf{K} = T(\mathbf{I} \ast \mathbf{K})$$

This means that if we shift the input image, the output feature map shifts correspondingly. If a vertical edge appears at position $(5, 10)$ in the input, the vertical edge filter will produce a high value at the corresponding position in the feature map. If we shift the input so the edge now appears at position $(15, 20)$, the high value in the feature map shifts to the corresponding new position. The feature detection is equivariant to translation — the detection moves with the feature.

This is in contrast to translation *invariance*, where the output would be exactly the same regardless of where the feature appears. Translation invariance is provided by pooling layers, not by convolution itself. The distinction is important: convolution tells you *what* features are present and *where* they are (equivariance), while pooling tells you only *what* features are present, discarding precise positional information (invariance) — see [[06 - Computer Vision/Core Operators and Geometry/Activation and Pooling Layers|Activation and Pooling Layers]].

### The parameter savings calculation

To appreciate the magnitude of parameter savings from weight sharing, let us compare a convolutional layer and a fully connected layer that process the same input.

**Convolutional layer**: Input size 224×224×3, 64 filters of size 3×3×3.
- Parameters per filter: $3 \times 3 \times 3 = 27$ weights + 1 bias = 28
- Total parameters: $64 \times 28 = 1{,}792$

**Fully connected layer**: Input size 224×224×3 = 150,528, output size 64.
- Parameters: $150{,}528 \times 64$ weights + 64 biases = $9{,}633{,}856$

The convolutional layer uses **5,373 times fewer parameters** than the equivalent fully connected layer. This enormous reduction is possible precisely because the 28 parameters of each filter are shared across all $222 \times 222 = 49{,}284$ spatial positions (the output feature map size with stride 1, no padding). In the fully connected layer, each of the 64 output neurons has its own independent set of 150,528 weights, none of which are shared.

> [!info] Weight Sharing Is an Inductive Bias
> Weight sharing encodes our prior belief that features are translation-equivariant — that the same pattern is meaningful regardless of where it appears. This is an inductive bias: it restricts the hypothesis space of the model to functions that are translation-equivariant, which is appropriate for images but might not be appropriate for other types of data. If the data does not satisfy this assumption (e.g., if features at different positions have fundamentally different meanings), weight sharing could actually hurt performance.

## Stride

The **stride** of a convolution is the number of pixels by which the filter is shifted between successive positions. A stride of $S = 1$ means the filter moves one pixel at a time (the default), producing an output feature map that is nearly the same size as the input (slightly smaller due to border effects). A stride of $S = 2$ means the filter moves two pixels at a time, skipping every other position, and producing an output feature map that is approximately half the size of the input.

With stride 1, the filter is placed at every possible position in the input, moving one pixel at a time horizontally, then shifting down one row and repeating. This produces the maximum possible output resolution — every local patch of the input contributes to the output. The output size for a 1D input of length $W$ with filter size $F$ and padding $P$ is $O = W - F + 2P + 1$. For a 2D input, the same formula applies to both height and width independently.

With stride 2, the filter is placed at every other position. Visually, if stride 1 visits positions 0, 1, 2, 3, 4, ..., stride 2 visits positions 0, 2, 4, 6, .... This skips half the positions, producing an output that is approximately half the spatial size of the input. The output size formula becomes $O = \lfloor\frac{W - F + 2P}{2}\rfloor + 1$.

Using stride > 1 serves two purposes. First, it reduces the spatial dimensions of the feature maps, which decreases memory usage and computational cost for subsequent layers. Second, it increases the receptive field of neurons in subsequent layers relative to the original input, because each position in the strided output covers a larger area of the input. This is an alternative to pooling for downsampling, and in fact, some modern architectures (like ResNet) use strided convolutions instead of pooling layers to reduce spatial resolution.

The general formula for the output size given stride $S$ is:

$$O = \left\lfloor \frac{W - F + 2P}{S} \right\rfloor + 1$$

where $W$ is the input size, $F$ is the filter size, $P$ is the padding, and $S$ is the stride. As $S$ increases, the output size decreases. For example, with $W = 224$, $F = 3$, $P = 1$:
- Stride 1: $O = \lfloor\frac{224 - 3 + 2}{1}\rfloor + 1 = 224$
- Stride 2: $O = \lfloor\frac{224 - 3 + 2}{2}\rfloor + 1 = 112$

Stride is treated in its own right in [[Strides - Skipping Pixels and Downsampling]].

## Padding and edge effects

### The shrinking problem

Without padding, every convolution operation reduces the spatial dimensions of the feature map. A 3×3 filter applied to a 224×224 input produces a 222×222 output; applied again, it produces 220×220, and so on. After many layers, the feature maps shrink to a tiny size, which has two serious problems:

1. **Edge effects**: Pixels near the border of the input are used by fewer filter positions than pixels in the center. A corner pixel appears in only one 3×3 patch, while a center pixel appears in nine patches. This means the network has less information about features near the edges, leading to a systematic bias toward the center of the image.
2. **Information loss**: Each convolution that reduces the spatial dimensions discards information about the boundary. For very deep networks, this shrinking can eliminate a significant portion of the input, making it impossible for the network to process the image effectively.

### Zero-padding

The most common solution is **zero-padding**, which involves adding rows and columns of zeros around the border of the input before applying the convolution. If we add $P$ rows/columns of zeros on each side, the effective input size becomes $W + 2P$. The output size formula becomes:

$$O = W - F + 2P + 1 \quad \text{(for stride 1)}$$

By choosing the right padding, we can control the output size precisely.

### "Same" padding and its formula

**"Same" padding** means choosing $P$ such that the output has the same spatial dimensions as the input (when stride = 1). Setting $O = W$ in the formula:

$$W = W - F + 2P + 1$$
$$2P = F - 1$$
$$P = \frac{F - 1}{2}$$

For a 3×3 filter: $P = \frac{3-1}{2} = 1$ — we need 1 pixel of padding on each side. For a 5×5 filter: $P = \frac{5-1}{2} = 2$ — we need 2 pixels of padding. For a 7×7 filter: $P = 3$.

Note that this formula only guarantees same-sized output when stride = 1. With stride > 1, "same" padding produces output size $\lceil W / S \rceil$, which is smaller than the input.

> [!warning] "Same" Padding with Odd Filter Sizes
> The formula $P = (F-1)/2$ only gives an integer result when $F$ is odd. This is why you almost always see odd-sized filters (3×3, 5×5, 7×7) in CNNs — they allow symmetric padding that preserves spatial dimensions exactly. Even-sized filters (2×2, 4×4) require asymmetric padding, which is possible but less clean. The 3×3 filter has become the de facto standard because it is the smallest odd-sized filter that can capture spatial relationships in both dimensions.

### Border strategies in classical image processing

When the kernel is positioned over pixels at the edge of the image, part of the kernel will extend beyond the image boundary, and classical image processing has several common strategies for handling this. The first is to **not filter the borders (cropping)**: the simplest method is to not calculate new values for the border pixels, so the output image will be slightly smaller than the input — exactly the "valid" behavior of an unpadded CNN convolution. The second is **padding with zeros**: the input image is extended by adding a border of black pixels (value 0), which allows the kernel to operate on all original pixels but can introduce a dark edge artifact. The third is **mirror padding (reflection)**: the border is extended by reflecting the pixel values from within the image. This is often a more effective method as it maintains a more natural transition at the edges and reduces artifacts. The full arithmetic of these choices, including the TensorFlow and PyTorch conventions for "valid" and "same", is developed in [[Padding - Mathematics, Edge Effects, and Valid vs Same]].

## The golden formula for output dimensions

The most important formula in convolutional neural networks relates the input dimensions, filter size, stride, and padding to the output dimensions. It applies to both the height and width of the output independently:

$$\boxed{O = \left\lfloor \frac{W - F + 2P}{S} \right\rfloor + 1}$$

where:
- $O$ = output spatial dimension (height or width)
- $W$ = input spatial dimension
- $F$ = filter (kernel) size
- $P$ = padding (number of zero-padded rows/columns added to each side)
- $S$ = stride (step size of the sliding window)
- $\lfloor \cdot \rfloor$ = floor function (round down to nearest integer)

### Derivation of the formula

To derive this formula, consider the convolution operation as a sliding window. The filter starts at the leftmost position and slides to the right by $S$ pixels each step. At each position, the filter covers $F$ pixels. The question is: how many positions can the filter visit before it falls off the right edge of the (padded) input?

The padded input has width $W + 2P$. The rightmost position the filter can occupy is where its right edge aligns with the right edge of the padded input, i.e., the filter's left edge is at position $W + 2P - F$. Starting from position 0, the positions visited are $0, S, 2S, 3S, \ldots$ up to the last position that does not exceed $W + 2P - F$. The number of valid positions is:

$$\text{Number of steps} = \left\lfloor \frac{W + 2P - F}{S} \right\rfloor$$

Since we count both the starting position (0) and the position after each step, the total number of positions (which equals the output size) is:

$$O = \left\lfloor \frac{W + 2P - F}{S} \right\rfloor + 1 = \left\lfloor \frac{W - F + 2P}{S} \right\rfloor + 1$$

The floor function accounts for the fact that if the filter cannot fit in the remaining input after the last complete step, that partial overlap is simply discarded (this is the "valid" convolution convention).

### Worked example 1: standard convolution

Input: $W = 32$, Filter: $F = 5$, Padding: $P = 0$, Stride: $S = 1$

$$O = \left\lfloor \frac{32 - 5 + 0}{1} \right\rfloor + 1 = 27 + 1 = 28$$

Output size: 28×28. The feature map shrinks by 4 pixels in each dimension.

### Worked example 2: same padding

Input: $W = 32$, Filter: $F = 5$, Padding: $P = 2$, Stride: $S = 1$

$$O = \left\lfloor \frac{32 - 5 + 4}{1} \right\rfloor + 1 = 31 + 1 = 32$$

Output size: 32×32. With $P = (F-1)/2 = 2$ pixels of padding on each side, the output is the same size as the input.

### Worked example 3: strided convolution with padding

Input: $W = 224$, Filter: $F = 3$, Padding: $P = 1$, Stride: $S = 2$

$$O = \left\lfloor \frac{224 - 3 + 2}{2} \right\rfloor + 1 = \left\lfloor \frac{223}{2} \right\rfloor + 1 = 111 + 1 = 112$$

Output size: 112×112. The spatial dimensions are halved compared to the input. This is a common configuration in modern architectures (like ResNet) where strided convolutions replace pooling layers for downsampling.

The formula is easy to wrap in a helper function, with floor division doing the work of the floor operator:

```python
# Function to compute output dimensions
def conv_output_size(W, F, P=0, S=1):
    """
    Compute the output dimension of a convolution operation.

    Parameters:
        W: input spatial dimension (int)
        F: filter/kernel size (int)
        P: padding on each side (int), default 0
        S: stride (int), default 1

    Returns:
        Output spatial dimension (int)
    """
    return (W - F + 2 * P) // S + 1  # Floor division handles the  operator

# Example 1: Standard convolution
print(f"Example 1: {conv_output_size(W=32, F=5, P=0, S=1)}")  # Output: 28

# Example 2: Same padding
print(f"Example 2: {conv_output_size(W=32, F=5, P=2, S=1)}")  # Output: 32

# Example 3: Strided convolution with padding
print(f"Example 3: {conv_output_size(W=224, F=3, P=1, S=2)}") # Output: 112
```

Edge cases of the formula — fractional results and kernels larger than the input — are examined in detail in [[The Output Spatial Dimension Formula]].

## Convolution in multiple channels

So far, we have considered convolution on single-channel (grayscale) inputs. However, real-world images are typically multi-channel (RGB with 3 channels), and after the first convolutional layer, all feature maps are multi-channel. Understanding how convolution works across channels is essential.

### How a filter with depth works

A filter that operates on a multi-channel input must have the same depth as the input. If the input has $C_{\text{in}}$ channels, each filter is a 3D tensor of size $F \times F \times C_{\text{in}}$. For example, a filter operating on an RGB image (3 channels) with a 3×3 spatial kernel would have dimensions 3×3×3 = 27 weights.

When this 3D filter is applied to the input, it is aligned with a 3×3×3 patch of the input (covering 3×3 spatial pixels across all 3 channels). The dot product is computed over all 27 elements simultaneously, producing a single scalar output value. This means the filter learns to detect a pattern that combines information from all input channels. For instance, in the first layer, a filter might learn to detect red-green color transitions by giving opposite signs to the red and green channel weights. The volume perspective — inputs, filters, and outputs all as 3D tensors with depth summation — is developed fully in [[Processing 3D Volumes, Depth Summation, and Biases]].

### The key rule: output channels equal the number of filters

If we apply $K$ different filters to the same input, each producing one 2D feature map, we obtain $K$ feature maps that are stacked along the channel dimension to form a 3D output tensor of size $O \times O \times K$. The number of output channels $K$ is entirely determined by the number of filters we choose to use — it is a hyperparameter set by the designer. Each filter independently learns to detect a different pattern, so using more filters increases the representational capacity of the layer.

The total number of parameters in a convolutional layer is therefore:

$$\text{Parameters} = K \times (F \times F \times C_{\text{in}} + 1)$$

where the $+1$ accounts for the bias term of each filter. For example, a layer with $C_{\text{in}} = 3$ (RGB), $F = 3$, and $K = 64$ filters has:

$$64 \times (3 \times 3 \times 3 + 1) = 64 \times 28 = 1{,}792 \text{ parameters}$$

In PyTorch, the same layer is created and inspected as follows:

```python
import torch
import torch.nn as nn

# Create a convolutional layer
# nn.Conv2d parameters:
#   - in_channels: number of input channels (3 for RGB)
#   - out_channels: number of filters/output channels (K=64)
#   - kernel_size: spatial size of each filter (3x3)
#   - stride: step size (1)
#   - padding: zero-padding (1 for 'same' output size)
conv_layer = nn.Conv2d(
    in_channels=3,      # Input has 3 channels (RGB)
    out_channels=64,    # Apply 64 filters → 64 output channels
    kernel_size=3,      # Each filter is 3×3
    stride=1,           # Move 1 pixel at a time
    padding=1           # Add 1 pixel of zero-padding on each side
)

# Check the number of parameters
num_params = sum(p.numel() for p in conv_layer.parameters())
print(f"Total parameters: {num_params}")  # Should print 1792

# The weight tensor has shape (64, 3, 3, 3) = (K, C_in, F, F)
# The bias tensor has shape (64,) = (K,)
print(f"Weight shape: {conv_layer.weight.shape}")  # torch.Size([64, 3, 3, 3])
print(f"Bias shape: {conv_layer.bias.shape}")      # torch.Size([64])

# Process a batch of images
input_tensor = torch.randn(1, 3, 224, 224)   # Batch of 1, 3 channels, 224×224
output_tensor = conv_layer(input_tensor)       # Forward pass
print(f"Output shape: {output_tensor.shape}")   # torch.Size([1, 64, 224, 224])
# Output has 64 channels and 224×224 spatial size (same padding preserved size)
```

## Convolution vs. cross-correlation

There is a subtle but important technical distinction between **convolution** and **cross-correlation** that is often glossed over in the deep learning literature. In the signal processing and mathematics communities, convolution is defined with a **flipped** kernel:

$$\text{True convolution: } (I \ast K)[i, j] = \sum_m \sum_n I[i-m, j-n] \cdot K[m, n]$$
$$\text{Cross-correlation: } (I \star K)[i, j] = \sum_m \sum_n I[i+m, j+n] \cdot K[m, n]$$

The difference is the sign of the indices: convolution flips the kernel (both horizontally and vertically), while cross-correlation does not. In signal processing, this flipping matters because it gives convolution the mathematical property of commutativity ($f \ast g = g \ast f$) and associativity, which are important for filtering and system analysis.

However, in deep learning, the kernel weights are **learned from data**. If the optimal kernel for cross-correlation is $\mathbf{K}$, then the optimal kernel for true convolution is simply $\mathbf{K}$ flipped — and since the network learns the kernel values, it will learn the flipped version automatically. Therefore, the distinction is meaningless in practice: cross-correlation with a learned kernel produces exactly the same set of representable functions as true convolution with a learned kernel.

For this reason, every major deep learning framework (PyTorch, TensorFlow, etc.) implements cross-correlation, not true convolution, despite calling it "convolution." This is an accepted convention in the deep learning community, and in everything that follows, when we say "convolution," we mean cross-correlation in the mathematical sense.

> [!note] Why Does This Matter?
> If you are implementing a CNN from scratch and you use true convolution (with kernel flipping), your model will still work correctly — it will simply learn the flipped version of whatever filters it would have learned with cross-correlation. The distinction only matters if you are initializing the network with pre-computed filters (like hand-crafted edge detectors), in which case you need to be consistent about whether the filters are defined for convolution or cross-correlation.

### Algebraic properties of convolution

In its true (kernel-flipped) form, convolution has several mathematical properties that are important in image processing, and they explain why the formal definition is worth keeping even though networks use cross-correlation.

**Commutativity:** $f \otimes h = h \otimes f$ — the order of the image and the filter does not matter. **Associativity:** $(f \otimes h_1) \otimes h_2 = f \otimes (h_1 \otimes h_2)$ — applying two filters sequentially is the same as applying a single filter that is the convolution of the two individual filters. **Distributivity:** $f \otimes (h_1 + h_2) = (f \otimes h_1) + (f \otimes h_2)$ — applying a filter that is the sum of two other filters is the same as applying each filter individually and summing the results.

Finally, **separability**: a 2D kernel $h(x,y)$ is separable if it can be expressed as the product of two 1D vectors, $h(x,y) = h_x(x) \cdot h_y(y)$. This property is extremely valuable for optimization: instead of a single 2D convolution, one can perform two much faster 1D convolutions (one along the rows, one along the columns). This significantly reduces computational complexity, especially for large kernels. Note that these properties hold for true convolution; cross-correlation with a symmetric kernel behaves identically, which is why hand-crafted symmetric filters can be swapped between the two conventions freely.

## The bias term in convolution

In addition to the filter weights, each filter in a convolutional layer has an associated **bias** term — a single scalar value that is added to every element of the feature map produced by that filter. Formally:

$$\text{Output}[i, j, k] = \sum_{c} \sum_{m} \sum_{n} \text{Input}[i+m, j+n, c] \cdot \text{Weight}[m, n, c, k] + \text{Bias}[k]$$

The bias $b_k$ for the $k$-th filter shifts the entire feature map up or down by a constant amount before the activation function is applied. This serves the same purpose as the bias in a fully connected layer: it allows the activation function's decision boundary to be positioned at any value, not just at zero. Without the bias, a ReLU activation would always threshold at zero, which would limit the flexibility of the feature detection.

The bias is shared across all spatial positions of the feature map (just as the filter weights are shared), so it adds only one extra parameter per filter. This is a negligible increase in parameter count, but it provides important representational flexibility. Some modern architectures (particularly those that use Batch Normalization immediately after convolution) omit the bias, because Batch Normalization has its own learnable shift parameter ($\beta$) that serves the same purpose. In such cases, setting `bias=False` in the convolutional layer slightly reduces the parameter count and computational cost without any loss of representational power.

```python
# Comparing convolutional layers with and without bias
conv_with_bias = nn.Conv2d(64, 128, kernel_size=3, padding=1, bias=True)
conv_without_bias = nn.Conv2d(64, 128, kernel_size=3, padding=1, bias=False)

params_with_bias = sum(p.numel() for p in conv_with_bias.parameters())
params_without_bias = sum(p.numel() for p in conv_without_bias.parameters())

# With bias: 128 * (3*3*64) + 128 = 73,856 + 128 = 73,984
# Without bias: 128 * (3*3*64) = 73,856
print(f"With bias: {params_with_bias}")       # 73984
print(f"Without bias: {params_without_bias}") # 73856
print(f"Savings: {params_with_bias - params_without_bias} parameters")  # 128
```

## See also

- [[CNN Course Overview]]
- [[Core Operators and Geometry Summary]]
- [[From Basic Convolution to Learned Weights]]
- [[Local Connectivity and Parameter Sharing]]
- [[Processing 3D Volumes, Depth Summation, and Biases]]
- [[06 - Computer Vision/Core Operators and Geometry/Activation and Pooling Layers|Activation and Pooling Layers]]
- [[Advanced Pooling and Global Average Pooling]]
- [[Strides - Skipping Pixels and Downsampling]]
- [[Padding - Mathematics, Edge Effects, and Valid vs Same]]
- [[The Output Spatial Dimension Formula]]
- [[Receptive Fields and 1x1 Convolutions]]
- [[The Mechanics of Spatial Filtering]]
- [[Hierarchical Feature Extraction]]
- [[06 - Computer Vision/Architecture and Connectivity/ResNet Bottleneck Blocks and Architectural Variants|ResNet Bottleneck Blocks and Architectural Variants]]
