---
title: Swin Transformer
type: concept
aliases: [Swin Transformer 2021, Liu 2021, Shifted Window Attention, Swin, Swin Transformer V2]
tags: [paper, swin, vision, hierarchical-transformer, computer-vision, efficient-attention]
sources:
  - "23 - Swin Transformer 2021"
created_index: 1
---

Swin Transformer introduced **shifted-window attention** — attention is computed within local windows, and the windows are shifted between layers so that information flows across window boundaries. Combined with a hierarchical architecture (patch merging reduces resolution as depth increases), Swin provides multi-scale features like CNNs while maintaining Transformer expressivity. Swin became the standard for dense vision tasks (detection, segmentation) where ViT's fixed resolution and lack of hierarchy were limitations. This note covers the problem it solved, its key mechanisms, its results, why it worked, its limitations, and its successors — including Swin Transformer V2, its direct scaling successor. See [[Attention and Transformers MOC]] for the surrounding area and [[ViT Architecture]] for the flat predecessor it improves on.

## Citation

Liu, Z., Lin, Y., Cao, Y., Hu, H., Wei, Y., Zhang, Z., Lin, S., & Guo, B. (2021). *Swin Transformer: Hierarchical Vision Transformer using Shifted Windows*. ICCV 2021 (Best Paper). arXiv:2103.14030.

## The problem being solved

[[ViT Architecture|ViT]] (2020) showed that Transformers work for vision, but it had two limitations for dense prediction tasks (object detection, semantic segmentation):

1. **Fixed resolution**: ViT processes images at a single resolution (e.g., 224×224 → 14×14 [[Patch Tokenization|patches]]). Dense prediction tasks require multi-scale features — coarse features for global context, fine features for localization. ViT's flat architecture doesn't provide this.

2. **Global attention cost**: ViT computes attention over all patches, which is O(N²) in the number of patches. For high-resolution images (e.g., 800×1333 for COCO detection), this is prohibitively expensive.

CNNs solve both problems via hierarchical architectures (ResNet, FPN) that produce features at multiple resolutions — see [[Evolution of CNN Architectures]] for how that hierarchy evolved. Swin Transformer brings this hierarchical structure to Transformers, with a key innovation that enables local attention to flow across windows.

## Key ideas

### Hierarchical architecture via patch merging

Swin processes images in 4 stages, each reducing spatial resolution by 2× and doubling channel dimension:

| Stage | Resolution (224 input) | Channels | Patch size |
|-------|------------------------|----------|------------|
| 1     | 56×56                  | 96       | 4×4        |
| 2     | 28×28                  | 192       | (merge 2×2)|
| 3     | 14×14                  | 384       | (merge 2×2)|
| 4     | 7×7                    | 768       | (merge 2×2)|

The first stage splits the image into 4×4 patches and embeds them. Subsequent stages merge 2×2 neighboring patches (concatenate their features, project to 2× channels). This mirrors the downsampling in CNNs and provides multi-scale features for dense prediction.

### Window-based self-attention (W-MSA)

Instead of computing attention over all patches, Swin computes attention within local windows. For a stage with H×W patches and window size M×M, the number of patches per window is M², and the number of windows is (H/M) × (W/M). Attention cost per layer: O((H/M) × (W/M) × M⁴) = O(H × W × M²), linear in image size.

The window size M is typically 7. This gives attention over 49 patches per window — much cheaper than attention over all 784 patches (28×28) in stage 2.

### Shifted window attention (SW-MSA)

Window attention has a problem: patches in different windows cannot communicate. Information is confined to windows, and there's no cross-window flow.

Swin solves this by shifting the windows between layers:

- Layer `l`: windows are at positions `(0, 0), (0, M), (M, 0), (M, M), ...`
- Layer `l+1`: windows are shifted by `(M/2, M/2)`, so they straddle the previous window boundaries.

With shifting, a patch in window A (layer `l`) is in a window that includes patches from windows A, B, C, D (layer `l+1`). Information flows across original window boundaries.

```mermaid
graph TD
  subgraph Layer l: Standard Windows
    A1[Window A<br/>patches 0-48] 
    B1[Window B<br/>patches 49-97]
    C1[Window C<br/>patches 98-146]
    D1[Window D<br/>patches 147-195]
  end
  subgraph Layer l+1: Shifted Windows
    A2[Shifted window<br/>patches from A, B, C, D]
    B2[Shifted window<br/>patches from A, B, C, D]
    C2[Shifted window<br/>patches from A, B, C, D]
    D2[Shifted window<br/>patches from A, B, C, D]
  end
  Note[Alternating layers: standard then shifted<br/>→ information flows across windows]
```

This is the vision cousin of the [[Sliding Window Attention|sliding-window attention]] family that Longformer and BigBird brought to NLP: keep attention local for efficiency, but make sure locality doesn't become isolation.

### Cyclic shift implementation

Naive implementation of shifted windows is inefficient (the shifted windows at the edges are partial). Swin uses a clever trick: cyclically shift the feature map so that the shifted windows align with standard windows, compute attention, then cyclically shift back. This avoids partial windows and makes the implementation efficient.

### Relative position bias

Swin adds a learned relative position bias to the attention scores:

$$\text{Attention}(Q, K, V) = \text{softmax}(Q K^T / \sqrt{d} + B) V$$

where `B` is a learned bias that depends on the relative position of the query and key within the window — compare the unbiased base form in [[Scaled Dot-Product Attention]]. This is similar to Transformer-XL's relative positional encoding but applied to 2D vision patches.

The relative position bias is parameterized as a small learnable table (size `(2M-1) × (2M-1)` for window size M). It captures 2D spatial relationships (e.g., "attend to the token above-right") that are important for vision but not for text.

## Key results

