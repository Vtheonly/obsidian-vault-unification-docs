---
title: Advanced Convolutional Operators - Depthwise, Dilated, Transposed, Grouped
type: concept
aliases:
  - Advanced Convolutional Operators — Depthwise, Dilated, Transposed, Grouped
  - Depthwise Separable Convolutions
  - Dilated Convolutions
  - Atrous Convolutions
  - Transposed Convolutions
  - Deconvolution
  - Grouped Convolutions
tags:
  - cnn
  - convolutional-neural-networks
  - computer-vision
  - deep-learning
  - depthwise-separable-convolution
  - dilated-convolution
  - atrous-convolution
  - transposed-convolution
  - grouped-convolution
  - mobilenet
  - deeplab
  - u-net
  - resnext
sources:
  - "01. Advanced Convolutional Operators - Depthwise, Dilated, Transposed, Grouped"
created_index: 1
---

Standard convolution, pooling, and 1×1 convolutions are the everyday operator set of CNN design, but they do not cover everything modern architectures need. Four advanced operators fill the gaps: **depthwise separable convolutions** (MobileNet), **dilated (atrous) convolutions** (DeepLab), **transposed convolutions** (U-Net, GANs), and **grouped convolutions** (ResNeXt). This note develops each operator from the problem it solves through its mechanics and cost arithmetic to its use cases and characteristic pitfalls, building directly on [[The Convolution Operation]] and [[Receptive Fields and 1x1 Convolutions]] and connecting to the architectural story in [[06 - Computer Vision/Architecture and Connectivity/Evolution of CNN Architectures|Evolution of CNN Architectures]].

## Depthwise separable convolutions

### The cost of standard convolution

Standard convolution is expensive because every output channel interacts with every input channel at every spatial position. A standard convolution with kernel size $K \times K$, input channels $C_{in}$, output channels $C_{out}$, on a $H \times W$ feature map costs:

$$\text{FLOPs} = H \times W \times K \times K \times C_{in} \times C_{out}$$

The kernel extent, the input depth, and the output depth all multiply together, so the bill grows with the square of the kernel size and with the product of the two channel counts. For a $3 \times 3$ conv with 64 input and 64 output channels on a $224 \times 224$ feature map: $224 \times 224 \times 3 \times 3 \times 64 \times 64 \approx 1.85 \text{ billion}$ FLOPs — for a single layer. This is expensive, especially for mobile and embedded deployment where compute and memory budgets are tight.

### The factorization: depthwise then pointwise

A **depthwise separable convolution** — the operator popularized by MobileNet and Xception — factors the standard convolution into two cheaper operations that split the work between spatial filtering and channel mixing. The two steps divide the labor as follows.

**Step 1 — depthwise convolution:** apply a separate $K \times K \times 1$ filter to each input channel independently. This captures spatial patterns but no cross-channel mixing. Cost: $H \times W \times K \times K \times C_{in}$.

**Step 2 — pointwise convolution:** apply a $1 \times 1 \times C_{in} \times C_{out}$ convolution to mix channels. Cost: $H \times W \times C_{in} \times C_{out}$.

**Total cost:** $H \times W \times K^2 \times C_{in} + H \times W \times C_{in} \times C_{out}$

The spatial term no longer scales with $C_{out}$, and the channel-mixing term no longer scales with $K^2$ — which is exactly where the savings come from. Neither step alone reproduces a standard convolution: the depthwise step cannot combine information across channels, and the pointwise step cannot see spatial neighborhoods. Together, however, they approximate what a standard convolution learns at a fraction of the price.

### The savings

The ratio of depthwise separable to standard convolution cost is:

$$\frac{K^2 \cdot C_{in} + C_{in} \cdot C_{out}}{K^2 \cdot C_{in} \cdot C_{out}} = \frac{1}{C_{out}} + \frac{1}{K^2}$$

For $K = 3$ and $C_{out} = 64$: $1/64 + 1/9 \approx 0.115$ — about **8-9× fewer FLOPs** than standard convolution, with minimal accuracy loss. The saving comes from never paying for the $K^2$ factor and the $C_{out}$ factor at the same time. Because the ratio is a sum of two small reciprocals, it stays small whenever kernels are modest and layers are reasonably wide.

