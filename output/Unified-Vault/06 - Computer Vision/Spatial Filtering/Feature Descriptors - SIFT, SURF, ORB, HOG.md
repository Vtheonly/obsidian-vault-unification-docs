---
title: Feature Descriptors - SIFT, SURF, ORB, HOG
type: concept
aliases:
  - SIFT and SURF
  - ORB Features
  - Histogram of Oriented Gradients
  - Local Binary Patterns
  - Keypoint Detection and Description
tags:
  - image-processing
  - computer-vision
  - feature-descriptors
  - sift
  - surf
  - orb
  - hog
  - lbp
  - keypoint-matching
sources:
  - "3.8 Feature Descriptors - SIFT, SURF, ORB, HOG"
created_index: 65
---

Before deep learning, **feature descriptors** were the heart of computer vision. The pipeline was: detect **keypoints** (interesting points like corners and blobs) → compute a **descriptor** (a vector summarizing the local appearance around each keypoint) → **match** descriptors between images, and this pipeline powered image stitching, 3D reconstruction, object recognition, and visual SLAM for two decades. Deep learning has largely replaced it for recognition, but feature descriptors remain essential for **geometric** tasks (stitching, SLAM, structure-from-motion) where you need precise point correspondences rather than semantic labels. This note covers the classical descriptor families — SIFT, SURF, ORB, HOG, and LBP — building on the gradient machinery of [[Sharpening and Edge Detection]] and the scale-space ideas of [[Canny and LoG Edge Detection]].

## Why feature descriptors exist

Consider the problem of **stitching two photos** of a landscape into a panorama. You need to:

1. Find points in photo A that correspond to points in photo B.
2. Compute the geometric transform that aligns them.
3. Warp and blend.

Step 1 is the hard part, and the reason it is hard is that you cannot compare pixel values directly: the same physical point will have different pixel values in the two photos because of different exposure, different angle, and different scale. What you need instead is a **description** of each point that is **invariant** to these changes — the same physical point should produce the same descriptor regardless of rotation, scale, illumination, and viewpoint.

A **feature descriptor** is exactly this: a function that takes a local image patch and produces a vector that is **invariant** (same point → same vector) and **distinctive** (different points → different vectors). The art is designing a descriptor that is invariant to the right things (rotation, scale, illumination) while remaining distinctive enough to match correctly. Every method in this note is a different compromise on that trade-off.

## The two-stage pipeline: detection then description

Most feature methods have two stages. The **detector** finds "interesting" locations (keypoints) in the image — interesting usually means corners (where two edges meet) or blobs (regions that differ from their surroundings). The **descriptor** then computes a vector summarizing the local appearance around each keypoint.

The two stages have different requirements. The detector must be **repeatable** — the same physical point should be detected in different images. The descriptor must be **invariant** and **distinctive**, as above. SIFT, SURF, and ORB are detector–descriptor pairs; HOG and LBP skip detection entirely and describe dense regions of the image.

## SIFT (Scale-Invariant Feature Transform)

**SIFT** (David Lowe, 1999/2004) is the gold-standard feature detector and descriptor. It is invariant to **scale, rotation, and partial illumination changes**, and partially invariant to **viewpoint changes**. For over a decade, SIFT was the default feature for every CV task that needed correspondences, and its construction explains why it earned that position.

### Scale-space extrema detection

The key challenge: a feature that is distinctive at one scale may not be at another — a corner in a low-resolution image might be a smooth curve at high resolution. SIFT addresses this with a **scale-space pyramid**: blur the image with Gaussians of increasing $\sigma$, then compute the **Difference of Gaussians (DoG)** between adjacent scales (which approximates the LoG — see [[Canny and LoG Edge Detection]]).

Keypoints are detected as **local extrema** of the DoG across both space and scale: a pixel is a keypoint if it is larger (or smaller) than all 26 of its neighbors (8 in the same scale + 9 in the scale above + 9 in the scale below).

### Keypoint localization

Not all extrema are good keypoints, so SIFT refines them in two ways:

- **Discard low-contrast keypoints** (DoG response below a threshold) — these are noise.
- **Discard edge responses** (keypoints along edges but not at corners) — these are poorly localized along the edge direction. Detected by checking the ratio of principal curvatures (similar to Harris corner detection).

The remaining keypoints are **stable** — they survive changes in scale, rotation, and illumination.

### Orientation assignment

