---
title: Image Processing Comprehensive Quiz
type: example
aliases:
  - Image Processing Quiz
  - Comprehensive Image Processing Quiz
  - Image Processing Mixed Quiz
tags:
  - computer-vision
  - image-processing
  - quiz
  - practice
  - opencv
  - noise
  - image-quality-metrics
  - spatial-filtering
  - morphology
  - frequency-domain
  - histograms
sources:
  - Q4
  - Q6
created_index: 60
---

This is the comprehensive self-assessment for the classical image-processing curriculum: eighty questions sweeping from digital image representation, color, and file formats through noise models, quality metrics, spatial filtering, mathematical morphology, and the frequency domain. Questions come in three formats — true/false statements, multiple-choice items, and matching pairs — so the same core facts are probed from several angles, and the classic traps (array shape ordering, the direction of PSNR, minimum- versus maximum-variance sub-regions, opening versus closing) are deliberately revisited in more than one round. Commit to an answer before unfolding each callout, and treat every explanation as a compressed review of the underlying concept. For focused drills on a single subfamily, pair this note with [[Image Fundamentals and Histograms Quiz]], [[Spatial Filtering and Convolution Quiz]], and [[Noise Degradation and Frequency Domain Quiz]]; the full set of underlying notes is mapped in [[Image Processing Global Index]].

## True or false

Thirty statements test precise definitions and easy-to-confuse facts; each is either exactly right or subtly wrong, so read every word — the false ones usually differ from the truth by a single swapped term. The statements run from image representation and formats through noise, filtering, and morphology to the frequency domain, mirroring the order of the course notes linked throughout. Where a statement is false, the explanation supplies the corrected fact, and the same distinction usually reappears in the multiple-choice and matching rounds.

### Digital images, color, and formats

How images are stored and seen: array shape ordering, pixel data types, color tuples, grayscale weights, and what compression schemes really discard — the territory of [[What is a Digital Image]], [[Color Spaces and Models]], and [[Image File Formats]].

> [!question] In OpenCV (and NumPy), a color image is represented as a 3D array where the dimensions are ordered as `(width, height, channels)`.
>> [!success]- Answer
>> False
>> **Explanation:** In NumPy/OpenCV, the shape is stored as `(height, width, channels)` (rows, columns, channels).

> [!question] A vector image is resolution-dependent and loses quality when scaled up.
>> [!success]- Answer
>> False
>> **Explanation:** Vector images are defined by mathematical instructions and are resolution-independent. Bitmap (raster) images lose quality when scaled.

> [!question] In a NumPy array representing a grayscale image, the data type `uint8` can store values from 0 to 255.
>> [!success]- Answer
>> True

> [!question] In the RGB color model, the color white is represented by the tuple `(0, 0, 0)` in an 8-bit system.
>> [!success]- Answer
>> False
>> **Explanation:** `(0, 0, 0)` is black. White is `(255, 255, 255)`.

> [!question] When converting a color image to grayscale, the standard formula gives equal weight (0.33) to Red, Green, and Blue channels.
>> [!success]- Answer
>> False
>> **Explanation:** The formula is weighted (e.g., $0.299R + 0.587G + 0.114B$) because the human eye is more sensitive to green light.

> [!question] The JPEG image format uses lossless compression, making it ideal for medical imaging where no data can be discarded.
>> [!success]- Answer
>> False
>> **Explanation:** JPEG uses lossy compression. Formats like PNG or TIFF (or specific DICOM settings) are used for lossless storage.

### Histograms and intensity transformations

Two statements on what histogram equalization actually computes, and on where it may safely be applied to color images — the distinctions drawn in [[Histogram Equalization]].

> [!question] Histogram equalization is valid for color images by applying the algorithm to the Red, Green, and Blue channels independently.
>> [!success]- Answer
>> False
>> **Explanation:** Equalizing RGB channels independently distorts the color balance. You should convert to a luminance-chrominance space (like YCrCb or LAB), equalize the luminance channel, and convert back.

