---
title: Image Processing Global Index
type: overview
aliases:
  - Global Index - Image Processing
  - Image Processing Index
  - Image Processing Chapter Roadmap
  - Image Processing Reading Guide
tags:
  - image-processing
  - computer-vision
  - classical-image-processing
  - index
  - reading-order
  - orientation
sources:
  - "00. Global Index"
created_index: 39
---

This note is the roadmap for the classical image-processing chapter of the computer vision area. The chapter covers classical digital image processing from first principles — what images are, how their intensities are transformed, how they are filtered, what the frequency domain reveals, and how morphology segments them — with bridges to the deep learning approaches that have extended (and in some cases replaced) the classical methods. It is the entry point for the image-processing notes; the CNN side of the area starts at [[CNN Course Overview]].

## How to read this chapter

The chapter is organized sequentially: fundamentals → intensity transforms → spatial filtering → frequency domain → morphology and segmentation. Each section builds on the previous one. If you are new to image processing, read linearly; if you are looking for a specific topic, use the section index below or the cross-reference map further down.

The key connection to keep in mind throughout: classical image processing and CNNs are the same operation — convolution. The difference is whether the kernel is designed by a human or learned from data. The explicit connection, including how CNNs end up learning classical filters, is made in [[From Basic Convolution to Learned Weights]].

## Fundamentals of digital images

The opening section defines the objects everything else operates on: how continuous scenes become digital images, how those images are represented and stored, and how color is encoded and processed.

- [[What is a Digital Image]] — sampling, quantization, coordinate systems, image types.
- [[Image Representation Types]] — raster (bitmap) vs. vector graphics.
- [[Resolution and Bit Depth]] — spatial resolution, DPI/PPI, intensity resolution.
- [[Color Spaces and Models]] — RGB, CMYK, HSL/HSV, YCbCr, LAB, grayscale conversion.
- [[Image File Formats]] — compression (lossy vs. lossless), JPEG, PNG, DICOM.
- [[Pixel Relationships and Distance Metrics]] — N4/N8 neighbors, adjacency, distance metrics.
- [[The Color Image Processing Pipeline]] — Bayer demosaicing, white balance, color correction, gamma encoding.

## Intensity transformations and histograms

The first processing layer operates on single pixels. These notes treat the histogram as a diagnostic, the point operations, and the contrast family from simple stretching to equalization and its adaptive variants.

- [[The Image Histogram]] — definition, visual analysis, implementation.
- [[Point Processing Operations]] — negatives, log transforms, gamma correction.
- [[Contrast Stretching]] — dynamic range expansion, linear stretching.
- [[Histogram Equalization]] — global equalization, the CDF.
- [[Advanced Histogram Techniques]] — AHE, CLAHE, histogram specification.

## Spatial filtering and neighborhood processing

The second layer operates on neighborhoods: the mechanics of correlation and convolution, the smoothing families, and the large topic of edges — their detection, their enhancement, the features built on them, and the geometric and multi-scale machinery around them.

- [[The Mechanics of Spatial Filtering]] — correlation vs. convolution, padding, stride.
- [[Linear Smoothing Filters]] — box filter, Gaussian filter, separability.
- [[Non-Linear Smoothing Filters]] — median, min/max, rank-order.
- [[Edge Preserving Filters]] — Nagao, bilateral, anisotropic diffusion.
- [[Sharpening and Edge Detection]] — Sobel, Prewitt, Laplacian, unsharp masking.
- [[Canny and LoG Edge Detection]] — Canny's 5-step pipeline, non-maximum suppression, hysteresis, LoG, DoG.
- [[Geometric Transformations and Interpolation]] — affine, perspective, nearest/bilinear/bicubic/Lanczos.
- [[Feature Descriptors - SIFT, SURF, ORB, HOG]] — keypoint detection, SIFT, ORB, HOG, LBP.
- [[Image Pyramids and Multi-Scale Representation]] — Gaussian/Laplacian pyramids, FPN.
- [[The Hough Transform]] — line and circle detection via parameter-space voting.
- [[Gabor Filters]] — Gaussian × sinusoid, dual localization.

One standalone concept note belongs beside this section: the mathematical properties of convolution itself — commutativity, distributivity, separability — is treated on the CNN side, in [[The Convolution Operation]].

## Frequency domain and restoration

The chapter then changes perspective and analyzes images as sums of frequencies, uses that view for filtering and restoration, and closes with how image quality is measured.

- [[Introduction to the Frequency Domain]] — waves, frequencies, the "soup" analogy.
- [[The Fourier Transform]] — 1D/2D DFT, FFT, magnitude/phase, why phase matters.
- [[Frequency Domain Filtering]] — low-pass (ideal/Butterworth/Gaussian), high-pass, notch.
- [[Image Degradation and Noise Models]] — Gaussian/salt-and-pepper/speckle/Poisson noise, blur, the Wiener filter.
- [[Image Quality Metrics]] — MSE, PSNR, SSIM, MS-SSIM, LPIPS.

The imaging-focused Fourier walkthrough with Python code (FFT, filtering, IFFT) is folded into [[The Fourier Transform]].

## Morphology and segmentation

The final classical section processes shapes: set-theoretic operators on regions, the segmentation workhorses built on them, and the bridge into deep learning that competes with them.

