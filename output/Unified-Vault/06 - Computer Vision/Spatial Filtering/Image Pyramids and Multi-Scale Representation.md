---
title: Image Pyramids and Multi-Scale Representation
type: concept
aliases:
  - Image Pyramid
  - Gaussian Pyramid
  - Laplacian Pyramid
  - Multi-Scale Representation
  - EXPAND Operation
  - DoG Pyramid
  - Difference of Gaussians Pyramid
  - Feature Pyramid Networks
  - FPN
  - 3.9 Image Pyramids and Multi-Scale Representation
tags:
  - image-processing
  - computer-vision
  - spatial-filtering
  - image-pyramids
  - gaussian-pyramid
  - laplacian-pyramid
  - multi-scale-representation
  - scale-space
  - aliasing
  - image-blending
sources:
  - "3.9 Image Pyramids and Multi-Scale Representation"
created_index: 68
---

An **image pyramid** is a multi-scale representation of an image — a stack of progressively smaller, smoother versions. Pyramids are essential for scale-invariant detection, because objects appear at different sizes in different images, and they serve as the data structure behind efficient multi-scale algorithms. This note covers the two main types: **Gaussian pyramids**, which pair smoothing with downsampling, and **Laplacian pyramids**, which extract the detail at each scale and allow perfect reconstruction. The construction rests on the Gaussian blur of [[Linear Smoothing Filters]] and on the resampling ideas of [[Geometric Transformations and Interpolation]].

## Why multi-scale?

An object can appear at any size in an image: a face might be 1000 pixels wide in a close-up portrait or 50 pixels wide in a wide group photo, and a detector that works at one scale will miss objects at other scales. The naive solution — run the detector at every scale by resizing the image — is expensive. Image pyramids make this efficient by pre-computing the multi-scale representation once.

A pyramid is also the natural data structure for algorithms that need to combine local detail (high resolution) with global context (low resolution). SIFT's scale space, CNN Feature Pyramid Networks, and Laplacian pyramid blending all use this structure.

## The Gaussian pyramid

A Gaussian pyramid is built by repeatedly **blurring with a Gaussian and downsampling by 2**:

1. Start with the original image $G_0$ (level 0).
2. Apply a Gaussian blur to $G_0$.
3. Downsample by 2 (drop every other pixel) → $G_1$ (level 1, half the resolution).
4. Repeat: blur $G_1$, downsample → $G_2$, etc.

```text
Level 0: G_0 (original, e.g., 512×512)
Level 1: G_1 (256×256, blurred + downsampled)
Level 2: G_2 (128×128)
Level 3: G_3 (64×64)
...
```

Each level is $\frac{1}{4}$ the size of the previous (half the width, half the height), and the pyramid has $\log_2(\min(H, W))$ levels. The name "pyramid" is literal: stacking the levels from largest at the base to smallest at the apex traces the familiar shape.

### Why blur before downsampling?

Downsampling without blurring causes **aliasing** — high frequencies that the smaller image cannot represent fold back as spurious low frequencies. The Gaussian blur is a low-pass filter that removes the high frequencies before they can alias. This is the Nyquist-Shannon sampling theorem in action.

> [!warning] Never downsample without blurring
> Skipping the Gaussian pre-blur is the classic pyramid-building mistake. The shrunken image does not merely lose detail — it gains spurious low-frequency patterns folded down from the high frequencies it can no longer represent.

### The EXPAND operation

The inverse of the pyramid construction is the **EXPAND** operation: upsample $G_{i+1}$ by 2 (insert zeros) and blur with the same Gaussian, producing a blurred approximation of $G_i$, denoted $\text{EXPAND}(G_{i+1})$. It is used in the Laplacian pyramid below and in multi-scale blending. EXPAND is what lets a coarse level stand in for the fine level it came from, after smoothing.

## The Laplacian pyramid

A Laplacian pyramid captures the **detail** at each scale — the information lost when going from level $i$ to level $i+1$. It is derived from the Gaussian pyramid:

$$L_i = G_i - \text{EXPAND}(G_{i+1})$$

$L_i$ is the difference between level $i$ of the Gaussian pyramid and the upsampled version of level $i+1$. It contains the **high-frequency detail** that was smoothed away when the Gaussian pyramid was built.

### Why "Laplacian"?

Each $L_i$ approximates the **Laplacian of the Gaussian** (LoG — the operator behind the detectors in [[Canny and LoG Edge Detection]]) at a different scale. The difference of two Gaussians at different scales is an approximation of the Laplacian, so the Laplacian pyramid is a **multi-scale edge/detail detector**. The same difference-of-Gaussians idea returns below as SIFT's scale space.

### Reconstruction

The original image can be perfectly reconstructed from the Laplacian pyramid:

$$G_i = L_i + \text{EXPAND}(G_{i+1})$$

