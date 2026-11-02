---
title: Image Fundamentals and Histograms Quiz
type: example
aliases:
  - Image Fundamentals Quiz
  - Digital Image Fundamentals Quiz
  - Fundamentals and Histograms Quiz
tags:
  - computer-vision
  - image-processing
  - quiz
  - practice
  - image-fundamentals
  - color-spaces
  - file-formats
  - histograms
  - pixel-distances
  - resolution
sources:
  - Q3
  - Q5
created_index: 59
---

This quiz tests the foundations that everything else in image processing stands on: what a digital image is, how bitmap and vector representations differ, how resolution and color depth determine what an image can show, and how histograms and pixel neighborhoods expose an image's tonal and geometric structure. Its sixty questions span the material from [[What is a Digital Image]] through [[Image Representation Types]], [[Resolution and Bit Depth]], [[Color Spaces and Models]], [[Image File Formats]], [[The Image Histogram]], and [[Pixel Relationships and Distance Metrics]]; the full curriculum is mapped in [[Image Processing Global Index]]. Three formats — true/false, multiple choice, and matching — revisit the same facts from different directions, and the wrong options are built from the most common mix-ups (PPI versus DPI, additive versus subtractive color, lossy versus lossless), so unfold each answer only after committing to one.

## True or false

Twenty statements open the quiz, grouped from raw pixel facts through representation, resolution, color, formats, histograms, and finally pixel relationships. Watch for statements that are true of one concept but attached to another — bitmap credited with vector properties, DPI credited with PPI — which is exactly the confusion this round is designed to expose.

### Digital images and pixels

Three statements about the atom of digital imaging: how images are quantized and how pixels are addressed.

> [!question] A digital image is inherently continuous, similar to an analog photograph.
>> [!success]- Answer
>> False

> [!question] A pixel's position is defined by a single numerical value rather than a coordinate pair.
>> [!success]- Answer
>> False

> [!question] The term "pixel" is short for "picture element."
>> [!success]- Answer
>> True

### Bitmap versus vector representation

Two statements on the scaling behavior that separates the two representation families.

> [!question] Vector images can be scaled to any size without loss of quality because they are based on mathematical formulas.
>> [!success]- Answer
>> True

> [!question] Bitmap images are ideal for graphics like logos and icons because they are resolution independent.
>> [!success]- Answer
>> False

### Resolution and color depth

Four statements on what resolution measures, what DPI is, and how many shades 8 bits buy you.

> [!question] Spatial resolution refers to the density of pixels per inch (PPI) rather than the total pixel dimensions of the image.
>> [!success]- Answer
>> False

> [!question] Spatial resolution is metadata that suggests how large an image should be when printed, measured in DPI.
>> [!success]- Answer
>> False

> [!question] An 8-bit grayscale image can represent 256 distinct shades of gray.
>> [!success]- Answer
>> True

> [!question] In an 8-bit grayscale image, the value 0 typically represents black and 255 represents white.
>> [!success]- Answer
>> True

### Color spaces

Two statements on the additive/subtractive divide and on what Hue controls in HSL.

> [!question] The RGB color model is subtractive and is primarily used for printing.
>> [!success]- Answer
>> False

> [!question] Changing the Hue in the HSL color model allows you to change the color of an object without affecting its brightness or intensity.
>> [!success]- Answer
>> True

### File formats and compression

Three statements on what lossless means, what RAW contains, and what travels inside a DICOM file.

> [!question] Lossless compression reduces file size by permanently discarding image data that is least perceptible to the human eye.
>> [!success]- Answer
>> False

> [!question] The RAW format consists of processed data that has been "baked in" by the camera's processor to reduce file size.
>> [!success]- Answer
>> False

> [!question] The DICOM format contains only the raw pixel data of medical images and no other information.
>> [!success]- Answer
>> False

### Histograms

Two statements on reading tonality off the histogram — the daily work of [[The Image Histogram]].

> [!question] A histogram that is clustered to the left side of the graph indicates a dark image.
>> [!success]- Answer
>> True

> [!question] A histogram with two distinct peaks (bimodal) is often useful for separating an object from its background using thresholding.
>> [!success]- Answer
>> True

### Pixel relationships and distances

Four statements on neighborhoods and the ordering of the standard distance metrics.

> [!question] In 4-connectivity (N4), pixels that are diagonally adjacent to the central pixel are considered neighbors.
>> [!success]- Answer
>> False

> [!question] 4-connectivity corresponds to pixels that are a Manhattan distance of 1 from the central pixel.
>> [!success]- Answer
>> True

