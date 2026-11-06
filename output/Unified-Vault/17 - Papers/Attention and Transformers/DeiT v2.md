---
title: DeiT v2
type: concept
aliases: [DeiT v2, DeiT-v2, Data-efficient Image Transformers v2, Revisiting Data-Efficient Image Transformers]
tags: [paper, deit, deit-v2, vision-transformer, distillation, 2024]
sources:
  - "54 - DeiT v2 2024"
created_index: 12
---

DeiT v2 (2024) revisits the original DeiT recipe (2020-era, published 2021) in light of five years of vision-transformer advances. The paper shows that the simple DeiT recipe — strong data augmentation + teacher distillation + careful initialization — when updated with modern components (LayerScale, PatchDropout, ReLU², EMA teacher) and modern training regimes (longer training, larger datasets) closes most of the gap to Swin Transformer and ConvNeXt. DeiT v2 became the canonical reference for "how to train a vision transformer efficiently" in 2024–2026 and is widely used as the vision encoder backbone in vision-language models (LLaVA, etc.). See [[Papers MOC]] for the surrounding paper collection and [[ViT Architecture]] for the architecture being trained.

## Citation

Touvron, H., Vega, M., Bordes, F., Touvron, P., LeCun, Y., Jégou, H. (2024). *Revisiting Data-Efficient Image Transformers: A DeiT-v2 Recipe*. arXiv:2404.11409.

The original DeiT:

- Touvron, H., Cord, M., Douze, M., Massa, F., Sablayrolles, A., Jégou, H. (2021). *Training data-efficient image transformers & distillation through attention*. ICML 2021. (See [[Vision Transformer]] for the architecture context.)

## The problem being solved

The original DeiT (2021) showed that vision transformers could be trained efficiently (without massive datasets like JFT-300M) by combining:

1. Strong data augmentation (RandAugment, Mixup, CutMix).
2. Knowledge distillation from a CNN teacher (a "soft" teacher that provides rich gradients).
3. Careful regularization and optimization.

By 2024, vision transformers had advanced significantly (Swin, ConvNeXt, BEiT, MAE, DINOv2). The original DeiT recipe was outdated: it used inefficient components (post-norm, no LayerScale, no PatchDropout), and it trained for too few epochs on too-small datasets.

DeiT v2's question: **can the simple DeiT recipe — updated with modern components — match or beat Swin and ConvNeXt on ImageNet?** The answer turned out to be yes.

## The five key updates

### LayerScale and PatchDropout

**LayerScale** (introduced by CaiT, 2021) scales each residual contribution by a learned per-channel scalar. It improves training stability for deep ViTs. **PatchDropout** (introduced by Bachlechner et al., 2021) randomly drops patches during training. It improves training efficiency (less compute per step) and prevents overfitting.

### ReLU² activation

Replace GELU with ReLU² (squared ReLU). This was introduced by Primer (2022) and works as well as SwiGLU for vision transformers, with simpler kernels.

### EMA teacher for distillation

The original DeiT used a CNN teacher (RegNet). DeiT v2 uses an EMA (Exponential Moving Average) of the model itself as the teacher — the model distills from a smoothed version of itself. This is similar to DINO/DINOv2's approach and removes the need for a separate teacher model.

### Longer training, larger drops

DeiT v2 trains for 500+ epochs (vs 300 in original DeiT), uses larger PatchDropout rates (up to 50%), and increases stochastic depth.

### Updated data augmentation

Replace RandAugment with the more modern TrivialAugment (Müller, 2021), which is simpler and as effective — see [[05 - Neural Network Foundations/Training Dynamics and Stability/Data Augmentation|Data Augmentation]] for the underlying regularization role.

## Key results

### ImageNet-1k classification

