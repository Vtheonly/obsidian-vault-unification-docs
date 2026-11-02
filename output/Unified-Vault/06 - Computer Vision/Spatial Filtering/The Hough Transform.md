---
title: The Hough Transform
type: concept
aliases:
  - Hough Transform
  - Hough Line Transform
  - Circle Hough Transform
  - Generalized Hough Transform
  - Probabilistic Hough Transform
  - 3.10 The Hough Transform — Detecting Lines and Curves
tags:
  - image-processing
  - computer-vision
  - spatial-filtering
  - hough-transform
  - parameter-space-voting
  - accumulator-array
  - line-detection
  - circle-detection
  - shape-detection
  - edge-detection
sources:
  - "3.10 The Hough Transform"
created_index: 72
---

The **Hough transform** is a classical technique for detecting **parametric shapes** — most commonly lines and circles — in edge images. Its defining strength is that it can find shapes even when they are broken, noisy, or partially occluded: rather than grouping edge pixels directly, it lets every edge pixel **vote** in a **parameter space**, and the shapes that accumulate many votes win. The transform consumes the edge maps produced by [[Sharpening and Edge Detection]] and [[Canny and LoG Edge Detection]], and it connects to the feature-extraction machinery of [[Feature Descriptors - SIFT, SURF, ORB, HOG]]. This note explains the line Hough transform (the canonical example) and the circle Hough transform.

## The problem with edge linking

After running an edge detector such as Sobel or Canny, you have an edge map — but the edges are individual pixels, not geometric shapes. To find a **line** in the image, you would need to group those edge pixels into line segments, and this is hard for three reasons: edges may have gaps where the detector missed some pixels, multiple lines may intersect, and noise creates spurious edge pixels. **Edge linking** — connecting adjacent edge pixels into chains — handles simple cases but breaks on exactly those gaps and intersections. The Hough transform takes a different, more robust approach to the same problem.

## The key idea: vote in parameter space

Instead of trying to connect edge pixels directly, the Hough transform lets each edge pixel **vote** for all the shapes it could be part of. Shapes that receive many votes are likely to be real, because many edge pixels agree on them. This inversion — from "find the shape that fits the pixels" to "let the pixels elect the shape" — is what makes the method tolerant of gaps, noise, and partial occlusion.

### The line parameterization

A line can be described by $y = mx + b$, where $m$ is the slope and $b$ is the intercept, so each line corresponds to a point $(m, b)$ in **parameter space**. For each edge pixel $(x_0, y_0)$, all lines passing through it satisfy $y_0 = m x_0 + b$, i.e., $b = y_0 - m x_0$ — which is itself a **line in $(m, b)$ parameter space**. Each edge pixel therefore votes for a **line of possibilities** in parameter space, and multiple edge pixels on the same image line vote for parameter-space lines that **all intersect at the same point**: the $(m, b)$ of the image line.

In outline, the algorithm is:

1. Discretize the parameter space into bins (the **accumulator array**).
2. For each edge pixel, compute the parameter-space line and increment all bins it passes through.
3. Find the bins with the most votes — these correspond to detected lines.

### The $(\rho, \theta)$ parameterization

The $(m, b)$ parameterization has a problem: vertical lines have $m = \infty$, which cannot be represented. The standard fix uses the **normal form**:

$$\rho = x \cos\theta + y \sin\theta$$

where $\rho$ is the perpendicular distance from the origin to the line and $\theta$ is the angle of the normal. Every line has a finite $(\rho, \theta)$ representation. Each edge pixel now votes for a **sinusoidal curve** in $(\rho, \theta)$ space — not a line, but the same principle applies.

> [!warning] Why not just use slope-intercept?
> The infinite-slope failure of $y = mx + b$ is the reason virtually every implementation parameterizes lines by $(\rho, \theta)$ instead: the normal form assigns every possible line — vertical ones included — a finite pair of coordinates that the accumulator can bin.

### The algorithm, concretely

The full line-transform pipeline runs as follows:

1. Run edge detection → binary edge image.
2. Initialize the accumulator array $A[\rho, \theta]$ to zeros. $\rho$ ranges over $[-D, D]$ (where $D$ is the image diagonal); $\theta$ ranges over $[0, \pi)$ (or $[0, 2\pi)$).
3. For each edge pixel $(x, y)$:
   - For each $\theta$ in the discretized range:
     - Compute $\rho = x \cos\theta + y \sin\theta$.
     - Increment $A[\rho, \theta]$.
4. Find local maxima in $A$ above a threshold — these are the detected lines.
5. (Optional) For each detected $(\rho, \theta)$, find the edge pixels that contributed to it, and determine the line segment endpoints.

The first four steps detect infinite lines; step 5 is what recovers the actual segment extent when endpoints are needed.

### Why this works

