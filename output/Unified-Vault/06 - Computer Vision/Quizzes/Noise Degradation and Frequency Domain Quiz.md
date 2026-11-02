---
title: Noise Degradation and Frequency Domain Quiz
type: example
aliases:
  - Noise and Degradation Quiz
  - Frequency Domain Quiz
  - Noise and Frequency Domain Quiz
tags:
  - computer-vision
  - image-processing
  - quiz
  - practice
  - noise
  - image-degradation
  - frequency-domain
  - image-quality-metrics
  - spatial-filtering
sources:
  - Q1
created_index: 61
---

This quiz drills the two foundational blocks of image restoration: the noise and degradation models that corrupt an image, and the split between the spatial domain and the frequency domain in which filtering can be performed. Its thirty questions cover the three classical noise models (additive Gaussian, impulsive salt-and-pepper, and multiplicative speckle), the MSE and PSNR quality metrics, and the Fourier transform's promise that convolution in one domain becomes element-wise multiplication in the other. The material synthesizes the noise models of [[Image Degradation and Noise Models]] with the two-domain view of [[Introduction to the Frequency Domain]]; the full area map is in [[Image Processing Global Index]]. Answers are folded into callouts — commit to an answer before unfolding, then check the reasoning.

## True or false

Ten statements on noise models, noise removal, and the two filtering domains open the quiz. Most of the false ones swap a key word — a domain, a filter name, or a cause — so read each statement at full attention before unfolding the answer.

### Noise models and their properties

Four statements about what digital noise is and how the three classical models behave.

> [!question] Digital noise is a natural part of the scene being photographed and is not considered an artifact.
>> [!success]- Answer
>> False

> [!question] Additive noise is typically modeled using a Gaussian distribution with a mean of zero.
>> [!success]- Answer
>> True

> [!question] Multiplicative (Speckle) noise is more visible in the brighter regions of an image.
>> [!success]- Answer
>> True

> [!question] Thermal noise in electronic sensors typically results in Impulsive (Salt-and-Pepper) noise.
>> [!success]- Answer
>> False

### Noise removal and quality

Two statements connect noise types to the filters that remove them — the median of [[Non-Linear Smoothing Filters]] — and to the metric that scores the restoration.

> [!question] Salt-and-pepper noise is best removed using an averaging (mean) filter.
>> [!success]- Answer
>> False

> [!question] A higher Peak Signal-to-Noise Ratio (PSNR) generally indicates better image quality.
>> [!success]- Answer
>> True

### Spatial versus frequency domain

Four statements test which operations belong to which domain, and what the frequency view of [[The Fourier Transform]] is actually good for.

> [!question] In the spatial domain, filtering is performed by modifying the frequency coefficients of the image.
>> [!success]- Answer
>> False

> [!question] Convolution in the spatial domain is mathematically equivalent to element-wise multiplication in the frequency domain.
>> [!success]- Answer
>> True

> [!question] The frequency domain provides a global perspective of the image, making it useful for removing periodic noise.
>> [!success]- Answer
>> True

> [!question] The Nagao filter is an example of a frequency domain filter.
>> [!success]- Answer
>> False

## Multiple choice

Eleven items with four options each; the wrong options are drawn from the neighboring concepts — the wrong domain, the wrong noise model, the wrong metric — so each choice rehearses a distinction rather than a memory. They move from noise models and metrics to the mechanics of the two domains.

### Noise models and metrics

Identifying models by formula, cause, and habitat, plus the fidelity metrics of [[Image Quality Metrics]].

> [!question] Which noise model is described by the formula `IB(i,j) = IP(i,j) + B(i,j)`?
> a) Multiplicative Noise
> b) Impulsive Noise
> c) Additive Noise
> d) Quantization Noise
>> [!success]- Answer
>> c) Additive Noise

> [!question] What is the primary cause of Impulsive (Salt-and-Pepper) noise?
> a) Thermal fluctuations
> b) Sensor defects or transmission errors
> c) Coherent imaging systems
> d) Lens distortion
>> [!success]- Answer
>> b) Sensor defects or transmission errors

> [!question] Which metric measures the average squared difference between the original and the degraded pixel values?
> a) PSNR
> b) MAE
> c) MSE
> d) SNR
>> [!success]- Answer
>> c) MSE

> [!question] In which type of imaging is Speckle (Multiplicative) noise most common?
> a) Standard digital photography
> b) Ultrasound and Radar
> c) Scanned documents
> d) Thermal imaging
>> [!success]- Answer
>> b) Ultrasound and Radar

> [!question] What determines the intensity of Gaussian noise in the additive model?
> a) The mean
> b) The standard deviation (sigma)
> c) The image brightness
> d) The sensor size
>> [!success]- Answer
>> b) The standard deviation (sigma)

### Domains and filtering

The transform, its use, and the operational difference between the domains — the territory of [[Frequency Domain Filtering]].

> [!question] Which domain represents an image as a sum of sine and cosine functions?
> a) Spatial Domain
> b) Frequency Domain
> c) Time Domain
> d) Color Domain
>> [!success]- Answer
>> b) Frequency Domain

> [!question] What tool is used to transform an image from the spatial domain to the frequency domain?
> a) Convolution Matrix
> b) Fourier Transform
> c) Gaussian Kernel
> d) Histogram Equalization
>> [!success]- Answer
>> b) Fourier Transform