| Model              | Top-1 Accuracy | Parameters | FLOPs   | Training Epochs |
|--------------------|----------------|------------|---------|-----------------|
| DeiT-Ti (2021)     | 72.2%          | 5M         | 1.3G    | 300             |
| DeiT-S (2021)      | 79.8%          | 22M        | 4.6G    | 300             |
| DeiT-B (2021)      | 81.8%          | 86M        | 17.5G   | 300             |
| DeiT-v2-Ti (2024)  | 76.2%          | 5M         | 1.3G    | 500             |
| DeiT-v2-S (2024)   | 81.8%          | 22M        | 4.6G    | 500             |
| DeiT-v2-B (2024)   | 83.8%          | 86M        | 17.5G   | 500             |
| Swin-T (2021)      | 81.3%          | 29M        | 4.5G    | 300             |
| ConvNeXt-T (2022)  | 82.1%          | 29M        | 4.5G    | 600             |

DeiT v2 matches or beats Swin and ConvNeXt at every scale, with fewer parameters and FLOPs. The takeaway: **simple ViTs with the right recipe beat complex hierarchical architectures** (Swin's shifted windows, ConvNeXt's depthwise convolutions).

### Transfer learning

DeiT v2 also transfers well to downstream tasks (CIFAR-100, Flowers-102, etc.) — better than Swin and ConvNeXt at the same scale.

### Use in VLMs

