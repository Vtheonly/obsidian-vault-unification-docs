---
title: Gabor Filters
type: concept
aliases:
  - Gabor Filter
  - Gabor Filter Bank
  - Principles of Gabor Filtering
  - "In-Depth: Principles of Gabor Filtering"
  - 02. Gabor Filters
tags:
  - image-processing
  - computer-vision
  - spatial-filtering
  - gabor-filters
  - linear-filters
  - texture-analysis
  - feature-extraction
  - edge-detection
  - frequency-domain
sources:
  - "02. Gabor Filters"
created_index: 66
---

A Gabor filter is a specialized linear filter widely used in computer vision for texture analysis, feature extraction, and edge detection. Its impulse response is a sinusoidal function multiplied by a Gaussian function — a construction that gives it a foothold in both the frequency domain and the spatial domain at once. This note covers the filter's construction, the parameters that control it, the dual localization that makes it powerful, and the filter banks used in practice. It belongs to the family of neighborhood operators introduced in [[The Mechanics of Spatial Filtering]].

## Core concept

A Gabor filter is a linear filter whose impulse response is defined by a sinusoidal function multiplied by a Gaussian function. This unique construction gives it properties of both the frequency and spatial domains. In essence, the filter is a Gaussian kernel that has been modulated by a plane wave (a sine or cosine wave).

### The two components

The Gaussian component acts as an "envelope," localizing the filter to a specific region of the image; it ensures that the analysis is focused on a neighborhood around the current pixel. The sinusoidal component is a wave with a specific frequency and orientation, and it makes the filter sensitive to patterns that match this frequency and orientation. The two components are complementary: one decides *where* the filter looks, and the other decides *what* it looks for.

### Key parameters

The behavior of a Gabor filter is controlled by several parameters defined in its mathematical formula:

| Parameter | Role |
| :--- | :--- |
| $\theta$ (theta) | The orientation of the sinusoidal wave. It determines which direction of edges or lines the filter is most sensitive to — e.g., 0° for vertical lines, 90° for horizontal lines. |
| $w$ or $\lambda$ (lambda) | The wavelength or frequency of the sinusoidal wave. It controls the thickness of the stripes the filter is tuned to detect. |
| $\sigma$ (sigma) | The standard deviation of the Gaussian envelope. It determines the size of the receptive field (the neighborhood the filter considers). |

Orientation selects the direction the filter responds to, wavelength selects the spatial rate of the pattern, and the Gaussian's spread sets how large a neighborhood contributes to the response.

## The power of dual localization

The primary strength of the Gabor filter is its optimal localization in both the **spatial domain** and the **frequency domain**. Because of the Gaussian envelope, the filter's response is concentrated in a small area of the image — this is its spatial localization. Because of the sinusoidal component, the filter is tuned to respond strongly to a narrow band of frequencies and orientations — this is its frequency localization.

> [!tip] Insight
> This dual localization allows the Gabor filter to identify *what* kind of pattern exists (frequency/orientation) and *where* it exists in the image (spatial location). This makes it exceptionally powerful for texture classification, as a texture can be defined by the distribution of specific oriented patterns across an area.

## Gabor filter banks

In practice, a single Gabor filter is not used in isolation. Instead, a **filter bank** is created, consisting of multiple Gabor filters with a range of different orientations and frequencies. By convolving an image with each filter in the bank, a rich set of feature responses is generated, and this set of responses can then be used as a feature vector to train a machine learning classifier for tasks like texture recognition or material identification.

## See also

- [[Image Processing Global Index]] — the orientation note for the classical image-processing chapter.
- [[The Mechanics of Spatial Filtering]] — kernels, correlation versus convolution, and boundary handling.
- [[Linear Smoothing Filters]] — the Gaussian family on its own, without modulation.
- [[Sharpening and Edge Detection]] — orientation-sensitive edge operators from the same chapter.
- [[Feature Descriptors - SIFT, SURF, ORB, HOG]] — the feature-descriptor family these responses feed.
- [[From Basic Convolution to Learned Weights]] — how CNN first layers end up learning classical filters, Gabor filters included.
- [[The Fourier Transform]] — the frequency-domain analysis the sinusoid tunes into.