- [[Mathematical Morphology Basics]] — set theory, structuring elements.
- [[Erosion and Dilation]] — the fundamental operations, duality.
- [[Opening and Closing]] — compound operations, idempotency.
- [[Morphological Algorithms]] — boundary extraction, region filling, skeletonization, Hit-or-Miss.
- [[Thresholding and Otsu's Method]] — Otsu's method, adaptive thresholding.
- [[Watershed Segmentation]] — marker-controlled watershed, the distance transform.
- [[Connected Components and Region Properties]] — labeling, shape/intensity properties, Hu moments.

Two notes in this stretch lead across to the deep-learning side: [[Deep Learning for Imaging]] (DnCNN, U-Net, residual learning) and [[From Basic Convolution to Learned Weights]] (how CNNs learn classical filters — Sobel, Gabor, Laplacian).

## Quizzes

The chapter's flashcards cover all of its topics and are collected in four quiz notes: [[Image Fundamentals and Histograms Quiz]], [[Spatial Filtering and Convolution Quiz]], [[Noise Degradation and Frequency Domain Quiz]], and [[Image Processing Comprehensive Quiz]].

## Cross-reference map

When you know the topic but not the note, use this map: the middle column is the primary treatment, the right column the natural companion reading.

| Topic | Primary location | Also see |
| :--- | :--- | :--- |
| What is an image | [[What is a Digital Image]] | [[Image Representation Types]], [[Resolution and Bit Depth]] |
| Color | [[Color Spaces and Models]], [[The Color Image Processing Pipeline]] | — |
| Histograms | [[The Image Histogram]], [[Point Processing Operations]], [[Contrast Stretching]], [[Histogram Equalization]], [[Advanced Histogram Techniques]] | — |
| Edge detection | [[Sharpening and Edge Detection]], [[Canny and LoG Edge Detection]] | [[From Basic Convolution to Learned Weights]] (bridge to CNNs) |
| Filtering | [[The Mechanics of Spatial Filtering]], [[Linear Smoothing Filters]], [[Non-Linear Smoothing Filters]], [[Edge Preserving Filters]] | [[Frequency Domain Filtering]] (frequency domain) |
| Geometric transforms | [[Geometric Transformations and Interpolation]] | [[Image Pyramids and Multi-Scale Representation]] (pyramids) |
| Feature descriptors | [[Feature Descriptors - SIFT, SURF, ORB, HOG]] | [[From Basic Convolution to Learned Weights]] (replaced by CNNs) |
| Pyramids / multi-scale | [[Image Pyramids and Multi-Scale Representation]] | [[Feature Descriptors - SIFT, SURF, ORB, HOG]] (SIFT scale space) |
| Hough transform | [[The Hough Transform]] | [[Sharpening and Edge Detection]] (edges feed Hough) |
| Fourier / frequency | [[Introduction to the Frequency Domain]], [[The Fourier Transform]], [[Frequency Domain Filtering]], [[Image Degradation and Noise Models]], [[Image Quality Metrics]] | [[Linear Smoothing Filters]] (Gaussian = same in both domains) |
| Noise / restoration | [[Image Degradation and Noise Models]] | [[Non-Linear Smoothing Filters]] (median for salt-pepper) |
| Quality metrics | [[Image Quality Metrics]] | — |
| Morphology | [[Mathematical Morphology Basics]], [[Erosion and Dilation]], [[Opening and Closing]], [[Morphological Algorithms]] | — |
| Segmentation | [[Thresholding and Otsu's Method]], [[Watershed Segmentation]], [[Connected Components and Region Properties]] | [[Deep Learning for Imaging]] (deep learning) |
| Classical → deep bridge | [[From Basic Convolution to Learned Weights]] | [[Sharpening and Edge Detection]] (the unsharp masking–ResNet connection) |
| Deep learning for imaging | [[Deep Learning for Imaging]] | — |

## Connections to the CNN side

The classical chapter connects to the CNN course at several points. Classical filters such as Sobel and Gabor are mathematically identical to CNN first-layer filters; the explicit bridge is [[From Basic Convolution to Learned Weights]]. The advanced CNN operators (Ch. 05.07) build directly on the classical foundations here — dilated convolutions (DeepLab) and transposed convolutions (U-Net decoders) are covered in [[Advanced Convolutional Operators - Depthwise, Dilated, Transposed, Grouped]]. Modern CV tasks (Ch. 05.08): object detection and segmentation use the metrics (IoU, mAP, Dice) and the architectures (U-Net, FCN) previewed in [[Deep Learning for Imaging]]; that material lives in [[Detection and Segmentation]]. Vision Transformers sit at the far end of the same line of thought: ViT's patch embedding is the deep-learning analog of the block-based processing used in JPEG compression (see [[Image File Formats]]) and classical image analysis. Finally, the image quality metrics (MSE, PSNR, SSIM) are the image-specific counterparts of the regression metrics used in machine learning evaluation.

For the full structure of the computer vision area and its learning paths, see [[CNN Course Overview]] and [[CNN Mastery Roadmap]].

## See also

- [[CNN Course Overview]] — the map of the CNN course.
- [[CNN Mastery Roadmap]] — the phased learning path to CNN engineering.
- [[From Basic Convolution to Learned Weights]] — the classical-to-deep bridge.
- [[The Convolution Operation]] — the shared operator, treated on the CNN side.
- [[Deep Learning for Imaging]] — the deep-learning systems that grew out of classical restoration.
- [[Detection and Segmentation]] — the modern tasks that consume these building blocks.
