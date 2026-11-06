---
title: Convolutional Neural Networks
type: reference
aliases:
  - CNN
  - CNNs
tags:
  - neural-networks
  - cnn
  - convolution
  - vision
  - resnet
  - parameter-sharing
  - depthwise-separable-convolution
sources:
  - "03 - CNNs"
created_index: 1
---

Convolutional Neural Networks (CNNs) are the architecture that made deep learning practical for images: a convolutional layer slides a small learned filter across the input and shares its weights at every position, instead of connecting every pixel to every neuron. That one design choice exploits spatial locality and translation invariance, buys enormous parameter efficiency, and lets stacked layers build a feature hierarchy from edges up to objects. CNNs were the dominant vision architecture from LeNet (1998) to the Vision Transformer (2020), and they remain the right choice for small datasets, mobile and edge deployment, and dense prediction — as well as being the conceptual ancestor of "sliding window attention" in modern Transformers.

> [!info] TL;DR
> CNNs use **convolution** — sliding a small filter across the input — to exploit spatial locality and translation invariance. Dominant for vision from 1998 (LeNet) to 2020 (Vision Transformer). Still important for efficient vision, video, and as the conceptual ancestor of "sliding window attention" in modern Transformers.

## The core idea: convolution

A **convolutional layer** slides a small filter (kernel) across the input, computing dot products at each position:

```text
Input (5x5):        Filter (3x3):      Output (3x3):
1 2 3 4 5           1 0 -1             (sum of element-wise products)
6 7 8 9 0           1 0 -1
1 2 3 4 5           1 0 -1
6 7 8 9 0
1 2 3 4 5
```

The same filter is shared across all positions, and this is the key difference from a dense layer: a dense layer learns a separate weight for every input–output pair, while a convolutional layer reuses one small set of weights everywhere. In this sense a CNN is an MLP with weight sharing (see [[Perceptrons and Multi-Layer Perceptrons]]) — the sharing is what gives the network its vision-friendly inductive bias.

## Why convolutions work for images

Four properties make convolution the right primitive for image data: spatial locality, translation invariance, parameter efficiency, and hierarchical feature composition. Each follows directly from sliding one small shared kernel across the input rather than connecting everything to everything.

### Spatial locality

Nearby pixels are correlated (an edge, a texture). A small filter (3×3, 5×5) captures local patterns efficiently. Dense layers would mix all pixels globally — wasteful and noisy — because most of what they model is the irrelevant interaction of distant, uncorrelated pixels.

### Translation invariance

A cat is a cat whether it's in the top-left or bottom-right of the image. By sharing the filter across positions, the CNN recognizes the same pattern anywhere. The pattern detector itself does not move or multiply — one kernel serves every location.

### Parameter efficiency

A 3×3 conv on a 224×224 image has 9 parameters (per filter). A dense layer connecting all pixels would have $224 \times 224 \approx 50$k parameters. CNNs therefore use far fewer parameters for the same input, which shrinks both memory and the risk of overfitting.

### Hierarchical features

Stacking conv layers builds a feature hierarchy: edges → textures → parts → objects. Early layers learn simple patterns; later layers compose them into complex ones. This composition is what lets a deep CNN recognize whole objects from elementary local evidence.

## The CNN block

A typical CNN layer chains a small fixed sequence of stages:

1. **Convolution**: apply the filter.
2. **Activation**: ReLU (or GELU).
3. **Pooling** (sometimes): downsample (max pool or average pool).
4. **BatchNorm** (sometimes): normalize activations.

Stack 5–50 of these blocks, then attach a dense head for classification. The activation step is the standard nonlinearity covered in [[Activation Functions]]; the normalization stage and its training/inference distinction are treated in [[05 - Neural Network Foundations/Training Dynamics and Stability/Batch Normalization|Batch Normalization]]. For ReLU conv stacks, He initialization is the standard init choice — see [[05 - Neural Network Foundations/Training Dynamics and Stability/Weight Initialization|Weight Initialization]].