Four observations explain the robustness. A single noisy edge pixel contributes one sinusoid, so it does not create a strong peak. Many edge pixels on the same line contribute sinusoids that all pass through the same $(\rho, \theta)$ point — this point gets many votes and is detected. Gaps in the edge do not matter, because the pixels on either side of the gap still vote for the same $(\rho, \theta)$. Intersecting lines are fine, because each line has its own peak in parameter space.

The Hough transform is a **global** method: it considers all edge pixels simultaneously, which makes it robust to noise and gaps but also computationally expensive — $O(\text{num\_edge\_pixels} \times \text{num\_}\theta\text{\_bins})$.

## The circle Hough transform

Circles are parameterized by center $(a, b)$ and radius $r$:

$$(x - a)^2 + (y - b)^2 = r^2$$

This has **3 parameters** (versus 2 for lines), so the accumulator is 3-dimensional: for each edge pixel and each possible radius $r$, the pixel votes for a circle of possibilities in $(a, b)$ space. The cost of that extra dimension is real, but there is a well-known optimization: the gradient direction at each edge pixel (from Sobel) tells you the direction toward the circle's center. Instead of voting for an entire circle of possible centers, each pixel votes only along the gradient direction — this reduces the votes per pixel from $O(\text{circumference})$ to $O(1)$ and dramatically speeds up the transform. OpenCV exposes this gradient-based variant through `cv2.HoughCircles`:

```python
import cv2
# Detect circles
circles = cv2.HoughCircles(
    image, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
    param1=100, param2=30, minRadius=10, maxRadius=100
)
```

## The generalized Hough transform

The Hough idea generalizes to any shape that can be parameterized. For arbitrary (non-parametric) shapes, the **Generalized Hough Transform** uses a lookup table of edge orientations relative to a reference point, built from a template shape. It is powerful but computationally expensive, and it is rarely used now that deep learning handles shape detection.

## Applications

The transform's tolerance of broken and partial shapes makes it a workhorse wherever known geometry must be located in an image. The classic deployments are:

- **Lane detection in autonomous driving:** detect lane markings (lines) on the road.
- **Document analysis:** detect text lines and table borders.
- **Medical imaging:** detect circular structures (cells, pupils, implants).
- **Industrial inspection:** detect manufactured parts with known shapes.
- **Particle counting:** count circular cells or droplets in microscopy images.

## Limitations

Four limitations should be kept in mind when choosing the tool.

1. **Computationally expensive:** the line transform is $O(N \cdot \Theta)$ where $N$ is the number of edge pixels and $\Theta$ is the number of $\theta$ bins. For large images, this is slow. The **Probabilistic Hough Transform** (OpenCV's `HoughLinesP`) samples edge pixels randomly instead of using all of them, which is much faster with similar results.
2. **Parameter tuning:** the accumulator threshold, the $\rho/\theta$ bin sizes, and (for circles) the radius range all need tuning. Bad parameters produce missed detections or false positives.
3. **Only finds parametric shapes:** lines, circles, ellipses. For arbitrary shapes, use template matching or deep learning.
4. **Co-linear but separate segments are merged:** the basic Hough transform detects lines, not line segments. To get segments, you must post-process — find the edge pixels that voted for each line and group them into segments.

## Key takeaways

The Hough transform detects parametric shapes — lines and circles — by voting in parameter space: each edge pixel votes for all the shapes it could be part of, and shapes receiving many votes are detected. Lines use the $(\rho, \theta)$ parameterization, which avoids the infinite-slope problem of slope-intercept form, and each edge pixel votes for a sinusoid in $(\rho, \theta)$ space. Circles use a 3-dimensional accumulator over $(a, b, r)$, and the gradient-direction optimization cuts the votes per pixel from $O(\text{circumference})$ to $O(1)$. Because voting is global, the transform is robust to gaps and noise, but it is computationally expensive — the probabilistic variant helps — and it only finds parametric shapes, so arbitrary shapes belong to template matching or deep learning while Hough remains useful for lines, circles, and their relatives in applications from lane detection and document analysis to medical imaging and industrial inspection.

## See also

- [[Image Processing Global Index]] — the orientation note for the classical image-processing chapter.
- [[Sharpening and Edge Detection]] — the edge detectors whose output feeds the Hough transform.
- [[Canny and LoG Edge Detection]] — the advanced edge pipeline that precedes shape voting.
- [[Feature Descriptors - SIFT, SURF, ORB, HOG]] — the feature-extraction family the transform connects to.
- [[Image Pyramids and Multi-Scale Representation]] — multi-scale machinery from the same filtering chapter.
- [[Introduction to the Frequency Domain]] — the next stop in the classical reading order.
- [[Spatial Filtering and Convolution Quiz]] — flashcards covering this chapter's material.