### Where depthwise separable convolutions are used

Depthwise separable convolutions are the backbone of the efficient-model family:

- **MobileNet** (Howard et al., 2017): built almost entirely from depthwise separable convolutions, enabling real-time inference on mobile devices.
- **MobileNetV2**: adds inverted residuals and linear bottlenecks on top of depthwise separable convs.
- **Xception** (Chollet, 2017): "extreme" Inception where the depthwise separable idea is pushed to the limit (see [[06 - Computer Vision/Architecture and Connectivity/Inception Architecture Deep Dive|Inception Architecture Deep Dive]]).
- **EfficientNet**: uses depthwise separable convs as a building block in its compound-scaled architecture.

In every case the motivation is the same: near-standard accuracy at a fraction of the compute, which is what makes real-time inference on phones and embedded devices feasible.

### Why the factorization works

The factorization is based on the **decoupling hypothesis**: spatial patterns (captured by the depthwise step) and channel patterns (captured by the pointwise step) are largely independent, so you can learn them separately without much loss. Empirically, this holds for most vision tasks — depthwise separable convs achieve ~95-99% of standard conv accuracy at ~10% of the cost. The hypothesis is an empirical regularity rather than a theorem, but the entire efficient-architecture family listed above is built on it.

## Dilated (atrous) convolutions

### The problem: receptive field without resolution loss

For dense prediction tasks (semantic segmentation), you need a large receptive field (to see context) but you cannot downsample (you need pixel-level output). The standard ways of growing the receptive field — pooling or strided convolutions — reduce spatial resolution, which destroys the pixel-level detail you need. This tension between context and resolution is the motivating problem; the downsampling tools being avoided are covered in [[Advanced Pooling and Global Average Pooling]] and [[Strides - Skipping Pixels and Downsampling]].

### Inserting spaces into the kernel

A **dilated convolution** (Yu and Koltun, 2016) inserts "holes" (spaces) between the kernel elements, expanding the receptive field without adding parameters or reducing resolution. A convolution with kernel size $K$ and dilation rate $r$ has an effective kernel size of $K + (K-1)(r-1) = K + (K-1)r - (K-1) = (K-1)r + 1$; equivalently, the effective receptive field is $K \times r - (r-1)$. Concretely: a $3 \times 3$ kernel with dilation 2 sees a $5 \times 5$ area; with dilation 4, a $9 \times 9$ area.

The geometry is easiest to see in the sampling grid itself. A $3 \times 3$ kernel with dilation 2 applies the 9 kernel weights at positions:

```text
W . . W . . W
. . . . . . .
W . . W . . W
. . . . . . .
W . . W . . W
```

(where `W` is a kernel weight and `.` is skipped). The kernel still has 9 parameters, but it sees a $5 \times 5$ area.

### Exponential receptive field growth

Stacking dilated convolutions with exponentially increasing dilation rates grows the receptive field exponentially with depth:

- Layer 1: $3 \times 3$, dilation 1 → RF = 3
- Layer 2: $3 \times 3$, dilation 2 → RF = 7
- Layer 3: $3 \times 3$, dilation 4 → RF = 15
- Layer 4: $3 \times 3$, dilation 8 → RF = 31

With 4 layers, you get a receptive field of 31 — comparable to a deep stack of standard convolutions or pooling, but **without any resolution loss**. Each doubling of the dilation rate lets a thin 9-parameter kernel reach twice as far, which is what makes the growth exponential in depth rather than merely additive.

### Where dilated convolutions are used

- **DeepLab** (Chen et al., 2017+): the leading semantic segmentation architecture, uses dilated convolutions to maintain resolution while gaining context. DeepLabv3 uses dilations of 6, 12, 18 in parallel (the "ASPP" — Atrous Spatial Pyramid Pooling module).
- **WaveNet** (van den Oord et al., 2016): audio generation, uses dilated convolutions to handle long-range temporal dependencies.
- **Context aggregation:** any task where you need a large receptive field without downsampling benefits from dilated convolutions.

