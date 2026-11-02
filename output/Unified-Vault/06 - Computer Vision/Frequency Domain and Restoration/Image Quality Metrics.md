---
title: Image Quality Metrics
type: reference
aliases:
  - Image Quality Assessment
  - Image Quality Metrics — MSE, PSNR, SSIM, and Beyond
  - MSE PSNR SSIM and Beyond
  - SSIM
  - PSNR
  - MS-SSIM
  - LPIPS
tags:
  - image-processing
  - computer-vision
  - quality-metrics
  - mse
  - psnr
  - ssim
  - ms-ssim
  - lpips
  - perceptual-quality
sources:
  - "4.5 Image Quality Metrics"
created_index: 29
---

After compressing, denoising, or restoring an image, you need to measure **how good the result is**. This reference covers the standard image quality metrics: MSE and PSNR (simple, widely used but limited), SSIM (perceptually motivated), and the modern perceptual metrics MS-SSIM and LPIPS. Each metric captures a different notion of "quality," and choosing the right one matters. The metrics quantify the outputs of the degradation and restoration pipeline covered in [[Image Degradation and Noise Models]] and [[Frequency Domain Filtering]]; the chapter map is [[Image Processing Global Index]].

> [!tldr] Quick guidance
> - **MSE/PSNR** — simple, differentiable, reproducible, but perceptually blind; fine as a loss or baseline, never as the sole quality measure.
> - **SSIM/MS-SSIM** — perceptually motivated; compare luminance, contrast, and structure in local windows.
> - **LPIPS** — deep-learning-based; the standard for generative models and image restoration.
> - The golden rule: never report only MSE/PSNR — always add a perceptual metric, and remember that the ultimate metric is human evaluation (MOS).

## The problem: what is "quality"?

If you have an original image $f$ and a processed version $\hat{f}$ (compressed, denoised, restored), how do you measure the difference? The naive answer — compare pixel by pixel — is unsatisfying because it does not match **human perception**. A slightly shifted edge (invisible to humans) produces large pixel-wise error; a smooth blur (very visible to humans) produces small pixel-wise error. Good quality metrics must capture **perceptual** quality, not just numerical difference.

## Mean squared error

$$\text{MSE} = \frac{1}{N} \sum_{i} (f_i - \hat{f}_i)^2$$

The MSE is the average squared difference between original and processed pixels. Its virtues are real: it is simple, differentiable (so it is usable as a loss function), and fast. Its vice is that it does not match perception — two images with the same MSE can look very different (one may have visible artifacts, the other a uniform slight blur).

The right role for MSE is as a training loss or as a baseline metric; it is also the same squared-error quantity used to evaluate regression models. It should never be used as the sole quality measure.

## Peak signal-to-noise ratio

$$\text{PSNR} = 10 \log_{10}\left(\frac{\text{MAX}^2}{\text{MSE}}\right) \quad \text{(dB)}$$

where MAX is the maximum possible pixel value (255 for 8-bit images). The logarithmic scale is intuitive — each 10 dB is a 10× improvement in MSE — and PSNR is widely used in the compression and denoising literature. But it is still based on MSE, so it inherits MSE's perceptual mismatch: a PSNR of 30 dB is "good" but does not guarantee visual quality.

Typical values anchor the scale:

| PSNR range | Interpretation |
| :--- | :--- |
| 20-30 dB | acceptable quality (visible artifacts) |
| 30-40 dB | good quality (minor artifacts) |
| 40+ dB | excellent quality (near-transparent) |
| > 50 dB | visually indistinguishable from the original |

PSNR is the standard metric for compression benchmarks (JPEG, JPEG2000, video codecs — 20-40 dB typical), despite its flaws, because it is simple and reproducible. Always report it alongside a perceptual metric (SSIM).

## Structural similarity index

SSIM (Wang et al., 2004) is the first major **perceptually-motivated** metric. Instead of comparing pixels, it compares **structural information** — the patterns of pixel values that convey structural content (edges, textures, object shapes).

### The SSIM formula

SSIM compares local windows (typically 11×11 or 8×8) of the two images, measuring three aspects:

$$\text{SSIM}(x, y) = \frac{(2\mu_x \mu_y + C_1)(2\sigma_{xy} + C_2)}{(\mu_x^2 + \mu_y^2 + C_1)(\sigma_x^2 + \sigma_y^2 + C_2)}$$

