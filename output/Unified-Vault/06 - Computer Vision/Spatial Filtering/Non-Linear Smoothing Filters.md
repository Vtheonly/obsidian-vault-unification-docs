---
title: Non-Linear Smoothing Filters
type: concept
aliases:
  - Rank-Order Filters
  - Order-Statistic Filters
  - Median Filter
  - Min and Max Filters
tags:
  - image-processing
  - computer-vision
  - spatial-filtering
  - smoothing
  - median-filter
  - rank-order-filters
  - order-statistics
  - impulse-noise
  - salt-and-pepper-noise
sources:
  - "3.3 Non-Linear Smoothing Filters"
created_index: 70
---

Non-linear filters do not use a weighted sum. Instead, they sort the pixels in the neighborhood and pick a value based on their rank — which is why this family is also called rank-order (order-statistic) filtering. Ranking changes what a filter can ignore: an extreme pixel can drag a weighted average far off course, but it occupies only one slot in a sorted list. That robustness makes the median filter, the head of this family, the most powerful tool for removing impulse noise (salt & pepper); the weighted-sum alternative lives in [[Linear Smoothing Filters]], and the adaptive smoothers in [[Edge Preserving Filters]].

## The median filter

The median filter is the most powerful tool for removing impulse noise (salt & pepper). For each pixel it runs a five-step procedure:

1. Select a neighborhood (e.g., $3 \times 3$).
2. List the 9 pixel values.
3. Sort them in ascending order.
4. Pick the middle value (the 5th value for $3 \times 3$).
5. Assign this value to the center pixel.

Because the output is one of the neighborhood's own values rather than a manufactured average, a corrupted pixel is replaced outright instead of smeared into its neighbors.

### Why the median beats the mean for noise

The mean filter is sensitive to outliers. Give it 8 black pixels (0) and 1 "salt" noise pixel (255): the mean is 28, and the noise survives as a gray smudge. The median filter ignores outliers — in the same scenario, the sorted list is `[0,0,0,0,0,0,0,0,255]`, the median is 0, and the noise is completely deleted. The pair of scenarios is the cleanest argument for matching the filter to the noise model, which is the business of [[Image Degradation and Noise Models]].

## Min and max filters

The rank machinery can pick other positions in the sorted list as well. The max filter picks the largest value in the neighborhood; its use is removing "pepper" noise (black dots), and it brightens the image. The min filter picks the smallest value; its use is removing "salt" noise (white dots), and it darkens the image. The pairing is symmetric — each extreme-value filter removes the noise that lives at the opposite end of the intensity range, at the cost of shifting overall brightness.

## Mean versus median

The choice between the two families is a set of trade-offs rather than a single winner:

| Feature | Mean Filter | Median Filter |
| :--- | :--- | :--- |
| **Type** | Linear (Weighted Sum) | Non-Linear (Order Statistics) |
| **Best For** | Gaussian (Uniform) Noise | Salt & Pepper (Impulsive) Noise |
| **Edge Quality** | Blurs edges significantly | Preserves sharp edges well |
| **Computation** | Fast (Simple arithmetic) | Slower (Requires sorting) |

The mean filter is the match for Gaussian (uniform) noise, and its simple arithmetic keeps computation fast. Against salt & pepper (impulsive) noise it fails exactly as the worked example above shows, turning each defect into a gray smudge. The median costs more — sorting every neighborhood is slower than summing it — but it deletes impulse noise completely and preserves sharp edges well. The right pick follows the noise model.

## See also

- [[Linear Smoothing Filters]] — the box and Gaussian smoothers, and the mean filter compared above.
- [[Edge Preserving Filters]] — smoothers that refuse to cross edges.
- [[The Mechanics of Spatial Filtering]] — the neighborhood operation every filter here runs on.
- [[Sharpening and Edge Detection]] — the downstream use of the edges the median preserves.
- [[Image Degradation and Noise Models]] — the noise models behind the "best for" row.
- [[Spatial Filtering and Convolution Quiz]] — self-testing on this subfamily.
- [[Image Processing Global Index]] — the area's reading map.
