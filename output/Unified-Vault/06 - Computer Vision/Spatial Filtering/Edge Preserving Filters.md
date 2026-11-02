---
title: Edge Preserving Filters
type: concept
aliases:
  - Edge-Preserving Smoothing
  - Nagao Filter
  - Bilateral Filter
  - Anisotropic Diffusion
  - Perona-Malik Diffusion
tags:
  - image-processing
  - computer-vision
  - spatial-filtering
  - smoothing
  - edge-preserving
  - nagao-filter
  - bilateral-filter
  - anisotropic-diffusion
  - perona-malik
sources:
  - "3.4 Edge Preserving Filters"
created_index: 64
---

Standard smoothing filters blur noise and edges alike — the same averaging that flattens a speck of noise also flattens a boundary. Edge-preserving filters attempt to smooth noise only in flat areas while "stopping" at edges. The three classical strategies are the Nagao filter, which adaptively selects the most uniform sub-neighborhood; the bilateral filter, which combines two Gaussian weights; and anisotropic diffusion (Perona-Malik), which recasts smoothing as heat flow that cannot cross an edge. They refine the fixed-kernel smoothers of [[Linear Smoothing Filters]], which blur noise and edges without distinction, and complement the rank-order smoothers of [[Non-Linear Smoothing Filters]].

## The Nagao filter

The Nagao filter is an adaptive filter that searches for the "best" neighborhood instead of committing to a fixed one. For a $5 \times 5$ window, it defines 9 overlapping sub-regions (representing corners, lines, and center), then runs a four-step selection:

1. Calculate the variance ($\sigma^2$) of each of the 9 sub-regions.
2. Find the sub-region with the minimum variance (the "calmest" or most uniform area).
3. Calculate the mean of only that specific sub-region.
4. Replace the center pixel with that mean.

The selection step is what makes the filter edge-preserving. If the center pixel is near an edge, the sub-regions crossing the edge will have high variance, while the sub-regions sitting entirely on one side of the edge will have low variance. By choosing the low-variance sub-region, the filter never "blurs across" the edge.

## The bilateral filter

The bilateral filter is the most popular edge-preserving smoother in modern photography. It uses two Gaussian weights combined:

1. **Spatial weight ($G_s$):** based on geometric distance (standard Gaussian) — closer pixels have more weight.
2. **Range weight ($G_r$):** based on intensity difference — pixels with a similar color to the center have more weight.

A neighbor must therefore pass both tests to influence the output. The result: a pixel that is physically close but has a vastly different color (like across an edge) is ignored. This is exactly the case where the plain Gaussian of [[Linear Smoothing Filters]] falls short, since it weights by geometric distance alone.

## Anisotropic diffusion (Perona-Malik)

Anisotropic diffusion is based on the physics of heat diffusion: it treats the image like a metal plate where heat (intensity) spreads over time. The smoothing rate is governed by a "conductivity" term, and letting that term differ by location is the whole trick. The conductivity is high in flat areas, giving fast smoothing there, and it is set to zero at edges, so heat cannot cross the edge. The visual result is a "cartoon" effect where colors are flat but boundaries are razor-sharp.

## See also

- [[Linear Smoothing Filters]] — the box and Gaussian smoothers these filters improve on.
- [[Non-Linear Smoothing Filters]] — the median family for impulse noise.
- [[The Mechanics of Spatial Filtering]] — the fixed-neighborhood machinery the Nagao filter adapts.
- [[Sharpening and Edge Detection]] — the edges these filters are built to protect.
- [[Image Degradation and Noise Models]] — matching the filter to the noise model.
- [[Spatial Filtering and Convolution Quiz]] — self-testing on this subfamily.
- [[Image Processing Global Index]] — the area's reading map.
