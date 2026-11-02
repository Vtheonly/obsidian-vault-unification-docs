---
title: ViT Architecture
type: concept
aliases:
  - ViT
  - Vision Transformer
tags:
  - vision-transformer
  - vit
  - transformer-encoder
  - patch-embedding
  - image-classification
  - multimodal
sources:
  - "04. ViT Architecture and Design Decisions"
  - "13 - Vision Transformer (ViT)"
created_index: 38
---

The Vision Transformer (ViT) treats image recognition as sequence modeling: an image is cut into patches, each patch is embedded as a token, and a standard Transformer encoder — the same design BERT uses for text — processes the token sequence. The only vision-specific component is the patch embedding at the front; everything behind it is a plain Transformer stack, which is why ViT inherits the way language Transformers scale with data and compute. This note assembles the full architecture, justifies each design decision, surveys the standard model sizes and the variant family, and records the practical concerns — resolution changes, preprocessing, multimodal use, and production failure modes — that come with running ViTs for real.

> [!info] TL;DR
> ViT (Dosovitskiy et al. 2020) applies the Transformer to images by splitting an image into patches, embedding each patch as a token, and processing with a standard Transformer encoder. Now the dominant architecture for vision, especially at scale.

## The idea: patches as tokens

Images are 2D grids of pixels — far too many tokens for naive Transformer attention. ViT's solution: **break the image into patches**, flatten each patch, and project to an embedding:

```
Image (224x224x3) → 14x14 = 196 patches of 16x16x3
                  → each patch flattened to 768-dim vector (via linear projection)
                  → add positional embedding
                  → process with Transformer encoder (12-32 layers)
                  → output: 196 contextualized patch embeddings
```

For classification, prepend a `[CLS]` token and use its final-layer representation (see [[CLS Token]]); the full tokenization pipeline is detailed in [[Patch Tokenization]]. ViT adapts the encoder architecture of [[The Transformer]], and the CNN alternatives it displaced at scale are surveyed in [[06 - Computer Vision/Architecture and Connectivity/Evolution of CNN Architectures|Evolution of CNN Architectures]].

## The full architecture

Putting the pieces together, here is the complete ViT, shown for ViT-Base:

```
Image (224×224×3)
    │
    ▼
┌─────────────────────────────┐
│ Patch Extraction + Embed    │  Conv2d(3, 768, kernel=16, stride=16)
│ → (196, 768) patch tokens   │  + learned 1D positional embeddings
│ + CLS token prepended        │  + learned CLS token
│ → (197, 768) input sequence  │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ Transformer Encoder Block 1 │  Multi-Head Self-Attention (12 heads)
│                             │  + Residual + LayerNorm
│                             │  Feedforward (3072 hidden, GELU)
│                             │  + Residual + LayerNorm
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ Transformer Encoder Block 2 │  (same structure)
└─────────────────────────────┘
    │
   ...
    │
    ▼
┌─────────────────────────────┐
│ Transformer Encoder Block 12│  (ViT-Base has 12 blocks)
└─────────────────────────────┘
    │
    ▼
    Extract CLS token's final representation (768-dim)
    │
    ▼
┌─────────────────────────────┐
│ LayerNorm                   │
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│ Linear Head (768 → num_classes)│
└─────────────────────────────┘
    │
    ▼
Class logits
```

This is ViT-Base: 12 layers, $d = 768$, 12 heads, $d_k = 64$, FFN hidden = 3072 ($4d$), ~86M parameters. The architecture is *exactly* a BERT-base Transformer encoder, with the only vision-specific component being the patch embedding — ViT is "BERT for images": the same encoder-only architecture as [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]], with different input tokenization. Each encoder block is the standard two-sublayer unit described in [[Transformer Block]] (see also [[Multi-Head Attention]] and [[Feed-Forward Network]]).

The same pipeline, sketched end-to-end and generalized beyond classification:

```
Image
  ↓
Patch extraction (16x16 patches)
  ↓
Linear projection to d_model dimensions (patch embedding)
  ↓
Add positional embeddings (learned, 2D)
  ↓
Optional: prepend [CLS] token
  ↓
Transformer encoder (N blocks)
  ↓
For classification: [CLS] representation → linear head
For dense tasks: patch representations → decoder
```

