---
title: Mathematical Morphology Basics
type: concept
aliases:
  - Mathematical Morphology
  - Morphology
  - Structuring Element
  - 5.1 Mathematical Morphology Basics
tags:
  - image-processing
  - computer-vision
  - mathematical-morphology
  - set-theory
  - structuring-element
  - binary-images
sources:
  - "5.1 Mathematical Morphology Basics"
created_index: 49
---

Mathematical morphology is a theory and technique for the analysis and processing of geometrical structures, based on set theory, lattice theory, and topology. Where spatial filtering is arithmetic — sums and products of pixel values — morphology is geometry: the image is probed with a small shape called a structuring element (SE), and what the probe reveals depends on how it fits or misses the shapes in the image. This note sets up the three pieces of vocabulary every morphological operation relies on: the image as a set, the structuring element with its attributes, and the two set operations — reflection and translation — used to position it.

## Morphology is geometry, not arithmetic

Spatial filters are based on arithmetic operations: weighted sums and products of pixel values. Morphological operations are based on **geometry** instead. We probe an image with a small shape — the structuring element — and observe how it fits or misses the shapes in the image, so the result is a statement about shape rather than about intensity. The arithmetic paradigm is developed in [[The Mechanics of Spatial Filtering]]; the geometric one powers everything from [[Erosion and Dilation]] to the compound operations and algorithms built on top of them.

## Images as sets

In morphology, an image is treated as a set of coordinates. For binary images the set lives in $\mathbb{Z}^2$: if a pixel at $(x,y)$ is 1 (white), it belongs to the set $A$; if it is 0 (black), it does not. By convention, morphology is performed on the foreground (the white pixels), so set membership means "this pixel is part of an object."

## The structuring element

The structuring element is the "kernel" of morphology: a small set used to probe the input image. It plays the role a kernel plays in spatial filtering, but its job is purely geometric — what matters is where its pixels sit, not any values they carry. Every morphological operation is defined by sliding this probe across the image and recording geometric answers.

### Shape, origin, and size

Three attributes define a structuring element. **Shape** can be a square, disk, cross, or line, and the shape you choose determines which features are preserved — for example, a horizontal line SE will "delete" vertical lines. **Origin**: one pixel in the SE is designated as the origin (usually the center) — the reference point that corresponds to the pixel currently being processed in the input image. **Size** controls the strength of every operation: a $3 \times 3$ SE has a small effect, while a $21 \times 21$ SE has a massive effect.

### Reflection and translation

Two set operations describe how the SE is oriented and moved. **Reflection** ($\hat{B}$) is the set of points in $B$ rotated $180^\circ$ around the origin. **Translation** ($B_z$) is the act of shifting the entire SE so that its origin sits at coordinate $z$. Both notations appear verbatim in the formal definitions of the fundamental operations — dilation probes with the translated reflection $(\hat{B})_z$, erosion with the translated element $(B)_z$ — which is why they are worth fixing before moving on to [[Erosion and Dilation]].

## The probe philosophy

Think of the SE as a physical probe or a "cookie cutter." Sliding it over the image, we can ask two questions: "Does the SE **fit** entirely inside the object?" and "Does the SE **touch** the object at any point?" These two questions are the foundation of the whole morphological family — erosion is the formal answer to the fit question, dilation to the touch question — and every operation built on top, from [[Opening and Closing]] to the algorithms in [[Morphological Algorithms]], composes those two answers.

## See also

- [[Erosion and Dilation]] — the two fundamental operations, defined with reflection and translation.
- [[Opening and Closing]] — compound operations that clean the image while preserving object size.
- [[Morphological Algorithms]] — boundary extraction, region filling, skeletonization, and Hit-or-Miss.
- [[Thresholding and Otsu's Method]] — how the binary images that morphology treats as sets are produced.
- [[The Mechanics of Spatial Filtering]] — the arithmetic paradigm morphology is contrasted with.
- [[Image Processing Global Index]] — the area's reading map.
