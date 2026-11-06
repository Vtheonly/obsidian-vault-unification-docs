---
title: Image File Formats
type: reference
aliases:
  - Image File Formats and Compression
  - Image Formats
  - Image Compression
  - Lossy vs Lossless Compression
  - JPEG PNG GIF TIFF DICOM
tags:
  - image-processing
  - computer-vision
  - file-formats
  - compression
  - lossless-compression
  - lossy-compression
  - jpeg
  - png
  - gif
  - tiff
  - dicom
sources:
  - "1.5 Image File Formats"
created_index: 33
---

Image formats are containers that define how the pixel data is organized and compressed. Choosing among them is primarily a choice between lossless and lossy compression, guided by how the image will be used and whether every original pixel must survive. This reference summarizes why compression is necessary, how the two compression families work, and the properties of the common formats — JPEG, PNG, GIF, TIFF, and DICOM.

> [!info] Choosing a format in one line
> Use lossless formats (PNG, TIFF) when the reconstruction must be exact — medical imaging, technical drawings, logos, text, archiving. Use lossy formats (JPEG, WebP, HEIF) for photographs and web images, where a massive size reduction is worth discarding fine detail.

## Why compression is necessary

Raw images are huge — a single Full HD photo in true color needs about 6.22 MB of raw storage, as the arithmetic in [[Resolution and Bit Depth]] shows — so storing them efficiently requires compression. Compression exploits two properties of natural images. **Data redundancy**: images contain repeated data — a blue sky is thousands of consecutive blue pixels. **Irrelevancy**: images contain details the human eye cannot see, which can be removed without a visible difference.

## Lossless compression

Lossless compression compresses data without losing a single bit of information: the reconstructed image is mathematically identical to the original. Two technique families dominate. *Run Length Encoding (RLE)* exploits repetition directly — instead of storing "White, White, White, White, White", it stores "5 Whites". *Huffman Coding / LZW* take a statistical route, assigning shorter binary codes to frequently occurring patterns. The lossless formats are **PNG**, **TIFF**, **GIF**, and **BMP** (usually uncompressed, but supports RLE), and they are best for medical imaging, technical drawings, logos, text, and archiving — anywhere an exact reconstruction is mandatory.

## Lossy compression

Lossy compression discards information that is "least important" to human perception, achieving massive file size reduction — often 10:1 or more. Its core technique uses the Discrete Cosine Transform (DCT) to separate low frequencies (general color/shape) from high frequencies (fine noise/texture). It then quantizes (rounds off) the high frequencies, effectively deleting fine detail. The lossy formats are **JPEG**, **WebP**, and **HEIF**, and they are best for photographs and web images. Pushing the compression too far produces characteristic artifacts: blockiness, "ringing" around text, and smudged details.

## Format reference

| Format | Compression | Transparency? | Use Case |
| :--- | :--- | :--- | :--- |
| **JPEG** | Lossy | No | Photos, Web. Small size, variable quality. |
| **PNG** | Lossless | Yes (Alpha) | Web graphics, logos, screenshots. |
| **GIF** | Lossless* | Yes (1-bit) | Simple animations. Limited to 256 colors only. |
| **TIFF** | Lossless/None | Yes | Print, Archival, Professional Photography. |
| **DICOM** | N/A | N/A | **Medical Standard.** Contains image data + metadata (Patient ID, Scan type). |

Most rows in the table map directly onto the two families above, with one special case. DICOM is not just an image format; it is a protocol. A DICOM file wraps the raw pixel data (often 16-bit grayscale for X-rays) with headers containing critical medical information, which is why it carries Patient ID and scan type alongside the image — and why medical imaging sits firmly on the lossless side of the divide.

## See also

- [[Image Processing Global Index]]
- [[Resolution and Bit Depth]]
- [[Image Representation Types]]
- [[What is a Digital Image]]
- [[Color Spaces and Models]]
- [[The Color Image Processing Pipeline]]
- [[Image Fundamentals and Histograms Quiz]]