The common thread is dense output — per-pixel segmentation maps, per-sample audio — where every output position needs both local detail and wide context. The task-level setting is covered in [[Detection and Segmentation]].

### The gridding artifact

Dilated convolutions have one characteristic failure mode. If you stack dilated convolutions with the same dilation rate, the receptive field has "holes" — pixels in the gaps never contribute. The skipped positions of one layer line up with the skipped positions of the next, so entire sets of input pixels are systematically ignored.

> [!warning] Avoiding the gridding artifact
> Never stack dilated convolutions with the same dilation rate. DeepLab addresses the problem by using different dilation rates in parallel (ASPP) or by varying rates across layers, so that the holes of one layer are covered by the samples of its neighbors.

## Transposed convolutions

### The problem: upsampling

Standard convolutions (with stride > 1) and pooling **downsample** — they reduce spatial resolution. But for tasks like semantic segmentation or image generation, you need to **upsample** — increase spatial resolution from a low-resolution feature map to a high-resolution output. The decoder side of an encoder-decoder architecture therefore needs an operator that grows resolution instead of shrinking it.

### The transposed convolution operator

A **transposed convolution** (sometimes inaccurately called "deconvolution") is the transpose of a regular convolution. It upsamples the input by scattering each input value across a larger output area according to the kernel. For a $2 \times 2$ input, $3 \times 3$ kernel, stride 2, no padding: each input pixel is multiplied by the $3 \times 3$ kernel and the result is added to a $3 \times 3$ patch of the output, with patches overlapping by the stride; the output is $4 \times 4$ (or more, depending on padding).

The name "transposed" comes from the matrix view: if a convolution is represented as a sparse matrix multiplication $Y = C X$ (where $C$ is the convolution matrix), the transposed convolution is $Y = C^\top X$ — the same matrix, transposed. A regular convolution *gathers*: each output value is a weighted sum over a patch of inputs. Its transpose *scatters*: each input value is spread across a patch of outputs.

### Where transposed convolutions are used

- **U-Net** (Ronneberger et al., 2015): the decoder uses transposed convolutions to upsample the bottleneck features back to the input resolution, with skip connections from the encoder. The standard architecture for medical image segmentation.
- **GANs** (generator): the generator takes a noise vector and upsamples it through transposed convolutions to produce an image.
- **Semantic segmentation decoders:** any encoder-decoder segmentation architecture (DeepLab v3+, FCN) uses transposed convolutions (or bilinear upsampling + convolutions) in the decoder.

All three uses share the same need: turning small, low-resolution feature maps back into large, spatially detailed outputs. Skip connections, which carry encoder detail across to the decoder, are discussed in [[06 - Computer Vision/Architecture and Connectivity/The Degradation Problem and Residual Connections|The Degradation Problem and Residual Connections]].

### The checkerboard artifact

The pitfall to watch with transposed convolutions is an artifact of uneven overlap.

> [!warning] The checkerboard artifact
> When the kernel size is not divisible by the stride, the transposed convolution produces uneven overlap — some output pixels receive contributions from multiple input pixels, others from only one. This creates a **checkerboard pattern** in the output.
>
> **Fix:** use kernel size divisible by stride (e.g., kernel 4, stride 2), or replace transposed convolutions with **upsampling + convolution** (resize the image with bilinear interpolation, then apply a regular convolution). The latter is preferred in many modern architectures because it avoids the checkerboard entirely.

## Grouped convolutions

### Splitting the channels into groups

A **grouped convolution** splits the input channels into $G$ groups and applies a separate convolution to each group. The output channels are also split into $G$ groups, with group $i$ of the output computed only from group $i$ of the input. For $C_{in}$ input channels, $C_{out}$ output channels, and $G$ groups: each group has $C_{in}/G$ input channels and $C_{out}/G$ output channels; each group's convolution is a standard conv with $C_{in}/G$ inputs and $C_{out}/G$ outputs; and the $G$ outputs are concatenated. The result looks like a single wide layer from the outside, but internally it is $G$ narrow, independent convolutions.

### The cost reduction

