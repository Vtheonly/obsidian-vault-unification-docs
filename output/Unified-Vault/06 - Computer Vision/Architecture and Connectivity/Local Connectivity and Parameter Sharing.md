---
title: Local Connectivity and Parameter Sharing
type: concept
aliases:
  - Local Connectivity
  - Parameter Sharing
  - Weight Sharing
  - Sparse Interactions
  - Sparse Connectivity
tags:
  - computer-vision
  - cnn
  - local-connectivity
  - parameter-sharing
  - weight-sharing
  - translation-invariance
  - mlp
  - parameter-counting
  - deep-learning
sources:
  - "01. Local Connectivity and Parameter Sharing"
created_index: 5
---

To understand the genius of convolutional architecture, we must quantify exactly what breaks if we attempt to use a standard fully connected multi-layer perceptron (MLP) for computer vision. This is not a hypothetical exercise — understanding the failure mode of the MLP is what makes the CNN's solution so elegant and necessary. Convolutional networks structurally resolve the MLP's parameter catastrophe by strictly obeying two mathematical visual constraints: **local connectivity** and **parameter sharing**; this note quantifies both, and shows how the whole CNN lineage — from VGG to ResNet to EfficientNet, surveyed in [[06 - Computer Vision/Architecture and Connectivity/Evolution of CNN Architectures|Evolution of CNN Architectures]] — builds on these two foundations, as previewed in [[CNN Course Overview]].

## The MLP catastrophe: why fully connected networks fail on images

If you flatten a moderately small $200 \times 200 \times 3$ RGB image into a 1-dimensional array to feed it into a standard MLP containing a highly conservative first hidden layer of just 1,000 neurons, you encounter mathematically disastrous consequences. The input shape is linearly $200 \times 200 \times 3 = 120,000$ values. Connecting that to 1,000 dense neurons requires **120,000,000 parameters** globally mapped purely for the very first layer. This explicitly guarantees instantaneous destructive overfitting and effectively exhausts onboard VRAM.

But the parameter explosion is only half of the problem. The other, equally devastating issue is the **loss of spatial structure**. When you flatten a 2D image into a 1D line, you destroy the spatial relationships between pixels. A pixel representing an eye is no longer mathematically "next to" the other pixels of the eye — it is simply entry #47,832 in a long, unstructured vector. The network has no way of knowing that pixels 47,832 through 47,840 form a coherent visual feature, because in a 1D array, proximity is meaningless.

These two problems are the fundamental reasons why MLPs are architecturally incapable of scaling to real-world image tasks. The **parameter explosion** makes the network computationally impossible to train and guarantees instant overfitting: 120 million parameters for just the first layer means the model has far more capacity than any reasonable training dataset can constrain, leading to memorization rather than generalization. The **loss of spatial structure** obliterates the 2D topology of the image — which pixels are adjacent, which form edges, which form corners — is entirely obliterated by the flattening operation, destroying exactly the information that vision depends on. (The flattening step itself, and where it *is* legitimately used at the end of a CNN, is the subject of [[The Fully Connected Layer and Flattening]].)

## Local connectivity (sparse interactions)

In an MLP, absolutely every single neuron is densely wired directly to every individual raw input pixel simultaneously. This means every neuron "sees" the entire image at once. While this gives each neuron maximum information, it is astronomically wasteful because most of those connections carry no useful signal.

The CNN alteration is strict locality: a specific neuron embedded deep in a CNN is rigidly deliberately completely locally connected — exclusively only to a strictly small, localized matrix region of the active topological input map (determined universally by the selected filter block size, e.g., a $3 \times 3$ filter). Instead of seeing the entire $200 \times 200$ image, each neuron sees only a tiny $3 \times 3$ patch — 9 pixels instead of 120,000.

Why does this work conceptually? In standard visual data, local configurations of nearby pixels strongly correlate and thereby generate meaningful edges and corners. Conversely, a single specific pixel stationed in the absolute top-left holds intrinsically zero reliable relationship with a pixel in the bottom-right corner. The statistical structure of natural images is inherently local — edges, corners, and textures are defined by the relationships between nearby pixels, not distant ones.

This is not just an empirical observation; it is a fundamental property of the physics of images. An edge exists because adjacent pixels have different intensities. A corner exists because edges meet at a specific local configuration. Color gradients exist because nearby pixels transition smoothly. None of these features depend on pixels that are far away. Local connectivity exploits this spatial reality by restricting each neuron's receptive field to the region where useful correlations actually exist (how those fields grow as layers stack is treated in [[Receptive Fields and 1x1 Convolutions]]).

