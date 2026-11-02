---
title: The Autoencoder
type: concept
aliases:
  - autoencoder
  - AE
  - The Autoencoder - Compression as Learning
  - compression as learning
tags:
  - autoencoders
  - generative-models
  - representation-learning
  - latent-space
  - unsupervised-learning
  - encoder-decoder
  - compression
sources:
  - "01. The Autoencoder — Compression as Learning"
created_index: 2
---

An **autoencoder** is a neural network trained to reconstruct its own input through a low-dimensional bottleneck: an encoder squeezes the input into a latent code, and a decoder expands that code back into an approximation of the original. The bottleneck is not an inconvenience — it is the mechanism that forces the network to learn the meaningful structure of the data, which is why the autoencoder is the foundation for VAEs, diffusion models, and many other generative architectures. This note covers the core mechanics, the compression-as-learning argument, the standard architecture, what the latent space reveals, the critical limitation that a trained autoencoder can reconstruct but cannot generate, and the classic variants (denoising, sparse, contractive). It assumes the standard neural-network toolkit ([[Artificial Neural Networks]]) and the general encoder-decoder pattern analyzed in [[Information Bottleneck and Latent Space]].

## The core idea

An **autoencoder** is a neural network trained to reconstruct its own input, through a bottleneck. It has two parts. An **encoder** $f_\phi$ maps the input $x$ to a low-dimensional latent representation $z = f_\phi(x)$, and a **decoder** $g_\theta$ maps the latent representation back to a reconstruction $\hat{x} = g_\theta(z)$. The network is trained to minimize the reconstruction error:

$$\mathcal{L} = \|x - g_\theta(f_\phi(x))\|^2$$

The bottleneck — the fact that $z$ is lower-dimensional than $x$ — is what makes this non-trivial. Without it, the network could just copy the input through; with it, the encoder must compress the input into a representation that preserves enough information for the decoder to reconstruct it.

This is the simplest possible instance of the encoder-decoder pattern behind [[Information Bottleneck and Latent Space]], and it is the foundation for VAEs ([[From Autoencoder to VAE]]), diffusion models, and many other generative architectures.

## Why compression forces learning

If the latent dimension is much smaller than the input dimension — say, compressing a 784-pixel MNIST digit into a 32-dimensional vector — the encoder cannot just memorize the input. It must learn the **meaningful structure** of the data: which combinations of pixels correspond to stroke direction, digit identity, thickness, style. Only by capturing these underlying factors can the decoder reconstruct the original from the compressed code.

This is the deep idea: **compression is learning.** To compress well, you must understand the data's structure. The autoencoder's latent space is a window into what the model has "understood" about the data.

A useful analogy: JPEG compression works because its designers understood that images are dominated by low-frequency spatial patterns (which DCT captures efficiently). An autoencoder *discovers* the equivalent structure from data, without a human designer specifying it. If you train an autoencoder on faces, its latent dimensions will correspond to pose, identity, expression, lighting — the "JPEG of faces," but learned automatically.

## Architecture

A standard autoencoder for images:

```text
Input (784) → [Encoder] → Latent (32) → [Decoder] → Reconstruction (784)
                  MLP or CNN              MLP or CNN (transpose)
```

The four components divide the labor:

- **Encoder:** typically a series of dense layers (for tabular data) or convolutional layers (for images) that progressively reduce dimensionality. For MNIST: 784 → 512 → 256 → 32.
- **Latent:** a single vector $z \in \mathbb{R}^k$, where $k$ is the latent dimension (a hyperparameter).
- **Decoder:** the mirror of the encoder, using dense or transposed-convolutional layers to expand the latent back to the input dimension. For MNIST: 32 → 256 → 512 → 784.
- **Loss:** mean squared error (MSE) between input and reconstruction, or binary cross-entropy if the input is normalized to $[0, 1]$.

Because the decoder mirrors the encoder, the one central hyperparameter is the latent dimension $k$: it fixes how much information can survive the bottleneck.

## What the latent space looks like

If you train an autoencoder on MNIST and visualize the latent space (via the dimensionality reduction tools t-SNE or UMAP — see [[t-SNE and UMAP]]), you find that the latent vectors cluster by digit class — even though the autoencoder was never given the labels. The compression forced the encoder to discover digit identity as a meaningful factor of variation, because identity is what most determines pixel values.