## The mathematics of convolution

A 2D convolution with kernel $\mathbf{K} \in \mathbb{R}^{k \times k}$ on input $\mathbf{X} \in \mathbb{R}^{H \times W}$ is:

$$
(\mathbf{X} * \mathbf{K})_{ij} = \sum_{a=0}^{k-1} \sum_{b=0}^{k-1} X_{i+a, j+b} \cdot K_{a, b}
$$

(Technically this is **cross-correlation** — the "convolution" in deep learning flips neither input nor kernel. True convolution flips the kernel, but this distinction is irrelevant for learned kernels.) Each output entry is one dot product of the kernel with a $k \times k$ patch of the input, taken at a particular offset.

### Output shape computation

For input $H \times W$, kernel $k \times k$, padding $p$, stride $s$:

$$
H_{\text{out}} = \left\lfloor \frac{H + 2p - k}{s} \right\rfloor + 1
$$

The same formula applies to $W_{\text{out}}$. With $p = (k-1)/2$ and $s = 1$, the output has the same spatial size as the input ("same" padding). Computing this shape explicitly is the reliable way to avoid silent shrinkage through a stack of layers.

### Parameter count

A conv layer with $C_{\text{in}}$ input channels, $C_{\text{out}}$ output channels, and kernel $k \times k$ has $C_{\text{out}} \times C_{\text{in}} \times k \times k + C_{\text{out}}$ parameters (weights + biases). For example, 3 → 64 channels with a 3×3 kernel gives 1,792 parameters. Compare a dense layer connecting every pixel of a 224×224×3 image to 64 outputs: $224 \times 224 \times 3 \times 64 = 9.6$M parameters. The parameter efficiency comes from **weight sharing** — the same kernel is applied at every spatial position.

### FLOP count

For input $C_{\text{in}} \times H \times W$, kernel $k \times k$, and $C_{\text{out}}$ output channels, the layer costs $2 \cdot C_{\text{out}} \cdot C_{\text{in}} \cdot k^2 \cdot H_{\text{out}} \cdot W_{\text{out}}$ FLOPs. Example: 3×224×224 → 64 channels, 3×3, stride 1, same padding: $2 \cdot 64 \cdot 3 \cdot 9 \cdot 224 \cdot 224 \approx 173$M FLOPs. Note that FLOPs scale with the output resolution, not the parameter count — a cheap-looking layer can still dominate compute on large inputs.

## Worked example: a LeNet-style CNN

The following PyTorch model is a small LeNet-style classifier — two conv+pool stages that grow the channel count while halving the spatial resolution, then a linear head over the flattened features:

```python
import torch.nn as nn

class SimpleCNN(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, padding=1)   # 1 channel in, 32 out, 3x3
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.pool = nn.MaxPool2d(2, 2)                # halves spatial dims
        self.fc = nn.Linear(64 * 7 * 7, num_classes)
    
    def forward(self, x):                              # x: (B, 1, 28, 28)
        x = self.pool(F.relu(self.conv1(x)))           # (B, 32, 14, 14)
        x = self.pool(F.relu(self.conv2(x)))           # (B, 64, 7, 7)
        x = x.flatten(1)                                # (B, 64*7*7)
        return self.fc(x)
```

The shape comments carry the lesson: pooling halves the spatial dimensions (28→14→7), the channel count grows (1→32→64), and the flatten before the fully connected head produces the $(B, 64 \cdot 7 \cdot 7)$ tensor the linear layer expects. Forgetting that flatten is one of the most common shape bugs in CNN code. How gradients flow backward through each of these layer types — convolution, pooling, normalization, ReLU — is dissected in [[05 - Neural Network Foundations/Backpropagation/Backpropagation and Gradient Flow in CNNs|Backpropagation and Gradient Flow in CNNs]].

