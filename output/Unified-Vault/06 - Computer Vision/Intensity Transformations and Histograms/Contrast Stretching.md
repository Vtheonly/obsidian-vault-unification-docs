---
title: Contrast Stretching
type: concept
aliases:
  - Normalization
  - Contrast Normalization
  - Linear Contrast Stretching
  - 2.3 Contrast Stretching
tags:
  - image-processing
  - computer-vision
  - intensity-transformation
  - contrast-enhancement
  - dynamic-range
sources:
  - "2.3 Contrast Stretching"
created_index: 41
---

Contrast stretching (often called normalization) is a linear scaling function designed to expand the range of intensity levels in an image so that it spans the full intensity range of the recording medium or display device. It addresses one of the most common image defects: the washed-out look of an image whose values occupy only a narrow slice of the available range. This note develops the linear stretching formula and its two extensions — the extreme case of thresholding and the outlier-robust practice of clipping.

## The problem: low contrast

Images often look "washed out" because of poor lighting, a lack of dynamic range in the sensor, or wrong aperture settings. Whatever the cause, the pixel values end up confined to a narrow band while most of the representable range goes unused. For example, an image whose darkest pixel is 100 and whose brightest is 150 wastes the ranges [0, 99] and [151, 255], squeezing every perceptible difference into a 50-level window.

## Linear stretching formula

The fix is to map the current range $[r_{min}, r_{max}]$ to a target range $[s_{min}, s_{max}]$ (usually $[0, 255]$) with a single linear rescaling:

$$ s = \left( \frac{s_{max} - s_{min}}{r_{max} - r_{min}} \right) (r - r_{min}) + s_{min} $$

Every input level is shifted, scaled, and re-offset so that the observed range lands exactly on the target range. Because the remap is applied to each pixel independently, contrast stretching belongs to the family of point operations introduced in [[Point Processing Operations]] — it is the linear, range-filling member of that family.

### Full expansion

To stretch to the full 8-bit range $[0, 255]$, the general formula simplifies to:

$$ s = 255 \cdot \frac{r - r_{min}}{r_{max} - r_{min}} $$

The logic of the simplified form runs in three steps:

1. Subtract the minimum ($r - r_{min}$): this shifts the histogram to start at 0.
2. Divide by the range ($r_{max} - r_{min}$): this normalizes values to $[0, 1]$.
3. Multiply by 255: this scales values to $[0, 255]$.

After the stretch, the histogram spans the full available range instead of clustering in a narrow band — an effect you can verify directly with [[The Image Histogram]].

## Thresholding as the extreme case

Thresholding is a special case of contrast stretching in which the transfer function collapses to a step function:

$$ s = \begin{cases} 0 & \text{if } r < \text{threshold} \\ 255 & \text{if } r \ge \text{threshold} \end{cases} $$

The result is a binary image — black and white only, with no intermediate grays. Its main use case is segmentation, separating an object from its background, and the question of how to choose the threshold is treated in [[Thresholding and Otsu's Method]].

## Clipping for outlier robustness

Strict linear stretching is vulnerable to outliers: a single dead white pixel makes $r_{max}=255$ and so prevents any stretching at all. The standard solution is to pick the 5th percentile and the 95th percentile as $r_{min}$ and $r_{max}$ instead of the true extrema. Any pixel $< 5th$ percentile is set to 0 (clipped to black), and any pixel $> 95th$ percentile is set to 255 (clipped to white). The middle data is stretched, which produces a much punchier, higher-contrast image.

## See also

- [[Image Processing Global Index]] — the orientation note for the image-processing chapter.
- [[Point Processing Operations]] — the point-operation family: negatives, log transforms, gamma correction.
- [[Histogram Equalization]] — the histogram-driven alternative for contrast enhancement.
- [[The Image Histogram]] — the diagnostic that reveals a compressed intensity range.
- [[Thresholding and Otsu's Method]] — threshold selection as a full segmentation topic.