> [!question] Histogram Equalization is a linear operation that scales pixel values by a constant factor.
>> [!success]- Answer
>> False
>> **Explanation:** It is a non-linear operation that redistributes pixel values based on the cumulative distribution function (CDF) to flatten the histogram.

### Noise and quality metrics

The classic noise models of [[Image Degradation and Noise Models]] and the meaning of the PSNR score from [[Image Quality Metrics]].

> [!question] Gaussian noise affects every single pixel in an image by adding a random value drawn from a normal distribution.
>> [!success]- Answer
>> True

> [!question] The "Salt" in Salt-and-Pepper noise refers to pixels being set to the minimum intensity value (0 or black).
>> [!success]- Answer
>> False
>> **Explanation:** "Salt" refers to white pixels (maximum value, 255). "Pepper" refers to black pixels.

> [!question] Salt-and-Pepper noise is best modeled as additive Gaussian noise.
>> [!success]- Answer
>> False
>> **Explanation:** Salt-and-Pepper is impulsive noise (replacing pixels), whereas Gaussian noise is additive (adding values to pixels).

> [!question] A high PSNR (Peak Signal-to-Noise Ratio) value indicates that the filtered image is very different from the original reference image.
>> [!success]- Answer
>> False
>> **Explanation:** A **higher** PSNR indicates better quality and higher fidelity to the original image (less noise/error).

### Spatial filtering

The largest block: linear versus non-linear filters, kernel-size and sigma effects, the Nagao filter's variance logic, Gabor localization, and two algebraic properties of convolution — the material of [[Linear Smoothing Filters]], [[Non-Linear Smoothing Filters]], and [[Gabor Filters]].

> [!question] The Median filter is a linear filter because it calculates the weighted average of the pixels in the neighborhood.
>> [!success]- Answer
>> False
>> **Explanation:** The Median filter is **non-linear**. It sorts the neighborhood values and picks the middle one, rather than calculating a weighted sum (convolution).

> [!question] Increasing the kernel size of a Mean (Averaging) filter results in a sharper image with more visible details.
>> [!success]- Answer
>> False
>> **Explanation:** Increasing the kernel size increases the blurring effect, reducing sharpness and detail.

> [!question] In the Nagao filter algorithm, the pixel is replaced by the mean of the sub-region that has the highest variance.
>> [!success]- Answer
>> False
>> **Explanation:** The Nagao filter selects the sub-region with the **minimum** variance to preserve edges.

> [!question] The Nagao filter is computationally faster than a simple Mean filter of the same size.
>> [!success]- Answer
>> False
>> **Explanation:** The Nagao filter is slower because it calculates variance and mean for multiple sub-regions for every pixel, whereas the Mean filter is a simple calculation.

> [!question] The Gabor filter is unique because it is localized in the spatial domain but not in the frequency domain.
>> [!success]- Answer
>> False
>> **Explanation:** The Gabor filter is optimized for **dual localization** in both the spatial and frequency domains.

> [!question] The Gabor filter is widely used because it provides optimal localization in both the spatial and frequency domains.
>> [!success]- Answer
>> True

> [!question] The convolution operation is commutative, meaning the order of the image and the filter does not matter ($f \otimes h = h \otimes f$).
>> [!success]- Answer
>> True

> [!question] A "Separable" filter allows a 2D convolution to be performed as two 1D convolutions, which significantly improves computational speed.
>> [!success]- Answer
>> True

### Morphology and segmentation

Set-theoretic morphology and marker-based segmentation: what erosion, dilation, opening, and closing actually do, and how watershed markers are seeded — the ground covered in [[Mathematical Morphology Basics]], [[Opening and Closing]], and [[Watershed Segmentation]].

> [!question] Mathematical Morphology operations like Erosion and Dilation are based on convolution with a weighted kernel.
>> [!success]- Answer
>> False
>> **Explanation:** They are based on set theory and shape fitting/hitting using a **Structuring Element**, not convolution with weighted values.