## Depthwise separable convolutions

A standard convolution has $C_{\text{out}} \times C_{\text{in}} \times k^2$ parameters. A **depthwise separable convolution** decomposes this into two cheaper operations:

1. **Depthwise conv**: one filter per input channel — $C_{\text{in}} \times k^2$ parameters.
2. **Pointwise conv** (1×1): mix channels — $C_{\text{out}} \times C_{\text{in}}$ parameters.

The total is $C_{\text{in}} \times k^2 + C_{\text{out}} \times C_{\text{in}}$ versus $C_{\text{out}} \times C_{\text{in}} \times k^2$. For $k = 3$, $C_{\text{out}} = C_{\text{in}} = 64$: 832 vs. 36,864 — 44× fewer parameters. This factorization is the foundation of MobileNet, EfficientNet, and most mobile/edge vision models. The cost is a slight quality reduction (~1-2% ImageNet accuracy).

## The ResNet revolution

Plain CNNs couldn't go deep — past ~20 layers, training degraded as gradients vanished through the stacked layers (see [[Backpropagation]] and [[05 - Neural Network Foundations/Training Dynamics and Stability/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]]). **ResNet** (2015) introduced **skip connections** (residuals):

$$
\mathbf{y} = \mathbf{x} + F(\mathbf{x})
$$

where $F$ is a stack of conv layers. The identity shortcut lets gradients flow directly through the network: if $F(\mathbf{x}) = 0$ is optimal, the block becomes an identity mapping — the network can learn to "skip" layers. This enabled 100+ layer CNNs. ResNet-50 was state of the art on ImageNet in 2015 and is still widely used as a backbone for downstream vision tasks. The same principle — residual connections — is used in every modern Transformer, whose residual stream is a direct descendant of this additive gradient path.

## The evolution of CNN architectures

| Model            | Year | Innovation                                          | Top-5 ImageNet Acc |
|------------------|------|-----------------------------------------------------|--------------------|
| LeNet            | 1998 | First successful CNN (digit recognition)            | N/A (MNIST)        |
| AlexNet          | 2012 | GPU training, ReLU, dropout (deep learning revolution) | 84.7%              |
| VGG              | 2014 | Deeper (16-19 layers), small 3×3 kernels            | 92.0%              |
| GoogLeNet/Inception | 2014 | Multi-scale parallel convs, 1×1 convs              | 93.3%              |
| ResNet           | 2015 | Residual connections (skip connections)             | 96.4%              |
| DenseNet         | 2017 | Dense connections (every layer connects to every other) | 96.4%              |
| MobileNet        | 2017 | Depthwise separable convs (mobile)                  | 90.6%              |
| EfficientNet     | 2019 | Compound scaling (width/depth/resolution)           | 97.1%              |
| ConvNeXt         | 2022 | Modernized ResNet (rivals ViT)                      | 97.8%              |

The lineage runs from LeNet's digit recognition through AlexNet — whose GPU training, ReLU, and dropout started the deep learning revolution — to VGG's deeper stacks of small 3×3 kernels, Inception/GoogLeNet's multi-scale parallel convolutions and 1×1 convs, ResNet's residuals, MobileNet's depthwise separable convs for mobile, and EfficientNet's compound scaling of width, depth, and resolution. All of these were state of the art before the Vision Transformer (2020). Each entry is a distinct design lesson: depth (VGG), multi-scale features (Inception), trainability of depth (ResNet), efficiency (MobileNet), and principled scaling (EfficientNet).

### Why ResNet was the breakthrough

Before ResNet, deeper networks performed **worse** — the **degradation problem** — and this was not overfitting but optimization difficulty. The identity shortcut $\mathbf{y} = \mathbf{x} + F(\mathbf{x})$ lets gradients flow directly through the network, so depth stops hurting optimization. If $F(\mathbf{x}) = 0$ is optimal, the layer becomes identity and the network can learn to "skip" layers; this is what enabled 100+ layer networks. The same principle — residual connections — is used in every modern Transformer.

