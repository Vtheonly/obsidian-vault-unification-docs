---
title: Opening and Closing
type: concept
aliases:
  - Morphological Opening
  - Morphological Closing
  - Opening
  - Closing
  - 5.3 Opening and Closing
tags:
  - image-processing
  - computer-vision
  - mathematical-morphology
  - binary-images
  - opening
  - closing
  - idempotency
sources:
  - "5.3 Opening and Closing"
created_index: 51
---

Erosion and dilation are powerful, but used alone they change the size of objects. **Opening** and **Closing** are compound operations that clean the image while attempting to preserve the original size of the objects: each runs the two fundamental operations in sequence, so the size change of the first step is compensated by the second. Opening attacks small bright features from the outside; closing fills small dark features from the inside; and both are idempotent — a second pass changes nothing. The primitives themselves are defined in [[Erosion and Dilation]].

## Opening

Opening ($\circ$) is defined as an erosion followed by a dilation:

$$ A \circ B = (A \ominus B) \oplus B $$

The erosion step first strips away everything the structuring element cannot fit inside — small bright spots and thin connections. The dilation step then grows the surviving objects back toward their original size, so the cleanup is permanent while the net size change is small.

### The ball-rolling analogy

Imagine the SE is a circular ball. The opening of $A$ by $B$ is the set of all points reached by the ball as it rolls **inside** the object. The ball cannot fit into narrow "isthmuses" (necks) or sharp outward corners, so those parts are never reached and vanish from the result.

The analogy predicts both the effect and the property of opening. **Effect:** it removes small bright spots (noise), breaks thin connections, and rounds off sharp "peaks" from the outside. **Property:** it is *anti-extensive* — the result is always a subset of the original image, since a ball rolling inside the object can only reach points the object already contains.

## Closing

Closing ($\bullet$) is defined as a dilation followed by an erosion:

$$ A \bullet B = (A \oplus B) \ominus B $$

The order is reversed. The dilation step first swallows small dark gaps as the objects grow, and the erosion step then shrinks the objects back — with the filled gaps left in place. The net effect is cleanup from the inside rather than the outside.

### The ball on the outside

The visual logic is the same ball, now rolling on the **outside** of the object. The ball cannot fit into narrow "gulfs" or small holes inside the object, and the contour it traces seals them shut. **Effect:** it fills small black holes (pepper noise), joins narrow breaks, and smooths contours by filling in sharp inward "valleys." **Property:** it is *extensive* — the original image is always a subset of the result, because filling in can only add points.

## Idempotency

A crucial property of both opening and closing is that they are **idempotent**:

$$ (A \circ B) \circ B = A \circ B $$

Applying the operation a second time changes nothing. Once the noise is removed or the hole is filled, it stays that way — there is nothing left for a repeat pass to clean.

## Opening vs. closing at a glance

The two compound operations are mirror images, and the contrast is easiest to read side by side:

| Operation | Sequence | Main Goal |
| :--- | :--- | :--- |
| **Opening** | Erode $\to$ Dilate | Remove small objects / Smooth outward |
| **Closing** | Dilate $\to$ Erode | Fill small holes / Smooth inward |

> [!info] Which one to reach for
> Bright, small, outward-facing artifacts — spots, spikes, thin bridges — call for **opening**. Dark, small, inward-facing ones — holes, narrow breaks, valleys — call for **closing**.

In short: each operation's sequence fixes which primitive acts first, and its goal follows the direction — outward for opening, inward for closing — from which the ball smooths the contour.

## See also

- [[Erosion and Dilation]] — the primitives each compound operation is built from.
- [[Mathematical Morphology Basics]] — structuring elements and the probe philosophy behind the ball analogy.
- [[Morphological Algorithms]] — boundary extraction, region filling, skeletonization, and Hit-or-Miss.
- [[Image Processing Global Index]] — the area's reading map.
