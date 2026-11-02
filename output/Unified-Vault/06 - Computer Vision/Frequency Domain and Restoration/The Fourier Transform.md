---
title: The Fourier Transform
type: concept
aliases:
  - The Fourier Transform (DFT and FFT)
  - The Fourier Transform in Imaging
  - Discrete Fourier Transform
  - DFT
  - Fast Fourier Transform
  - FFT
  - 2D DFT
tags:
  - image-processing
  - computer-vision
  - frequency-domain
  - fourier-transform
  - dft
  - fft
  - magnitude-spectrum
  - phase-spectrum
  - convolution-theorem
sources:
  - "4.2 The Fourier Transform"
  - "05. The Fourier Transform in Imaging"
created_index: 31
---

The Fourier transform is the mathematical operation that converts a signal from the spatial (or time) domain to the frequency domain, exposing which sinusoidal components make up an image and how strongly each is present. This note develops the 1D and 2D Discrete Fourier Transform (DFT), the Fast Fourier Transform (FFT) that makes it computable, and the magnitude and phase spectra it produces — together with the critical insight that **phase matters more than magnitude** for image structure. It closes with the transform's key properties, above all the convolution theorem, which underpin the filter designs of [[Frequency Domain Filtering]] and the restoration models of [[Image Degradation and Noise Models]]. The note builds on [[Introduction to the Frequency Domain]] and anchors the classical image-processing chapter indexed in [[Image Processing Global Index]].

## From the spatial to the frequency domain

A digital image is typically represented in the **spatial domain**, where each point corresponds to a pixel value at a specific `(x, y)` coordinate — a description of *where* things are in the image. The Fourier transform converts this spatial representation into the **frequency domain**, which describes the rate of change of pixel values: it shows the constituent frequencies that make up the image. The two representations carry exactly the same information in different forms.

Image frequencies have a direct visual interpretation. **Low frequencies** correspond to areas of the image where pixel values change slowly and smoothly — the coarse structure and general shapes, such as a clear sky or a wall. **High frequencies** correspond to areas where pixel values change rapidly — fine details, edges, textures, and noise. In a visual representation of the Fourier transform (the magnitude spectrum), low frequencies are typically located at the center and high frequencies at the periphery, a layout produced by the `fftshift` convention described below.

## The 1D discrete Fourier transform

For a discrete signal $f[n]$ of length $N$ (e.g., one row of an image), the DFT is:

$$F[k] = \sum_{n=0}^{N-1} f[n] \cdot e^{-j 2\pi kn / N}, \quad k = 0, 1, \ldots, N-1$$

Each $F[k]$ is a **complex number** representing the amplitude and phase of the sinusoidal component at frequency $k$. The inverse DFT reconstructs the original signal:

$$f[n] = \frac{1}{N} \sum_{k=0}^{N-1} F[k] \cdot e^{j 2\pi kn / N}$$

The DFT decomposes the signal into $N$ frequency components, and the inverse DFT sums them back. No information is lost — the DFT is a **change of representation**, not an approximation.

### Euler's formula and the two parts of $F[k]$

Using Euler's formula $e^{-j\theta} = \cos\theta - j\sin\theta$, each $F[k]$ can be written as:

$$F[k] = \sum_n f[n] \cos(2\pi kn/N) - j \sum_n f[n] \sin(2\pi kn/N)$$

So $F[k]$ has a **real part** (the cosine component) and an **imaginary part** (the sine component). The **magnitude** $|F[k]| = \sqrt{\text{Re}^2 + \text{Im}^2}$ is the amplitude of that frequency; the **phase** $\angle F[k] = \arctan(\text{Im}/\text{Re})$ is the phase offset.

## The 2D DFT for images

For a 2D image $f[x, y]$ of size $M \times N$, the 2D DFT is:

$$F[u, v] = \sum_{x=0}^{M-1} \sum_{y=0}^{N-1} f[x, y] \cdot e^{-j 2\pi (ux/M + vy/N)}$$

Each $F[u, v]$ represents a 2D sinusoidal grating at spatial frequency $(u, v)$ — $u$ is the horizontal frequency, $v$ is the vertical frequency. The magnitude $|F[u, v]|$ is the strength of that grating in the image; the phase $\angle F[u, v]$ is its position. Every image is therefore exactly a superposition of such gratings, each weighted by its magnitude and displaced by its phase.

### The FFT (Fast Fourier Transform)

Computing the DFT directly is $O(N^2)$ for a 1D signal of length $N$ — too slow for images. The **Fast Fourier Transform** (Cooley and Tukey, 1965) computes the same result in $O(N \log N)$ by exploiting the symmetry of the complex exponentials. For a 512×512 image, this is the difference between minutes and milliseconds — **always use the FFT**, not the direct DFT.

```python
import numpy as np
F = np.fft.fft2(image)           # 2D FFT
F_shifted = np.fft.fftshift(F)   # shift zero-frequency to center (for visualization)
magnitude = np.log(np.abs(F_shifted) + 1)  # log-scaled magnitude for display
```

## The magnitude and phase spectra

The DFT produces a complex-valued array, and we usually visualize two things: the magnitude spectrum and the phase spectrum. Together they form the complete frequency-domain description of the image. They play very different roles, however, and the imbalance between those roles is the subject of the key insight below.

### The magnitude spectrum

$|F[u, v]|$ is the strength of each frequency. Because magnitudes span a huge range — the DC component $F[0,0]$ is the sum of all pixels, which is enormous — we display the **log magnitude** $\log(|F[u,v]| + 1)$ for visualization.

The magnitude spectrum tells you **how much of each frequency is present**. For a typical natural image, the DC component (center, after `fftshift`) is the brightest, carrying the image's average brightness; low frequencies (near the center) are bright, because smooth structure dominates; and high frequencies (near the edges) are dim, because fine detail and noise are less energetic. The spectrum is roughly radially symmetric for isotropic images, which have no preferred direction.

