---
title: Erosion and Dilation
type: concept
aliases:
  - Erosion
  - Dilation
  - Morphological Erosion
  - Morphological Dilation
  - 5.2 Erosion and Dilation
tags:
  - image-processing
  - computer-vision
  - mathematical-morphology
  - binary-images
  - erosion
  - dilation
  - duality
sources:
  - "5.2 Erosion and Dilation"
created_index: 48
---

Erosion and dilation are the two fundamental operations of mathematical morphology: every other morphological algorithm is built by combining these two. Dilation "grows" or "thickens" objects in a binary image, while erosion "shrinks" or "thins" them, and each is the mathematical dual of the other. This note gives each operation's set-theoretic definition, its pixel-level procedure, and its classic applications, then records the duality identity that ties the two together. The vocabulary used throughout — the structuring element (SE), its reflection, and its translation — is set up in [[Mathematical Morphology Basics]].

## Dilation

Dilation ($\oplus$) "grows" or "thickens" objects in a binary image. Formally, the dilation of image set $A$ by structuring element $B$ is the set

$$ A \oplus B = \{z \mid (\hat{B})_z \cap A \neq \emptyset \} $$

In plain English: the dilation of $A$ by $B$ is the set of all points $z$ such that the reflected SE, when translated to $z$, **overlaps with at least one pixel** of $A$. This is the "touch" probe: a single pixel of overlap is enough to make $z$ part of the result, so the foreground spreads outward wherever the structuring element grazes it.

### Pixel-level procedure

Applied to an image, the definition becomes a simple loop:

1. Place the origin of the SE on pixel $(x,y)$.
2. Look at all image pixels covered by the SE.
3. If **any** of those pixels are 1, the output at $(x,y)$ is 1.
4. Otherwise, the output is 0.

### Applications

Dilation's growing behavior makes it the tool of choice for two cleanup jobs. Bridging gaps: if a line is broken by a small 1-pixel gap, dilation will connect it, because the thickened line reaches across the break. Filling small holes: pepper noise (black dots inside white objects) is filled, as the surrounding object expands over the dark specks.

## Erosion

Erosion ($\ominus$) "shrinks" or "thins" objects. It is the mathematical dual of dilation. Formally, the erosion of $A$ by $B$ is the set

$$ A \ominus B = \{z \mid (B)_z \subseteq A \} $$

In plain English: the erosion of $A$ by $B$ is the set of all points $z$ such that the SE, when translated to $z$, is **contained entirely** within $A$. This is the "fit" probe: the point survives only where the whole structuring element fits inside the object. Note what is being translated, too — dilation uses the reflected element $(\hat{B})_z$, whereas erosion uses the structuring element itself, $(B)_z$.

### Pixel-level procedure

The loop is identical to dilation's; only the test changes:

1. Place the origin of the SE on pixel $(x,y)$.
2. Look at all image pixels covered by the SE.
3. If **every single** covered pixel is 1, the output at $(x,y)$ is 1.
4. If even one covered pixel is 0 (background), the output is 0.

> [!info] The one-word difference
> Dilation asks whether **any** covered pixel is 1; erosion asks whether **every** covered pixel is 1. The two procedures are otherwise identical, which is exactly why they behave as duals.

### Applications

Erosion's shrinking behavior gives it two mirror-image jobs. Eliminating noise: small isolated white pixels (salt noise) disappear because the SE cannot "fit" inside them. Separating objects: if two circles are touching by a thin neck, erosion will remove the neck, leaving two separate circles.

## Duality

Erosion and dilation are duals with respect to set complementation:

$$ (A \ominus B)^c = A^c \oplus \hat{B} $$

*Meaning:* eroding the foreground is the same as dilating the background. The complement of an eroded image is the dilation of the complemented image by the reflected structuring element — one identity with two readings, depending on which color you call the foreground.

## See also

- [[Mathematical Morphology Basics]] — set-theoretic foundations: structuring elements, reflection, translation.
- [[Opening and Closing]] — compound operations that pair erosion with dilation to clean the image while preserving object size.
- [[Morphological Algorithms]] — boundary extraction, region filling, skeletonization, and Hit-or-Miss, all built by combining these two operations.
- [[Image Degradation and Noise Models]] — salt-and-pepper noise: erosion clears the salt, dilation fills the pepper.
- [[Image Processing Global Index]] — the area's reading map.