> [!question] Which filter is explicitly mentioned as being suitable for removing Impulsive noise?
> a) Mean filter
> b) Gaussian filter
> c) Median filter
> d) Low-pass filter
>> [!success]- Answer
>> c) Median filter

> [!question] How is spatial filtering typically implemented?
> a) By sliding a filter mask (kernel) across the image
> b) By multiplying the image by a scalar
> c) By inverting the colors
> d) By applying a Fourier Transform
>> [!success]- Answer
>> a) By sliding a filter mask (kernel) across the image

> [!question] Which of the following is an advantage of the frequency domain?
> a) It allows for direct manipulation of individual pixels.
> b) It is computationally cheaper for very small kernels.
> c) Complex convolutions become simple multiplications.
> d) It does not require a transform step.
>> [!success]- Answer
>> c) Complex convolutions become simple multiplications.

## Matching

Ten matching questions pair each concept with its formula, cause, definition, or domain; together they form a compact summary sheet of the whole topic. Match each group independently, then verify — several distractor pairs differ by a single word.

### Noise models and metrics

Formulas, causes, metric descriptions, and the visual signature of each noise type.

> [!question] Match the noise model with its mathematical formula.
>> [!example] Group A
>> a) Additive Noise
>> b) Multiplicative Noise
>> c) Impulsive Noise
>
>> [!example] Group B
>> n) `IB = IP * B`
>> o) `IB = 0` or `255`
>> p) `IB = IP + B`
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

> [!question] Match the noise type with its common cause.
>> [!example] Group A
>> a) Gaussian Noise
>> b) Salt-and-Pepper Noise
>> c) Speckle Noise
>
>> [!example] Group B
>> n) Sensor defects or dead pixels.
>> o) Coherent imaging (Radar, Sonar).
>> p) Thermal noise in electronics.
>
>> [!success]- Answer
>> a) -> p)
>> b) -> n)
>> c) -> o)

> [!question] Match the metric with its description.
>> [!example] Group A
>> a) MSE
>> b) PSNR
>
>> [!example] Group B
>> n) Logarithmic metric where higher values indicate better quality.
>> o) Average squared difference between pixel values.
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

> [!question] Match the noise visual appearance with the noise type.
>> [!example] Group A
>> a) Fine, grain-like texture
>> b) Sparse black and white dots
>> c) Noise proportional to brightness
>
>> [!example] Group B
>> n) Multiplicative (Speckle)
>> o) Additive (Gaussian)
>> p) Impulsive (Salt-and-Pepper)
>
>> [!success]- Answer
>> a) -> o)
>> b) -> p)
>> c) -> n)

### Domains, filters, and terminology

Domain definitions, filter domiciles, operational mechanisms, and core vocabulary.

> [!question] Match the domain with its definition.
>> [!example] Group A
>> a) Spatial Domain
>> b) Frequency Domain
>
>> [!example] Group B
>> n) Represents the rate at which pixel values change.
>> o) Represents the image plane based on coordinates (x,y).
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

> [!question] Match the filter type with its domain of application.
>> [!example] Group A
>> a) Mean Filter
>> b) Low-pass Filter (via Spectrum)
>
>> [!example] Group B
>> n) Frequency Domain.
>> o) Spatial Domain.
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

> [!question] Match the operational mechanism with the domain.
>> [!example] Group A
>> a) Convolution
>> b) Element-wise Multiplication
>
>> [!example] Group B
>> n) Primary operation for filtering in the Frequency Domain.
>> o) Primary operation for filtering in the Spatial Domain.
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

> [!question] Match the terminology with the concept.
>> [!example] Group A
>> a) Kernel
>> b) Fourier Transform
>> c) Digital Noise
>
>> [!example] Group B
>> n) Unwanted random variations in brightness/color.
>> o) Decomposes image into sine and cosine functions.
>> p) A filter mask used in spatial processing.
>
>> [!success]- Answer
>> a) -> p)
>> b) -> o)
>> c) -> n)

> [!question] Match the specific spatial filter with its category.
>> [!example] Group A
>> a) Median Filter
>> b) Mean Filter
>
>> [!example] Group B
>> n) Rank-order filter.
>> o) Linear/Smoothing filter.
>
>> [!success]- Answer
>> a) -> n)
>> b) -> o)

> [!question] Match the advantage with the domain.
>> [!example] Group A
>> a) Intuitive and efficient for small kernels.
>> b) Powerful for removing periodic noise.
>
>> [!example] Group B
>> n) Frequency Domain.
>> o) Spatial Domain.
>
>> [!success]- Answer
>> a) -> o)
>> b) -> n)

## See also

- [[Image Processing Global Index]]
- [[Image Degradation and Noise Models]]
- [[Image Quality Metrics]]
- [[Introduction to the Frequency Domain]]
- [[The Fourier Transform]]
- [[Frequency Domain Filtering]]
- [[The Mechanics of Spatial Filtering]]
- [[Linear Smoothing Filters]]
- [[Non-Linear Smoothing Filters]]
- [[Image Processing Comprehensive Quiz]]
- [[Image Fundamentals and Histograms Quiz]]
- [[Spatial Filtering and Convolution Quiz]]
