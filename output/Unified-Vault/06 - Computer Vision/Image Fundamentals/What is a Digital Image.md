---
title: What is a Digital Image
type: concept
aliases:
  - Digital Image
  - Digital Image Definition
  - Definition of a Digital Image
  - Sampling and Quantization
tags:
  - digital-image
  - sampling
  - quantization
  - pixel
  - pixel-grid
  - coordinate-system
  - nyquist
  - aliasing
  - bit-depth
  - image-types
  - array-representation
sources:
  - "1.1 What is a Digital Image"
created_index: 38
---

A digital image is a two-dimensional discrete function — a grid of numbers obtained by sampling space and quantizing intensity. This note defines the digital image mathematically and conceptually, and explains the two fundamental operations, **sampling** and **quantization**, that convert continuous reality into the discrete form a computer can process. Understanding these foundations is essential because every subsequent operation in image processing — from blurring to edge detection to compression — operates on this discrete representation. The note closes with the coordinate conventions, image dimensionalities, and in-memory layouts that follow from the definition; [[Resolution and Bit Depth]] and [[Image Representation Types]] expand the practical side.

## The definition: a two-dimensional discrete function

A digital image is a **two-dimensional discrete function**:

$$f(x, y) \quad \text{where} \quad x \in \{0, 1, \ldots, M-1\}, \quad y \in \{0, 1, \ldots, N-1\}$$

Here $x, y$ are **spatial coordinates** (column, row) — integers, because the image is sampled on a grid. The value $f(x, y)$ is the **intensity** (or color) at that coordinate — a discrete value, because the intensity is quantized. The product $M \times N$ is the image **resolution** (width × height in pixels).

For a grayscale image, $f(x, y)$ is a single number — the brightness, typically 0–255 for 8-bit images. For a color image, $f(x, y)$ is a vector: usually 3 values for RGB, but possibly more (RGBA, multispectral, hyperspectral).

The key insight is that a digital image is a **discrete approximation** of continuous reality. The real world is continuous — light varies smoothly in both space and intensity — whereas the digital image samples it on a grid and quantizes the intensity to fixed levels. Everything in image processing operates on this discrete approximation, which is why the two discretization steps deserve a close look.

## Digitization: sampling and quantization

Digitization happens in two independent steps. Sampling discretizes space — it decides *where* the image can be measured — and quantization discretizes intensity — it decides *which* values the measurement can take. Doing either one too coarsely produces a characteristic artifact: aliasing from under-sampling, banding from under-quantization.

### Sampling: spatial discretization

The continuous image — the light falling on the sensor — is **sampled** at discrete spatial positions, producing the pixel grid. Each sample is the average (or integral) of the continuous image over a small region, namely the pixel's area.

The **sampling rate** is the number of pixels per unit area (PPI — pixels per inch, for displays; DPI — dots per inch, for printing). Higher sampling means more pixels and finer spatial detail; lower sampling means fewer pixels, coarser detail, and **aliasing**, in which high-frequency patterns fold back as spurious low frequencies — a failure mode revisited in [[Geometric Transformations and Interpolation]].

The **Nyquist-Shannon sampling theorem** states that to capture a signal with maximum frequency $f_{max}$, you must sample at least $2 f_{max}$ times. Below this rate, aliasing occurs: fine patterns (stripes, textures) appear as coarser, wrong patterns. This is why phone cameras have optical low-pass filters — to blur frequencies above the Nyquist rate before sampling.

### Quantization: intensity discretization

The continuous intensity at each sample is **quantized** to a fixed number of levels — typically 256 levels (8 bits) for grayscale, and 256 per channel for 8-bit RGB.

The **bit depth** is the number of bits per pixel, and it determines the number of intensity levels: 8 bits gives 256 levels, 16 bits gives 65,536 levels, and 1 bit gives 2 levels (binary). Higher bit depth means finer intensity gradation and smoother gradients; lower bit depth means fewer levels, which shows up as **banding** (visible steps in smooth gradients) and **posterization**.