> [!question] Opening is defined as Dilation followed by Erosion.
>> [!success]- Answer
>> False
>> **Explanation:** Opening is **Erosion** followed by **Dilation**. (Dilation followed by Erosion is Closing).

> [!question] A "Closing" morphological operation is effectively used to connect objects that are close together and fill small holes within them.
>> [!success]- Answer
>> True

> [!question] To use the Watershed algorithm for segmentation, it is common to use a distance transform to identify the "sure foreground" markers.
>> [!success]- Answer
>> True

> [!question] In Python/OpenCV, applying `cv2.threshold` with `cv2.THRESH_OTSU` requires you to manually specify the optimal threshold value.
>> [!success]- Answer
>> False
>> **Explanation:** Otsu's method automatically calculates the optimal threshold value based on the image histogram.

### Pixel distances

A single statement ordering the standard distance metrics.

> [!question] The Euclidean distance between two pixels is always greater than or equal to the Chessboard distance.
>> [!success]- Answer
>> True
>> **Explanation:** $d_{inf} \le d_2 \le d_1$. The Chessboard distance is the "shortest" because it allows diagonal shortcuts.

### The frequency domain

Which frequencies live where, and what a low-pass filter does — the core distinctions of [[Introduction to the Frequency Domain]].

> [!question] A low-pass filter in the frequency domain is equivalent to a smoothing/blurring operation in the spatial domain.
>> [!success]- Answer
>> True

> [!question] In the frequency domain, high-frequency components correspond to the smooth background areas of an image.
>> [!success]- Answer
>> False
>> **Explanation:** High frequencies correspond to rapid changes in intensity, such as edges, noise, and fine details. Low frequencies correspond to smooth areas.

### OpenCV essentials

Two API facts about loading and converting images that are worth knowing cold.

> [!question] To convert a BGR image to Grayscale in OpenCV, you use the flag `cv2.COLOR_BGR2GRAY`.
>> [!success]- Answer
>> True

> [!question] In Python/OpenCV, the command `cv2.imread('image.jpg', 0)` loads the image in grayscale mode.
>> [!success]- Answer
>> True

## Multiple choice

Thirty items with four options each; the distractors encode the most common misconceptions, so a wrong choice is itself diagnostic of what to restudy. The themes follow the same order as the true/false round, from representation and the processing chain down to the frequency domain and the OpenCV API. Where several options look plausible, prefer the one that is exactly true rather than merely familiar.

### Digital images and the processing chain

Library roles, vector versus bitmap properties, and the canonical order of the processing chain.

> [!question] Which Python library is primarily used to represent images as multi-dimensional arrays in the provided code examples?
> a) Pandas
> b) NumPy
> c) Matplotlib
> d) SciPy
>> [!success]- Answer
>> b) NumPy

> [!question] Which of the following is NOT a property of Vector images?
> a) Resolution independent.
> b) Small file sizes for simple graphics.
> c) composed of mathematical primitives (lines, curves).
> d) Best suited for photorealistic photographs.
>> [!success]- Answer
>> d) Best suited for photorealistic photographs.

> [!question] In the "Processing Chain" concept described in the objectives, what is the logical order of operations?
> a) Segmentation -> Preprocessing -> Acquisition -> Feature Extraction
> b) Acquisition -> Preprocessing -> Segmentation -> Feature Extraction -> Interpretation
> c) Interpretation -> Segmentation -> Preprocessing -> Acquisition
> d) Preprocessing -> Interpretation -> Segmentation -> Acquisition
>> [!success]- Answer
>> b) Acquisition -> Preprocessing -> Segmentation -> Feature Extraction -> Interpretation

### Color and histograms

Color spaces for human-intuitive editing, channel tools, histogram stretching and normalization, and where a dark image's histogram peaks.

