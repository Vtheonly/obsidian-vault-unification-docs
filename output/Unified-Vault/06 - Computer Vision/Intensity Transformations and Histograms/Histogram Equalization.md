---
title: Histogram Equalization
type: concept
aliases:
  - HE
  - Histogram Flattening
tags:
  - image-processing
  - computer-vision
  - histogram
  - histogram-equalization
  - contrast-enhancement
  - cumulative-distribution-function
  - intensity-transformations
sources:
  - "2.4 Histogram Equalization (HE)"
created_index: 42
---

While [[Contrast Stretching]] spreads the histogram linearly, histogram equalization transforms the image so that the output histogram is approximately **uniform** (flat). The transformation that accomplishes this is the cumulative distribution function of the input histogram. This note develops the entropy argument for a flat histogram, the CDF formula, a step-by-step discrete example, and the artifacts the discrete version produces.

## The goal: maximizing entropy

Information theory tells us that an image contains the most information (maximum entropy) when all gray levels are equiprobable. Visually, this means the image has optimal contrast across all gray levels. The goal is a transformation $s = T(r)$ such that $p_s(s) = \text{constant}$ — a mapping after which every output level is equally likely.

## The mathematical foundation (CDF)

The transformation function that accomplishes this is the **cumulative distribution function (CDF)** of the input histogram:

$$ s_k = T(r_k) = (L-1) \sum_{j=0}^{k} p_r(r_j) $$

Here $L$ is the number of gray levels (256), $p_r(r_j)$ is the probability (normalized count) of gray level $j$, and the sum $\sum p_r$ is the cumulative probability. Each output level is thus the input's cumulative probability rescaled to the image's gray-level range.

### Why the CDF?

Two properties make the CDF the right choice of transformation:

1. **Monotonicity:** the CDF is monotonically increasing ($T(r)$ never goes down as $r$ goes up). This preserves the order of brightness — dark pixels stay darker than bright pixels.
2. **Range:** the CDF outputs values between 0 and 1. Multiplying by $(L-1)$ scales it to the image range.

## A discrete example step by step

Assume a 3-bit image ($L=8$, values 0-7) with total pixels $N$. Equalization runs in five steps:

1. **Count pixels ($n_k$):** $r_0=0$: 10 pixels; $r_1=1$: 20 pixels ... etc.
2. **Calculate PDF ($p_r$):** divide counts by $N$.
3. **Calculate CDF:** accumulate the probabilities — $CDF_0 = p_0$, then $CDF_1 = p_0 + p_1$, then $CDF_2 = p_0 + p_1 + p_2$, and so on up the gray levels.
4. **Map new levels ($s_k$):** $s_k = \text{round}((L-1) \times CDF_k)$, which here is $s_k = \text{round}(7 \times CDF_k)$.
5. **Replace:** go through the original image. Every pixel with value $r_0$ is replaced by $s_0$, every $r_1$ by $s_1$, etc.

## Visual result

After equalization the histogram is flattened, and the image typically shows significantly increased contrast. One artifact is inherent: because discrete values are grouped together, the histogram won't be perfectly flat — it will look "sparse" or comb-like — but the cumulative distribution will be linear. The linear CDF, not a perfectly flat bar plot, is what carries the contrast gain.

## See also

- [[Image Processing Global Index]]
- [[Contrast Stretching]]
- [[The Image Histogram]]
- [[Advanced Histogram Techniques]]
- [[Point Processing Operations]]
- [[Image Fundamentals and Histograms Quiz]]