This is the autoencoder's superpower: **unsupervised structure discovery.** By training only on reconstruction, the model learns a representation that captures the data's intrinsic structure. This representation can then be used for downstream tasks (classification, clustering, visualization) without labels.

## The limitation: autoencoders cannot generate

Here is the critical problem: **a trained autoencoder can reconstruct, but it cannot generate.**

To generate a new example, you would sample a random latent vector $z \sim \mathcal{N}(0, I)$ and decode it: $\hat{x} = g_\theta(z)$. But the latent space of a trained autoencoder is **not** a nice Gaussian distribution. It is an arbitrary, irregular point cloud — some regions have many training examples (and decode to valid digits), other regions have none (and decode to garbage). Sampling uniformly from a Gaussian will mostly land in empty regions, producing garbage.

> [!warning] Reconstruction is not generation
> The decoder only behaves well on latent vectors near the encodings of training examples; a random sample from $\mathcal{N}(0, I)$ usually lands in an empty region and decodes to garbage. Generation requires the latent space itself to be regularized.

This is the problem that VAEs fix. The VAE adds a regularization term that forces the latent space to be close to a known distribution (Gaussian), so that random sampling produces valid examples — the step taken in [[From Autoencoder to VAE]].

## Variants

The vanilla objective — plain reconstruction through a bottleneck — is not the only option: denoising, sparse, and contractive autoencoders modify the objective to learn more robust or interpretable representations. The first two are developed in depth in [[Denoising and Sparse Autoencoders]].

### Denoising autoencoder

Train the autoencoder to reconstruct the *original* input from a *corrupted* version:

$$\mathcal{L} = \|x - g_\theta(f_\phi(\tilde{x}))\|^2$$

where $\tilde{x} = x + \epsilon$ is the input with noise added. This forces the encoder to learn robust features that survive corruption, rather than memorizing the input. Denoising autoencoders produce more meaningful latent spaces and are the conceptual precursor to diffusion models (which train a denoising objective at multiple noise levels — see [[The Forward Process]]).

### Sparse autoencoder

Add an L1 penalty on the latent activations:

$$\mathcal{L} = \|x - \hat{x}\|^2 + \lambda \|z\|_1$$

This forces the latent representation to be sparse — only a few dimensions active per input. Sparse autoencoders learn more interpretable features (each dimension tends to correspond to a specific, identifiable concept) and are used in interpretability research.

### Contractive autoencoder

Add a penalty on the **Jacobian** of the encoder — the derivative of the latent with respect to the input:

$$\mathcal{L} = \|x - \hat{x}\|^2 + \lambda \left\|\frac{\partial f_\phi(x)}{\partial x}\right\|_F^2$$

This forces the encoder to be locally insensitive to small input perturbations, producing a representation that captures only the directions of variation that matter. Contractive autoencoders are theoretically elegant but less commonly used in practice.

## What you should walk away with

The essentials in six points:

1. An autoencoder is an encoder-decoder trained to reconstruct its input through a low-dimensional bottleneck.
2. The bottleneck forces the encoder to learn the data's meaningful structure — compression is learning.
3. The latent space captures intrinsic factors of variation (e.g., digit identity for MNIST), even without labels.
4. The critical limitation: autoencoders cannot generate new examples, because their latent space is not a nice distribution — random sampling produces garbage.
5. Variants (denoising, sparse, contractive) modify the objective to learn more robust or interpretable representations.
6. The generation problem is fixed by VAEs, which regularize the latent space to be Gaussian.

## See also

- [[12 - Generative Models/Chapter Overview|Chapter Overview]] — where autoencoders sit among the generative families
- [[Denoising and Sparse Autoencoders]] — the two constrained variants in depth
- [[From Autoencoder to VAE]] — regularizing the latent space so random sampling works
- [[The Forward Process]] — diffusion's denoising objective at many noise levels
- [[Score-Based and Latent Diffusion]] — where the denoising idea leads
- [[Information Bottleneck and Latent Space]] — the general encoder-decoder pattern
- [[t-SNE and UMAP]] — visualizing the learned latent space
