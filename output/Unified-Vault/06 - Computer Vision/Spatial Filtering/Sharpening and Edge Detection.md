---
title: Sharpening and Edge Detection
type: concept
aliases:
  - Sobel Operator
  - Prewitt Operator
  - Laplacian Kernel
  - Unsharp Masking
  - High-Boost Filtering
tags:
  - image-processing
  - computer-vision
  - edge-detection
  - sharpening
  - sobel
  - prewitt
  - laplacian
  - unsharp-masking
  - gradients
sources:
  - "3.5 Sharpening and Edge Detection"
created_index: 71
---

Sharpening is the opposite of blurring: while blurring is an **integration** (averaging pixels together, which suppresses differences), sharpening is a **differentiation** (calculating the rate of change, which amplifies differences). This note covers the two classical edge-detection approaches — first-derivative (Sobel, Prewitt) and second-derivative (Laplacian) — plus the unsharp masking technique built on the Laplacian. It assumes the convolution mechanics of [[The Mechanics of Spatial Filtering]] and the smoothing filters of [[Linear Smoothing Filters]]; the more sophisticated Canny and LoG detectors refine the raw operators introduced here.

## Why edges matter

An **edge** is a boundary between two regions with different intensity. Edges are the most information-rich parts of an image: they delineate objects, reveal texture, and carry most of the structural content. The human visual cortex devotes enormous processing to edges (the Hubel-Wiesel simple cells detect oriented edges — see [[06 - Computer Vision/CNN Foundations and Philosophy/Introduction and Foundations of CNNs|Introduction and Foundations of CNNs]]), and classical image processing follows the same strategy: find the edges, and you have found the structure.

Mathematically, an edge is a location where the image's intensity changes rapidly. "Rapidly" means the **derivative** is large. So edge detection is fundamentally about computing derivatives of the image — and the choice between first and second derivatives shapes everything that follows.

## First derivative: gradients

The first derivative of an image tells us the **slope** of the intensity at each pixel. Where the slope is large, there is an edge; where the slope is zero, the image is flat.

In 2D, the derivative is a **gradient** — a vector with two components:

$$\nabla f = \begin{bmatrix} G_x \\ G_y \end{bmatrix} = \begin{bmatrix} \partial f / \partial x \\ \partial f / \partial y \end{bmatrix}$$

- **Magnitude** (edge strength): $\|\nabla f\| = \sqrt{G_x^2 + G_y^2}$
- **Direction** (edge orientation): $\theta = \arctan(G_y / G_x)$

In practice, the magnitude is often approximated as $|G_x| + |G_y|$ (faster to compute, similar results).

### The Sobel operator

The most common edge detector. It uses two $3 \times 3$ kernels to estimate $G_x$ and $G_y$ by computing weighted differences between pixels on either side of the center:

$$ G_x = \begin{bmatrix} -1 & 0 & 1 \\ -2 & 0 & 2 \\ -1 & 0 & 1 \end{bmatrix}, \quad G_y = \begin{bmatrix} -1 & -2 & -1 \\ 0 & 0 & 0 \\ 1 & 2 & 1 \end{bmatrix} $$

**Why these specific weights?** The Sobel kernel combines two ideas:

1. **A difference** (the $[-1, 0, 1]$ pattern) estimates the derivative — the rate of change in one direction.
2. **A smoothing** (the $[1, 2, 1]$ weighting perpendicular to the difference) averages over three rows, reducing noise. Without the smoothing, a single noisy pixel would produce a spurious edge.

So the Sobel operator is simultaneously a **differentiator in one direction and a smoothing filter in the perpendicular direction**. This is a design insight worth internalizing: edge detection is noisy, so you must smooth while differentiating.

### The Prewitt operator

A simpler variant that uses uniform weighting instead of the $[1,2,1]$ smoothing:

$$ G_x = \begin{bmatrix} -1 & 0 & 1 \\ -1 & 0 & 1 \\ -1 & 0 & 1 \end{bmatrix} $$

Prewitt is faster but noisier than Sobel (no smoothing emphasis on the center row). In practice, Sobel is preferred: without the smoothing, a single noisy pixel can create a spurious response, and the saving in cost rarely outweighs that.

### What the gradient tells you

- **Magnitude image:** bright where edges are strong, dark in flat regions. This is the "edge map."
- **Direction image:** the angle of the edge at each pixel. Used for non-maximum suppression in Canny (see [[Canny and LoG Edge Detection]]) and for analyzing edge orientation distributions.

**Limitation of first-derivative methods:** Sobel produces **thick edges** — the gradient is large over several pixels around the actual edge transition, so the edge map shows a blurry band rather than a sharp line. Thinning these to 1-pixel-wide lines requires the Canny detector, covered in [[Canny and LoG Edge Detection]].

## Second derivative: the Laplacian

The second derivative finds the **zero crossings** of the slope — the exact inflection points where the intensity transition is steepest. This produces thinner, more precise edge locations than the first derivative.

### The Laplacian kernel

The Laplacian is the sum of the second partial derivatives: $\nabla^2 f = \frac{\partial^2 f}{\partial x^2} + \frac{\partial^2 f}{\partial y^2}$. Two common $3 \times 3$ approximations:

$$ \begin{bmatrix} 0 & 1 & 0 \\ 1 & -4 & 1 \\ 0 & 1 & 0 \end{bmatrix} \quad \text{(4-connected)} \qquad \begin{bmatrix} 1 & 1 & 1 \\ 1 & -8 & 1 \\ 1 & 1 & 1 \end{bmatrix} \quad \text{(8-connected)} $$

