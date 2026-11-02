---
title: Image Degradation and Noise Models
type: concept
aliases:
  - Noise Models
  - Image Degradation Model
  - Degradation and Restoration
  - Image Restoration Models
tags:
  - image-processing
  - computer-vision
  - noise
  - degradation
  - restoration
  - wiener-filter
  - gaussian-noise
  - salt-and-pepper-noise
  - speckle-noise
  - poisson-noise
sources:
  - "4.4 Image Degradation and Noise Models"
created_index: 28
---

Real images are degraded by noise, blur, and other distortions. Understanding the **noise model** — what type of noise, how it is added, what it looks like — is essential for choosing the right restoration method. This note covers the degradation model that unifies blur and noise, the common noise types and how to identify them, the classical blur models, and the restoration methods (inverse and Wiener filtering) built on the frequency-domain machinery of [[The Fourier Transform]] and [[Frequency Domain Filtering]]. Results are judged with the metrics of [[Image Quality Metrics]], the deep-learning successors appear in [[Deep Learning for Imaging]], and the chapter map is [[Image Processing Global Index]].

## The degradation model

A degraded image $g$ is modeled as the original image $f$ passed through a degradation system $H$ plus noise $n$:

$$g(x, y) = H[f(x, y)] + n(x, y)$$

Here $H$ is the **degradation function** (usually a blur — motion blur, defocus, atmospheric turbulence), $n$ is the **noise** (random, signal-independent or signal-dependent), $f$ is the original (unknown) image, and $g$ is what we observe. **Restoration** is the problem of estimating $f$ from $g$, given (or estimating) $H$ and $n$. This is **ill-posed** — many $f$'s could produce the same $g$ — so restoration requires assumptions about $f$ (smoothness, sparsity) or about the noise (distribution).

### Enhancement vs. restoration

**Enhancement** improves the image's appearance subjectively (contrast, sharpness) — it uses no model of degradation. **Restoration** recovers the original image using a model of how it was degraded — it is objective and model-based. Restoration is harder but more principled: if you know the degradation model, you can invert it (or approximately invert it); if you don't, you're just guessing.

## Noise models

The five standard noise models differ in how the noise combines with the signal, and each points to a different best filter. Gaussian, salt-and-pepper, speckle, Poisson, and uniform noise cover the additive, impulsive, multiplicative, and signal-dependent cases met in practice. The identification heuristics at the end of this section tell you which one you are facing.

### Gaussian (additive) noise

$$n(x, y) \sim \mathcal{N}(0, \sigma^2)$$

Each pixel has independent Gaussian noise added, and the noise is the same regardless of the pixel's intensity (signal-independent). Its sources are thermal noise in the sensor and electronic noise in the amplifier, and it appears grainy and uniform across the image. The best filter is a Gaussian low-pass (linear, optimal under Gaussian noise assumptions), or wavelet thresholding — additive Gaussian noise is the case linear filters handle well.

### Salt-and-pepper (impulsive) noise

Random pixels are set to 0 (pepper) or 255 (salt), with probability $p$. Its sources are faulty pixels in the sensor, bit errors in transmission, and dust on the lens; it appears as scattered black and white dots. The best filter is the **median filter** (see [[Non-Linear Smoothing Filters]]): linear filters (Gaussian, mean) fail because averaging with 0 or 255 pulls the result toward the extreme, while the median ignores the extreme values entirely.

### Speckle (multiplicative) noise

$$g = f \cdot (1 + n), \quad n \sim \mathcal{N}(0, \sigma^2)$$

The noise is **multiplied** by the signal — brighter pixels have more noise — which is fundamentally different from additive noise. Speckle arises in coherent imaging systems (ultrasound, SAR radar, holography), where the coherent illumination causes interference patterns (speckle). It appears granular, "salt-and-pepper-like" but proportional to intensity. The standard remedy is a log-transform (which converts multiplicative noise to additive), then filtering, then an exp-transform back — or specialized adaptive filters (Lee, Frost).

### Poisson (shot) noise

$$n \sim \text{Poisson}(\lambda)$$

where $\lambda$ is the expected photon count. The noise variance equals the mean — brighter pixels have more noise, but the *relative* noise decreases as $\sqrt{\lambda}/\lambda = 1/\sqrt{\lambda}$. Its sources are low-light imaging (few photons) and fluorescence microscopy, and it appears grainy in dark regions (where photon counts are low) and clean in bright regions. The best filter is specialized Poisson denoising, often based on variance-stabilizing transforms like the Anscombe transform, followed by Gaussian denoising.

