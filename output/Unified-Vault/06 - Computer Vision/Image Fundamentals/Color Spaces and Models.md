---
title: Color Spaces and Models
type: concept
aliases:
  - Color Models
  - Color Spaces
  - Color Models and Spaces
  - RGB CMYK HSL HSV YCbCr LAB
tags:
  - color
  - color-models
  - color-spaces
  - rgb
  - cmyk
  - hsl
  - hsv
  - ycbcr
  - yuv
  - cielab
  - lab
  - luminance
  - chrominance
  - grayscale-conversion
  - chroma-subsampling
sources:
  - "1.4 Color Spaces and Models"
created_index: 32
---

A color model is a mathematical way to describe colors as tuples of numbers — triplets or quadruplets, depending on the model. Different models exist because they solve different problems: displaying light, printing ink, or matching human perception. This note covers the major color models — RGB, CMYK, HSL/HSV, YCbCr/YUV, and LAB — along with the conversion logic between them and the question of which space to reach for in which task. It assumes the digital-image basics of [[What is a Digital Image]], and it feeds directly into [[The Color Image Processing Pipeline]], which shows how cameras actually produce RGB values.

## RGB: the additive model

RGB is an **additive color model**, used in monitors, cameras, and screens. It models the mixing of **light**: all colors start from black (no light) and are built by adding wavelengths. Black is the absence of light, written $(0,0,0)$; white is all channels at maximum intensity, written $(255,255,255)$; and intermediate colors are mixed by addition — red plus green makes yellow.

Geometrically, RGB is represented as a **Cartesian unit cube** with one axis per channel (R, G, B). The "main diagonal" from $(0,0,0)$ to $(255,255,255)$ is the **grayscale** line: every point on it has equal amounts of red, green, and blue ($r=g=b$).

RGB has three limitations for image processing. It is **device-dependent** — different cameras and monitors produce different RGB values for the same physical color. It is **non-intuitive** — it is hard to reason about a request like "make this more pink" in terms of R, G, and B changes. And it is **correlated** — changing the brightness of a pixel changes all three channels together. For these reasons, image processing often converts to a perceptual space (HSV, LAB) or a luminance-chrominance space (YCbCr, YUV) before doing serious work.

## CMYK: the subtractive model

CMYK (Cyan, Magenta, Yellow, Key/Black) is a **subtractive color model**, used in printing. It models the mixing of **pigments and ink**: pigments absorb (subtract) light, so white paper — which reflects all light — starts out bright, and adding ink removes wavelengths. Cyan absorbs red (reflecting green and blue), magenta absorbs green, and yellow absorbs blue.

Why is there a K channel? Theoretically, C+M+Y should produce black. In practice, mixing all three inks creates a muddy brown and uses expensive ink. Pure black ink (the "Key") is added for sharp text, deep blacks, and cost savings, since black ink is cheaper than three colored inks.

## HSL and HSV: perceptual coordinates

HSL/HSV is a **perceptual model**, used in color pickers, image editing, and human-computer interaction. Its purpose is to fix RGB's intuitiveness problem: if you are asked to "make this pixel a bit more pink," computing the required change in R, G, and B is hard. HSL/HSV solves this by decomposing a color into three perceptual axes:

- **Hue (H):** the "type" of color (red, orange, blue), measured in degrees ($0^\circ$ to $360^\circ$) around a color wheel. Red is 0°, green is 120°, blue is 240°.
- **Saturation (S):** the "purity" of the color. 100% is a vivid color; 0% is gray.
- **Lightness (L) / Value (V):** the brightness. 0% is black; 100% is white in HSL, or the full color in HSV.

The difference between the two variants is how Lightness and Value treat full saturation. In HSL, L=50% is the pure color and L=100% is white; in HSV, V=100% is the pure color. HSV is more common in computer vision, while HSL is more common in graphics tools.

The payoff for processing is illumination robustness. Suppose you want to detect a red car in an image that contains shadows: in RGB this is terrible, because the shadow changes all three RGB values at once. In HSV, the shadow only changes the Value (V) while the Hue (H) remains "red," which makes object detection much more robust to illumination changes.

