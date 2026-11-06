---
title: Strides - Skipping Pixels and Downsampling
type: concept
aliases:
  - Strides
  - Stride Mechanics
  - Skipping Pixels
  - Strided Convolutions
  - Learnable Downsampling
tags:
  - cnn
  - convolution
  - stride
  - downsampling
  - strided-convolution
  - max-pooling
  - receptive-field
  - resnet
  - vgg
  - computational-cost
sources:
  - "07. Strides - Skipping Pixels and Downsampling"
created_index: 24
---

By default, a CNN filter slides exactly 1 pixel at a time ($S=1$), placing itself at every possible spatial position and producing the largest feature map the configuration allows. The **stride** is the parameter that changes this: it dictates the fixed integer distance the filter shifts horizontally and vertically after each computation, so a stride of 2 deliberately skips every other position and roughly halves the output in each spatial dimension. This seemingly simple parameter has profound implications for computational efficiency, receptive field growth, and the trend — cemented by ResNet — of replacing fixed pooling with learnable strided convolutions. This note works through the mechanics, mathematics, and architectural roles of striding, and anchors the [[CNN Course Overview]] alongside [[The Convolution Operation]] and [[The Output Spatial Dimension Formula]].

## Stride mechanics in one and two dimensions

At the default stride of 1, the filter is placed at every possible spatial position: first at $(1,1)$, then $(1,2)$, then $(1,3)$, and so on, covering every column in every row. If a configuration specifies $S=2$, the filter completes its calculations at the current position and then shifts 2 pixels forward, intentionally ignoring the pixel in between — it lands at positions $(1,1)$, $(1,3)$, $(1,5)$, and so on, covering only every other column and every other row.

To understand what stride does geometrically, imagine a filter sliding across a 1D signal of length 8 with a kernel of size 3.

**Stride = 1 (default):**

```text
Position 1: [x x x] . . . .   →  output pixel 1
Position 2: . [x x x] . . .   →  output pixel 2
Position 3: . . [x x x] . .   →  output pixel 3
Position 4: . . . [x x x] .   →  output pixel 4
Position 5: . . . . [x x x]   →  output pixel 5
Output size: 5
```

**Stride = 2:**

```text
Position 1: [x x x] . . . .   →  output pixel 1
Position 3: . . [x x x] . .   →  output pixel 2
Position 5: . . . . [x x x]   →  output pixel 3
Output size: 3
```