### The phase spectrum

$\angle F[u, v]$ is the phase of each frequency. This looks like noise when visualized, but it is **critically important** — it encodes the spatial structure, that is, where edges and features are located. A phase image that appears unreadable therefore holds most of what makes the image recognizable.

## The fftshift convention

The DFT output has the zero-frequency (DC) component at position $[0, 0]$ (top-left corner), with frequencies increasing outward and wrapping around, so the high frequencies end up at the corners. For visualization, we **shift** the zero-frequency to the center using `fftshift`, so the spectrum is symmetric around the center — low frequencies in the middle, high frequencies at the edges. This is the convention for all frequency-domain visualization and filtering.

## Phase matters more than magnitude

> [!important] The key insight
> The phase, not the magnitude, determines what the image looks like. For most image processing, we manipulate the magnitude (filtering, compression) and leave the phase alone — the phase is too important to change.

This is the most important and surprising fact about the Fourier transform of images. Take two images A and B, compute their DFTs, and reconstruct two hybrids: image 1 from the magnitude of A combined with the phase of B, and image 2 from the magnitude of B combined with the phase of A. The result: image 1 looks like image B (the phase donor), and image 2 looks like image A.

Why does phase dominate? The magnitude tells you *which frequencies are present*; the phase tells you *how they are aligned*. Edges, lines, and object boundaries are defined by the alignment of frequencies — constructive interference at the edge, destructive elsewhere. If you keep the phases but change the magnitudes, the edges are still there, just at different contrast; if you keep the magnitudes but scramble the phases, all the frequencies are present but misaligned, and the image becomes unrecognizable noise.

## Properties of the Fourier transform

These properties are essential for understanding frequency-domain filtering:

- **Linearity:** $\mathcal{F}\{a \cdot f + b \cdot g\} = a \cdot F + b \cdot G$.
- **Convolution theorem:** $\mathcal{F}\{f * g\} = F \cdot G$. Spatial convolution = frequency multiplication. This is the basis for efficient large-kernel filtering.
- **Correlation theorem:** $\mathcal{F}\{f \star g\} = F^* \cdot G$ (where $*$ is complex conjugate). Used for template matching.
- **Shift invariance:** shifting $f$ in space only changes the phase of $F$, not the magnitude. (This is why the magnitude spectrum is shift-invariant — useful for recognition.)
- **Rotation:** rotating $f$ by $\theta$ rotates $F$ by $\theta$. The spectrum rotates with the image.
- **Scaling:** scaling $f$ by $a$ scales $F$ by $1/a$ (and vice versa). Enlarging the image in space compresses the spectrum in frequency.

The convolution theorem is the workhorse of this list, and the next section shows it in action. The others explain familiar observations: why recognition systems can rely on magnitude spectra alone (shift invariance), and why enlarging an image in space compresses its spectrum in frequency (scaling).

## The convolution theorem at work: filtering in the frequency domain

The most important reason to use the Fourier transform in image processing is a powerful mathematical property: **convolution in the spatial domain is equivalent to element-wise multiplication in the frequency domain**. This means that the computationally expensive process of sliding a kernel over an image can be replaced by a much faster process:

1. Transform both the image and the filter's kernel into the frequency domain using the Fast Fourier Transform (FFT).
2. Perform a simple element-wise multiplication of the two resulting matrices.
3. Transform the result back into the spatial domain using the Inverse FFT (IFFT).

A full filtering pass therefore proceeds as follows. First compute the FFT of the input image, which results in a complex-valued matrix. Then create a frequency-domain filter — a mask of the same size, with values of 1 for frequencies to be kept and 0 for frequencies to be removed: a **low-pass filter** keeps low frequencies (center of the spectrum) and removes high frequencies, producing a blurring/smoothing effect; a **high-pass filter** keeps high frequencies and removes low frequencies — this accentuates edges and details; and a **band-pass/reject filter** selectively keeps or removes a specific range of frequencies. Multiply the FFT of the image by the filter mask element-wise, then compute the IFFT of the resulting matrix to transform back into the spatial domain, yielding the filtered image. The concrete filter designs — ideal, Butterworth, Gaussian, and notch — are developed in [[Frequency Domain Filtering]].

### Implementation notes (Python/OpenCV)

The FFT is typically implemented using the `numpy` library in Python. The full round trip, including the shift conventions, is:

```python
import numpy as np
import cv2

# 1. Compute the FFT of a grayscale image
# The result is a complex array.
f = np.fft.fft2(input_image)

# 2. Shift the zero-frequency component to the center for visualization and filtering
# The raw FFT output has the low frequencies at the corners.
fshift = np.fft.fftshift(f)

# At this point, you would create and apply your filter mask to fshift.

# 3. To transform back, first perform the inverse shift
f_ishift = np.fft.ifftshift(fshift_after_filtering)

# 4. Compute the inverse FFT
img_back = np.fft.ifft2(f_ishift)
img_back = np.abs(img_back) # Take the absolute value to get the real image
```

## See also

- [[Introduction to the Frequency Domain]] — the chapter opener this note builds on.
- [[Frequency Domain Filtering]] — the filter designs built on the convolution theorem.
- [[Image Degradation and Noise Models]] — degradation and Wiener restoration in the frequency domain.
- [[Image Quality Metrics]] — measuring the results of filtering and restoration.
- [[The Convolution Operation]] — the spatial-domain operation the convolution theorem replaces.
- [[Canny and LoG Edge Detection]] — the LoG operator, which also has a frequency-domain view.
- [[Image Processing Global Index]] — the area's reading map.