> [!question] Which color space is generally considered more intuitive for human manipulation of color (e.g., changing "redness" without affecting brightness)?
> a) RGB
> b) CMYK
> c) HSL (Hue, Saturation, Lightness)
> d) Grayscale
>> [!success]- Answer
>> c) HSL (Hue, Saturation, Lightness)

> [!question] What does the `cv2.split()` function do?
> a) Divides an image into two halves.
> b) Separates a multi-channel image (e.g., RGB) into individual single-channel arrays.
> c) Splits the image frequency spectrum.
> d) Segments objects from the background.
>> [!success]- Answer
>> b) Separates a multi-channel image (e.g., RGB) into individual single-channel arrays.

> [!question] Which Python library is primarily used for visualization and plotting histograms in the provided labs?
> a) OpenCV
> b) NumPy
> c) Matplotlib
> d) Pandas
>> [!success]- Answer
>> c) Matplotlib

> [!question] In Histogram Stretching (Dynamic Expansion), if the original pixel range is $[50, 200]$ and we want to expand it to $[0, 255]$, what happens to a pixel with value 50?
> a) It becomes 128.
> b) It becomes 255.
> c) It becomes 0.
> d) It remains 50.
>> [!success]- Answer
>> c) It becomes 0.

> [!question] What is the result of `cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX)`?
> a) It clips all values above 255.
> b) It stretches the histogram so the minimum pixel value becomes 0 and the maximum becomes 255.
> c) It converts the image to a normal Gaussian distribution.
> d) It resizes the image to 255x255 pixels.
>> [!success]- Answer
>> b) It stretches the histogram so the minimum pixel value becomes 0 and the maximum becomes 255.

> [!question] If you have a dark image, where would the peaks of its histogram be located?
> a) On the right side (high values).
> b) On the left side (low values).
> c) Spread evenly across the middle.
> d) At 0 and 255 only.
>> [!success]- Answer
>> b) On the left side (low values).

### Noise and quality metrics

Which filter suits which noise, the additive noise equation, and the two standard fidelity metrics.

> [!question] Which filter is most effective at removing Salt-and-Pepper (impulsive) noise?
> a) Gaussian Filter
> b) Mean Filter
> c) Median Filter
> d) Laplacian Filter
>> [!success]- Answer
>> c) Median Filter

> [!question] Which noise model is described by the equation $g(x,y) = f(x,y) + \eta(x,y)$ where $\eta$ is a random variable with mean zero?
> a) Multiplicative Noise
> b) Salt-and-Pepper Noise
> c) Gaussian (Additive) Noise
> d) Quantization Noise
>> [!success]- Answer
>> c) Gaussian (Additive) Noise

> [!question] What is the mathematical formula for Mean Squared Error (MSE) between two images $I$ and $K$ of size $M \times N$?
> a) $\sum \sum (I(i,j) - K(i,j))$
> b) $\frac{1}{MN} \sum_{i=0}^{M-1} \sum_{j=0}^{N-1} [I(i,j) - K(i,j)]^2$
> c) $10 \cdot \log_{10}(\frac{255^2}{MSE})$
> d) $\max(I(i,j) - K(i,j))$
>> [!success]- Answer
>> b) $\frac{1}{MN} \sum_{i=0}^{M-1} \sum_{j=0}^{N-1} [I(i,j) - K(i,j)]^2$

> [!question] Which metric is calculated as $10 \cdot \log_{10}(\frac{R^2}{MSE})$?
> a) Mean Squared Error
> b) Standard Deviation
> c) Peak Signal-to-Noise Ratio (PSNR)
> d) Histogram Equalization
>> [!success]- Answer
>> c) Peak Signal-to-Noise Ratio (PSNR)

### Spatial filtering

Kernel-size and sigma effects, why padding exists, the mean filter's main weakness, and the Nagao filter's selection rule.

> [!question] What is the primary disadvantage of the Mean (Averaging) filter?
> a) It increases noise.
> b) It is computationally expensive.
> c) It blurs edges and fine details.
> d) It only works on color images.
>> [!success]- Answer
>> c) It blurs edges and fine details.