Swin Transformer achieved SOTA on ImageNet classification, COCO object detection, and ADE20K semantic segmentation:

| Task                          | Previous SOTA    | Swin Transformer |
|-------------------------------|------------------|------------------|
| ImageNet-1K (top-1)           | 88.5 (ViT-Huge)  | 87.3 (Swin-L)    |
| COCO detection (AP^box)       | 55.1             | 58.7 (Swin-L)    |
| ADE20K segmentation (mIoU)    | 48.4             | 53.5 (Swin-L)    |

The most striking results were on dense prediction (detection and segmentation): Swin outperformed previous SOTA by 3.6 and 5.1 points respectively. This was the first Transformer to clearly beat CNN-based methods (DetectoRS, SETR) on dense prediction, validating the hierarchical approach.

On ImageNet classification, Swin slightly underperformed ViT-Huge (which had more pretraining data), but it was much more efficient (similar accuracy with fewer parameters and FLOPs).

## Why it worked

### Hierarchy matches dense prediction

Dense prediction tasks require multi-scale features. Swin's hierarchical architecture (4 stages, each with half the resolution) provides this naturally, matching the structure of CNN feature pyramids (FPN, PAN). ViT's flat architecture doesn't.

### Shifted windows enable cross-window flow

Without shifting, window attention is too local — each window is isolated, and the model cannot integrate information across the image. Shifting solves this elegantly: alternating layers with standard and shifted windows create cross-window connections while keeping attention local.

### Linear complexity in image size

W-MSA is O(H × W × M²) — linear in image size. This makes Swin practical for high-resolution images (detection at 800×1333, segmentation at 512×2048), where ViT's O(H² W²) would be prohibitive.

### Relative position bias for 2D

The learned relative position bias captures 2D spatial relationships that are essential for vision. This generalizes better than absolute position embeddings, especially for variable image sizes.

## Limitations

### Fixed window size

The window size M is fixed at model design time. This means Swin cannot adaptively choose attention patterns based on content — the windows are the same regardless of what's in the image.

### Patch merging loses information

The hierarchical downsampling (patch merging) loses spatial detail. For tasks requiring fine-grained localization (small object detection, boundary-aware segmentation), this can hurt. Modern variants (Swin-V2, CSWin) address this with adaptive merging or different window patterns.

### Complexity at very high resolution

While linear in image size, Swin's constant factors are still significant. For very high-resolution images (e.g., 4K satellite imagery), even Swin is expensive. Techniques like sparse attention or hierarchical dilated windows extend further.

### Replaced by native-resolution approaches

NaViT (2023) and other native-resolution ViTs process images at their original resolution without fixed patch sizes. For some tasks, this is simpler and more effective than Swin's hierarchical approach.

## Successors

### Swin Transformer V2 (2022)

Improved scaling: larger window sizes, scaled cosine attention, log-spaced continuous position bias. Scaled to 3B parameters and achieved SOTA on more benchmarks. The three techniques each address a specific failure mode that appeared when naively scaling Swin up — instability in attention at large window sizes (scaled cosine attention), and the poor transfer of the learned position-bias table across window sizes (the log-spaced continuous parameterization replaces the discrete table).

### CSWin Transformer (2022)

Cross-shaped window attention: horizontal and vertical strips instead of square windows. Better global context with similar efficiency.

### BEiT (Microsoft, 2021)

Self-supervised pretraining for ViT-family models, including Swin. Showed that Swin can be pretrained without labels and match supervised performance.

### DINOv2 (Meta, 2023)

Self-supervised ViT pretraining at scale. Uses standard ViT (not Swin) but achieves SOTA on dense prediction, suggesting that with enough data, flat architectures can match hierarchical ones.

## Impact and legacy

Swin Transformer's influence on computer vision:

1. **Standard for dense prediction.** Swin became the default backbone for object detection and semantic segmentation in 2022–2023. Most SOTA detection and segmentation models used Swin as the encoder.

2. **Hierarchical Transformers as a paradigm.** Swin showed that hierarchical architecture (multi-scale features) is valuable for Transformers, not just for CNNs. This influenced architectures in other domains (video, 3D, medical imaging).

3. **Shifted window as a technique.** The shifted-window idea (alternate local windows with shifted versions) appears in modified form in several subsequent architectures. The general principle — use local attention but ensure cross-window flow — became standard.

4. **Relative position bias for 2D.** Swin's relative position bias (a 2D learned table) influenced how vision Transformers handle position. Modern vision Transformers (NaViT, DINOv2) use RoPE-2D or similar relative encodings.

5. **Bridge to multimodal.** Swin's hierarchical features are used as visual encoders in some multimodal LLMs. The multi-scale features are particularly useful for tasks that require both global understanding and local detail (e.g., document understanding, chart reading).

For AI engineers working on vision tasks, Swin remains a strong choice for dense prediction. If you're doing object detection, semantic segmentation, or any task that benefits from multi-scale features, Swin (or its variants) is a standard option.

## Further reading

- Original paper: arXiv:2103.14030
- Swin V2: arXiv:2111.09883
- CSWin: arXiv:2207.10224
- [[ViT Architecture]] — the flat predecessor.

## See also

- [[Attention and Transformers MOC]] — the topical hub for this note.
- [[Sliding Window Attention]] — the NLP cousin of window attention.
- [[Scaled Dot-Product Attention]] — the base attention rule Swin extends with a position bias.
- [[ViT Architecture]] and [[Patch Tokenization]] — the flat vision-Transformer design Swin departs from.
- [[Inductive Bias]] — the CNN-versus-ViT inductive-bias discussion that motivates hierarchical designs.
- [[Evolution of CNN Architectures]] — the CNN lineage whose multi-scale habits Swin imports.