Two readings of that sketch deserve comment. It labels the positional embeddings "2D," whereas the original ViT in fact uses learned **1D** positional embeddings — one vector per position in the flattened patch sequence — which experiments show is sufficient (the section on positional embeddings below gives the full argument); 2D or factorized encodings belong to later variable-resolution variants such as DeiT and Swin. And the sketch's "196 contextualized patch embeddings" output refers to the patches themselves: with the classification token prepended, the sequence the encoder actually processes is 197 tokens (196 patches + CLS). Note also the dense-task branch — for detection or segmentation, the patch representations feed a decoder rather than a classification head.

## The patchify operation in detail

The patchify step is the conceptual bridge from images to sequences. Given an image $X \in \mathbb{R}^{H \times W \times C}$ and patch size $P$, you split $X$ into $N = (H/P) \cdot (W/P)$ non-overlapping patches, each of shape $P \times P \times C$. Each patch is flattened to a $P^2 C$-vector and projected to $d_{\text{model}}$ via a linear layer.

For the standard ViT-Base/16 on 224×224 images: $N = 14 \times 14 = 196$ patches, $P=16$, $C=3$, so each flattened patch has $16 \cdot 16 \cdot 3 = 768$ elements — conveniently equal to $d_{\text{model}} = 768$, so the projection is essentially identity plus a learned bias. This is not a coincidence; the patch size and $d_{\text{model}}$ were chosen to make the math clean.

Equivalent implementations:

```python
# Option A: Convolution with stride = patch size (most common)
self.patch_embed = nn.Conv2d(3, d_model, kernel_size=16, stride=16)
# x: (B, 3, 224, 224) → (B, d_model, 14, 14) → reshape (B, 196, d_model)

# Option B: Explicit unfold + linear
patches = x.unfold(2, 16, 16).unfold(3, 16, 16)  # (B, 3, 14, 14, 16, 16)
patches = patches.contiguous().view(B, 196, 768)
tokens = self.proj(patches)  # (B, 196, d_model)
```

The Conv2d version is preferred — it's a single fused op and is faster. The unfold version is more pedagogical.

## The three standard variants

| Model | Layers | $d$ | Heads | FFN | Params | Patches (224px) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ViT-Tiny | 12 | 192 | 3 | 768 | 5.5M | 196 |
| ViT-Small | 12 | 384 | 6 | 1536 | 22M | 196 |
| ViT-Base | 12 | 768 | 12 | 3072 | 86M | 196 |
| ViT-Large | 24 | 1024 | 16 | 4096 | 307M | 196 |
| ViT-Huge | 32 | 1280 | 16 | 5120 | 632M | 196 |

Notice that the patch count (196) stays constant across model sizes — the model scales by deepening and widening, not by adding more patches. This is because the $O(N^2)$ attention cost makes adding patches expensive: going from 196 to 784 patches (16×16 to 8×8) quadruples the attention cost.

For higher-resolution variants (ViT-L/384, ViT-H/14), the patch size is reduced (14×14 instead of 16×16) or the image is larger (384px instead of 224px), increasing the patch count and the attention cost but providing finer spatial detail.

## Computational complexity

For an image of $N$ patches with hidden size $d$ and $L$ layers, self-attention costs $O(N^2 \cdot d)$ per layer (the same quadratic complexity as text attention), the FFN costs $O(N \cdot d^2)$ per layer, and the total is $O(L \cdot N^2 \cdot d + L \cdot N \cdot d^2)$.

For 224×224 images with 16×16 patches, $N=196$ — totally fine. For 1024×1024 images: $N=4096$, $N^2 \approx 17M$ — memory becomes the bottleneck. This is why high-resolution vision models use:

- **Windowed attention** (Swin): $O(N \cdot w^2)$ instead of $O(N^2)$.
- **Hierarchical downsampling** (Swin, ViTDet): reduce $N$ after early layers.
- **Linear attention** (Perceiver, Hyena): replace softmax with a kernelized approximation.

The attention-family treatments of these ideas are [[Sliding Window Attention]] and [[Linear Attention]].

## Design decisions, justified

Each component of the ViT is a deliberate choice, often different from the original NLP Transformer. Let's justify the major ones:

### Why GELU instead of ReLU in the FFN?

The original Transformer used ReLU in the FFN. BERT switched to GELU (Gaussian Error Linear Unit — activation functions are surveyed in [[06 - Computer Vision/Core Operators and Geometry/Activation and Pooling Layers|Activation and Pooling Layers]]), and ViT followed BERT. GELU is smoother than ReLU (no sharp kink at 0) and empirically performs slightly better in Transformers. The difference is small, but GELU has become the de facto standard for Transformer FFNs.