> [!question] What is the primary purpose of the `sigma` ($\sigma$) parameter in a Gaussian filter?
> a) It rotates the kernel.
> b) It controls the spread (width) of the bell curve, determining the amount of blurring.
> c) It sets the threshold for edge detection.
> d) It determines the size of the matrix (e.g., 3x3 vs 5x5).
>> [!success]- Answer
>> b) It controls the spread (width) of the bell curve, determining the amount of blurring.

> [!question] When implementing a custom spatial filter (like the Mean filter in the lab), why is "padding" applied to the image?
> a) To increase the resolution of the image.
> b) To handle the border pixels where the kernel would hang off the edge.
> c) To add a black frame for aesthetic purposes.
> d) To convert the image to color.
>> [!success]- Answer
>> b) To handle the border pixels where the kernel would hang off the edge.

> [!question] Why is "Padding" (e.g., `cv2.copyMakeBorder`) often used before applying a spatial filter?
> a) To make the image look nicer.
> b) To ensure border pixels can be processed by the kernel without going out of bounds.
> c) To convert the image to grayscale.
> d) To increase the contrast of the edges.
>> [!success]- Answer
>> b) To ensure border pixels can be processed by the kernel without going out of bounds.

> [!question] In the context of the Nagao filter, why is the sub-region with the minimum variance chosen?
> a) To maximize the blur effect.
> b) To ensure the region is on one side of an edge (homogeneous), preserving the edge sharpness.
> c) To find the region with the most texture.
> d) To reduce computational complexity.
>> [!success]- Answer
>> b) To ensure the region is on one side of an edge (homogeneous), preserving the edge sharpness.

> [!question] In the Nagao filter, after calculating the variance of all sub-regions, which mean value is assigned to the central pixel?
> a) The mean of the sub-region with the highest variance.
> b) The mean of the sub-region with the lowest variance.
> c) The average of the means of all sub-regions.
> d) The mean of the entire neighborhood.
>> [!success]- Answer
>> b) The mean of the sub-region with the lowest variance.

### Morphology and segmentation

Choosing operations by goal: separating touching objects, filling holes, composing closing, thinning to a skeleton, and seeding watershed markers.

> [!question] If you want to separate two touching circular objects in a binary image without significantly reducing their size, which morphological operation sequence is best?
> a) Dilation
> b) Closing
> c) Opening (Erosion followed by Dilation)
> d) Edge Detection
>> [!success]- Answer
>> c) Opening (Erosion followed by Dilation)

> [!question] Which morphological operation is best suited for filling small holes inside foreground objects?
> a) Erosion
> b) Opening
> c) Closing
> d) Skeletonization
>> [!success]- Answer
>> c) Closing

> [!question] Which morphological operation is mathematically defined as `Erode(Dilate(Image))`?
> a) Opening
> b) Closing
> c) Gradient
> d) Skeletonization
>> [!success]- Answer
>> b) Closing

> [!question] In the Zhang-Suen algorithm (used in the lab), what is the goal of the operation?
> a) To count the number of objects.
> b) To reduce a binary shape to a 1-pixel wide skeleton.
> c) To fill holes in the object.
> d) To expand the object boundaries.
>> [!success]- Answer
>> b) To reduce a binary shape to a 1-pixel wide skeleton.

> [!question] In the context of the Watershed algorithm, what do the "markers" represent?
> a) The boundaries of the image.
> b) Seeds representing sure foreground and sure background regions.
> c) The location of noise pixels.
> d) The corners of the objects.
>> [!success]- Answer
>> b) Seeds representing sure foreground and sure background regions.

### Pixel distances

Two items connect movement rules and connectivity to the distance metrics they induce.

> [!question] Which distance metric corresponds to the number of steps taken if you can only move horizontally and vertically (no diagonals)?
> a) Euclidean ($d_2$)
> b) Chebyshev ($d_\infty$)
> c) Manhattan ($d_1$)
> d) Mahalanobis
>> [!success]- Answer
>> c) Manhattan ($d_1$)