### ConvNeXt: CNNs strike back

ConvNeXt (Liu et al. 2022) modernized the ResNet architecture with insights from the Vision Transformer:

- Larger kernels (7×7 instead of 3×3).
- LayerNorm instead of BatchNorm.
- GELU instead of ReLU.
- Fewer activation functions (only one per block).
- Inverted bottleneck (wide → narrow → wide).

The result: ConvNeXt matches or beats ViT on ImageNet, proving CNNs are still competitive when modernized. This challenges the "ViT replaced CNNs" narrative — the modernized block rivals ViT blocks with the same local, weight-shared machinery.

## CNNs versus the Vision Transformer

| Criterion                    | CNN (ResNet, ConvNeXt)    | ViT (ViT, DeiT, Swin)      |
|------------------------------|---------------------------|----------------------------|
| Small datasets (<100K images) | Better (inductive bias)  | Data-hungry                |
| Large datasets (>10M images)  | Good                     | Better (scales)            |
| Mobile / edge                | More efficient            | Heavier                    |
| Dense prediction (detection)  | Better (hierarchical)    | ViTDet closes the gap      |
| Long-range dependencies       | Limited receptive field  | Global attention           |
| Transfer learning            | Strong                    | Strong (often better)      |
| Interpretability             | Feature visualization    | Attention visualization    |

ViT now matches or beats CNNs on large datasets, but CNNs remain relevant for smaller datasets (ViT is data-hungry), mobile / edge deployment (CNNs are more efficient), and dense prediction such as segmentation and detection (U-Net architectures). The 2026 recommendation: start with a pretrained ViT (DINOv2, SigLIP) for most vision tasks, and use a CNN (ConvNeXt, EfficientNet) when (1) data is limited, (2) the target is mobile/edge deployment, or (3) dense prediction has strict latency requirements. The gap has narrowed — both are viable for most tasks.

## Worked example: a modern ConvNeXt-style block

```python
import torch
import torch.nn as nn

class ConvNeXtBlock(nn.Module):
    """ConvNeXt-style block: depthwise conv → LN → pointwise → GELU → pointwise."""
    def __init__(self, dim, layer_scale=1e-6):
        super().__init__()
        self.dw_conv = nn.Conv2d(dim, dim, kernel_size=7, padding=3, groups=dim)
        self.norm = nn.LayerNorm(dim)
        self.pw1 = nn.Linear(dim, dim * 4)  # expand
        self.act = nn.GELU()
        self.pw2 = nn.Linear(dim * 4, dim)  # contract
        self.gamma = nn.Parameter(layer_scale * torch.ones(dim)) if layer_scale else 1.0

    def forward(self, x):
        residual = x
        x = self.dw_conv(x)                   # depthwise: local spatial
        x = x.permute(0, 2, 3, 1)             # (B, H, W, C) for LayerNorm
        x = self.norm(x)
        x = self.pw1(x)                        # expand
        x = self.act(x)
        x = self.pw2(x)                        # contract
        x = self.gamma * x
        x = x.permute(0, 3, 1, 2)             # back to (B, C, H, W)
        return residual + x                    # residual

# A ConvNeXt stage: stem + N blocks + downsample
class ConvNeXtStage(nn.Module):
    def __init__(self, in_dim, out_dim, n_blocks, stride=2):
        super().__init__()
        self.downsample = nn.Conv2d(in_dim, out_dim, kernel_size=stride, stride=stride)
        self.blocks = nn.Sequential(*[ConvNeXtBlock(out_dim) for _ in range(n_blocks)])

    def forward(self, x):
        return self.blocks(self.downsample(x))
```