## YCbCr and YUV: separating luminance from chrominance

YCbCr and YUV are **luminance-chrominance** spaces, used in JPEG compression and video (MPEG, TV broadcasting). They separate **luminance** (brightness, Y) from **chrominance** (color information, Cb/Cr or U/V). The rationale is that the human eye is more sensitive to brightness than to color, so the chrominance can be compressed more aggressively without visible quality loss. JPEG and video codecs subsample the chrominance — for example 4:2:0 keeps one Cb/Cr value per 4 pixels — while keeping full luminance resolution.

The conversion from RGB is:

$$Y = 0.299R + 0.587G + 0.114B$$
$$Cb = 0.564(B - Y)$$
$$Cr = 0.713(R - Y)$$

The Y formula is the **luminance** — the same weighted average used for grayscale conversion, reflecting the eye's greater sensitivity to green.

## CIELAB: the perceptually uniform space

CIELAB (LAB) is a **perceptually uniform** color space, used for color difference measurement and color-based segmentation. It was designed so that a fixed Euclidean distance in LAB corresponds to a fixed perceptual color difference, regardless of where in the color space you are. RGB and HSV are not perceptually uniform: a distance of 10 in the blue region looks different from a distance of 10 in the yellow region.

The three axes are:

- **L:** lightness (0 = black, 100 = white).
- **a:** the green-red axis (negative = green, positive = red).
- **b:** the blue-yellow axis (negative = blue, positive = yellow).

The practical use case follows directly from the uniformity: if you want to measure "how different are these two colors," or segment an image by color, LAB is the right space, because Euclidean distance in LAB is meaningful. RGB distance is not.

## Grayscale conversion: weighted luminance

Converting a color image to grayscale is not just `(R+G+B)/3`. The human eye is more sensitive to green light than to red or blue — a consequence of the relative density of cone cells — so we use a weighted average to calculate the luminance ($Y$):

$$ Y = 0.299R + 0.587G + 0.114B $$

The weight for green (0.587) is much higher than the weight for blue (0.114), directly reflecting that sensitivity. This is the same $Y$ used in YCbCr. A naive average `(R+G+B)/3` produces a grayscale image that looks "off": blues appear too bright and greens too dark.

## Choosing the right color space

The models above are complementary rather than competing — each was designed for a purpose, and the table below maps common tasks to the space that serves them best.

| Task | Recommended space | Why |
| :--- | :--- | :--- |
| Display / storage | RGB | Native to displays and most image formats |
| Color-based detection | HSV | Shadow/lighting changes only affect V, not H |
| Color difference measurement | LAB | Perceptually uniform — Euclidean distance is meaningful |
| Compression | YCbCr | Subsample chrominance (human eye is less sensitive to color detail) |
| Printing | CMYK | Subtractive model matches ink-on-paper physics |
| Grayscale conversion | RGB → Y | Weighted luminance reflects human perception |

## Key takeaways

Each model earns its place by solving one of the three problems — light, ink, or perception — and the conversion formulas tie them together. In brief:

1. **RGB** is additive (light), device-dependent, and non-intuitive for processing.
2. **CMYK** is subtractive (ink), used for printing.
3. **HSL/HSV** is perceptual — it separates hue, saturation, and brightness, and is best for illumination-robust color detection.
4. **YCbCr/YUV** separates luminance from chrominance — the basis of JPEG and video compression (chroma subsampling).
5. **LAB** is perceptually uniform — Euclidean distance is meaningful, making it best for color difference measurement and color-based segmentation.
6. Grayscale conversion uses the weighted luminance $Y = 0.299R + 0.587G + 0.114B$, reflecting the eye's green sensitivity — not a naive average.

## See also

- [[Image Processing Global Index]]
- [[What is a Digital Image]]
- [[The Color Image Processing Pipeline]]
- [[Image Representation Types]]
- [[Image File Formats]]
- [[Resolution and Bit Depth]]
- [[Point Processing Operations]]
