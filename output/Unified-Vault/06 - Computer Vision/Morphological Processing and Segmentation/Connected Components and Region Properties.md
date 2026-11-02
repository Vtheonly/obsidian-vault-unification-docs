---
title: Connected Components and Region Properties
type: concept
aliases:
  - Connected Component Labeling
  - Connected Component Analysis
  - CCL
  - Region Property Extraction
  - Blob Analysis
tags:
  - image-processing
  - computer-vision
  - segmentation
  - connected-components
  - region-properties
  - image-moments
  - hu-moments
  - morphological-processing
sources:
  - "5.9 Connected Components and Region Properties"
created_index: 47
---

After [[Thresholding and Otsu's Method]] or another segmentation step produces a binary (or labeled) image, the next question is: **how many separate objects are there, and what are their properties?** Answering it is the job of **connected component labeling** and **region property extraction** — the final step in almost every classical segmentation pipeline. This note covers the two-pass labeling algorithm, the choice between 4- and 8-connectivity (and the topological paradox that comes with it), the property families derived from image moments, and the complete pipeline from preprocessing to measurement. It leans on the N4/N8 connectivity definitions from [[Pixel Relationships and Distance Metrics]].

## Connected component labeling

A **connected component** is a maximal set of foreground pixels where you can travel between any two pixels in the set by stepping only between adjacent foreground pixels (4-connectivity or 8-connectivity — see [[Pixel Relationships and Distance Metrics]]). **Connected component labeling** assigns a unique integer label to each connected component. Background is 0; the first object is 1; the second is 2; and so on. The result is a **labeled image** where each object has a unique ID — the representation that every counting, measuring, and filtering stage downstream operates on.

### The two-pass algorithm

The standard algorithm makes two passes over the image.

**Pass 1 (top-left to bottom-right):** for each foreground pixel, look at its already-visited neighbors (above and left, for 4-connectivity). If none are labeled, assign a new label. If one is labeled, copy that label. If two have different labels, copy one and record that the two labels are equivalent (they are part of the same object).

**Pass 2:** resolve the equivalences — replace each label with its "root" in the equivalence table, so all pixels of the same object get the same final label.

This is $O(N)$ where $N$ is the number of pixels — very fast. In OpenCV:

```python
import cv2
import numpy as np

# Binary image
_, binary = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)

# Connected components
num_labels, labels = cv2.connectedComponents(binary, connectivity=8)
# num_labels includes background (label 0), so num_objects = num_labels - 1
# labels is an H×W array where each object has a unique integer
```

### 4-connectivity vs 8-connectivity

**4-connectivity** connects pixels only if they share an edge (up/down/left/right). It is the stricter rule — two diagonal pixels land in different components. **8-connectivity** connects pixels if they share an edge OR a corner. It is more permissive — diagonal pixels belong to the same component.

Which to use? It depends on the image. For objects with smooth boundaries, 8-connectivity is usually right (diagonal connections are real). For objects connected only by thin diagonal bridges that are likely noise, 4-connectivity avoids merging them. The choice should be deliberate, not default.

> [!warning] The connectivity paradox
> If you use 8-connectivity for the foreground, you should use **4-connectivity for the background** (and vice versa). Otherwise you get a topological paradox: two foreground objects that "touch" diagonally would be merged by 8-connectivity, but the background "between" them would also be one component by 8-connectivity — yet they surround each other, which is impossible for a single component. The fix is to use opposite connectivity for foreground vs background.

## Region properties

Once you have labeled components, you compute **properties** of each region. These properties are the features you use to count, classify, or filter objects. They come in three families — basic geometry, shape descriptors, and intensity statistics — and most trace back to the region's moments, described after the tables.

### Basic properties

| Property | Definition |
| :--- | :--- |
| **Area** | Number of pixels in the region. |
| **Centroid** | The mean $(x, y)$ position of the region's pixels. |
| **Bounding box** | The smallest axis-aligned rectangle containing the region. |
| **Perimeter** | Length of the region's boundary (approximated by counting boundary pixels). |

The basic properties answer the simplest questions — how big an object is, where it sits, and what rectangle it fits in. Area and centroid fall directly out of the region's moments ($m_{00}$ is the area, $m_{10}/m_{00}$ and $m_{01}/m_{00}$ give the centroid), and the bounding box and perimeter anchor the normalized shape descriptors that follow.

### Shape properties

| Property | Definition | What it measures |
| :--- | :--- | :--- |
| **Circularity** | $4\pi \cdot \text{Area} / \text{Perimeter}^2$ | 1.0 for a perfect circle; < 1 for elongated shapes. |
| **Eccentricity** | From the fitted ellipse: $c/a$ (ratio of minor to major axis) | 0 for a circle; → 1 for a line. |
| **Solidity** | Area / Convex Hull Area | 1.0 for convex shapes; < 1 for shapes with indentations. |
| **Extent** | Area / Bounding Box Area | Fraction of the bounding box that is filled. |
| **Aspect ratio** | Bounding box width / height | Elongation. |
| **Orientation** | Angle of the major axis of the fitted ellipse | The direction the object points. |

Each descriptor compares the region against a reference — the perfect circle for circularity, the fitted ellipse for eccentricity and orientation, the convex hull for solidity, the bounding box for extent and aspect ratio. Circular, convex, box-filling shapes score the ideal values (1.0, or 0 for eccentricity), and departures from them quantify elongation, indentation, or sparseness. These are the numbers a filter stage uses to discard regions that are too small, too large, or the wrong shape.

### Intensity properties

When the original image is grayscale, the labels also gather intensity statistics per region:

| Property | Definition |
| :--- | :--- |
| **Mean intensity** | Average grayscale value of the region's pixels in the original image. |
| **Std intensity** | Standard deviation of grayscale values. |
| **Min/Max intensity** | Extreme values. |
| **Texture** (optional) | LBP, GLCM (gray-level co-occurrence matrix) features computed over the region. |

Mean and standard deviation summarize how bright and how uniform each region is, while the min and max expose the extremes. Optional texture features — LBP or GLCM descriptors computed over the region — extend the description from raw intensities to spatial pattern.

### Moments

The properties above are derived from **image moments** — weighted sums of pixel positions:

$$m_{pq} = \sum_{(x,y) \in \text{region}} x^p y^q \cdot I(x, y)$$

The raw moments already carry the basics:

- $m_{00}$ = area (for binary images) or sum of intensities (for grayscale).
- $m_{10}/m_{00}$, $m_{01}/m_{00}$ = centroid.
- **Central moments** (computed relative to the centroid) give shape descriptors.
- **Hu moments** (7 specific combinations of central moments) are **translation, scale, and rotation invariant** — they are the same for the same shape regardless of position, size, or orientation. Used for shape matching.

In scikit-image, labeling and measurement pair up directly:

```python
from skimage import measure

labels = measure.label(binary)
regions = measure.regionprops(labels, intensity_image=image)
for region in regions:
    print(region.area, region.centroid, region.eccentricity, region.mean_intensity)
```

## The complete classical segmentation pipeline

Putting it all together, the workhorse pipeline for classical object segmentation runs in eight stages:

1. **Preprocess:** grayscale conversion, denoising (Gaussian/median filter), contrast enhancement.
2. **Segment:** thresholding (Otsu/adaptive) or edge detection → binary image.
3. **Clean up:** morphological opening (remove noise) + closing (fill holes).
4. **Separate touching objects:** distance transform + markers + watershed (if needed).
5. **Label:** connected component labeling → each object has a unique ID.
6. **Measure:** compute region properties (area, centroid, shape, intensity).
7. **Filter:** discard regions that are too small, too large, or the wrong shape.
8. **Output:** count, classify, or measure the remaining objects.

The same skeleton appears across domains with the emphasis shifting: **cell counting** runs threshold → watershed → label → count; **defect detection** runs threshold → label → measure and flags regions with abnormal properties; **particle analysis** runs threshold → watershed → label and measures the size distribution; **document analysis** runs threshold → label → measure and classifies characters. In every case, labeling and measurement are the stages that turn pixels into countable, classifiable objects.

## Key takeaways

Connected component labeling assigns a unique ID to each separate object in a binary image, using 4- or 8-connectivity, and runs in two linear passes over the pixels. Use **opposite connectivity** for foreground vs background to avoid the topological paradox. **Region properties** describe each object: area, centroid, bounding box, perimeter, circularity, eccentricity, solidity, extent, aspect ratio, orientation, and intensity statistics. **Hu moments** are translation-, scale-, and rotation-invariant shape descriptors built from central moments, used for shape matching. The complete classical segmentation pipeline is preprocess → threshold → morphology → watershed → label → measure → filter, and it is the workhorse of cell counting, defect detection, particle analysis, and document analysis.

## See also

- [[Image Processing Global Index]]
- [[Mathematical Morphology Basics]]
- [[Erosion and Dilation]]
- [[Opening and Closing]] — the cleanup pair in stage 3 of the pipeline
- [[Thresholding and Otsu's Method]] — the binarization stage
- [[Watershed Segmentation]] — separating touching objects in stage 4
- [[Morphological Algorithms]]
- [[Pixel Relationships and Distance Metrics]] — the N4/N8 connectivity definitions
- [[Deep Learning for Imaging]]