This modernized CNN block — a 7×7 depthwise conv, LayerNorm, GELU, an inverted bottleneck, and layer scale — rivals ViT blocks on ImageNet, proving CNNs can be modernized to match Transformers. Each element implements one of the ConvNeXt design choices listed above: the depthwise conv supplies local spatial mixing, the two pointwise layers form the wide→narrow→wide inverted bottleneck, and the residual addition carries the gradient path. The stage wrapper shows the standard downsampling pattern — a strided convolution reduces resolution first, then the blocks operate at the new size.

## Relation to Transformer attention

CNNs and self-attention are conceptually related. A **convolution** is a "local attention" with fixed weights; a **self-attention** layer is a "global convolution" with input-dependent weights. Sliding-window attention (Mistral 7B, Longformer) is essentially a CNN-style local attention pattern applied to sequences — attention within a window of size $w$ behaves exactly like a CNN with kernel size $w$, except that attention weights are input-dependent while conv weights are fixed (learned once). The attention mechanism generalizes convolution, which is why CNN-inspired local patterns appear in sparse attention designs.

## Why this matters

CNNs are the **historical foundation** of deep learning: the deep learning revolution started with AlexNet (2012) — a CNN. For vision tasks where data is limited or compute is constrained, CNNs are still the right choice. The convolution pattern — parameter sharing across positions — shows up in modern architectures in modified forms (sliding window attention, depthwise convs in Mamba). And for multimodal AI, CNN backbones (ResNet, ViT) encode the images that LLMs then attend to.

## Production implications

Use **pretrained CNN backbones** (ResNet-50, EfficientNet-B0) for vision tasks with limited data; the HuggingFace `transformers` and `timm` libraries make this trivial. For **object detection / segmentation**, Faster R-CNN, YOLO, Mask R-CNN, and DETR all use CNN backbones. For **mobile / edge** targets, MobileNetV3 and EfficientNet-Lite are the standard picks. For **large-scale vision**, ViT usually wins, but requires more data and compute.

## Common pitfalls and failure modes

Most CNN debugging falls into two families: shape mistakes (padding, stride, flatten, channel layout) and resource mistakes (channel budgeting, throughput). The pitfall list gives the recurring coding errors; the failure-mode table maps observed symptoms to causes and fixes.

### Common pitfalls

The five classics, each with its symptom and fix:

- **No padding** — output shrinks each layer. Use `padding='same'` or compute output dims explicitly.
- **Wrong stride** — `stride=2` downsamples (like pooling); `stride=1` keeps resolution.
- **Forgetting flatten before the FC head** — common shape bug.
- **Too many channels early** — wastes parameters; better to increase channels as resolution decreases.
- **Mixing up "channels first" vs "channels last"** — PyTorch uses (B, C, H, W); TensorFlow uses (B, H, W, C). Don't mix.

The first three corrupt tensor shapes outright; the last two waste parameters or silently transpose the layout.

### Common failure modes

The table below pairs each observed symptom with its most likely cause and the standard fix.

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Output shrinks each layer | No padding | Use `padding='same'` or compute output dims |
| Memory explosion | Too many channels early | Increase channels as resolution decreases |
| Slow training | Small batch size; conv-bound | Increase batch; use mixed precision |
| Wrong channel format | Mixing NHWC and NCHW | PyTorch = NCHW; TF = NHWC; don't mix |
| Poor accuracy on small dataset | CNN overfitting; ViT too data-hungry | Use pretrained CNN; strong augmentation |
| Detection model misses small objects | Receptive field too large | Use FPN (Feature Pyramid Network); multi-scale |

The "poor accuracy on small dataset" row pairs naturally with the augmentation lever covered in [[05 - Neural Network Foundations/Training Dynamics and Stability/Data Augmentation|Data Augmentation]] — a pretrained backbone plus strong augmentation is the standard recipe when labeled images are scarce.

## Interview questions