**Properties:**

- In a **flat area** (constant intensity), the Laplacian is **0** — the second derivative of a constant is zero.
- At an **edge**, the Laplacian produces a **double-line**: one positive response (on one side of the edge) and one negative response (on the other side), with a **zero crossing** exactly at the edge location.
- The zero crossing is the precise edge location — this is the Laplacian's advantage over Sobel.

**Noise sensitivity:** The second derivative amplifies noise much more than the first derivative (differentiating twice doubles the high-frequency boost). The Laplacian almost always requires **pre-blurring** the image with a Gaussian to be usable. This observation leads directly to the **LoG (Laplacian of Gaussian)** operator, covered in [[Canny and LoG Edge Detection]].

### Unsharp masking and high-boost filtering

The Laplacian's response to fine detail makes it useful for **sharpening**. The technique is called **unsharp masking** (a name from analog photography):

1. Compute the Laplacian $L = \nabla^2 f$ (extracts the fine detail).
2. Subtract a fraction of the Laplacian from the original:

$$ f_{\text{sharpened}} = f - k \cdot L $$

where $k$ controls the sharpening strength (typically $k = 1$). If the Laplacian kernel's center coefficient is negative (as above), you **subtract**; if positive, you **add**.

**Intuition:** the Laplacian extracts the high-frequency detail (edges, texture). Adding it back to the original amplifies those details, making the image appear sharper. This is the same idea as the "clarity" slider in photo editors.

**High-boost filtering** generalizes this:

$$ f_{\text{high-boost}} = A \cdot f - L = (A - 1) \cdot f + (f - L) $$

where $A \geq 1$. When $A = 1$, this reduces to standard unsharp masking. When $A > 1$, the original is amplified and the sharpening is added on top.

> [!TIP] The deep learning connection
> Unsharp masking computes `output = input + correction`, where the correction is a fixed high-pass filter. **ResNet** computes `output = input + F(input)`, where F is a *learned* function. ResNet is a learned generalization of unsharp masking. See [[From Basic Convolution to Learned Weights]] and [[06 - Computer Vision/Architecture and Connectivity/The Degradation Problem and Residual Connections|The Degradation Problem and Residual Connections]].

## First derivative vs second derivative

| Feature | First Derivative (Sobel) | Second Derivative (Laplacian) |
| :--- | :--- | :--- |
| **Response** | Strong response to thick edges (ramps, steps) | Responds to fine lines, points, and noise |
| **Output** | Produces a **thick**, blurry edge band | Produces a **thin**, double-line with zero crossings |
| **Noise Sensitivity** | Moderate | Very High (requires pre-blurring) |
| **Edge Localization** | Imprecise (edge is several pixels wide) | Precise (zero crossing pinpoints the edge) |
| **Main Use** | Object detection, boundaries, gradient features | High-detail sharpening, precise edge localization |
| **Direction info** | Yes (magnitude + direction) | No (isotropic — no direction) |

**When to use which:**

- Use **Sobel** when you need the edge magnitude and direction (e.g., for Canny's non-maximum suppression, or for feature descriptors like HOG in [[Feature Descriptors - SIFT, SURF, ORB, HOG]]).
- Use the **Laplacian** (or LoG) when you need precise, thin edge locations (e.g., for measuring edge thickness, or for medical image boundary extraction).
- Use **unsharp masking** when you want to sharpen an image for display.

## The edge detection pipeline

A complete edge detection system does not just apply Sobel or Laplacian — it follows a pipeline:

1. **Pre-smooth** with a Gaussian to reduce noise (noise creates spurious edges).
2. **Compute the gradient** (Sobel or similar).
3. **Threshold** the gradient magnitude to keep only strong edges.
4. **Thin** the edges to 1-pixel width (non-maximum suppression — see Canny).
5. **Link** edge pixels into continuous contours (hysteresis thresholding — see Canny).

Steps 4 and 5 are what make the **Canny edge detector** the gold standard — it takes the raw Sobel gradient and refines it into clean, thin, connected edges. The full detector is covered in [[Canny and LoG Edge Detection]].

> [!summary] What to remember
> Edges are locations of rapid intensity change — detected by computing derivatives. **Sobel** (first derivative) gives edge magnitude + direction but produces thick, noisy edges; it simultaneously differentiates in one direction and smooths in the perpendicular. **Laplacian** (second derivative) gives thin, precise edge locations (via zero crossings) but is extremely noise-sensitive and requires pre-blurring. **Unsharp masking** sharpens by subtracting the Laplacian from the original — `output = input - Laplacian` — and is the classical precursor to ResNet's residual connections. A complete edge detector follows a pipeline: smooth → differentiate → threshold → thin → link; Canny implements this pipeline optimally.

## See also

- [[Canny and LoG Edge Detection]] — the production-grade pipeline built on these raw operators.
- [[The Mechanics of Spatial Filtering]] — correlation, convolution, and kernel mechanics.
- [[Linear Smoothing Filters]] — the Gaussian pre-blur that tames the Laplacian.
- [[Feature Descriptors - SIFT, SURF, ORB, HOG]] — HOG and SIFT consume the gradient magnitude and direction Sobel provides.
- [[The Hough Transform]] — linking edge pixels into parametric shapes.
- [[From Basic Convolution to Learned Weights]] — how CNNs learn these edge detectors automatically.
- [[06 - Computer Vision/Architecture and Connectivity/The Degradation Problem and Residual Connections|The Degradation Problem and Residual Connections]] — the learned generalization of unsharp masking.
- [[Image Processing Global Index]] — the area's reading map.