### Why learned 1D positional embeddings?

The original NLP Transformer used fixed sinusoidal encodings. ViT uses **learned 1D** positional embeddings. Three reasons:

- **Learned > sinusoidal for vision.** Empirically, learned embeddings slightly outperform sinusoidal for ViTs, probably because the 2D structure of patches is not well-captured by the 1D sinusoid pattern.
- **1D is sufficient.** You might expect 2D positional embeddings (one for row, one for column) to be necessary for images, but experiments show 1D is enough — the model learns the 2D structure from the 1D ordering.
- **Fixed image size.** ViTs are typically trained at a fixed resolution (224px), so the maximum sequence length is known. Learned embeddings are fine for fixed-length inputs; sinusoidal's extrapolation advantage is irrelevant.

The same argument runs the other way around: image patches have a clear 2D structure, but a 1D positional embedding is sufficient because the model can learn the 2D layout from the data; sinusoidal 1D positional encodings don't naturally encode 2D structure; and learned embeddings are simpler and empirically equivalent or better. For models that need to handle variable resolution (DeiT, Swin), rotary or factorized 2D encodings are used instead — see [[Positional Encoding]], [[Sinusoidal and Learned Positional Encodings]], and [[RoPE]].

### Why Pre-LN instead of Post-LN?

The original Transformer used Post-LN (LayerNorm after the residual addition). ViT follows BERT and GPT in using **Pre-LN** (LayerNorm before the sublayer). Pre-LN is more stable for training deep stacks (12+ layers) because the residual path is purely additive, preserving gradient flow. Post-LN requires careful warmup and is prone to instability in deep models. The full comparison lives in [[Pre-Norm vs Post-Norm]] and [[Residual Connections]].

### Why the CLS token instead of GAP?

The CLS token is a learnable readout that adapts to the task, slightly more expressive than fixed averaging. The full story — including when global average pooling is the better choice — is in [[CLS Token]].

### Why no dropout in the patch embedding?

The patch embedding is a single linear transformation; dropout here would corrupt the input before the Transformer can process it. Dropout is applied *inside* the Transformer blocks (on attention weights and FFN outputs) but not on the patch embeddings or positional embeddings.

### Why 16×16 patches?

The patch size $P = 16$ is a compromise:

- $P = 32$: too coarse — each patch averages 1024 pixels, losing fine detail. Sequence length 49 (very cheap).
- $P = 16$: good balance — each patch covers 256 pixels, fine enough for most ImageNet classes. Sequence length 196 (manageable).
- $P = 8$: too fine — each patch covers 64 pixels, providing detail but making the sequence length 784 (expensive attention).

For higher-resolution tasks (medical imaging, satellite), smaller patches (8×8 or 14×14) are used with appropriate compute budgets.

## Positional-embedding interpolation for variable resolution

For **variable resolution** (e.g., processing 224×224 and 384×384 with the same model), the learned embeddings need to be interpolated. The standard technique:

```python
# Interpolate positional embeddings to new resolution
import torch.nn.functional as F
pos_embed = model.pos_embed  # (1, 197, d)  — 196 patches + CLS
new_N = (new_size // patch_size) ** 2
old_grid = int((pos_embed.shape[1] - 1) ** 0.5)  # 14
new_grid = int(new_N ** 0.5)                      # e.g., 24
pos_tokens = pos_embed[:, 1:]  # drop CLS
pos_tokens = pos_tokens.reshape(1, old_grid, old_grid, d).permute(0, 3, 1, 2)
pos_tokens = F.interpolate(pos_tokens, size=(new_grid, new_grid), mode='bicubic', align_corners=False)
pos_tokens = pos_tokens.permute(0, 2, 3, 1).reshape(1, new_N, d)
new_pos_embed = torch.cat([pos_embed[:, :1], pos_tokens], dim=1)
```

This bicubic interpolation works well — fine-tuning a 224×224 model at 384×384 is a standard trick to boost accuracy by ~1-2%. The model adapts quickly because the patch embeddings are resolution-agnostic; only the position information changes.

## The training recipe

The ViT training recipe reveals a lot about the model's data hunger:

| Stage | Dataset | Detail |
| :--- | :--- | :--- |
| Pretraining | JFT-300M (300M images, 18K classes) | The original ViT was pretrained on Google's proprietary massive dataset. Without this, ViT underperforms ResNet. |
| Fine-tuning | ImageNet-1K (1.3M images, 1K classes) | Replace the classification head with a fresh one for the target classes, fine-tune the whole model. |
| Resolution bump | ImageNet-1K at 384px | After fine-tuning at 224px, fine-tune again at higher resolution for a final accuracy boost. |

The reliance on JFT-300M was the original ViT's biggest limitation. Subsequent work (DeiT, MAE, DINO) made ViTs competitive on ImageNet-1K alone through aggressive augmentation and self-supervised pretraining, but the original recipe needed the massive dataset. Why the data hunger exists at all is the subject of [[Inductive Bias]].

## What ViT learns — attention visualizations

When you visualize the attention patterns of a trained ViT, you find that **early layers** attend to local neighborhoods (patches near the query patch), even though there is no architectural constraint forcing this — the model *learns* locality from data. **Middle layers** attend to semantically related patches regardless of distance — e.g., a patch containing a dog's ear attends to other patches containing ears or fur. **Late layers** attend to the CLS token and to the most discriminative patches for the classification task.

This is striking: the ViT, with no built-in locality prior, *discovers* locality in its early layers. The CNN gets locality for free; the ViT learns it. This is the data-driven-learning advantage — but it only works because the ViT was trained on enough data (JFT-300M) to discover the prior.

## Why ViT replaced CNNs

At scale, ViT beats ResNet-style CNNs on ImageNet and downstream tasks, for four reasons. **Global attention** captures long-range dependencies that CNNs need many layers to learn. ViT **scales better** with data and compute. The architecture is **simpler** — no convolution-specific design choices. And it has **multi-modal compatibility** — patches are tokens, so they can mix with text tokens.

But ViT has weaknesses. It is **data-hungry** — it needs large datasets to learn what CNNs learn implicitly (translation invariance, locality). It is **less efficient on small images** — CNNs win for 32x32 (CIFAR). And it has **no built-in inductive bias** for vision — the model must learn everything (see [[Inductive Bias]]). Despite these, the trend is clear: **ViTs have replaced CNNs as the default image encoder for large-scale vision tasks**, just as Transformers replaced RNNs for sequence tasks. CNNs remain relevant for small-data regimes and edge deployment, but the center of gravity has shifted to attention-based architectures.

## Variants and successors

The ViT spawned a large family. **DeiT** (Touvron et al. 2021) makes ViT competitive on ImageNet-1K alone, via aggressive augmentation and CNN-teacher distillation. **Swin Transformer** (Liu et al. 2021) is a hierarchical architecture with shifted-window attention, reintroducing multi-scale priors; it is state-of-the-art on dense prediction tasks (detection, segmentation). **MAE** (He et al. 2022) is masked-autoencoder pretraining for ViTs — mask 75% of patches, reconstruct them — providing a strong self-supervised pretraining objective that works on ImageNet-1K alone. The **DINO** line of self-supervised ViTs produces features that rival supervised ones across many tasks: DINO (Caron et al. 2021) introduced the self-distillation approach, DINOv2 (Oquab et al. 2023) scaled it into a general-purpose feature extractor, and DINOv3 (2024) extended it further. **CLIP** (Radford et al. 2021) applies the co-train recipe — an image encoder (a ViT) and a text encoder (a Transformer) trained together on 400M image-text pairs — producing image features aligned with language: the most common use of a ViT as one tower of a vision-language contrastive model, and the backbone of modern multimodal AI. **SigLIP** (Zhai et al. 2023) is an improved CLIP with sigmoid loss; it is better at scale.

The wider landscape at a glance:

| Variant       | Year | Key Innovation                                  | Best For                              |
|---------------|------|-------------------------------------------------|---------------------------------------|
| ViT           | 2020 | Patches as tokens, plain Transformer encoder    | Large-scale classification            |
| DeiT          | 2021 | Distillation token, strong augmentation         | Data-efficient training (ImageNet only)|
| Swin          | 2021 | Shifted window attention, hierarchical          | Dense prediction (detection, segmentation) |
| ViTDet        | 2022 | Plain ViT for detection via simple neck         | Detection without hierarchical backbone |
| BEiT          | 2021 | Masked image modeling (BERT for images)         | Self-supervised pretraining           |
| MAE           | 2022 | Masked autoencoders (75% masking)               | Efficient self-supervised pretraining |
| DINOv2/v3     | 2023-24 | Self-distillation + image-level contrastive   | General-purpose frozen features       |
| SigLIP        | 2023 | Sigmoid loss (vs softmax) for CLIP training     | Image-text alignment at scale         |
| EVA / EVA-02  | 2023-24 | CLIP-initialized, weakly-supervised scaling  | State-of-the-art open vision encoder  |
| NaViT         | 2023 | Native aspect ratio, no resizing                | Variable-resolution training          |