For each keypoint, compute the gradient magnitude and direction over a local neighborhood. Accumulate these into a **36-bin orientation histogram** (10° per bin). The peak of the histogram is the keypoint's **dominant orientation**. All subsequent computations are done relative to this orientation, making the descriptor **rotation-invariant**: rotate the image, and the dominant orientation rotates with it, so the descriptor computed relative to that orientation does not change.

### Descriptor computation

In a 16×16 window around the keypoint (rotated to the dominant orientation):

1. Divide the window into 4×4 sub-regions (16 sub-regions total).
2. In each sub-region, compute an 8-bin orientation histogram (weighted by gradient magnitude and a Gaussian window).
3. Concatenate the 16 histograms × 8 bins = **128-dimensional descriptor vector**.
4. Normalize the vector (to handle illumination changes), clip large values (to handle saturation), and re-normalize.

The 128-dimensional SIFT descriptor is the signature of the keypoint. Two keypoints from different images that describe the same physical location will have similar SIFT descriptors (small Euclidean distance).

### Matching SIFT descriptors

To match keypoints between two images:

1. For each descriptor in image A, find the **nearest neighbor** in image B and the **second-nearest neighbor**.
2. Apply **Lowe's ratio test**: keep the match only if the nearest distance is less than 0.7× the second-nearest distance. This rejects ambiguous matches (where two descriptors in B are equally close to the one in A).
3. (Optional) Apply **RANSAC** to find the geometric transform consistent with the largest set of matches, rejecting outliers.

The ratio test is the quiet workhorse of classical vision: a match is only trusted when it is clearly better than the runner-up. Once a consistent set of matches survives, the geometric transform between the images can be estimated and applied with the machinery of [[Geometric Transformations and Interpolation]].

## SURF (Speeded-Up Robust Features)

**SURF** (Bay et al., 2006) is a faster approximation of SIFT, using **integral images** (a data structure that allows computing the sum of any rectangular region in constant time) to speed up the computations. SURF uses the **Hessian matrix** (instead of DoG) for detection and **Haar wavelet responses** for the descriptor. It is ~3× faster than SIFT with comparable accuracy. SURF was patented (now expired) and is available in OpenCV.

## ORB (Oriented FAST and Rotated BRIEF)

**ORB** (Rublee et al., 2011) is a fast, **patent-free** alternative to SIFT/SURF, designed for real-time applications. It combines:

- **FAST** (Features from Accelerated Segment Test) for keypoint detection — a fast corner detector that examines a circle of 16 pixels around a candidate and counts contiguous bright/dark pixels.
- **BRIEF** (Binary Robust Independent Elementary Features) for the descriptor — a 256-bit binary string where each bit is the result of comparing two random pixels in the patch.
- **Orientation estimation** added to both (the "O" and "R" in ORB) for rotation invariance.

ORB's binary descriptor is extremely fast to compute and to match (Hamming distance via XOR, which CPUs compute in a single instruction). ORB is the default feature detector in OpenCV and is used in real-time systems like visual SLAM, AR, and mobile CV apps.

```python
import cv2
orb = cv2.ORB_create()
keypoints, descriptors = orb.detectAndCompute(image, None)
# descriptors is a (N, 32) uint8 array — 256 bits per descriptor
```

## HOG (Histogram of Oriented Gradients)

**HOG** (Dalal and Triggs, 2005) is not a keypoint descriptor — it is a **dense** descriptor computed over the entire image. It was famously used for **pedestrian detection** (the first reliable real-time human detector) and remains a baseline for object detection.

### How HOG works

1. Compute the gradient (magnitude + direction) at every pixel (using Sobel).
2. Divide the image into **cells** (e.g., 8×8 pixels).
3. In each cell, compute a **9-bin orientation histogram** (20° per bin, over 0°–180° — "unsigned" gradients, because the sign of the gradient is less useful than its orientation for object shape).
4. Group cells into **blocks** (e.g., 2×2 cells = 16×16 pixels) and **normalize** the histograms within each block (to handle illumination changes). Blocks overlap, so each cell contributes to multiple normalized blocks.
5. Concatenate all normalized block histograms into the final **HOG descriptor** — a long vector (e.g., 3780 dimensions for a 64×128 image).

The HOG descriptor captures the **distribution of edge orientations** in local regions. Two images of the same object class (e.g., pedestrians) will have similar HOG descriptors because they have similar edge orientation patterns, even if the exact pixel values differ. That robustness to appearance variation within a class is precisely what a detector needs.

### HOG with a linear SVM