> [!question] The Manhattan distance between two pixels is always greater than or equal to the Euclidean distance between them.
>> [!success]- Answer
>> True

> [!question] The Chebyshev distance (d_inf) corresponds to the minimum number of moves a Knight would need to travel on a chessboard.
>> [!success]- Answer
>> False

## Multiple choice

Twenty items with four options each follow the same thematic order. Many options are plausible-looking near-misses — the wrong formula weight, the wrong chess piece, the wrong compression scheme — so verify the exact wording of the option you pick.

### Digital images and representation

Library roles, matrix shapes, and the mosaic analogy that separates bitmap from vector.

> [!question] Which Python library is mentioned as being central to image processing due to its optimized tools for matrix operations?
> a) Pandas
> b) NumPy
> c) TensorFlow
> d) Matplotlib
>> [!success]- Answer
>> b) NumPy

> [!question] Which mathematical representation is typically used for a color image in computer processing?
> a) A single list of numbers
> b) A 3D matrix (or three 2D matrices)
> c) A vector graph
> d) A binary tree
>> [!success]- Answer
>> b) A 3D matrix (or three 2D matrices)

> [!question] Which image format is described as "resolution dependent" and analogous to a mosaic?
> a) Vector
> b) SVG
> c) Bitmap
> d) AI
>> [!success]- Answer
>> c) Bitmap

> [!question] In a vector image, what are the primary components used to describe the visual?
> a) Pixels and grids
> b) Mathematical objects (points, lines, curves)
> c) Light intensity values
> d) Voxels
>> [!success]- Answer
>> b) Mathematical objects (points, lines, curves)

> [!question] Which of the following is a characteristic of Vector Images?
> a) Large file sizes for simple shapes
> b) Resolution Dependent
> c) Composed of a grid of pixels
> d) Resolution Independent
>> [!success]- Answer
>> d) Resolution Independent

### Resolution and color depth

Pixel density terminology and the counting that bit depths do.

> [!question] What is the term for the density of pixels within a physical area for digital displays?
> a) Spatial Resolution
> b) PPI (Pixels Per Inch)
> c) Bit Depth
> d) Aspect Ratio
>> [!success]- Answer
>> b) PPI (Pixels Per Inch)

> [!question] How many distinct colors can be represented in a 24-bit True Color image?
> a) 256
> b) 65,536
> c) Approximately 16.7 million
> d) 1 billion
>> [!success]- Answer
>> c) Approximately 16.7 million

> [!question] What is the bit depth of a binary image?
> a) 1-bit
> b) 8-bit
> c) 16-bit
> d) 24-bit
>> [!success]- Answer
>> a) 1-bit

### Color spaces

Perceptual uniformity, the luminance weights, and the subtractive printing model.

> [!question] Which color space is designed to be perceptually uniform, making it excellent for measuring color differences?
> a) RGB
> b) CMYK
> c) Lab (CIELAB)
> d) HSL
>> [!success]- Answer
>> c) Lab (CIELAB)

> [!question] What is the standard formula for converting RGB to Grayscale to account for human eye sensitivity?
> a) (R + G + B) / 3
> b) 0.5 * R + 0.5 * G + 0.0 * B
> c) 0.299 * R + 0.587 * G + 0.114 * B
> d) Max(R, G, B)
>> [!success]- Answer
>> c) 0.299 * R + 0.587 * G + 0.114 * B

> [!question] In the RGB to Grayscale conversion formula `0.299 * R + 0.587 * G + 0.114 * B`, which color contributes the most to luminance?
> a) Red
> b) Green
> c) Blue
> d) All contribute equally
>> [!success]- Answer
>> b) Green

> [!question] Which color model is described as a subtractive model used in printing?
> a) RGB
> b) HSL
> c) XYZ
> d) CMYK
>> [!success]- Answer
>> d) CMYK

### File formats and compression

Choosing formats by use case and knowing what each one throws away.

> [!question] Which file format is best suited for web graphics and logos requiring transparency?
> a) JPEG
> b) PNG
> c) BMP
> d) RAW
>> [!success]- Answer
>> b) PNG

> [!question] Which format is described as a simple, raw format that stores pixel data directly but is inefficient for storage?
> a) JPEG
> b) PNG
> c) BMP
> d) TIFF
>> [!success]- Answer
>> c) BMP

> [!question] What is the primary disadvantage of using Lossy compression like JPEG?
> a) Larger file sizes
> b) Incompatibility with web browsers
> c) Permanent loss of some image data/quality
> d) Cannot store color information
>> [!success]- Answer
>> c) Permanent loss of some image data/quality