Starting from the top — the smallest Gaussian level, which is also the smallest Laplacian's "base" — expand and add the corresponding Laplacian level, and repeat down to level 0. This gives lossless reconstruction: the Laplacian pyramid is a complete representation, not an approximation.

### Applications of Laplacian pyramids

Because the Laplacian pyramid decomposes an image into per-scale detail, it supports operations that are awkward to express at a single scale. The four classics are:

1. **Image blending:** to blend two images seamlessly (the apple+orange classic example), blend each Laplacian level separately with a smooth mask, then reconstruct. Because each scale is blended independently, the result has no visible seams.
2. **Image compression:** the Laplacian levels are sparser than the original (mostly zeros in smooth regions), so they can be compressed more efficiently — the basis of some early wavelet compression schemes.
3. **Texture synthesis:** generate textures by sampling from the Laplacian statistics of an example texture.
4. **Multi-scale detail enhancement:** amplify or suppress specific scales by scaling the Laplacian levels before reconstruction.

## The DoG pyramid (SIFT's scale space)

SIFT — the descriptor covered in [[Feature Descriptors - SIFT, SURF, ORB, HOG]] — uses a variant: the **Difference of Gaussians (DoG) pyramid**. Instead of subtracting the expanded version (as the Laplacian pyramid does), SIFT subtracts **adjacent Gaussian levels**:

$$\text{DoG}_i = G_i(\sigma) - G_i(k\sigma)$$

where $k$ is a scale ratio (e.g., $k = 2^{1/3}$). The DoG approximates the LoG and is used to find scale-space extrema — keypoints that are stable across scales.

## Pyramids in deep learning: Feature Pyramid Networks

Modern object detectors (see [[Detection and Segmentation]]) face the same multi-scale problem. **Feature Pyramid Networks (FPN)** (Lin et al., 2017) build a pyramid from a CNN's feature maps: the CNN naturally produces features at decreasing resolutions (after each pooling or strided-conv layer), and FPN adds a top-down path with lateral connections to produce a pyramid of rich features at each scale. The detector then runs on all pyramid levels, detecting large objects at coarse levels and small objects at fine levels.

FPN is the deep-learning successor to the Gaussian pyramid: it serves the same purpose (multi-scale detection) but uses learned features instead of Gaussian blur. Its position in the CNN architecture timeline is traced in [[06 - Computer Vision/Architecture and Connectivity/Evolution of CNN Architectures|Evolution of CNN Architectures]].

## Practical use in OpenCV

```python
import cv2

# Gaussian pyramid
level0 = image
level1 = cv2.pyrDown(level0)  # blur + downsample by 2
level2 = cv2.pyrDown(level1)
level3 = cv2.pyrDown(level2)

# Expand back
expanded = cv2.pyrUp(level1)  # upsample + blur

# Laplacian pyramid
laplacian0 = level0.astype(float) - cv2.pyrUp(level1).astype(float)
# (must match sizes; pyrUp doubles the dimensions)
```

`cv2.pyrDown` performs the blur-plus-downsample step of the Gaussian pyramid and `cv2.pyrUp` performs the upsample-plus-blur of EXPAND, so the top Laplacian level is just the floating-point difference between `level0` and `cv2.pyrUp(level1)`. Mind the code comment: the sizes must match before subtracting, because `pyrUp` doubles the dimensions.

## Key takeaways

An image pyramid is a multi-scale stack in which each level is smaller and smoother than the one below. The Gaussian pyramid is built by blur + downsample, and the blur must come first to avoid aliasing. The Laplacian pyramid holds the detail at each scale, $L_i = G_i - \text{EXPAND}(G_{i+1})$, capturing multi-scale edges and details, and it is a complete representation — the image can be perfectly reconstructed from it. Its applications include seamless multi-scale blending, compression, texture synthesis, and detail enhancement. SIFT's DoG pyramid and deep learning's FPN are modern successors built on the same pyramid structure, and pyramids remain the data structure for any algorithm that needs to handle objects at multiple scales.

## See also

- [[Image Processing Global Index]] — the orientation note for the classical image-processing chapter.
- [[Linear Smoothing Filters]] — the Gaussian filter that powers pyramid construction.
- [[Geometric Transformations and Interpolation]] — resizing and resampling, the operation downsampling builds on.
- [[Canny and LoG Edge Detection]] — the LoG operator that Laplacian levels approximate.
- [[Feature Descriptors - SIFT, SURF, ORB, HOG]] — SIFT and its DoG scale space.
- [[06 - Computer Vision/Architecture and Connectivity/Evolution of CNN Architectures|Evolution of CNN Architectures]] — where FPN sits in the CNN architecture timeline.
- [[Detection and Segmentation]] — the modern detectors that consume feature pyramids.
- [[The Hough Transform]] — the next stop in the spatial-filtering reading order.
- [[Introduction to the Frequency Domain]] — the frequency-domain view of what each pyramid level keeps and discards.
