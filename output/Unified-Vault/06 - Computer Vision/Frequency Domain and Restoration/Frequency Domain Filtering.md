---
title: Frequency Domain Filtering
type: concept
aliases:
  - Frequency Domain Filters
  - Low-Pass and High-Pass Frequency Filters
  - Notch Filtering
tags:
  - image-processing
  - computer-vision
  - frequency-domain
  - filtering
  - low-pass-filter
  - high-pass-filter
  - band-reject-filter
  - band-pass-filter
  - notch-filter
  - butterworth-filter
  - gaussian-filter
sources:
  - "4.3 Frequency Domain Filtering"
created_index: 27
---

The convolution theorem ($\mathcal{F}\{f * g\} = F \cdot G$) means that filtering in the spatial domain is **multiplication** in the frequency domain. This note covers how to design filters directly in the frequency domain — low-pass, high-pass, band-reject, and notch — and why this is sometimes easier and faster than spatial filtering. It builds on the transform machinery of [[The Fourier Transform]] and [[Introduction to the Frequency Domain]], and it supplies the noise-removal tools used by the restoration models of [[Image Degradation and Noise Models]]. The note anchors the frequency-domain subfamily of the classical chapter indexed in [[Image Processing Global Index]].

## The frequency-domain filtering pipeline

To filter an image in the frequency domain:

1. **Pad** the image (to avoid wraparound artifacts from the DFT's periodicity assumption — usually pad to 2× the image size).
2. **FFT:** compute $F = \text{FFT}(f)$.
3. **Shift:** move zero-frequency to the center: $F_{shifted} = \text{fftshift}(F)$.
4. **Multiply** by a filter mask $H$: $G_{shifted} = F_{shifted} \cdot H$.
5. **Unshift:** $G = \text{ifftshift}(G_{shifted})$.
6. **Inverse FFT:** $g = \text{IFFT}(G)$.
7. **Crop** back to the original size (remove the padding).

The filter $H$ is a 2D array of the same size as the (padded) image, with values that specify how much of each frequency to keep (1 = keep, 0 = remove, values in between = partial). The padding step matters because the DFT assumes the image is periodic, so without it the filtering wraps around the borders and contaminates the result. Everything else in this note is the question of what shape $H$ should take.

## Low-pass filters (blurring)

A low-pass filter keeps low frequencies (near the center) and removes high frequencies (near the edges). The result is a blurred image — the high-frequency detail is gone. Three standard designs — ideal, Butterworth, and Gaussian — trade off the sharpness of the cutoff against artifacts in the output.

### Ideal low-pass filter

$$H(u, v) = \begin{cases} 1 & \text{if } D(u, v) \leq D_0 \\ 0 & \text{if } D(u, v) > D_0 \end{cases}$$

where $D(u, v) = \sqrt{(u - u_c)^2 + (v - v_c)^2}$ is the distance from the center and $D_0$ is the cutoff frequency. The ideal filter passes every frequency inside the cutoff radius and blocks every frequency outside it. Its **problem** is that the sharp cutoff causes **ringing artifacts** (Gibbs phenomenon) — ripples around edges in the filtered image. This is the frequency-domain equivalent of the spatial sinc-function kernel (which has infinite support); ideal filters are mathematically clean but visually poor.

### Butterworth low-pass filter

$$H(u, v) = \frac{1}{1 + [D(u, v) / D_0]^{2n}}$$

where $n$ is the filter **order**. $n=1$ is maximally smooth (no ringing); higher $n$ approaches the ideal filter (more ringing but sharper cutoff). $n=2$ is a common compromise. The Butterworth filter transitions smoothly from passband to stopband, avoiding the ideal filter's ringing, and it is the standard choice when you want a controlled tradeoff between sharpness and ringing.

### Gaussian low-pass filter

$$H(u, v) = \exp\left(-\frac{D(u, v)^2}{2\sigma^2}\right)$$

The Gaussian has no ringing (it is smooth everywhere) and its inverse FFT is also a Gaussian, so the equivalent spatial filter is also a Gaussian — a special property of Gaussians. The Gaussian is the "friendliest" filter — no artifacts — but has a gradual cutoff that may not remove enough high-frequency noise.

> [!note] Key fact
> The Gaussian low-pass filter in the frequency domain corresponds exactly to the Gaussian blur in the spatial domain (see [[Linear Smoothing Filters]]). They are the same operation, just in different domains. This is why the convolution theorem is useful — you can choose whichever domain is more convenient.

## High-pass filters (sharpening and edge extraction)

A high-pass filter keeps high frequencies and removes low frequencies, extracting edges and fine detail. Any low-pass design can be turned into a high-pass filter by subtraction:

$$H_{HP}(u, v) = 1 - H_{LP}(u, v)$$

So there are ideal, Butterworth, and Gaussian high-pass filters, with the same tradeoffs as their low-pass counterparts.

One caveat matters in practice: a pure high-pass filter removes the DC component (the image's average brightness), so the result has negative values and zero mean. For display, you usually add back the DC or offset the result. A **high-boost filter** adds back a fraction of the original, $H_{HB} = (A - 1) + H_{HP}$, which sharpens while preserving brightness (see [[Sharpening and Edge Detection]]).

## Band-reject and band-pass filters

A **band-reject** filter removes a specific band of frequencies (between $D_0$ and $D_1$), keeping both lower and higher frequencies. A **band-pass** does the reverse — keeps only the band. These are useful when the noise or signal of interest occupies a known frequency range.

## Notch filters: the killer use case

A **notch filter** removes specific frequencies (or small regions around them) rather than a whole band. This is the frequency domain's superpower: **surgical removal of periodic noise**.

### The problem: periodic noise

If an image has periodic interference (e.g., from electrical noise at 50/60 Hz, or from a scanning device's mechanical rhythm), this appears as **distinct spikes** in the frequency spectrum — bright points at the interference frequency. The noise is concentrated at specific, known frequencies, not spread across the spectrum. That concentration is exactly what makes it surgically removable.

### The solution: notch filter

Identify the spikes in the magnitude spectrum (they are visually obvious — bright dots away from the center), and set $H = 0$ at those locations (small neighborhoods around each spike). Inverse-FFT to get the cleaned image. The standard procedure is:

1. FFT + fftshift the image.
2. Visually inspect the magnitude spectrum for spikes.
3. Manually or automatically create a mask $H$ that is 0 at the spike locations and 1 elsewhere.
4. Multiply, inverse-FFT.

This is **nearly impossible in the spatial domain** — periodic noise's spatial kernel is a sinusoid with infinite support, so spatial convolution would require an infinitely large kernel. In the frequency domain, it is pointwise multiplication — trivial. This is the standard method for removing moiré patterns, electrical interference, and scanning artifacts.

## When to filter in the frequency vs the spatial domain

| Situation | Better domain | Why |
| :--- | :--- | :--- |
| Small kernel (3×3, 5×5) | Spatial | FFT overhead dominates |
| Large kernel (15×15+) | Frequency | $O(N \log N)$ beats $O(N^2 k^2)$ |
| Periodic noise removal | Frequency | Spatial equivalent has infinite support |
| Gaussian blur | Either | Same operation; frequency is faster for large $\sigma$ |
| Non-linear filter (median, etc.) | Spatial | No frequency equivalent (convolution theorem only applies to linear filters) |
| Custom frequency response | Frequency | Design $H$ directly |

**Rule of thumb:** for linear filters with kernels larger than ~13×13, the frequency domain is faster. For non-linear filters or small kernels, the spatial domain is better.

The table's logic follows directly from the convolution theorem and its limits. The frequency domain wins when the equivalent spatial kernel is huge or has infinite support; the spatial domain wins when the kernel is small (the FFT's fixed overhead dominates) or when the operation is non-linear, since the convolution theorem only applies to linear filters. The median filter of [[Non-Linear Smoothing Filters]] is the canonical example of an operation with no frequency-domain equivalent.

> [!summary] What to remember
> Frequency-domain filtering = FFT the image, multiply by a filter mask, inverse-FFT. **Low-pass filters** come in ideal (ringing), Butterworth (controlled tradeoff), and Gaussian (no ringing, gradual cutoff) forms — and Gaussian in frequency = Gaussian in space. **High-pass** is $1 - H_{LP}$: it extracts edges but removes brightness, so use high-boost to preserve it. **Notch filters** are the killer use case — surgical removal of periodic noise by zeroing specific frequencies, which is nearly impossible in the spatial domain. The frequency domain is faster for large kernels ($O(N \log N)$ vs $O(N^2 k^2)$); the spatial domain is better for small kernels and non-linear filters.

## See also

- [[The Fourier Transform]] — the DFT, FFT, and convolution theorem this note relies on.
- [[Introduction to the Frequency Domain]] — why the frequency view helps.
- [[Image Degradation and Noise Models]] — degradation models and Wiener restoration.
- [[Image Quality Metrics]] — measuring filtering and restoration results.
- [[Linear Smoothing Filters]] — the spatial-domain Gaussian this note meets in the frequency domain.
- [[Sharpening and Edge Detection]] — spatial sharpening and the high-boost idea.
- [[Non-Linear Smoothing Filters]] — filters with no frequency-domain equivalent.
- [[Image Processing Global Index]] — the area's reading map.
