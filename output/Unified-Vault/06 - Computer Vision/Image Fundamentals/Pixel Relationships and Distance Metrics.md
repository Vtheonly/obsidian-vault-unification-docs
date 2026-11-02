---
title: Pixel Relationships and Distance Metrics
type: concept
aliases:
  - Pixel Neighborhoods
  - Pixel Adjacency
  - Distance Metrics
  - Digital Distance Metrics
  - N4 and N8 Neighbors
tags:
  - pixel-neighborhoods
  - adjacency
  - connectivity
  - 4-neighbors
  - 8-neighbors
  - m-adjacency
  - euclidean-distance
  - city-block-distance
  - chessboard-distance
  - manhattan-distance
  - chebyshev-distance
sources:
  - "1.6 Pixel Relationships and Distance Metrics"
created_index: 35
---

Understanding how pixels relate to their neighbors is fundamental for spatial filtering, segmentation, and morphology. This note defines the two standard neighborhoods of a pixel, the adjacency rules that turn "nearby" into "connected," and the three distance metrics used to measure how far apart two pixels are on the integer grid of [[What is a Digital Image]]. Together they provide the vocabulary that the neighborhood operations in [[The Mechanics of Spatial Filtering]] and the connectivity-based methods in [[Connected Components and Region Properties]] are built on.

## Neighbors of a pixel

For a coordinate $(x,y)$, which surrounding pixels matter? There are two standard answers, depending on whether diagonal positions count.

### The 4-neighbors

The **4-neighbors** of $(x,y)$, written $N_4$, are the pixels that share an **edge** with it. Their coordinates are $(x+1, y), (x-1, y), (x, y+1), (x, y-1)$ — the top, bottom, left, and right locations. Visually, they form a "cross" shape around the pixel.

### The 8-neighbors

The **8-neighbors** of $(x,y)$, written $N_8$, are the pixels that share an **edge or a corner** with it. Their coordinates are those of $N_4$ plus the 4 diagonal positions: $(x+1, y+1), (x+1, y-1), (x-1, y+1), (x-1, y-1)$ — the four diagonal neighbors, often denoted $N_D$. Visually, the 8-neighbors form a "square" surrounding the pixel.

## Adjacency and connectivity

Simply being next to each other is not enough for two pixels to belong to the same object. For two pixels to be "connected," they usually also need to share a property, such as color.

Formally, let $V$ be the set of intensity values that define "adjacency" — for example, $V=\{1\}$ for binary white pixels. Then:

1. **4-Adjacency:** two pixels $p$ and $q$ with values from $V$ are 4-adjacent if $q$ is in the set $N_4(p)$.
2. **8-Adjacency:** two pixels $p$ and $q$ with values from $V$ are 8-adjacent if $q$ is in the set $N_8(p)$.

> [!warning] The connectivity paradox
> Using 8-adjacency can sometimes lead to ambiguity in which an object appears connected and separated at the same time, depending on interpretation — a situation common in thin diagonal lines. This is solved by **m-adjacency**, but for most purposes understanding 4-adjacency versus 8-adjacency is sufficient.

## Distance metrics

How far apart are two pixels $p(x,y)$ and $q(s,t)$? In continuous math there is one answer, but in a digital grid there are three.

### Euclidean distance

The **Euclidean distance** $D_e$ is the straight-line distance, "as the crow flies":

$$ D_e(p, q) = \sqrt{(x-s)^2 + (y-t)^2} $$

Its equidistant shape is the circle: points at a fixed $D_e$ from a center form a circle. It is the most accurate metric geometrically, but it is computationally expensive — square roots are slow for computers.

### City-block distance

The **city-block distance** $D_4$, also called the **Manhattan** distance, is the distance when you can only move horizontally and vertically — like a taxi driving in Manhattan:

$$ D_4(p, q) = |x-s| + |y-t| $$

Its equidistant shape is the diamond: points at a fixed $D_4$ from a center form a diamond shape. (Circles, diamonds, and squares are the three metrics' equidistant shapes.) Its logic corresponds to counting steps in the $N_4$ neighborhood.

### Chessboard distance

The **chessboard distance** $D_8$, also called the **Chebyshev** distance, is the distance when you can move in any of the 8 directions — like a king in chess:

$$ D_8(p, q) = \max(|x-s|, |y-t|) $$

Its equidistant shape is the square: points at a fixed $D_8$ from a center form a square. Its logic corresponds to counting steps in the $N_8$ neighborhood — the diagonal move counts as distance 1, just like a horizontal move.

The three metrics are easiest to keep straight side by side, because each pairs a formula with a distinctive equidistant shape and a neighborhood whose steps it counts:

| Metric | Definition | Equidistant shape | Counts steps in |
| :--- | :--- | :--- | :--- |
| Euclidean $D_e$ | $\sqrt{(x-s)^2 + (y-t)^2}$ | Circle | — (straight line) |
| City-block $D_4$ | $\|x-s\| + \|y-t\|$ | Diamond | $N_4$ |
| Chessboard $D_8$ | $\max(\|x-s\|, \|y-t\|)$ | Square | $N_8$ |

## A worked comparison

Consider $p(0,0)$ and $q(3,3)$. The three metrics give three different answers:

- **Euclidean:** $\sqrt{3^2 + 3^2} = \sqrt{18} \approx 4.24$
- **City-block:** $|3| + |3| = 6$ (3 right, 3 down)
- **Chessboard:** $\max(3, 3) = 3$ (3 diagonal moves)

The insight to carry away is the ordering $D_8 \leq D_e \leq D_4$: the chessboard distance is always the "shortest" integer path, because diagonal moves are highly efficient.

## See also

- [[Image Processing Global Index]]
- [[What is a Digital Image]]
- [[The Mechanics of Spatial Filtering]]
- [[Connected Components and Region Properties]]
- [[Mathematical Morphology Basics]]