The cost is $G$ times smaller than a standard convolution:

$$\text{FLOPs}_{grouped} = \frac{1}{G} \times \text{FLOPs}_{standard}$$

because each group's conv has $1/G$ the input channels and $1/G$ the output channels. The saving is a direct consequence of the group structure: every factor of $G$ removed from each channel count removes a factor of $G$ from the multiply-accumulate count.

### Where grouped convolutions are used

- **AlexNet** (2012): used grouped convolutions to split the model across 2 GPUs (historical motivation — memory constraints).
- **ResNeXt** (Xie et al., 2017): showed that increasing the number of groups ($G = 32$) while keeping the total parameter count fixed improves accuracy. The "cardinality" (number of groups) is a new dimension of model capacity, alongside width and depth. See [[06 - Computer Vision/Architecture and Connectivity/ResNet Bottleneck Blocks and Architectural Variants|ResNet Bottleneck Blocks and Architectural Variants]] for the ResNet family context.
- **Depthwise convolution** (MobileNet): is the extreme case of grouped convolution with $G = C_{in} = C_{out}$ — each group has exactly one input and one output channel. This closes the loop with the depthwise step of depthwise separable convolutions above.

The historical arc runs from a hardware workaround in AlexNet, to a deliberate capacity lever in ResNeXt, to the backbone of mobile architectures.

### Why grouped convolutions work

Grouped convolutions provide a different **structural prior**: instead of every output channel seeing every input channel (dense connectivity), each output channel sees only a subset. This can be beneficial for two reasons. First, it forces the model to learn **decorrelated features** in different groups (a form of regularization). Second, it increases the "effective" number of paths through the network (cardinality), which ResNeXt showed is more efficient than just increasing width.

## Operator summary

The four operators compress into one comparison:

| Operator | Cost vs standard | Key use case | Used in |
| :--- | :--- | :--- | :--- |
| Depthwise separable | ~8-9× cheaper | Mobile/efficient models | MobileNet, Xception, EfficientNet |
| Dilated | Same cost, larger RF | Dense prediction (no resolution loss) | DeepLab, WaveNet |
| Transposed | Upsampling (increases resolution) | Decoders, generators | U-Net, GANs, segmentation |
| Grouped | $1/G$ cost | Efficient parallelism, cardinality | ResNeXt, AlexNet |

Reading the table row by row: depthwise separable convolutions factor standard conv into depthwise (spatial) + pointwise (channel), reducing cost ~8-9× with minimal accuracy loss, and power MobileNet and EfficientNet. Dilated convolutions insert holes in the kernel, expanding the receptive field without reducing resolution, and power DeepLab for segmentation. Transposed convolutions are the transpose of regular convs, used for upsampling in decoders (U-Net) and generators (GANs) — with the checkerboard artifact as the pitfall to watch. Grouped convolutions split channels into groups, reducing cost by $1/G$ and increasing "cardinality," and power ResNeXt. These operators are essential for modern architectures — MobileNet, DeepLab, U-Net, ResNeXt all depend on them. The [[CNN Course Overview]] and [[CNN Mastery Roadmap]] situate them within the wider curriculum.

## See also

- [[CNN Course Overview]]
- [[CNN Mastery Roadmap]]
- [[The Convolution Operation]]
- [[Receptive Fields and 1x1 Convolutions]]
- [[Strides - Skipping Pixels and Downsampling]]
- [[Advanced Pooling and Global Average Pooling]]
- [[06 - Computer Vision/Architecture and Connectivity/Evolution of CNN Architectures|Evolution of CNN Architectures]]
- [[06 - Computer Vision/Architecture and Connectivity/Inception Architecture Deep Dive|Inception Architecture Deep Dive]]
- [[06 - Computer Vision/Architecture and Connectivity/ResNet Bottleneck Blocks and Architectural Variants|ResNet Bottleneck Blocks and Architectural Variants]]
- [[06 - Computer Vision/Architecture and Connectivity/The Degradation Problem and Residual Connections|The Degradation Problem and Residual Connections]]
- [[Detection and Segmentation]]
- [[Deep Learning for Imaging]]
