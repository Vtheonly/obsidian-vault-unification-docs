---
title: The Color Image Processing Pipeline
type: concept
aliases:
  - Color Image Processing Pipeline
  - From Sensor to RGB
  - Sensor to RGB Pipeline
  - Camera Color Pipeline
tags:
  - image-processing
  - color
  - bayer-pattern
  - color-filter-array
  - demosaicing
  - white-balance
  - color-correction
  - gamma-encoding
  - srgb
  - jpeg-compression
  - raw-image
sources:
  - "1.7 The Color Image Processing Pipeline"
created_index: 37
---

When you take a photo with a digital camera or phone, the image sensor does **not** produce RGB pixels directly — it produces a **mosaic** of single-channel measurements that must be converted into a full-color image through a multi-step pipeline. The stages of that pipeline — **demosaicing, white balance, color correction, and gamma encoding**, followed by compression for storage — explain why raw camera images look different from JPEGs, why white balance matters, and why deep learning models that train on JPEGs are training on heavily-processed data. This note walks through each stage in order, from the color-blind sensor to the final `.jpg` file. It builds directly on [[What is a Digital Image]] and [[Color Spaces and Models]], and it is the processing story behind the storage choices catalogued in [[Image File Formats]].

## The sensor and the Bayer pattern

A camera sensor is a grid of **photodiodes** that measure light intensity. Each photodiode produces a single number — the total light that hit it — and nothing more. The sensor is therefore **color-blind**: it measures intensity, not color.

To capture color, a **Color Filter Array (CFA)** is placed over the sensor so that each photodiode sees only one color (red, green, or blue). The standard CFA is the **Bayer pattern** (Bryce Bayer, 1976), which arranges the filters in a 2×2 repeating pattern:

```text
R  G
G  B
```

Notice that there are **two green filters** for every one red and one blue. This is deliberate: the human eye is most sensitive to green light — the luminance formula weights green at 0.587, as shown in [[Color Spaces and Models]] — so the sensor captures more green detail to match human perception.

The raw sensor output is therefore a **single-channel** image in which each pixel is either R, G, or B — but never all three. This is called a **Bayer-pattern image** or **RAW image**, and it is the starting point for everything that follows.

## Demosaicing: interpolating the missing colors

Each pixel carries only one color measurement, but a full-color image needs all three (R, G, B) at every pixel. **Demosaicing** interpolates the missing values. For a green pixel at position $(x, y)$, we have the green value directly, and we need R and B — these are interpolated from the neighboring R and B pixels, using bilinear interpolation or more sophisticated edge-aware methods. For a red pixel the situation is mirrored: we have the red value directly, and we need G and B, interpolated from neighbors.

The simplest demosaicing algorithm is **bilinear interpolation** — averaging the nearest same-color neighbors. More sophisticated methods, such as edge-directed and frequency-domain approaches, produce sharper results with fewer artifacts (zipper patterns and false colors among them).

> [!info] Why demosaicing matters for deep learning
> The demosaicing algorithm introduces **correlations** between neighboring pixels, because they share interpolated values. A CNN trained on demosaiced JPEGs sees these correlations, not the raw sensor data. This is one reason why training on RAW data (where available) can produce different results.

## White balance

Different light sources have different "colors" — incandescent bulbs are yellowish, fluorescent lights are greenish, and shade is bluish. The human visual system **automatically adapts** (a property called color constancy) so that a white object looks white under any illumination. A camera must achieve the same effect computationally, and that computation is **white balance**.

The problem is that the sensor measures the light as it actually is. Under incandescent light, a white card produces R=250, G=220, B=150 — a yellowish reading — and without correction the photograph looks yellow. The fix is to scale each channel so that a "neutral" (gray) object has equal R, G, and B values. The common methods are:

- **Gray world assumption:** assume the average of the scene is gray, and scale the channels so their means are equal. Simple, but often wrong.
- **White patch / max RGB:** assume the brightest pixels are white, and scale the channels so the max values are equal. Also simple, and also often wrong.
- **Manual / preset:** the photographer specifies the light source (daylight, cloudy, incandescent, fluorescent) and the camera applies a known correction.
- **Learning-based:** modern cameras and phones use neural networks or statistical methods to estimate the illuminant. This is how phone cameras produce good white balance automatically.

White balance is a **per-image, per-channel scaling** — it multiplies each channel by a gain factor. The order of operations matters: white balance is applied **before** color correction and gamma, so that the later stages work on illuminant-neutralized values.

## Color correction: from camera RGB to sRGB

The camera's RGB, even after demosaicing and white balance, is **device-dependent** — different cameras produce different RGB values for the same scene. **Color correction** transforms the camera's RGB into a standard color space (typically sRGB) so that the image looks consistent across devices.

The transformation is done via a **3×3 color matrix** calibrated for the specific camera:

$$\begin{pmatrix} R_{sRGB} \\ G_{sRGB} \\ B_{sRGB} \end{pmatrix} = M_{\text{camera} \to \text{sRGB}} \begin{pmatrix} R_{\text{cam}} \\ G_{\text{cam}} \\ B_{\text{cam}} \end{pmatrix}$$

