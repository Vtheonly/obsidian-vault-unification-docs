---
title: Morphological Algorithms
type: concept
aliases:
  - Boundary Extraction
  - Region Filling
  - Skeletonization
  - Hit-or-Miss Transform
  - Thinning and Thickening
tags:
  - image-processing
  - computer-vision
  - mathematical-morphology
  - boundary-extraction
  - region-filling
  - skeletonization
  - hit-or-miss-transform
  - grayscale-morphology
  - morphological-processing
sources:
  - "5.4 Morphological Algorithms"
created_index: 50
---

The morphological primitives ($\oplus, \ominus, \circ, \bullet$) compose into algorithms that extract structural information from binary images. This note covers the classic morphological algorithms: boundary extraction, region filling, skeletonization, and the Hit-or-Miss transform for pattern matching, together with the thinning/thickening duality and the extension of the whole toolkit to grayscale images. It assumes the primitives from [[Mathematical Morphology Basics]], [[Erosion and Dilation]], and [[Opening and Closing]].

## Boundary extraction

How do we find the "outline" of a binary object $A$? The morphological answer is a subtraction, run in two moves:

1. **Erode** $A$ by a small $3 \times 3$ SE. This gives a slightly smaller version of $A$ (shrunk by one pixel on all sides).
2. **Subtract** the eroded version from the original:

$$\beta(A) = A - (A \ominus B)$$

The result is a **1-pixel-thick boundary** of the object — the pixels that are in $A$ but not in the eroded $A$ (i.e., the outermost layer).

Why this works: erosion removes the boundary pixels (shrinks the object), so subtracting the shrunk version from the original leaves exactly the pixels that were removed — the boundary. Applications include measuring perimeter (count the boundary pixels), edge-based feature extraction, and detecting object contours for shape analysis.

## Region filling

If we have a boundary and want to fill the inside, we grow a seed outward and clip the growth at the boundary:

1. Start with a point $X_0$ inside the boundary.
2. **Iteratively dilate** the point: $X_k = (X_{k-1} \oplus B) \cap A^c$.
3. The intersection with $A^c$ (the complement of the boundary) ensures the "growth" doesn't leak outside the boundary.
4. Stop when $X_k = X_{k-1}$ (convergence — the region is filled).

Why this works: dilation expands the seed point, but the intersection with $A^c$ (everything except the boundary) clips the expansion at the boundary. The seed grows until it fills the entire interior, then stops. Applications include filling holes in segmented objects (e.g., a donut-shaped object that should be solid) and flood fill — the "paint bucket" tool in image editors is a variant of this.

## Skeletonization (thinning / medial axis)

The goal is to reduce an object to a **1-pixel-wide "stick figure"** that represents its topology — the **medial axis** (the set of points equidistant from at least two boundary points). The procedure: repeatedly erode the image but **do not** remove pixels if doing so would break the connectivity (split the object into two pieces) or remove an endpoint (shorten the skeleton). The result is a skeleton that is equidistant from the boundaries — a compact representation of the object's shape.

**The Zhang-Suen algorithm** (1984) is the standard thinning algorithm. It makes two passes per iteration, each removing specific "deletable" pixels (those with the right number of neighbors and the right crossing number). The algorithm converges when no more pixels can be removed.

Skeletons are the working representation wherever stroke or ridge structure matters:

- **OCR:** skeletonize handwritten characters before feature extraction — the skeleton is invariant to stroke width.
- **Fingerprint analysis:** the skeleton of fingerprint ridges is the basis for minutiae detection.
- **Vessel/road extraction:** skeletonize segmented blood vessels or roads to get the centerline network.
- **Shape matching:** skeletons are more compact and rotation/translation-invariant than the original shapes.

## Hit-or-miss transform (pattern matching)

The Hit-or-Miss Transform (HMT) is a **binary template matching** operation that finds all locations where a specific pattern (described by two SEs — one for the object, one for the background) matches the image. Given a pattern described by $B_1$ (the object part) and $B_2$ (the background part):

$$A \circledast B = (A \ominus B_1) \cap (A^c \ominus B_2)$$

The result is the set of points where $B_1$ fits entirely inside the object AND $B_2$ fits entirely inside the background — i.e., the exact pattern is present.

Applications:

- Finding specific configurations (e.g., corner detection — define a corner pattern).
- Detecting isolated points (a single foreground pixel surrounded by background).
- Pruning skeleton endpoints (find and remove the endpoint pattern).

The HMT is the morphological equivalent of convolution with a template — it locates exact binary patterns. It is sensitive to exact matches (a single pixel difference fails), so it is less used than correlation-based template matching for real images.

## Thickening and thinning

**Thinning** (used in skeletonization) and **thickening** are dual operations:

- **Thinning:** $A \oslash B = A - (A \circledast B)$ — remove pixels that match a "deletable" pattern.
- **Thickening:** $A \odot B = A \cup (A^c \circledast B)$ — add pixels that match an "addable" pattern.

By choosing the right patterns $B$, thinning produces skeletons and thickening produces "grown" structures. Multiple patterns (usually 8, one per direction) are applied in sequence to make the operation rotation-symmetric.

## Grayscale morphology

All of the above is for **binary** morphology. The operations extend to grayscale images:

- **Grayscale erosion** = local minimum (darkens the image).
- **Grayscale dilation** = local maximum (brightens the image).
- **Grayscale opening** = removes bright spots smaller than the SE.
- **Grayscale closing** = removes dark spots smaller than the SE.
- **Morphological gradient** = dilation - erosion (edge detector).
- **Top-hat transform** = image - opening (extracts bright features smaller than the SE).
- **Bottom-hat transform** = closing - image (extracts dark features smaller than the SE).

Grayscale morphology is useful for **background correction** (top-hat removes uneven illumination), **feature extraction** (morphological gradient for edges), and **non-linear smoothing** (opening removes bright noise, closing removes dark noise).

## Key takeaways

**Boundary extraction** is $\beta(A) = A - (A \ominus B)$: erode and subtract to get the 1-pixel boundary. **Region filling** iteratively dilates a seed, intersecting with the complement of the boundary, until convergence. **Skeletonization** thins an object to a 1-pixel medial axis while preserving connectivity and endpoints; Zhang-Suen is the standard algorithm, and it is used in OCR, fingerprints, and vessel extraction. The **Hit-or-Miss Transform** is binary pattern matching — find locations where an object SE fits AND a background SE fits. In **grayscale morphology**, erosion is the local minimum and dilation the local maximum; top-hat and bottom-hat extract bright and dark features smaller than the SE, and the morphological gradient detects edges.

## See also

- [[Image Processing Global Index]]
- [[Mathematical Morphology Basics]]
- [[Erosion and Dilation]]
- [[Opening and Closing]]
- [[Thresholding and Otsu's Method]] — the binarization that precedes these algorithms
- [[Watershed Segmentation]]
- [[Connected Components and Region Properties]]
- [[Deep Learning for Imaging]]