### Histograms

Reading contrast and exposure off the distribution of intensities.

> [!question] What does a narrow histogram occupying a small portion of the intensity range indicate?
> a) High contrast
> b) Low contrast
> c) Overexposure
> d) Underexposure
>> [!success]- Answer
>> b) Low contrast

> [!question] If a histogram is clustered to the **left** side of the graph, how would the image appear?
> a) Bright
> b) Dark
> c) Low Contrast (Gray)
> d) High Contrast
>> [!success]- Answer
>> b) Dark

### Pixel relationships and distances

Neighborhood definitions and the names and formulas of the three distance metrics.

> [!question] Which neighborhood definition includes the 4 horizontal/vertical neighbors plus the 4 diagonal neighbors?
> a) N4
> b) N8
> c) N16
> d) N-Cross
>> [!success]- Answer
>> b) N8

> [!question] Which distance metric is known as the "Chessboard Distance"?
> a) Euclidean Distance
> b) Manhattan Distance
> c) Chebyshev Distance
> d) Hamming Distance
>> [!success]- Answer
>> c) Chebyshev Distance

> [!question] Which distance metric is calculated as `|xp - xq| + |yp - yq|`?
> a) Euclidean Distance
> b) Manhattan Distance
> c) Chebyshev Distance
> d) Minkowski Distance
>> [!success]- Answer
>> b) Manhattan Distance

## Matching

Twenty matching questions close the quiz by pairing every major term with its definition, value, formula, or use case. Together the groups form a one-page summary of the fundamentals; if any column feels uncertain, the pairing names exactly which linked note to revisit.

### Image representation

Pixels, matrices, and what each representation family is made of.

> [!question] Match the image representation term with its definition.
>> [!example] Group A
>> a) Pixel
>> b) Bitmap Image
>> c) Vector Image
>
>> [!example] Group B
>> n) Composed of mathematical objects like lines and curves.
>> o) The smallest individual component of a digital image.
>> p) Composed of a grid of individual pixels, resolution dependent.
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> n)

> [!question] Match the matrix representation with the image type.
>> [!example] Group A
>> a) 2D Matrix
>> b) 3D Matrix
>
>> [!example] Group B
>> n) Color Image (includes channels like R, G, B).
>> o) Grayscale Image (single intensity value).
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

> [!question] Match the matrix element with the image type it represents.
>> [!example] Group A
>> a) Single value (0-255)
>> b) Triplet value (R, G, B)
>> c) Binary value (0 or 1)
>
>> [!example] Group B
>> n) 1-bit Image.
>> o) Grayscale Image.
>> p) Color Image.
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> n)

> [!question] Match the image characteristic with the correct format type.
>> [!example] Group A
>> a) Bitmap
>> b) Vector
>
>> [!example] Group B
>> n) Stores instructions like "draw a red circle".
>> o) Stores specific color values for every pixel in a grid.
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

### Resolution and color depth

Resolution terminology and the capacities of the standard bit depths.

> [!question] Match the resolution term with its definition.
>> [!example] Group A
>> a) Spatial Resolution
>> b) DPI (Dots Per Inch)
>
>> [!example] Group B
>> n) The density of pixels/dots for printing.
>> o) The pixel dimensions of the image (e.g., 1920 x 1080).
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

> [!question] Match the color depth with its capacity.
>> [!example] Group A
>> a) 1-bit
>> b) 8-bit
>> c) 24-bit
>
>> [!example] Group B
>> n) 256 possible shades (Grayscale).
>> o) Approximately 16.7 million colors (True Color).
>> p) 2 values (Black or White).
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

### Color spaces

Model characteristics, RGB corner values, and the HSL components.

> [!question] Match the color space with its primary characteristic.
>> [!example] Group A
>> a) RGB
>> b) CMYK
>> c) HSL
>
>> [!example] Group B
>> n) Subtractive model used in printing.
>> o) Additive model used for digital displays.
>> p) Aligned with human perception (Hue, Saturation, Lightness).
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)

> [!question] Match the RGB tuple with the color it represents.
>> [!example] Group A
>> a) (0, 0, 0)
>> b) (255, 255, 255)
>> c) (R=G=B)
>
>> [!example] Group B
>> n) White.
>> o) Shade of Gray.
>> p) Black.
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