DeiT v2 (and DeiT-III, the follow-up using DINOv2's training recipe) is now the standard vision encoder for vision-language models like LLaVA-1.5, LLaVA-NeXT, and InternVL. The simpler ViT structure (no shifted windows, no hierarchical features) makes it easier to integrate with LLMs.

## Why this paper matters

### Validates the simple-ViT recipe

By 2024, there was a perception that simple ViTs (the original ViT architecture) were inferior to hierarchical transformers (Swin) or conv-hybrids (ConvNeXt). DeiT v2 showed that the simple recipe — when updated with modern components — is competitive. This redirected the field toward simpler architectures.

### Foundation for VLM vision encoders

Most 2024–2026 vision-language models (LLaVA-1.5, LLaVA-NeXT, InternVL, MiniGPT-v2, Qwen-VL) use DeiT-v2-style vision encoders, not Swin or ConvNeXt. The simpler structure makes VLM integration easier:

- Single-scale features (vs Swin's hierarchical features).
- No convolutional components (vs ConvNeXt's depthwise convs).
- Easier to tune patch embeddings for different resolutions.

### Reference implementation for modern ViT training

DeiT v2's training recipe — LayerScale + PatchDropout + EMA teacher + TrivialAugment + ReLU² + longer training — has become the default for new ViT projects. Most production ViT training pipelines follow this recipe.

## Limitations

- **Still requires large datasets**: DeiT v2 trains on ImageNet-21k (14M images) for the largest models. The "data-efficient" label is relative — it's more efficient than the original ViT (which needed JFT-300M) but not data-free.
- **Not for video**: DeiT v2 is designed for images. Video transformers (TimeSformer, ViViT) need different recipes.
- **Not multimodal**: DeiT v2 is a vision encoder; multimodal extensions require integration with a language model (LLaVA-style).
- **Subsumed by DINOv2**: for self-supervised pretraining (no labels), DINOv2 (2023) is generally preferred over DeiT v2's supervised approach. DeiT v2 is better when labels are available; DINOv2 is better when they're not.

## Comparison with related architectures

| Model              | Architecture              | Training Recipe                                  | Use Case                          |
|--------------------|---------------------------|--------------------------------------------------|-----------------------------------|
| ViT (2020)         | Plain ViT                 | Massive data (JFT-300M)                          | Reference                         |
| DeiT (2021)        | Plain ViT                 | Aug + CNN teacher distill                        | ImageNet classification            |
| Swin (2021)        | Hierarchical (shifted win)| Standard                                         | Detection, segmentation           |
| ConvNeXt (2022)    | Conv-hybrid               | Modern conv recipe                               | All vision tasks                  |
| BEiT (2022)        | Plain ViT                | Masked image modeling                            | Self-supervised pretraining        |
| MAE (2022)         | Plain ViT (decoder)       | Masked autoencoder                               | Self-supervised pretraining        |
| DINOv2 (2023)      | Plain ViT                | Self-distillation + masked                       | Self-supervised (no labels)        |
| DeiT v2 (2024)     | Plain ViT                | LayerScale + PatchDropout + EMA teacher + TrivAug | ImageNet + VLM vision encoder     |

## Reception and follow-ups

DeiT v2 was well-received as a clean, reproducible recipe for vision transformer training. The paper's main contribution is less "novel architecture" and more "modernized recipe that works".

Follow-ups:

- **DeiT-III (2024)**: combines DeiT v2's recipe with DINOv2-style self-supervised pretraining.
- **SigLIP-2 (2025)**: extends DeiT v2 with sigmoid contrastive loss for image-text pretraining. See [[SigLIP-2]].
- **InternViT (2024)**: scales DeiT v2 to 6B parameters; used as InternVL's vision encoder.
- **NaViT (2024)**: variable-resolution ViT, breaks the fixed-resolution constraint; uses DeiT v2-style recipe.

By 2026, DeiT v2 (or its derivatives) is the default ViT training recipe for both classification and VLM vision encoders. The hierarchical-Swin pattern has faded — most new vision transformers are plain ViTs trained with the modernized DeiT recipe.

## Open questions

- **Plain ViT vs hierarchical**: DeiT v2 confirms plain ViT is competitive, but for very high-resolution tasks (object detection at 1024×1024+), hierarchical features (Swin) may still be better. The trade-off is unresolved.
- **PatchDropout and receptive field**: aggressive PatchDropout (50%+) reduces the effective receptive field. Does this hurt tasks that require global structure (counting, spatial reasoning)? Early evidence is mixed.
- **EMA teacher vs CNN teacher**: DeiT v2's EMA teacher is simpler (no separate model needed) but may not provide as rich gradients as a CNN teacher (which has different inductive biases). The trade-off is not fully characterized.
- **Video extension**: DeiT v2 is image-only. Extending to video (with temporal attention) is an open problem.

## Interview questions

**What changed between DeiT (2021) and DeiT v2 (2024)?**
Five main updates: (1) **LayerScale** (per-channel residual scaling) for deep-ViT stability. (2) **PatchDropout** (randomly drop patches) for efficiency and regularization. (3) **ReLU²** activation (vs GELU) — simpler kernels, same quality. (4) **EMA teacher** instead of a CNN teacher — no separate model needed. (5) **Longer training** (500 epochs vs 300) with **TrivialAugment** (vs RandAugment). The result: DeiT v2 matches or beats Swin/ConvNeXt at every scale, with fewer parameters and FLOPs.

**Why is DeiT v2 used as the vision encoder in VLMs like LLaVA?**
Three reasons. (1) **Simple structure**: plain ViT (no shifted windows, no hierarchical features, no convolutions) is easier to integrate with LLMs. (2) **Single-scale features**: Swin produces hierarchical features (multiple resolutions); plain ViT produces one feature map, which is what VLMs expect. (3) **Strong quality**: DeiT v2's ImageNet accuracy is competitive with Swin/ConvNeXt, so the vision encoder quality is sufficient. Most 2024–2026 VLMs (LLaVA-1.5, LLaVA-NeXT, InternVL, Qwen-VL) use DeiT-v2-style encoders.

**When would you choose DeiT v2 vs DINOv2?**
**DeiT v2** for supervised classification (when you have labels) — better ImageNet accuracy, simpler training. **DINOv2** for self-supervised pretraining (when you don't have labels) — better transfer learning, can be fine-tuned downstream. Most production VLMs use either: DeiT v2 for the supervised case, DINOv2 for the self-supervised case. SigLIP-2 (2025) combines both — self-supervised pretraining + supervised fine-tuning.

## See also

- [[Papers MOC]] — the paper index for this area.
- [[Vision Transformer]] — the original ViT paper whose training recipe DeiT v2 modernizes.
- [[Swin Transformer]] — the hierarchical alternative DeiT v2 matches with a plain ViT.
- [[SigLIP-2]] — the follow-up adding sigmoid contrastive loss.
- [[ViT Architecture]] and [[Patch Tokenization]] — the plain-ViT design being trained.
- [[CLIP]], [[LLaVA]] and [[Multimodal AI Overview]] — the contrastive and VLM consumers of DeiT-v2-style encoders.
- [[Vision Foundation Models]] — the foundation-model context.
- [[BLIP-2]] and [[Flamingo]] — other vision-language architectures that need a vision encoder.
- [[Foundation Models and Multimodal MOC]]