> [!question] If a pixel has 8-connectivity with its neighbors, which distance metric best describes the distance to its diagonal neighbors?
> a) 1 (Chessboard Distance)
> b) $\sqrt{2}$ (Euclidean Distance)
> c) 2 (Manhattan Distance)
> d) 0
>> [!success]- Answer
>> a) 1 (Chessboard Distance)

### The frequency domain

What sits at the center of the shifted spectrum, what a high-pass filter does, and which filter is a Gaussian modulated by a sinusoid.

> [!question] In the frequency domain, what does the center of the spectrum usually represent after an FFT shift?
> a) High frequency components (Edges).
> b) Low frequency components (Smooth areas).
> c) Noise.
> d) The image borders.
>> [!success]- Answer
>> b) Low frequency components (Smooth areas).

> [!question] In the frequency domain, what is the effect of a "High-Pass Filter"?
> a) It blurs the image.
> b) It removes noise but keeps edges.
> c) It enhances edges and sharp details while attenuating low-frequency background.
> d) It increases the overall brightness of the image.
>> [!success]- Answer
>> c) It enhances edges and sharp details while attenuating low-frequency background.

> [!question] Which filter is essentially a Gaussian kernel modulated by a sinusoidal wave?
> a) Median Filter
> b) Gabor Filter
> c) Sobel Filter
> d) Box Filter
>> [!success]- Answer
>> b) Gabor Filter

### OpenCV essentials

One item on the display call that pauses execution until a key is pressed.

> [!question] What does `cv2.waitKey(0)` do in the provided code examples?
> a) Closes the window immediately.
> b) Pauses the execution indefinitely until a key is pressed.
> c) Waits for 0 milliseconds and then proceeds.
> d) Saves the image to disk.
>> [!success]- Answer
>> b) Pauses the execution indefinitely until a key is pressed.

## Matching

Twenty matching questions pair terms with definitions, formulas, effects, or use cases; each group is matched independently, and several groups deliberately overlap, so a term that seems to fit two descriptions is a signal to re-read both. Work through them group by group — together they double as a compact revision summary of the whole chapter. The groups follow the same thematic order as the earlier rounds.

### Noise, metrics, and filters

Noise descriptions and parameters, evaluation methodology, filter characteristics, and kernel types.

> [!question] Match the noise type with its description.
>> [!example] Group A
>> a) Gaussian Noise
>> b) Salt-and-Pepper Noise
>> c) Speckle Noise
>
>> [!example] Group B
>> n) Multiplicative noise often found in radar/ultrasound.
>> o) Random occurrence of black and white pixels.
>> p) Additive noise following a normal distribution.
>
>> [!success]- Answer
>> a) -> p)
>> b) -> o)
>> c) -> n)

> [!question] Match the noise parameter to the noise type it controls.
>> [!example] Group A
>> a) Variance / Sigma
>> b) Probability density (p)
>
>> [!example] Group B
>> n) Salt-and-Pepper Noise.
>> o) Gaussian Noise.
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

> [!question] Match the filter comparison metric to its description.
>> [!example] Group A
>> a) MSE (Mean Squared Error)
>> b) Visual Inspection
>> c) Execution Time
>
>> [!example] Group B
>> n) Subjective evaluation by the human eye.
>> o) Objective calculation of pixel difference fidelity.
>> p) Measure of computational cost/efficiency.
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)

> [!question] Match the filter with its primary characteristic.
>> [!example] Group A
>> a) Mean Filter
>> b) Median Filter
>> c) Nagao Filter
>> d) High-Pass Filter
>
>> [!example] Group B
>> n) Non-linear, preserves edges, removes impulsive noise.
>> o) Linear, smooths image but blurs edges.
>> p) Adaptive, smooths homogeneous regions, preserves edges.
>> q) Enhances edges, removes low frequencies.
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)
>> d) -> q)