The three factors of the formula each capture one aspect:

- **Luminance:** $(2\mu_x \mu_y + C_1) / (\mu_x^2 + \mu_y^2 + C_1)$ — compares the means (brightness).
- **Contrast:** $(2\sigma_x \sigma_y + C_2) / (\sigma_x^2 + \sigma_y^2 + C_2)$ — compares the standard deviations (contrast).
- **Structure:** $(\sigma_{xy} + C_3) / (\sigma_x \sigma_y + C_3)$ — compares the correlation (structural similarity, normalized by contrast).

where $\mu$ is the mean, $\sigma$ is the standard deviation, $\sigma_{xy}$ is the covariance, and $C_1, C_2, C_3$ are small constants to avoid division by zero. The overall SSIM is the mean of the local SSIM values over all windows. It ranges from $-1$ to $1$, with $1$ = perfect match.

### Why SSIM is better than MSE

SSIM captures **structural** similarity, which is what humans perceive. Two images with the same MSE but different structure (one has a shifted edge, the other a uniform blur) will have different SSIM — the shifted edge preserves structure (high SSIM), the blur destroys it (low SSIM). This matches perception.

### Limitations of SSIM

SSIM is still a **local** metric (window-based), so it does not capture global artifacts. It assumes the degradation is local and moderate, and fails on severe distortions (e.g., color shifts, geometric warps). Finally, the fixed window size may not match the scale of the artifacts.

## Multi-scale SSIM

MS-SSIM (Wang et al., 2003) computes SSIM at **multiple scales** (by downsampling the image repeatedly) and combines the results. This captures quality at different frequencies — fine detail at the original scale, coarse structure at downsampled scales. MS-SSIM outperforms single-scale SSIM, especially for images with artifacts at specific scales (e.g., JPEG block artifacts at the 8×8 scale). It is the standard perceptual metric for image compression research.

## LPIPS (learned perceptual image patch similarity)

LPIPS (Zhang et al., 2018) is a **deep-learning-based** perceptual metric. It extracts features from a pretrained CNN (VGG, AlexNet, or SqueezeNet) at multiple layers for both images, and computes the weighted L2 distance between the feature representations.

Why it works: the CNN has been trained on ImageNet to recognize objects, so its features capture **semantic** structure (edges, textures, object parts). Two images that look similar to a human produce similar CNN features, even if they differ in pixels. Its advantage over SSIM is that LPIPS captures high-level perceptual quality that SSIM misses — for example, a generated face that looks "uncanny" may have high SSIM but a high LPIPS distance. LPIPS is the standard metric for generative models (GANs, diffusion) and image restoration (super-resolution, denoising): if you are training a GAN, you report LPIPS, not just MSE/SSIM.

## Choosing the right metric

| Task | Primary metric | Also report |
| :--- | :--- | :--- |
| Compression (JPEG, video) | PSNR | MS-SSIM |
| Denoising / restoration | PSNR, SSIM | LPIPS |
| Super-resolution | SSIM, LPIPS | PSNR |
| Generative models (GAN, diffusion) | LPIPS, FID | SSIM |
| Benchmarking / comparison | All of the above | — |

**The golden rule:** never report only MSE/PSNR. Always include a perceptual metric (SSIM at minimum, LPIPS for generative models). MSE/PSNR are reproducible but perceptually blind; the perceptual metrics catch quality issues that MSE misses.

## The ultimate metric: human evaluation

No computational metric perfectly matches human perception. For final quality assessment (e.g., comparing two compression standards), the gold standard is **human subjective evaluation** — show the images to human raters and collect Mean Opinion Scores (MOS). This is expensive and slow, which is why computational metrics are used for development, but final benchmarks use human studies.

## See also

- [[Image Degradation and Noise Models]] — the degradations these metrics are asked to judge.
- [[Frequency Domain Filtering]] — filtering pipelines whose output quality is measured here.
- [[The Fourier Transform]] — the frequency-domain view behind multi-scale analysis.
- [[Deep Learning for Imaging]] — the learned restoration and generation systems evaluated with LPIPS.
- [[Noise Degradation and Frequency Domain Quiz]] — self-testing on this subfamily.
- [[Image Processing Global Index]] — the area's reading map.