## Parameter sharing (weight sharing)

In an MLP connection schema, every single connection requires its own distinctly unique weight. If neuron A connects to pixel (0,0), that connection has weight $w_1$. If neuron B also connects to pixel (0,0), that connection has weight $w_2$ — a completely different parameter. Every connection is unique.

Inside a convolutional network, the exact same $3 \times 3$ filter applies the identical $9$ parameters across every pixel of the input. The filter that detects a horizontal edge at the top-left corner of the image uses the exact same 9 weights as it slides across to detect a horizontal edge at the bottom-right corner.

Why it works: if detecting a horizontal edge works at the top left, those identical 9 weights will detect a horizontal edge at the bottom right. This is the principle of **translation invariance** — useful features are useful regardless of where they appear in the image. A horizontal edge is a horizontal edge whether it is at position (5, 5) or position (150, 180). There is no reason to learn 120 million different ways to detect the same pattern at different locations when a single, shared set of 9 weights can do the job everywhere.

> [!tip] Terminology: translation invariance
> Because the same filter scans the entire image, a CNN can detect a feature (like a cat's ear) regardless of where it appears in the frame. This is called **translation invariance**, and it is a fundamental reason why CNNs dominate computer vision. "Translation" in this context means spatial shifting — moving the feature to a different location in the image. "Invariance" means the detection result does not change. A cat's ear detected at the top-left produces the same activation pattern as the same ear at the bottom-right, because the identical filter weights are applied at both locations.

The result: instead of 120 million parameters, a $3 \times 3$ filter on an RGB image requires exactly $(3 \times 3 \times 3) + 1 (bias) = 28$ parameters. This drastic reduction makes deep networks possible.

## The parameter crash: the arithmetic

Let us trace the exact parameter count for both architectures side by side:

| Architecture | Connection Type | First Layer Parameters |
|---|---|---|
| MLP (Fully Connected) | Every neuron → every pixel | $120,000 \times 1,000 = 120,000,000$ |
| CNN (3x3 Filter on RGB) | Shared 3x3x3 filter + 1 bias | $(3 \times 3 \times 3) + 1 = 28$ per filter |

If we use 32 such filters (a very common first-layer configuration), the total CNN parameters become $32 \times 28 = 896$ — compared to 120,000,000 for the MLP. That is a reduction factor of over 130,000×. This is not a modest improvement; it is the difference between a network that is impossible to train and one that trains efficiently on a consumer GPU.

## How the two principles work together

Local connectivity and parameter sharing are not independent design choices — they are deeply interconnected and mutually reinforcing. Local connectivity alone (without parameter sharing) would reduce the number of connections per neuron, but each connection would still require its own unique weight. Parameter sharing alone (without local connectivity) would be meaningless — you cannot share weights across a fully connected layer because each neuron is connected to the entire image, not a local patch.

The power of CNNs comes from combining both: each neuron looks at only a small local region (local connectivity), and the same set of weights is used to examine every local region across the entire image (parameter sharing). Together, they create an architecture that is both computationally efficient and inherently designed to detect spatially invariant features.

> [!info] The bigger picture
> These two principles — local connectivity and parameter sharing — are the mathematical foundation that makes deep vision networks possible. Without them, the parameter count would be so astronomical that no amount of data or compute could train the network effectively. Every subsequent architectural innovation in CNNs (from VGG to ResNet to EfficientNet) builds on top of these two fundamental constraints.

## See also

- [[CNN Course Overview]]
- [[CNN Mastery Roadmap]]
- [[The Convolution Operation]]
- [[From Basic Convolution to Learned Weights]]
- [[06 - Computer Vision/CNN Foundations and Philosophy/Core Architecture and Philosophy|Core Architecture and Philosophy]]
- [[Processing 3D Volumes, Depth Summation, and Biases]]
- [[Hierarchical Feature Extraction]]
- [[The Fully Connected Layer and Flattening]]
- [[Receptive Fields and 1x1 Convolutions]]
- [[06 - Computer Vision/Architecture and Connectivity/Evolution of CNN Architectures|Evolution of CNN Architectures]]
- [[06 - Computer Vision/Architecture and Connectivity/VGG16 Architecture Deep Dive|VGG16 Architecture Deep Dive]]