### Uniform noise

$n \sim \text{Uniform}(a, b)$ is rarely physical, though it is sometimes used as a model for quantization noise. It is the least commonly encountered of the five models in practice. It completes the standard catalog after the additive, impulsive, multiplicative, and signal-dependent cases above.

## Noise identification

How do you know which noise model applies? Three diagnostics, in increasing order of sophistication:

1. **Look at the noise profile:** if the noise is uniform across intensity, it's additive (Gaussian). If it's proportional to intensity, it's multiplicative (speckle). If it's extreme dots, it's impulsive (salt-and-pepper).
2. **Look at the histogram:** Gaussian noise broadens the histogram symmetrically. Salt-and-pepper adds spikes at 0 and 255. Speckle broadens the histogram proportionally to intensity.
3. **Look at the frequency spectrum:** periodic noise appears as spikes. White noise (Gaussian) spreads across all frequencies. Speckle has a characteristic structure.

The frequency-spectrum diagnostic connects directly to the notch-filter machinery of [[Frequency Domain Filtering]]: a spike pattern in the spectrum is exactly what a notch mask removes. The three diagnostics complement each other — the profile tells you how the noise scales with intensity, the histogram shows how it distributes across values, and the spectrum reveals any periodic component.

## Blur models (the $H$ in $g = Hf + n$)

### Motion blur

When the camera or subject moves during exposure, the image is blurred along the direction of motion. In the frequency domain, motion blur appears as a **directional sinc pattern**. Concretely, the spectrum is attenuated along lines perpendicular to the motion, so the blur's orientation is readable directly off the spectrum.

### Defocus blur

When the lens is out of focus, point sources become disks (the circle of confusion). In the frequency domain, defocus blur attenuates high frequencies. The blur acts as a low-pass filter, so the high-frequency content that carries fine detail is what it removes.

### Atmospheric turbulence

In long-range imaging (astronomy, surveillance), atmospheric turbulence causes a time-varying blur. It is modeled as a Gaussian low-pass whose strength depends on the turbulence. The stronger the turbulence, the stronger the effective low-pass attenuation.

## Restoration methods

### Inverse filtering

If we know $H$, we can (try to) invert it: $\hat{f} = \mathcal{F}^{-1}\{G / H\}$. The problem: where $H$ is near zero (high frequencies, for a blur), the division $G/H$ **amplifies noise** catastrophically. Inverse filtering is useless in the presence of noise.

### Wiener filtering

The **Wiener filter** is the optimal linear filter for restoring a signal degraded by a known blur and additive noise. It balances de-blurring against noise amplification:

$$\hat{F} = \frac{H^*}{|H|^2 + S_n/S_f} G$$

where $S_n$ is the noise power spectrum and $S_f$ is the signal power spectrum. The term $S_n/S_f$ (the noise-to-signal ratio) regularizes the division — where the noise is high, the filter backs off (does not try to de-blur). The Wiener filter is the classical solution to the deblurring problem: it is optimal in the mean-squared-error sense, under Gaussian assumptions. Modern methods (deep learning — see [[Deep Learning for Imaging]]) outperform it, but it remains the baseline.

> [!summary] What to remember
> The degradation model is $g = H[f] + n$: restoration estimates $f$ from $g$ given (or estimating) $H$ and $n$. **Gaussian noise** is additive and uniform — use linear filters (Gaussian low-pass). **Salt-and-pepper noise** is impulsive and extreme — use the **median filter** (linear filters fail). **Speckle noise** is multiplicative and proportional to intensity — log-transform + filter, or adaptive filters. **Poisson noise** is signal-dependent and worse in dark regions — variance-stabilizing transforms. **Blur models:** motion (directional), defocus (low-pass), atmospheric (Gaussian low-pass). **Inverse filtering** amplifies noise (useless in practice); **Wiener filtering** balances de-blurring against noise — the classical optimal solution and still the baseline.

## See also

- [[Frequency Domain Filtering]] — the filtering pipeline, filters, and notch removal used against noise.
- [[The Fourier Transform]] — the transform the restoration formulas run on.
- [[Image Quality Metrics]] — measuring how well restoration worked.
- [[Non-Linear Smoothing Filters]] — the median filter for salt-and-pepper noise.
- [[Linear Smoothing Filters]] — the Gaussian low-pass for additive noise.
- [[Deep Learning for Imaging]] — learned denoising beyond the classical baseline.
- [[Noise Degradation and Frequency Domain Quiz]] — self-testing on this subfamily.
- [[Image Processing Global Index]] — the area's reading map.
