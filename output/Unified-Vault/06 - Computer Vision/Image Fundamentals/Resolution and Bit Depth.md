---
title: Resolution and Bit Depth
type: concept
aliases:
  - Spatial Resolution
  - Intensity Resolution
  - Color Depth
  - Bit Depth
  - Image Resolution
  - PPI and DPI
tags:
  - image-processing
  - computer-vision
  - digital-images
  - spatial-resolution
  - bit-depth
  - color-depth
  - ppi
  - dpi
  - dynamic-range
  - file-size
sources:
  - "1.3 Resolution and Bit Depth"
created_index: 36
---

Digital image quality is described along two independent dimensions: "How many pixels?" (spatial resolution) and "How much information per pixel?" (intensity resolution). The first determines how finely a scene is sampled, the second how many distinct colors or gray levels each sample can record. This note covers both dimensions — pixel counts, the PPI/DPI link to physical size, bit depth and its level counts, and the raw storage arithmetic that follows from them. It builds on [[What is a Digital Image]] and motivates the compression covered in [[Image File Formats]].

## Spatial resolution

Spatial resolution is the measure of the smallest discernible detail in an image. It can be expressed in two related but different ways: as a pure digital pixel count, or as a physical density that links the pixel grid to the physical world. Confusing the two is one of the most common practical misunderstandings in imaging.

### Pixel count

The most basic definition of spatial resolution is the width and height of the grid. A Full HD image, for example, measures $1920 \times 1080$, so its total is $1920 \times 1080 = 2,073,600$ pixels ($\approx 2$ Megapixels). More pixels mean more samples of the scene, and therefore a smaller smallest discernible detail — the grid itself is the product of the sampling step described in [[What is a Digital Image]].

### Physical density (PPI and DPI)

Physical density is often confused with pixel count; it is the metric that links the digital pixels to the physical world. The distinction is between two device-specific terms: **PPI (Pixels Per Inch)** is used for screens, while **DPI (Dots Per Inch)** is used for printers. The same pixel grid produces very different physical sizes depending on this density:

$$ \text{Physical Size (Inches)} = \frac{\text{Pixel Dimension}}{\text{Resolution (PPI)}} $$

As a worked example, take an image that is $1000$ pixels wide. Printed at $100$ DPI, it will be $10$ inches wide (low quality print). Printed at $300$ DPI, it will be $3.33$ inches wide (high quality photo print) — the same thousand pixels, packed three times more densely by the printer.

> [!warning] DPI metadata is not pixel data
> Changing the DPI metadata in a file does **not** change the image data (the pixels); it only tells the printer how big to print it.

## Intensity resolution (color depth and bit depth)

Intensity resolution is the second dimension of quality: how much information each pixel carries. Bit depth is the number of bits used to represent the color of a **single pixel**, and it determines both the **dynamic range** and the **color palette** of the image. Where spatial resolution grows with the size of the grid, intensity resolution grows with the information encoded at each grid position.

### Calculating the number of levels

If a pixel depth is $k$ bits, the number of unique colors/gray levels $L$ is:

$$ L = 2^k $$

Each additional bit doubles the number of representable values. This exponential growth explains why the standard depths are powers of two, and why even a modest depth already spans far more values than the eye can separate.

### Common bit depths

Four depths cover the practical regimes, from binary line art to transparent color:

| Depth | Levels | Notes |
| :--- | :--- | :--- |
| 1-bit (binary / monochrome) | $2^1 = 2$ levels (0 and 1) | Strictly black and white — no gray; used for text and line art |
| 8-bit (grayscale) | $2^8 = 256$ levels (0 to 255) | Standard for black and white photography |
| 24-bit (true color / RGB) | $2^8 \times 2^8 \times 2^8 = 16,777,216$ colors | Standard for JPEGs and monitors |
| 32-bit (RGBA) | 24-bit color + 8-bit alpha channel (transparency) | Used in PNGs and game assets |

Three details in this table deserve comment. True color uses 8 bits for Red, 8 bits for Green, and 8 bits for Blue, and its $16,777,216$ colors make it the standard for JPEGs and monitors; 32-bit RGBA extends it with an 8-bit **alpha channel** for transparency, which is why PNGs and game assets use it. On the grayscale side, the human eye can distinguish roughly 30-100 shades of gray depending on conditions, so 256 levels are usually sufficient to simulate continuity — which is why black and white photography standardized on 8-bit rather than something deeper.

## Storage calculation

It is essential to be able to calculate the raw file size of an uncompressed image. Once the pixel dimensions and the bit depth are known, the raw size follows directly:

$$ \text{Size (bits)} = \text{Width} \times \text{Height} \times \text{Bit Depth} $$

To get Bytes, divide by 8. As a worked exercise, calculate the size of a standard Full HD ($1920 \times 1080$) image in True Color ($24$-bit):

1. Total Pixels = $2,073,600$.
2. Total Bits = $2,073,600 \times 24 = 49,766,400$ bits.
3. Total Bytes = $49,766,400 / 8 = 6,220,800$ bytes.
4. Convert to MB = $6.22$ MB.

Storing 6 MB per photo is inefficient, and this calculation is exactly why compression (JPEG) is necessary — the lossless and lossy schemes that make digital photography practical are covered in [[Image File Formats]]. The formula also exposes the only two levers available for shrinking a raw image: fewer pixels or fewer bits per pixel, each trading away detail or color fidelity.

## See also

- [[Image Processing Global Index]]
- [[What is a Digital Image]]
- [[Image Representation Types]]
- [[Color Spaces and Models]]
- [[The Color Image Processing Pipeline]]
- [[Image File Formats]]
- [[Pixel Relationships and Distance Metrics]]
- [[Image Fundamentals and Histograms Quiz]]