> [!question] Match the Kernel type with its operation.
>> [!example] Group A
>> a) Kernel with all values = 1/9
>> b) Kernel with center = 1, others = 0
>> c) Kernel with Gaussian distribution
>
>> [!example] Group B
>> n) Identity (No change).
>> o) Weighted smoothing.
>> p) Mean (Box) smoothing.
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

### Digital images, color, and formats

Basic terminology, color space channels, compression types, and file extensions.

> [!question] Match the term with its definition in the context of Digital Images.
>> [!example] Group A
>> a) Pixel
>> b) Resolution
>> c) Color Depth
>> d) Metadata
>
>> [!example] Group B
>> n) The dimensions of the image (Width x Height).
>> o) The smallest individual element of an image.
>> p) Information about the image (e.g., DPI, camera settings).
>> q) The number of bits used to represent the color of a pixel.
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> q)
>> d) -> p)

> [!question] Match the color space channel with its description.
>> [!example] Group A
>> a) L (in Lab)
>> b) H (in HSL)
>> c) Y (in YCrCb)
>
>> [!example] Group B
>> n) Luminance or Lightness.
>> o) Hue (color type).
>> p) Luma (brightness) component of video signals.
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)
>> c) -> p)

> [!question] Match the file format with its compression type.
>> [!example] Group A
>> a) JPEG
>> b) PNG
>> c) BMP
>> d) RAW
>
>> [!example] Group B
>> n) Lossless compression, supports transparency.
>> o) Lossy compression, good for photos.
>> p) Uncompressed or minimally processed sensor data.
>> q) Uncompressed, simple structure.
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> q)
>> d) -> p)

> [!question] Match the file extension with the format name.
>> [!example] Group A
>> a) .png
>> b) .jpg
>> c) .dcm
>
>> [!example] Group B
>> n) Digital Imaging and Communications in Medicine.
>> o) Portable Network Graphics.
>> p) Joint Photographic Experts Group.
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> n)

### Python and OpenCV

Array attributes and the core OpenCV functions.

> [!question] Match the Python variable type to its content in the context of OpenCV.
>> [!example] Group A
>> a) `img.shape`
>> b) `img.dtype`
>> c) `img.size`
>
>> [!example] Group B
>> n) Total number of pixels (or elements) in the array.
>> o) Tuple of dimensions (Height, Width, Channels).
>> p) Data type of the pixels (e.g., uint8).
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> n)

> [!question] Match the OpenCV function with its purpose.
>> [!example] Group A
>> a) `cv2.imread`
>> b) `cv2.cvtColor`
>> c) `cv2.warpAffine`
>> d) `cv2.threshold`
>
>> [!example] Group B
>> n) Applies geometric transformations (rotation, translation).
>> o) Loads an image from a file.
>> p) Converts images between color spaces (e.g., BGR to Gray).
>> q) Converts a grayscale image to binary.
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> n)
>> d) -> q)

### Morphology, logic, and segmentation

Operation effects, noise removal by structuring element, binary logic, task-to-algorithm pairings, and structuring element shapes.

> [!question] Match the Morphological Operation with its effect.
>> [!example] Group A
>> a) Erosion
>> b) Dilation
>> c) Opening
>> d) Closing
>
>> [!example] Group B
>> n) Expands objects, fills holes.
>> o) Shrinks objects, removes small islands.
>> p) Removes small objects/noise, smooths from outside.
>> q) Fills small holes, smooths from inside.
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)
>> d) -> q)

> [!question] Match the Morphological Structuring Element to the noise it best removes.
>> [!example] Group A
>> a) Erosion
>> b) Dilation
>
>> [!example] Group B
>> n) Removes small black holes (Pepper noise) inside white objects.
>> o) Removes small white spots (Salt noise) in the background.
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