With stride 2, the filter skips position 2 and position 4 entirely. The intermediate pixels at those positions are never examined by the filter at its stopping points (though they may be included within the filter's receptive field at other positions). This skipping is what causes the output to shrink — there are simply fewer valid filter positions when the step size is larger.

In 2D, the stride applies independently to both the horizontal and vertical directions. A stride of $S=2$ means the filter shifts 2 columns right after each computation, and when it reaches the right boundary, it shifts 2 rows down and returns to the leftmost valid column position. The result is a grid of output pixels that samples every other position from the stride-1 output, effectively downsampling the feature map by a factor of 2 in each dimension.

> [!info] Stride and the Receptive Field
> It is important to understand that stride does not reduce the *size* of the filter's receptive field at each position. A $3 \times 3$ filter with stride 2 still looks at a $3 \times 3$ patch of the input at each stopping point. What changes is *where* the filter stops — it makes fewer stops, skipping intermediate positions. The result is that each output pixel still represents a $3 \times 3$ local neighborhood, but the output pixels are spread further apart, covering the input more coarsely.

## The mathematics of striding

Plugging the stride variable into the spatial output formula from [[The Output Spatial Dimension Formula]] proves the dramatic effect quantitatively:

$$O = \left\lfloor \frac{W - K + 2P}{S} \right\rfloor + 1$$

Let's work through a detailed example. Assuming we process an initial tensor with Width $W = 64$, utilizing a Kernel $K = 3$, implementing Padding $P = 1$ (standard same-padding for a $3 \times 3$ kernel), and Stride $S = 2$:

$$O = \left\lfloor \frac{64 - 3 + 2(1)}{2} \right\rfloor + 1 = \left\lfloor \frac{63}{2} \right\rfloor + 1 = \lfloor 31.5 \rfloor + 1 = 31 + 1 = 32$$

**The transformative result:** deploying a stride of $S = 2$ cuts the entire spatial dimension axis exactly in half ($64 \times 64 \rightarrow 32 \times 32$). The total number of spatial positions drops from 4,096 to 1,024 — a **75% reduction** in the amount of data flowing through the network at this point. All subsequent layers operate on this smaller feature map, which means every convolution, every activation, and every gradient computation is roughly 4× cheaper in terms of both memory and compute.

Let's verify this with another example to build confidence. With $W = 128$, $K = 3$, $P = 1$, $S = 2$:

$$O = \left\lfloor \frac{128 - 3 + 2}{2} \right\rfloor + 1 = \left\lfloor \frac{127}{2} \right\rfloor + 1 = \lfloor 63.5 \rfloor + 1 = 63 + 1 = 64$$

The output is $64 \times 64$ — again, exactly half of $128 \times 128$. The floor operation discarded the 0.5, which corresponds to the rightmost column and bottom row being slightly too far for the filter to reach with stride 2. This loss of a single pixel at the boundary is negligible compared to the 4× reduction in computational cost. Edge cases of this floor behavior — including fractional results and kernels larger than the input — are examined in [[The Output Spatial Dimension Formula]].

## The three primary roles of striding

Why would we actively seek out this aggressive data reduction? The answer lies in three critical roles that striding plays in CNN architecture design.

### Computational conservation

By forcibly dropping the overall spatial grid dimensionality, the computational requirements for all subsequent layers plummet. If a feature map is $64 \times 64$ with 128 channels, it contains $64 \times 64 \times 128 = 524,288$ values. After a stride-2 convolution that halves the spatial dimensions to $32 \times 32$ (with 256 channels), the feature map contains $32 \times 32 \times 256 = 262,144$ values — half as many, even though the channel count doubled. This keeps total tensor sizes manageable, avoiding GPU memory limits on large-scale training runs.

Without spatial downsampling at intermediate points in the network, the computational cost of processing high-resolution feature maps through deep stacks of layers would be astronomical. A $224 \times 224$ feature map with 512 channels processed by a $3 \times 3$ convolution requires approximately $224 \times 224 \times 512 \times 3 \times 3 \times 512 \approx 52$ billion multiply-accumulate operations — for a single layer! After stride-2 downsampling to $112 \times 112$, the same operation requires only about 13 billion operations — a 4× reduction from a single downsampling step.

### Receptive field growth

By physically compressing the spatial boundaries, filters in subsequent layers are computationally empowered to access proportionally far wider patch fields of the original raw pixel input. This concept — the **receptive field** — is one of the most important in CNN theory and is explored in depth in [[Receptive Fields and 1x1 Convolutions]]. Here is the essential intuition:

- When a $3 \times 3$ filter operates on a stride-1 feature map, each output pixel represents a $3 \times 3$ patch of the previous layer's feature map.
- When a $3 \times 3$ filter operates on a stride-2 feature map (which was downsampled by 2×), each pixel in that feature map already represents a $2 \times$ larger area of the original input. So the same $3 \times 3$ filter now effectively "sees" a $6 \times 6$ patch of the original input.
- After multiple stride-2 downsampling steps, a single $3 \times 3$ filter in a deep layer can have a receptive field covering the entire input image. This is how deep CNNs learn to recognize global patterns (like the overall shape of a dog) using only small local filters.

This progressive receptive field growth is the fundamental mechanism that allows CNNs to build hierarchical representations: early layers see small local patterns, and deeper layers see increasingly global patterns, all achieved through the same $3 \times 3$ filter size combined with progressive downsampling.

### Learnable downsampling

Deep neural architectures, notably those following the ResNet design philosophy, actively abandon external downsampling layers (specifically MaxPooling operations) in favor of **strided convolutions**. The reason is fundamentally about expressive power:

- **MaxPooling** uses a fixed, unlearnable mathematical function (taking the maximum value in a window) to discard 75% of the spatial data. The network has no say in *which* values are discarded and *how* the downsampling is performed — it is a rigid, non-adaptive operation.
- **Strided convolution** forces the network to *learn* the best way to downsample the image. Because the convolution operation has learnable weights, the network can discover the optimal linear combination of input values that preserves the most important information when reducing the spatial resolution. The downsampling logic is optimized by the training process, just like every other aspect of the network.

This is a profound distinction. With MaxPooling, you are hard-coding the downsampling strategy (take the maximum). With strided convolution, you are letting the network *learn* the downsampling strategy. In practice, this means strided convolutions almost always outperform MaxPooling for downsampling, because the learned downsampling can be task-specific and adaptive.

> [!tip] Strides vs. Pooling — A Preview
> The debate between strided convolutions and pooling layers for downsampling is one of the key design decisions in CNN architecture. Here is a brief comparison:
>
> | Feature | Max Pooling | Strided Convolution |
> |---|---|---|
> | **Learnable?** | No — fixed max operation | Yes — learned weights |
> | **Parameters** | Zero | Filter weights + bias |
> | **Expressiveness** | Limited to max operation | Can learn any linear combination |
> | **Task-Adaptive** | No — same operation regardless of task | Yes — optimized for the specific loss function |
> | **Common Usage** | Older architectures (VGG, LeNet) | Modern architectures (ResNet, EfficientNet) |
> | **When to Use** | When you want a simple, parameter-free downsample | When you want the network to learn optimal downsampling |
>
> This debate is explored fully in [[06 - Computer Vision/Core Operators and Geometry/Activation and Pooling Layers|Activation and Pooling Layers]] and [[Advanced Pooling and Global Average Pooling]].

## The ResNet approach: replacing max pooling with strided convolutions

The ResNet architecture (He et al., 2015) was a landmark in demonstrating the power of strided convolutions. In the original ResNet paper, the authors made a deliberate design choice to use strided convolutions for all spatial downsampling, completely eliminating MaxPooling layers from the main network path. The only pooling operations in ResNet are an initial $7 \times 7$ stride-2 convolution (which aggressively downsamples the input) and a global average pooling at the very end of the network (which is not a spatial downsampling operation but rather a channel-wise reduction).

The ResNet downsampling pattern looks like this:

1. **Initial layer:** $7 \times 7$ convolution with stride 2 → input goes from $224 \times 224$ to $112 \times 112$
2. **Max Pooling $3 \times 3$ with stride 2:** $112 \times 112 \rightarrow 56 \times 56$ (this is the one exception in ResNet)
3. **Conv block with stride 2:** $56 \times 56 \rightarrow 28 \times 28$
4. **Conv block with stride 2:** $28 \times 28 \rightarrow 14 \times 14$
5. **Conv block with stride 2:** $14 \times 14 \rightarrow 7 \times 7$

Each stride-2 convolution in steps 3–5 is a standard convolutional layer with `stride=2` set as a parameter. The filter weights are learned during training, which means the network learns the optimal way to reduce the spatial resolution at each stage. This is in contrast to VGGNet (Simonyan & Zisserman, 2014), which used MaxPooling layers exclusively for all downsampling, with all convolutions operating at stride 1 — the two philosophies are compared in [[06 - Computer Vision/Architecture and Connectivity/ResNet Bottleneck Blocks and Architectural Variants|ResNet Bottleneck Blocks and Architectural Variants]] and [[06 - Computer Vision/Architecture and Connectivity/VGG16 Architecture Deep Dive|VGG16 Architecture Deep Dive]].

## Stride values beyond 2

While $S=2$ is by far the most common stride value used in practice (because it produces a clean 2× reduction), other stride values are possible:

- **$S=1$ (default):** No downsampling. The output is as large as possible for the given configuration. Used for the vast majority of convolutional layers in a network.
- **$S=2$:** 2× spatial reduction. The standard choice for downsampling. Used at strategic points in the network to halve the spatial resolution.
- **$S=3$ or higher:** Rarely used. While possible, larger strides discard too much spatial information too quickly and provide coarser feature maps. In practice, if you need a 4× reduction, it is almost always better to apply two stride-2 convolutions (each reducing by 2×) rather than one stride-4 convolution (reducing by 4× in one step). The two-step approach gives the network more opportunity to learn intermediate representations.

> [!caution] Stride Must Be a Positive Integer
> The stride value must always be a positive integer. Fractional strides do not make sense in the standard convolution operation — you cannot shift a filter by 1.5 pixels. However, **transposed convolutions** (used in upsampling for tasks like image segmentation) can achieve the effect of fractional strides by inserting zeros between input pixels before applying a standard convolution. This is an advanced topic — see [[Advanced Convolutional Operators - Depthwise, Dilated, Transposed, Grouped]].

## Summary

Stride is the parameter that controls how far the filter shifts between successive computations. A stride of 1 (the default) produces the largest possible output feature map; a stride of 2 halves the spatial dimensions and discards 75% of the spatial data. The three primary roles of striding are: (1) computational conservation — reducing the cost of all subsequent operations; (2) receptive field growth — enabling deeper layers to "see" larger regions of the original input; and (3) learnable downsampling — replacing fixed operations like MaxPooling with adaptive, trainable downsampling that is optimized for the specific task. Modern architectures like ResNet use strided convolutions for downsampling, demonstrating that learned downsampling consistently outperforms fixed operations. The stride parameter, combined with padding (see [[Padding - Mathematics, Edge Effects, and Valid vs Same]]), gives the architect precise control over the spatial dimensions of every tensor in the network.

## See also

- [[CNN Course Overview]]
- [[Core Operators and Geometry Summary]]
- [[The Convolution Operation]]
- [[The Output Spatial Dimension Formula]]
- [[Padding - Mathematics, Edge Effects, and Valid vs Same]]
- [[Receptive Fields and 1x1 Convolutions]]
- [[06 - Computer Vision/Core Operators and Geometry/Activation and Pooling Layers|Activation and Pooling Layers]]
- [[Advanced Pooling and Global Average Pooling]]
- [[Advanced Convolutional Operators - Depthwise, Dilated, Transposed, Grouped]]
- [[06 - Computer Vision/Architecture and Connectivity/ResNet Bottleneck Blocks and Architectural Variants|ResNet Bottleneck Blocks and Architectural Variants]]
- [[06 - Computer Vision/Architecture and Connectivity/VGG16 Architecture Deep Dive|VGG16 Architecture Deep Dive]]