## ViT in multimodal models

Modern multimodal LLMs (LLaVA, Qwen-VL, GPT-4V) use a ViT to encode images:

```
Image → ViT → patch embeddings → projector → LLM token space → LLM
```

The ViT produces image "tokens" that the LLM attends to via cross-attention (or treats as additional input tokens).

The vision encoders in 2024-2026 VLMs (LLaVA-NeXT, Qwen2-VL, InternVL, Cambrian) typically use an **Open-CLIP ViT-L/14@336** or **SigLIP-SO/14@384** as the backbone, keep the vision encoder frozen or LoRA-tuned, map ViT tokens into the LLM embedding space with a 2-4 layer MLP projector (or a Q-Former for BLIP-2), and optionally use dynamic resolution (NaViT-style) to handle arbitrary aspect ratios. A typical LLaVA-NeXT setup:

```python
class LlavaVisionEncoder(nn.Module):
    def __init__(self, llm_dim=4096):
        super().__init__()
        self.vit = create_vit("siglip-so400m-patch14-384")  # frozen
        self.projector = nn.Sequential(
            nn.Linear(self.vit.dim, llm_dim),
            nn.GELU(),
            nn.Linear(llm_dim, llm_dim),
        )
    def forward(self, images):
        with torch.no_grad():
            patch_features = self.vit(images)  # (B, N_patches, vit_dim)
        return self.projector(patch_features)  # (B, N_patches, llm_dim)
```

The number of image tokens depends on resolution: 384×384 / 14² = 27×27 = 729 tokens, or 1024×1024 → 5329 tokens. This is why high-res VLMs are expensive — each image can consume thousands of context tokens. Modern ViT variants also use grouped attention for efficiency (see [[GQA MQA and MLA]]), and the same patchify idea extends beyond classification and VLMs into diffusion models (DiT, FLUX patchify latents into Transformer tokens).

## Running ViTs in practice

ViT is the **standard vision encoder**; every multimodal LLM uses a ViT or ViT-derivative. The "patches as tokens" idea is the conceptual basis for treating any modality (audio, video, 3D) as a sequence. And for **RAG with images** (PDFs with figures, screenshots, diagrams), ViT-based encoders produce the embeddings.

A minimal classification example with the `google/vit-base-patch16-224` checkpoint:

```python
from transformers import ViTForImageClassification, ViTImageProcessor
from PIL import Image
import torch

processor = ViTImageProcessor.from_pretrained("google/vit-base-patch16-224")
model = ViTForImageClassification.from_pretrained("google/vit-base-patch16-224")

image = Image.open("cat.jpg").convert("RGB")
inputs = processor(images=image, return_tensors="pt")
outputs = model(**inputs)
logits = outputs.logits
predicted_class = logits.argmax(-1)
```

In production: for **image classification** with sufficient data, fine-tune a pretrained ViT — the HuggingFace `timm` library has hundreds of variants. For **embedding images in RAG**, use DINOv2 or SigLIP, which produce general-purpose image embeddings. For **multimodal LLMs** (LLaVA, Qwen-VL), the ViT is the image encoder, so choose a model with a strong ViT. **Quantization**: ViT quantizes well to INT8, and most serving frameworks support it. **Patch size matters**: smaller patches = more tokens = more compute; 16x16 is standard, 14x14 for higher resolution.

Four pitfalls account for most silent quality failures. **Wrong image preprocessing** — ViT expects specific normalization (ImageNet stats typically); a mismatch causes silent quality loss. **Image size mismatch** — ViT's positional embeddings are tied to the training resolution, so resizing requires interpolating them (see the interpolation technique above). **Too few patches for high-res** — for fine-grained tasks, use a smaller patch size or higher resolution. **Forgetting `[CLS]` for classification** — global average pooling works too, but `[CLS]` is the ViT default.

