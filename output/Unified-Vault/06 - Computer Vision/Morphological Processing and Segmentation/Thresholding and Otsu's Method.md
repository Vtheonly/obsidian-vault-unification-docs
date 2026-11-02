---
title: Thresholding and Otsu's Method
type: concept
aliases:
  - Otsu's Method
  - Otsu Thresholding
  - Automatic Threshold Selection
  - Adaptive Thresholding
  - Image Binarization
tags:
  - image-processing
  - computer-vision
  - segmentation
  - thresholding
  - otsu-method
  - adaptive-thresholding
  - histogram
  - morphological-processing
sources:
  - "5.7 Thresholding and Otsu's Method"
created_index: 52
---

**Thresholding** is the simplest segmentation method: classify each pixel as foreground or background based on its intensity. Despite its simplicity, thresholding is extremely useful — it is the first step in many document-analysis, medical-imaging, and industrial-inspection pipelines. The key question is **how do you choose the threshold?** Otsu's method answers this automatically, and this note develops it along with the adaptive variant for uneven lighting. The method is best read with the histogram background from [[The Image Histogram]] and [[Histogram Equalization]].

## The basic idea

Given a grayscale image, choose a threshold $T$. Pixels with intensity $> T$ are "foreground"; pixels with intensity $\leq T$ are "background" (or vice versa). The result is a **binary image** — the simplest possible segmentation.

```python
import cv2
_, binary = cv2.threshold(image, thresh=127, maxval=255, type=cv2.THRESH_BINARY)
```

This works when the image has a clear bimodal histogram (two peaks: one for foreground, one for background) and you can pick $T$ between the peaks. But how do you find the right $T$ automatically?

## Otsu's method — automatic threshold selection

**Otsu's method** (Nobuyuki Otsu, 1979) finds the threshold that **maximizes the between-class variance** — the threshold that best separates the two classes (foreground and background).

### The intuition

A good threshold should produce two classes (foreground and background) that are:

- **Internally homogeneous** (low variance within each class).
- **Mutually distinct** (the means of the two classes are far apart).

Otsu maximizes the **between-class variance**:

$$\sigma_B^2(T) = w_0(T) \cdot w_1(T) \cdot [\mu_0(T) - \mu_1(T)]^2$$

where $w_0, w_1$ are the fractions of pixels in class 0 and class 1 (weights), and $\mu_0, \mu_1$ are the mean intensities of each class. The threshold $T^*$ that maximizes $\sigma_B^2(T)$ is Otsu's threshold.

### The algorithm

1. Compute the image histogram (256 bins for 8-bit images).
2. For each possible threshold $T$ from 0 to 255:
   - Compute $w_0, w_1$ (fractions of pixels below and above $T$).
   - Compute $\mu_0, \mu_1$ (mean intensities of each class).
   - Compute $\sigma_B^2(T) = w_0 \cdot w_1 \cdot (\mu_0 - \mu_1)^2$.
3. Return the $T$ that maximizes $\sigma_B^2$.

This is $O(256)$ operations — extremely fast. OpenCV implements it as a flag:

```python
_, binary = cv2.threshold(image, thresh=0, maxval=255, type=cv2.THRESH_BINARY + cv2.THRESH_OTSU)
# thresh=0 is ignored when OTSU is used; Otsu computes the threshold automatically.
```

### Why maximizing between-class variance works

There is a mathematical identity: the **total variance** of the image is constant (it depends only on the pixel values, not on $T$). The total variance decomposes as:

$$\sigma_{total}^2 = \sigma_B^2(T) + \sigma_W^2(T)$$

where $\sigma_W^2$ is the **within-class variance** (the weighted sum of variances within each class). Since $\sigma_{total}^2$ is constant, **maximizing $\sigma_B^2$ is equivalent to minimizing $\sigma_W^2$** — which is exactly what we want (minimize internal variance = make classes homogeneous).

So Otsu's method is the optimal threshold for the criterion of "minimize within-class variance," and it is computed in $O(256)$ time. Elegant and efficient.

## When Otsu fails

Otsu assumes a **bimodal** histogram (two clear peaks). It fails when:

1. **Unimodal histogram:** the image has no clear foreground/background separation (e.g., a smooth gradient). Otsu will pick a threshold, but it will not be meaningful.
2. **Illumination gradient:** if one side of the image is brighter than the other (uneven lighting), a single global threshold cannot work — the "foreground" on the dark side may be darker than the "background" on the bright side. Use **adaptive thresholding** (below).
3. **More than two classes:** if the histogram has 3+ peaks (e.g., dark background, medium gray object, bright highlight), Otsu (which finds one threshold = two classes) cannot handle it. Use **multi-Otsu** (find $k-1$ thresholds for $k$ classes) or a different method.
4. **Noisy images:** noise broadens the histogram peaks, making the "valley" between them shallow. Pre-smooth or use adaptive methods.

## Adaptive thresholding

For images with uneven illumination, a single global threshold does not work. **Adaptive thresholding** computes a different threshold for each pixel, based on the local neighborhood:

$$\text{binary}(x, y) = \begin{cases} 1 & \text{if } I(x, y) > T(x, y) \\ 0 & \text{otherwise} \end{cases}$$

where $T(x, y)$ is computed from the local neighborhood (e.g., the mean or a Gaussian-weighted mean of the $k \times k$ neighborhood around $(x, y)$, minus a constant $C$).

```python
binary = cv2.adaptiveThreshold(
    image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY, blockSize=11, C=2
)
```

Adaptive thresholding is the standard method for **document binarization** (converting scanned documents to black-and-white for OCR), where uneven lighting is common.

## Practical pipeline: thresholding + morphology

Thresholding rarely produces perfect segmentation on its own — the binary image usually has noise (small holes, small spurious objects, rough boundaries). The standard pipeline:

1. **Threshold** (Otsu or adaptive) → binary image.
2. **Morphological opening** (erosion + dilation) → removes small noise.
3. **Morphological closing** (dilation + erosion) → fills small holes.
4. **Connected component labeling** (see [[Connected Components and Region Properties]]) → identify individual objects.
5. **Filter by size/shape** → remove components that are too small or the wrong shape.

This pipeline is the workhorse of classical segmentation — document analysis, cell counting, defect detection, and many other industrial tasks use exactly this sequence.

## Key takeaways

Thresholding classifies pixels as foreground/background by intensity — the simplest segmentation. **Otsu's method** finds the threshold that maximizes between-class variance (= minimizes within-class variance), computed in $O(256)$ time; it is the standard automatic threshold. Otsu assumes a **bimodal histogram** — it fails on unimodal, multi-modal, or unevenly-illuminated images. **Adaptive thresholding** computes a local threshold per pixel — the standard for document binarization with uneven lighting. The practical pipeline is threshold → morphological opening/closing → connected components → filter, and it is the workhorse of classical segmentation.

## See also

- [[Image Processing Global Index]]
- [[The Image Histogram]] — the bimodality Otsu assumes
- [[Histogram Equalization]]
- [[Mathematical Morphology Basics]]
- [[Erosion and Dilation]] — the primitives behind opening and closing
- [[Opening and Closing]] — the cleanup stages of the pipeline
- [[Morphological Algorithms]]
- [[Watershed Segmentation]] — separating touching objects after binarization
- [[Connected Components and Region Properties]] — labeling and filtering the thresholded objects