> [!question] Match the HSL component with its description.
>> [!example] Group A
>> a) Hue
>> b) Saturation
>> c) Lightness
>
>> [!example] Group B
>> n) The brightness of the color.
>> o) The "purity" or intensity of the color.
>> p) The type of color (e.g., red, yellow).
>
>> [!success]- Answer
>> a) -> p)
>> b) -> o)
>> c) -> n)

### File formats and compression

Use cases, specialized domains, and what each compression family discards.

> [!question] Match the image format with its best use case.
>> [!example] Group A
>> a) JPEG
>> b) PNG
>> c) RAW
>
>> [!example] Group B
>> n) Professional photography requiring post-processing flexibility.
>> o) Photographs on the web with a balance of quality and size.
>> p) Graphics requiring transparency and sharp edges.
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> n)

> [!question] Match the specialized format with its domain.
>> [!example] Group A
>> a) DICOM
>> b) TIFF
>
>> [!example] Group B
>> n) Medical imaging and communication.
>> o) Desktop publishing and archiving.
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)

> [!question] Match the compression type with its definition.
>> [!example] Group A
>> a) Lossy Compression
>> b) Lossless Compression
>
>> [!example] Group B
>> n) Reduces file size without discarding any data.
>> o) Discards least perceptible data to achieve smaller file sizes.
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

> [!question] Match the file format with its compression characteristic.
>> [!example] Group A
>> a) PNG
>> b) JPEG
>> c) BMP
>
>> [!example] Group B
>> n) Lossy compression.
>> o) Lossless compression.
>> p) Typically uncompressed.
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)

> [!question] Match the format with its specific feature.
>> [!example] Group A
>> a) DICOM
>> b) RAW
>
>> [!example] Group B
>> n) Minimally processed data directly from the sensor.
>> o) Contains patient information and acquisition parameters.
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

### Histograms

Shapes, and what each histogram-processing technique is for.

> [!question] Match the histogram shape with the image characteristic.
>> [!example] Group A
>> a) Clustered to the right
>> b) Spread out across the range
>> c) Bimodal (two peaks)
>
>> [!example] Group B
>> n) High contrast.
>> o) Bright image.
>> p) Useful for thresholding (separating object from background).
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)
>> c) -> p)

> [!question] Match the histogram processing technique with its purpose.
>> [!example] Group A
>> a) Histogram Equalization
>> b) Thresholding
>> c) Image Comparison
>
>> [!example] Group B
>> n) Separating an object from the background based on intensity.
>> o) Using the histogram as a feature to measure similarity.
>> p) Increasing global contrast by redistributing pixel intensities.
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

### Pixel relationships and distances

Distance formulas and names, and the chess pieces that model each neighborhood.

> [!question] Match the distance metric with its description.
>> [!example] Group A
>> a) Euclidean Distance
>> b) Manhattan Distance
>> c) Chebyshev Distance
>
>> [!example] Group B
>> n) Sum of absolute differences (City-Block).
>> o) Maximum of absolute differences (Chessboard).
>> p) Straight-line geometric distance.
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

> [!question] Match the connectivity type with the number of neighbors.
>> [!example] Group A
>> a) N4 (4-Neighbors)
>> b) N8 (8-Neighbors)
>
>> [!example] Group B
>> n) Includes horizontal, vertical, and diagonal neighbors.
>> o) Includes only horizontal and vertical neighbors.
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

> [!question] Match the distance metric formula symbol with its common name.
>> [!example] Group A
>> a) d₂
>> b) d₁
>> c) d_inf
>
>> [!example] Group B
>> n) Manhattan Distance.
>> o) Chebyshev Distance.
>> p) Euclidean Distance.
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

> [!question] Match the neighbor definition with the visual logic.
>> [!example] Group A
>> a) 4-Neighbors
>> b) 8-Neighbors
>
>> [!example] Group B
>> n) Like a King's movement in Chess.
>> o) Like a Rook's movement in Chess (non-diagonal).
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

## See also

- [[Image Processing Global Index]]
- [[What is a Digital Image]]
- [[Image Representation Types]]
- [[Resolution and Bit Depth]]
- [[Color Spaces and Models]]
- [[The Color Image Processing Pipeline]]
- [[Image File Formats]]
- [[The Image Histogram]]
- [[Histogram Equalization]]
- [[Advanced Histogram Techniques]]
- [[Point Processing Operations]]
- [[Pixel Relationships and Distance Metrics]]
- [[Thresholding and Otsu's Method]]
- [[Image Processing Comprehensive Quiz]]
- [[Spatial Filtering and Convolution Quiz]]
- [[Noise Degradation and Frequency Domain Quiz]]
