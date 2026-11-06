---
title: Linear Smoothing Filters
type: concept
aliases:
  - Blurring
  - Box Filter
  - Mean Filter
  - Gaussian Filter
  - Gaussian Blur
  - Smoothing Filters
tags:
  - image-processing
  - computer-vision
  - spatial-filtering
  - smoothing
  - blurring
  - box-filter
  - mean-filter
  - gaussian-filter
  - separability
  - noise-reduction
sources:
  - "3.2 Linear Smoothing Filters"
created_index: 69
---

Linear filters replace a pixel value with a weighted sum of its neighbors, and smoothing — blurring — is the branch of that family used for noise reduction and for removing small, irrelevant details. The two standard linear smoothers are the box (mean) filter, which gives every neighbor the same weight, and the Gaussian filter, which weighs neighbors by the bell curve. This note covers both kernels, the normalization rule every smoothing kernel must obey, and the separability property that makes large Gaussian blurs affordable. The neighborhood mechanics underneath are covered in [[The Mechanics of Spatial Filtering]]; the rank-order and edge-preserving alternatives are [[Non-Linear Smoothing Filters]] and [[Edge Preserving Filters]].

## The box (mean) filter

The box filter is the simplest linear filter: every pixel in the neighborhood has the same weight. Its kernel sets all coefficients to 1 and divides them by the total number of pixels, so the $3 \times 3$ example is

$$\frac{1}{9} \begin{bmatrix} 1 & 1 & 1 \\ 1 & 1 & 1 \\ 1 & 1 & 1 \end{bmatrix}$$

The effect is to average out local variations, which is exactly the mechanism behind the noise reduction and detail removal smoothing is used for. The drawback is that the filter is very "brute-force": it blurs sharp edges, and if the kernel is large it creates a "square" artifacting look.

## The Gaussian filter

The Gaussian filter is the "gold standard" for natural-looking blur. Its weights are determined by the 2D Gaussian distribution (the bell curve), so influence falls off smoothly with distance from the center instead of staying flat across the whole kernel.

### The Gaussian formula

Each kernel weight is a sample of the 2D Gaussian:

$$ G(x, y) = \frac{1}{2\pi\sigma^2} e^{-\frac{x^2 + y^2}{2\sigma^2}} $$

Here $\sigma$ (Sigma) is the **standard deviation**; it controls the "spread" of the blur. Higher $\sigma = $ wider bell curve $=$ more blurring. Tuning the blur therefore means tuning one number.

### Key properties

Three properties explain why the Gaussian replaces the box filter in practice. It is isotropic — it blurs equally in all directions, with no preferred axis. It is a weighted average in which pixels closer to the center have a much higher influence than those on the edges, which preserves edges better than a box filter. And it is separable: a 2D Gaussian filter can be implemented by applying a 1D Gaussian horizontally, then another 1D Gaussian vertically.

Separability is the property with the practical payoff. The cost of filtering an image drops from $O(M \cdot N \cdot K^2)$ to $O(M \cdot N \cdot 2K)$ when the 2D kernel is split into its two 1D passes; for a $15 \times 15$ kernel, this is nearly 7.5 times faster.

## Kernel normalization

For any smoothing filter, the sum of all coefficients in the kernel must equal 1 — a crucial point, because the coefficient sum directly rescales overall brightness:

> [!warning] Coefficient sums and brightness
> If the sum $> 1$, the image becomes brighter. If the sum $< 1$, the image becomes darker. If the sum $= 0$, the image becomes black (mostly used in edge detection).

The box filter's division by the pixel count is this rule in action: the $\frac{1}{9}$ prefactor of the $3 \times 3$ kernel exists precisely so that the nine coefficients sum to 1.

## See also

- [[The Mechanics of Spatial Filtering]] — the neighborhood operation every kernel here runs on.
- [[Non-Linear Smoothing Filters]] — the rank-order alternative for impulse noise.
- [[Edge Preserving Filters]] — smoothers that stop at edges.
- [[Sharpening and Edge Detection]] — where sum-to-zero kernels are mostly used.
- [[Image Degradation and Noise Models]] — the noise models each smoother fits best.
- [[Frequency Domain Filtering]] — the Gaussian low-pass from the frequency-domain side.
- [[Image Pyramids and Multi-Scale Representation]] — the Gaussian filter applied across scales.
- [[Spatial Filtering and Convolution Quiz]] — self-testing on this subfamily.
- [[Image Processing Global Index]] — the area's reading map.