The recurring failure modes in production:

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Quality drop on real images vs benchmarks | Wrong normalization stats | Use ImageNet stats or model-specific stats from the model card |
| Quality varies wildly with image size | Positional embedding not interpolated | Use bicubic interpolation when resizing |
| Image tokens leak into text generation | Chat template misconfigured | Check the chat template handles `<image>` tokens correctly |
| Out-of-memory on long-context VLM | Too many image tokens at high res | Tile the image (LLaVA-NeXT) or use lower resolution |
| ViT works on 224 but fails on 384 | Forgot to interpolate pos embeddings | Always interpolate when changing resolution |
| Different results from `transformers` vs `timm` | Different default preprocessing | Use the exact processor for the model you loaded |

## Interview questions

**How does ViT convert an image into a sequence?** Patchify — split the image into non-overlapping $P \times P$ patches, flatten each, linearly project to $d_{\text{model}}$, add positional embeddings, and prepend an optional `[CLS]` token. For 224×224 with $P=16$, this gives 196 patch tokens.

**Why does ViT need more data than CNNs to train from scratch?** CNNs have built-in inductive biases — locality (convolution kernel), translation invariance (weight sharing), and hierarchical feature composition. ViT has none of these — attention is permutation-invariant (positional embeddings add order, not locality). Without these priors, ViT must learn them from data, requiring ~10-100× more images than CNNs to match performance.

**How do you fine-tune a ViT pretrained at 224 resolution on 384 resolution images?** Bicubic-interpolate the learned positional embeddings to the new grid size (14×14 → 24×24 for 384), keep the patch size constant (16), and fine-tune for a few epochs. The model adapts quickly because the patch embeddings are resolution-agnostic; only the position information changes.

**When would you choose Swin over ViT?** For dense prediction tasks (object detection, semantic segmentation, panoptic). Swin's hierarchical features (multi-scale) and windowed attention ($O(N)$ instead of $O(N^2)$) make it dramatically more efficient for high-resolution outputs. For classification or as a VLM encoder, plain ViT is usually better — Swin's hierarchical structure complicates the projector.

**Why is the [CLS] token used for classification instead of global average pooling?** Two reasons. (1) The [CLS] token is explicitly trained to aggregate information for the classification task (it has no positional content of its own, so it must learn to attend globally). (2) Global average pooling averages all patch tokens, including those far from the salient object, which can dilute signal. Empirically, [CLS] is ~0.5% better on ImageNet, but GAP works nearly as well and is simpler.

**How many tokens does a 1024×1024 image produce with patch size 14?** $(1024/14)^2 \approx 73^2 = 5329$ tokens. With $d_{\text{model}}=1152$, this is 6.1M elements per image — significant context budget. This is why VLMs use dynamic resolution (NaViT) or tiling (LLaVA-NeXT) to manage cost.

## Further reading

The primary papers are Dosovitskiy et al. (2020), *An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale* (the original ViT); Touvron et al. (2021), *Training data-efficient image transformers & distillation through attention* (DeiT); Liu et al. (2021), *Swin Transformer: Hierarchical Vision Transformer using Shifted Windows*; and Radford et al. (2021), *Learning Transferable Visual Models From Natural Language Supervision* (CLIP).

## See also

- [[Attention and Transformers MOC]] — area overview
- [[Patch Tokenization]], [[CLS Token]], [[Inductive Bias]] — the ViT pipeline and its data-requirements analysis
- [[The Transformer]], [[Transformer Block]], [[Multi-Head Attention]], [[Feed-Forward Network]], [[Residual Connections]], [[Normalization Layers]] — the encoder stack ViT reuses
- [[Positional Encoding]], [[Sinusoidal and Learned Positional Encodings]], [[RoPE]] — position representations, learned 1D and beyond
- [[Pre-Norm vs Post-Norm]] — the normalization placement ViT inherits from BERT and GPT
- [[08 - Attention and Transformers/Transformer Architecture/BERT|BERT]] — ViT is essentially "BERT for images"
- [[GQA MQA and MLA]], [[Sliding Window Attention]], [[Linear Attention]] — efficiency tools used by ViT descendants
- [[06 - Computer Vision/Architecture and Connectivity/Evolution of CNN Architectures|Evolution of CNN Architectures]] and [[06 - Computer Vision/CNN Foundations and Philosophy/Introduction and Foundations of CNNs|Introduction and Foundations of CNNs]] — the CNN lineage ViT replaced at scale
- [[06 - Computer Vision/Core Operators and Geometry/Activation and Pooling Layers|Activation and Pooling Layers]] — activations (GELU vs ReLU) and pooling (GAP) in the CNN context