**Q: Why do CNNs use weight sharing, and what does it buy?**
A: Weight sharing means the same kernel is applied at every spatial position. This buys: (1) parameter efficiency — a 3×3 conv has 9 parameters regardless of image size; a dense layer has $H \times W$ parameters; (2) translation invariance — a cat is a cat anywhere in the image; (3) locality — nearby pixels are correlated, so small kernels capture relevant patterns. The cost: less flexibility than a dense layer, but this is a feature (inductive bias) for vision.

**Q: What is depthwise separable convolution, and why is it efficient?**
A: Decompose a standard conv ($C_{\text{out}} \times C_{\text{in}} \times k^2$ params) into depthwise ($C_{\text{in}} \times k^2$, one filter per channel) + pointwise ($C_{\text{out}} \times C_{\text{in}}$, 1×1 conv). For $k=3$, $C_{\text{out}} = C_{\text{in}} = 64$: 832 vs. 36,864 — 44× fewer parameters. The cost: ~1-2% accuracy reduction. Foundation of MobileNet, EfficientNet, and mobile vision.

**Q: Why did ResNet enable deeper networks?**
A: Before ResNet, deeper networks performed worse (degradation problem) — gradients vanished through many layers. ResNet's identity shortcut $\mathbf{y} = \mathbf{x} + F(\mathbf{x})$ provides a direct path for gradients. If $F(\mathbf{x}) = 0$ is optimal, the layer becomes identity — the network can "skip" layers. This enabled 100+ layer networks. The same principle (residual connections) is used in every modern Transformer.

**Q: When would you choose a CNN over a ViT?**
A: Choose CNN when: (1) small datasets (<100K images) — CNN's inductive bias (locality, translation invariance) helps with limited data; (2) mobile/edge — CNNs are more efficient; (3) dense prediction (detection, segmentation) — hierarchical features work well. Choose ViT when: (1) large datasets — ViT scales better; (2) long-range dependencies matter; (3) transfer learning — ViT often transfers better. The gap has narrowed; both are viable for most tasks in 2026.

**Q: How does ConvNeXt modernize CNNs to rival ViT?**
A: ConvNeXt applies ViT-inspired changes to ResNet: (1) larger kernels (7×7 vs. 3×3) for wider receptive field; (2) LayerNorm instead of BatchNorm; (3) GELU instead of ReLU; (4) fewer activations (one per block, not per layer); (5) inverted bottleneck (wide→narrow→wide, like ViT's FFN). Result: ConvNeXt matches or beats ViT on ImageNet, proving CNNs are still competitive when modernized.

**Q: How does sliding window attention relate to convolution?**
A: Sliding window attention (Mistral 7B, Longformer) applies attention only within a local window of size $w$ — exactly like a CNN with kernel size $w$. The difference: attention weights are input-dependent (learned per position), while conv weights are fixed (learned once). Attention generalizes convolution — a conv is "local attention with fixed weights". This is why CNN-inspired patterns appear in efficient attention.

## Further reading

The canonical references are LeCun et al. (1998), *Gradient-Based Learning Applied to Document Recognition* (LeNet); Krizhevsky et al. (2012), *ImageNet Classification with Deep CNNs* (AlexNet); and He et al. (2016), *Deep Residual Learning for Image Recognition* (ResNet).

## See also

- [[Neural Network Foundations MOC]]
- [[Recurrent Neural Networks]]
- [[Seq2Seq and the Information Bottleneck]]
- [[Perceptrons and Multi-Layer Perceptrons]]
- [[Artificial Neural Networks]]
- [[Activation Functions]]
- [[Backpropagation]]
- [[05 - Neural Network Foundations/Backpropagation/Backpropagation and Gradient Flow in CNNs|Backpropagation and Gradient Flow in CNNs]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Batch Normalization|Batch Normalization]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Weight Initialization|Weight Initialization]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Data Augmentation|Data Augmentation]]
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Vanishing and Exploding Gradients|Vanishing and Exploding Gradients]]