The matrix is determined by photographing a color chart with known reference colors — for example the X-Rite ColorChecker — and solving for the matrix that maps the camera's measured values to the reference values.

## Gamma encoding

The sensor measures light **linearly**: doubling the light doubles the pixel value. Human perception is **non-linear** — we perceive brightness roughly logarithmically, so a doubling of light feels like a smaller, constant-step increase. To use the limited 8 bits per channel efficiently, the pipeline applies **gamma encoding**:

$$V_{\text{encoded}} = V_{\text{linear}}^{1/\gamma}$$

with $\gamma \approx 2.2$. This compresses the bright range (where the eye is less sensitive) and expands the dark range (where the eye is more sensitive), giving more perceptual precision per bit.

**sRGB** uses a slightly modified gamma curve — a linear portion near black, followed by a 2.2 power law — but the principle is the same: the stored pixel values are **non-linear** (gamma-encoded), not linear light measurements.

> [!warning] Pixel values are not linear light
> The "0.5" in a pixel value is **not** half the light — it is about 21.4% of the light, because $0.5^{2.2} \approx 0.218$. This surprises people who assume pixel values are linear, and it has practical consequences:
>
> - Image augmentation that adds or subtracts pixel values assumes linearity, but gamma-encoded values are non-linear. Some augmentations should be done in linear space (convert to linear, augment, convert back).
> - Mixing images from different sources (RAW vs JPEG vs HDR) requires understanding their gamma state.

## Compression: the JPEG step

The final step for JPEG storage is compression: convert the image to YCbCr, subsample the chrominance (4:2:0 — keep full luminance, downsample chroma by 2 in each direction), apply the DCT (Discrete Cosine Transform) in 8×8 blocks, quantize the DCT coefficients (discarding high frequencies), and entropy-code the result.

This is why JPEG images have **block artifacts** at high compression — the 8×8 DCT blocks become visible. The YCbCr conversion and chroma subsampling are covered in [[Color Spaces and Models]], the file-format trade-offs in [[Image File Formats]], and the DCT itself in [[The Fourier Transform]] (it is a Fourier-related transform).

## The full pipeline at a glance

```text
Light → Lens → Sensor (photodiodes + Bayer CFA) → RAW (single-channel mosaic)
  → Demosaicing → RGB (linear, device-dependent)
  → White balance → RGB (linear, illuminant-corrected)
  → Color correction → sRGB (linear, device-independent)
  → Gamma encoding → sRGB (non-linear, the "normal" image)
  → JPEG compression → .jpg file
```

Each step involves choices — the demosaicing algorithm, the white balance method, the color matrix, the gamma curve, and the compression quality — and every one of them affects the final image. The labels in the diagram also track two independent properties: the data is device-dependent until color correction, and it stays linear until gamma encoding. This is why two cameras photographing the same scene produce different JPEGs: they make different choices at each step of the pipeline.

## Implications for deep learning

1. **JPEGs are heavily processed.** A CNN trained on JPEGs is training on the output of a 5-step pipeline, not on "raw" visual data. The demosaicing, white balance, color correction, gamma, and compression all introduce structure that the CNN may learn to rely on.
2. **Augmentation in linear vs gamma space.** Some augmentations (brightness changes, blending) are physically meaningful in linear space, not gamma space. Converting to linear, augmenting, and converting back is more correct but slower.
3. **Domain shift across cameras.** A model trained on images from one camera may not generalize to another, because the color matrices and demosaicing differ. This is a real problem for medical imaging and surveillance.
4. **RAW data exists.** Some deep learning work — notably in computational photography, covered in [[Deep Learning for Imaging]] — trains on RAW sensor data to avoid the pipeline's assumptions. This requires access to RAW files (DNG, CR2, NEF) and custom demosaicing and color pipelines.

## Key takeaways

The pipeline is short enough to hold in your head as a sequence of five transformations, each with a clear purpose. Walking through it once more from the top:

1. A camera sensor produces a **Bayer-pattern mosaic** (one color per pixel), not RGB.
2. **Demosaicing** interpolates the missing colors, introducing inter-pixel correlations.
3. **White balance** scales the channels to neutralize the illuminant color (gray world, white patch, or learning-based).
4. **Color correction** maps device-dependent camera RGB to standard sRGB via a calibrated 3×3 matrix.
5. **Gamma encoding** ($V^{1/2.2}$) converts linear light to perceptual space, compressing the bright range and expanding the dark range. Stored pixel values are non-linear.
6. **JPEG compression** (YCbCr + chroma subsampling + DCT + quantization) introduces block artifacts.
7. A CNN trained on JPEGs is training on the output of this 5-step pipeline, not raw visual data — this affects augmentation, domain shift, and what the model actually "sees."

## See also

- [[Image Processing Global Index]]
- [[What is a Digital Image]]
- [[Color Spaces and Models]]
- [[Image File Formats]]
- [[Resolution and Bit Depth]]
- [[Point Processing Operations]]
- [[The Fourier Transform]]
- [[Deep Learning for Imaging]]