**Quantization error** is the difference between the true continuous intensity and the quantized value. This error is bounded by $\pm 0.5$ LSB (least significant bit) and is usually modeled as uniform noise. For 8-bit images, the error is at most $\pm 0.5/255 \approx 0.2\%$ — small but not zero, and still visible in dark regions or smooth gradients.

## The coordinate system: where is the origin?

In **mathematics**, the origin $(0, 0)$ is at the bottom-left, with $y$ increasing upward. In **image processing**, the origin is at the **top-left**, with $y$ increasing downward:

```text
(0,0) ──────── x (columns) ───────
  │
  │
y (rows)
  │
  ▼
```

This convention comes from how images are stored in memory — row-major order, writing the first row, then the second row, and so on — and how displays scan, from top to bottom. It is the opposite of mathematical convention and is a perennial source of confusion: when rotating images, for example, the rotation direction appears reversed.

The practical implication is in indexing. When you index an image as `image[y, x]` (in NumPy/OpenCV), the first index is the **row** (y) and the second is the **column** (x) — the opposite of the mathematical $(x, y)$ convention.

## Image types by dimensionality

The discrete-function definition extends beyond 2D grayscale and color, and the table below catalogs the main image types by their dimensions and typical uses.

| Type | Dimensions | Example |
| :--- | :--- | :--- |
| Binary | $M \times N \times 1$ (1 bit) | Scanned documents, masks |
| Grayscale | $M \times N \times 1$ (8 or 16 bit) | X-rays, medical images |
| Color (RGB) | $M \times N \times 3$ | Photographs |
| Color (RGBA) | $M \times N \times 4$ | Photos with transparency |
| Multispectral | $M \times N \times k$ (k = 4–10) | Satellite imagery (red, green, blue, near-IR, ...) |
| Hyperspectral | $M \times N \times k$ (k = 100s) | Remote sensing, material identification |
| Volumetric (3D) | $M \times N \times P$ | CT/MRI scans, 3D microscopy |
| Video | $M \times N \times T$ | Time series of images |

Most image processing deals with 2D grayscale or RGB images, but the concepts extend to all of these types. The pattern across the table is that every type is the same $M \times N$ spatial grid, extended with more channels ($k$), more slices ($P$), or time ($T$).

## How images are stored in memory

A grayscale image is a 2D array: `image[row, col]` holds the intensity at that pixel. A color image is a 3D array — `image[row, col, channel]` or `image[channel, row, col]`, depending on the framework:

- **NumPy / OpenCV:** `(H, W, C)` — height, width, channels. BGR order (not RGB), for historical OpenCV reasons.
- **PyTorch:** `(C, H, W)` — channels first. RGB order.
- **TensorFlow:** `(H, W, C)` — channels last. RGB order.

The channel ordering (RGB vs BGR) and the dimension ordering (CHW vs HWC) are common sources of bugs when switching between frameworks, so always check the convention.

## Key takeaways

The definition, the two discretization steps, and the storage conventions compress into six points:

1. A digital image is a **2D discrete function** $f(x, y)$ on an integer grid, with quantized intensity.
2. **Sampling** discretizes space (the pixel grid); **quantization** discretizes intensity (the bit depth).
3. Insufficient sampling causes **aliasing**; insufficient quantization causes **banding/posterization**.
4. The **Nyquist theorem** requires sampling at $2 \times$ the maximum frequency to avoid aliasing.
5. The image processing coordinate system has its origin at the **top-left**, with $y$ increasing downward — the opposite of math convention.
6. Images are stored as arrays; the dimension order (HWC vs CHW) and channel order (RGB vs BGR) vary by framework.

## See also

- [[Image Processing Global Index]]
- [[Image Representation Types]]
- [[Resolution and Bit Depth]]
- [[Color Spaces and Models]]
- [[The Color Image Processing Pipeline]]
- [[Pixel Relationships and Distance Metrics]]
- [[Geometric Transformations and Interpolation]]