> [!question] Match the Logical Operation with its effect on a Binary Image.
>> [!example] Group A
>> a) AND
>> b) OR
>> c) NOT
>
>> [!example] Group B
>> n) Inverts the image (Black becomes White).
>> o) Union of two images.
>> p) Intersection of two images.
>
>> [!success]- Answer
>> a) -> p)
>> b) -> o)
>> c) -> n)

> [!question] Match the Image Processing task with the appropriate algorithm/method.
>> [!example] Group A
>> a) Removing Salt-and-Pepper Noise
>> b) Enhancing Contrast
>> c) Finding Image Skeleton
>> d) Segmentation of touching cells
>
>> [!example] Group B
>> n) Histogram Equalization / CLAHE
>> o) Watershed Algorithm
>> p) Median Filter
>> q) Zhang-Suen Algorithm
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> q)
>> d) -> o)

> [!question] Match the Structural Element shape to its likely usage.
>> [!example] Group A
>> a) Disk/Circle SE
>> b) Line SE
>
>> [!example] Group B
>> n) Detecting or filtering features with specific orientation.
>> o) Isotropic processing (equal in all directions), e.g., for round cells.
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

### Histograms and distances

Histogram shapes and distance-metric analogies.

> [!question] Match the Histogram shape with the image characteristic.
>> [!example] Group A
>> a) Histogram clustered to the left
>> b) Histogram clustered to the right
>> c) Narrow histogram in the middle
>> d) Histogram spread across full range
>
>> [!example] Group B
>> n) High contrast image.
>> o) Dark image.
>> p) Low contrast image.
>> q) Bright image.
>
>> [!success]- Answer
>> a) -> o)
>> b) -> q)
>> c) -> p)
>> d) -> n)

> [!question] Match the distance metric with its geometric analogy.
>> [!example] Group A
>> a) Euclidean Distance
>> b) Manhattan Distance
>> c) Chebyshev Distance
>
>> [!example] Group B
>> n) City block navigation (grid movement).
>> o) King's movement in Chess.
>> p) Straight line (ruler).
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

### The frequency domain

Frequency-domain filters with their spatial effects, and the vocabulary of the Fourier representation — the material of [[Frequency Domain Filtering]] and [[The Fourier Transform]].

> [!question] Match the Frequency Domain Filter with its spatial equivalent/effect.
>> [!example] Group A
>> a) Low-Pass Filter
>> b) High-Pass Filter
>> c) Band-Reject Filter
>
>> [!example] Group B
>> n) Edge detection / Sharpening.
>> o) Removes periodic noise.
>> p) Blurring / Smoothing.
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

> [!question] Match the Frequency Domain concept with its definition.
>> [!example] Group A
>> a) Fourier Transform
>> b) DC Component
>> c) Inverse FFT
>
>> [!example] Group B
>> n) The term corresponding to zero frequency (average brightness).
>> o) Converts frequency representation back to spatial domain.
>> p) Decomposes an image into sine and cosine components.
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

## See also

- [[Image Processing Global Index]]
- [[What is a Digital Image]]
- [[Image Representation Types]]
- [[Resolution and Bit Depth]]
- [[Color Spaces and Models]]
- [[Image File Formats]]
- [[The Image Histogram]]
- [[Histogram Equalization]]
- [[Image Degradation and Noise Models]]
- [[Image Quality Metrics]]
- [[The Mechanics of Spatial Filtering]]
- [[Linear Smoothing Filters]]
- [[Non-Linear Smoothing Filters]]
- [[Gabor Filters]]
- [[Mathematical Morphology Basics]]
- [[Erosion and Dilation]]
- [[Opening and Closing]]
- [[Morphological Algorithms]]
- [[Watershed Segmentation]]
- [[Thresholding and Otsu's Method]]
- [[Introduction to the Frequency Domain]]
- [[The Fourier Transform]]
- [[Frequency Domain Filtering]]
- [[Image Fundamentals and Histograms Quiz]]
- [[Spatial Filtering and Convolution Quiz]]
- [[Noise Degradation and Frequency Domain Quiz]]