The classic HOG pipeline: compute HOG over a sliding window, feed the descriptor to a **linear SVM** classifier (trained on positive examples of the object and negative examples of background), and threshold the SVM score. This was the state-of-the-art for pedestrian detection before deep learning. The sliding window matters because a pedestrian can appear anywhere in the frame: the classifier decides, window by window, whether the local gradient statistics look like the object class it was trained on.

### HOG versus SIFT

| | SIFT | HOG |
| :--- | :--- | :--- |
| Computed at | Sparse keypoints | Dense grid (every cell) |
| Dimensionality | 128 per keypoint | Thousands per image |
| Purpose | Matching (find correspondences) | Detection (is there an object here?) |
| Invariance | Scale, rotation, illumination | Illumination (within blocks) |

SIFT is for **matching** (find the same point in two images); HOG is for **detection** (is there a pedestrian in this window?). They are complementary tools, not competitors: one summarizes sparse, precisely localized patches, the other summarizes the whole window.

## LBP (Local Binary Patterns)

**LBP** (Ojala et al., 1996) is a simple texture descriptor. For each pixel:

1. Compare the pixel to its 8 neighbors.
2. If a neighbor is greater than the center, write 1; else 0.
3. The 8 bits form a binary number (0–255) — the LBP code for that pixel.

The **histogram of LBP codes** over a region is the texture descriptor. LBPs are extremely fast to compute and are invariant to monotonic illumination changes (thresholding makes them robust to brightness shifts). They are used for **texture classification** and **face recognition** (the original "Eigenfaces" successor).

## What deep learning replaced — and what it did not

For **recognition** tasks (is this a cat? what object is here?), deep learning has almost completely replaced feature descriptors. A CNN's early layers learn filters that resemble Gabor filters and SIFT-like edge detectors, and the later layers compose these into semantic representations that outperform hand-crafted features (see [[Gabor Filters]] and [[From Basic Convolution to Learned Weights]]).

But feature descriptors remain essential for **geometric** tasks:

- **Image stitching / panorama:** SIFT/ORB to find correspondences, then compute the homography. Deep learning has not replaced this — you need precise point correspondences, not semantic similarity.
- **Visual SLAM** (Simultaneous Localization and Mapping): ORB-SLAM (the dominant SLAM system) uses ORB features for real-time camera tracking.
- **Structure from Motion (SfM):** reconstruct 3D geometry from 2D photos (used in photogrammetry, Google Maps 3D, etc.). Relies on feature matching.
- **Augmented Reality:** AR frameworks (ARKit, ARCore) use feature tracking for pose estimation.

The reason is a genuine division of labor: deep learning is good at **semantic** matching (cat matches cat) but feature descriptors are better at **precise geometric** matching (this exact pixel location matches that exact pixel location, to sub-pixel accuracy). For stitching and SLAM, you need the latter.

> [!summary] What to remember
> Feature descriptors have two stages: **detect** keypoints (repeatable interesting points) and **describe** them (invariant + distinctive vectors). **SIFT** is the gold standard — scale-invariant (DoG scale space), rotation-invariant (dominant orientation), illumination-invariant (normalized 128-D descriptor) — matched via nearest-neighbor + Lowe's ratio test. **SURF** is a faster approximation of SIFT using integral images; **ORB** is the patent-free real-time alternative (FAST detector + BRIEF binary descriptor) used in SLAM and AR. **HOG** is a dense descriptor (gradients over a grid) used for detection (pedestrians) — complementary to SIFT, which is for matching. **LBP** is a simple illumination-robust texture descriptor used for texture classification and face recognition. Deep learning replaced feature descriptors for **recognition**, but they remain essential for **geometric** tasks (stitching, SLAM, SfM, AR) where precise point correspondences are needed.

## See also

- [[Sharpening and Edge Detection]] — the Sobel gradients that SIFT orientation histograms and HOG are built on.
- [[Canny and LoG Edge Detection]] — the LoG operator that SIFT's DoG scale space approximates.
- [[Geometric Transformations and Interpolation]] — warping matched correspondences: affine and perspective transforms, interpolation.
- [[Image Pyramids and Multi-Scale Representation]] — the multi-scale pyramid idea behind the SIFT scale space.
- [[The Hough Transform]] — line and circle detection via parameter-space voting.
- [[Gabor Filters]] — the filter family that CNN early layers end up resembling.
- [[From Basic Convolution to Learned Weights]] — how learned filters replaced hand-crafted descriptors for recognition.
- [[Detection and Segmentation]] — the modern form of the object-detection problem HOG was famous for.
- [[Introduction to the Frequency Domain]] — the frequency-domain view that complements these spatial methods.
- [[Image Processing Global Index]] — the area's reading map.
