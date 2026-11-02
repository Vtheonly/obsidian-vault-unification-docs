---
title: Chapter Overview
type: overview
aliases:
  - "00 - Generative Models: Chapter Overview"
  - "Generative Models: Chapter Overview"
  - Generative Models area overview
  - Generative Models MOC
tags:
  - generative-models
  - overview
  - autoencoders
  - variational-autoencoder
  - gans
  - diffusion
  - latent-space
sources:
  - "00 - Generative Models: Chapter Overview"
created_index: 3
---

This note is the orientation for the Generative Models area: why the area exists, what its notes cover, and the order to read them in. The area tours the four major families of generative models — autoencoders, variational autoencoders, GANs, and diffusion models — arranged as a progression in which each family fixes the central limitation of the one before it. Skim this note top to bottom before diving into any content note, and return whenever you lose the thread.

> [!info] Where this area sits
> **Prerequisites:** [[Artificial Neural Networks]] for the neural-network basics; [[Attention and Transformers MOC]] for the text encoders used in modern generative models; and [[Information Bottleneck and Latent Space]], the conceptual foundation.
> **Connections:** all of these models are encoder-decoder architectures ([[Information Bottleneck and Latent Space]]) specialized for generation rather than classification.

## Why this area exists

Most of what you study in deep learning is **discriminative** — models that predict a label or value from an input. A CNN classifies an image; a Transformer translates a sentence; an MLP regresses a price. These models answer the question: "given input $X$, what is $Y$?"

**Generative** models answer a different question: "given a training set of examples, how can I generate *new* examples that look like they came from the same distribution?" They learn the data distribution $p(X)$ itself, rather than $p(Y|X)$.

This capability underpins modern AI's most visible applications:

- **Image generation:** DALL-E, Stable Diffusion, Midjourney
- **Text generation:** GPT, Claude, LLaMA
- **Code generation:** Codex, Copilot
- **Audio synthesis:** music generation, voice cloning
- **Drug discovery:** generating novel molecular structures
- **Data augmentation:** generating synthetic training data

This area covers the four major families of generative models: **autoencoders** (reconstruction), **variational autoencoders** (probabilistic generation), **GANs** (adversarial generation), and **diffusion models** (iterative denoising). Text generation belongs to the decoder-only Transformer lineage ([[Decoder-Only Architecture]]); this area focuses on the *other* modalities, especially images.

## The reading order

The area consists of this overview plus eleven content notes, organized into four families. The order below is the intended reading order: each family assumes the previous one, and within a family each note assumes the notes before it.

| Family | Notes | Core idea |
|---|---|---|
| Autoencoders | [[The Autoencoder]], [[Denoising and Sparse Autoencoders]] | Reconstruction — compression as learning |
| Variational autoencoders | [[From Autoencoder to VAE]], [[The Reparameterization Trick]], [[The KL Divergence Loss]] | Probabilistic generation — a samplable latent space |
| GANs | [[The Adversarial Game]], [[Training Dynamics and Mode Collapse]], [[Wasserstein GANs and Modern Variants]] | Adversarial generation — sharp, realistic samples |
| Diffusion models | [[The Forward Process]], [[The Reverse Process]], [[Score-Based and Latent Diffusion]] | Iterative denoising — stable training, state-of-the-art quality |

### Autoencoders

The starting point: a network trained to reconstruct its own input through a low-dimensional bottleneck, which turns compression into learning. The family's two notes give the core mechanics and then the constrained variants that keep the representation meaningful.

1. [[The Autoencoder]] — the encoder-decoder bottleneck: why forcing reconstruction through a low-dimensional code makes the network learn the data's structure, and what the latent space does and does not give you.
2. [[Denoising and Sparse Autoencoders]] — the two variants that stop the network from copying instead of learning: denoising (reconstruct the clean input from a corrupted one) and sparsity (an L1 penalty that makes latent dimensions interpretable), with the denoising idea pointing straight ahead to diffusion.

### Variational autoencoders

The first genuinely generative family: the latent code becomes a learned probability distribution, so sampling a random vector and decoding it produces a valid new example. Three notes assemble the machinery.

1. [[From Autoencoder to VAE]] — the architectural change that turns a deterministic compressor into a generative model, and the two-part objective that trains it.
2. [[The Reparameterization Trick]] — the rewrite that makes the sampled latent differentiable, so backpropagation can reach the encoder.
3. [[The KL Divergence Loss]] — the regularizer that pulls the latent distribution toward the prior, its closed Gaussian form, and the blurriness it costs.

### GANs

The adversarial family: two networks trained against each other — a generator that turns noise into fake samples and a discriminator that judges them — yielding sharp, realistic samples at the price of notoriously difficult training.

1. [[The Adversarial Game]] — the minimax contest between generator and discriminator, the Nash equilibrium it converges to in theory, and why the adversarial loss yields sharper samples than reconstruction-based training.
2. [[Training Dynamics and Mode Collapse]] — the characteristic failure modes of adversarial training (mode collapse, instability, hard evaluation) and the standard fixes.
3. [[Wasserstein GANs and Modern Variants]] — replacing the loss geometry with the Wasserstein distance, and the variant wave (StyleGAN, BigGAN, CycleGAN, pix2pix) it stabilized.

### Diffusion models

The destination of the progression: the model learns to reverse a noise-adding process, and generation is the iterative removal of noise — a stable supervised objective that currently defines the state of the art.

1. [[The Forward Process]] — the fixed, unlearned corruption that gradually turns a clean image into pure noise, and the closed form that makes training cheap.
2. [[The Reverse Process]] — the learned denoising chain, the DDPM noise-prediction objective, the U-Net denoiser, and the sampling loop that generates images.
3. [[Score-Based and Latent Diffusion]] — the score-based reformulation that unified the theory, the latent-space trick that made high-resolution generation practical, and the text-to-image systems it underpins.

## The conceptual arc

The area follows a progression: each family fixes a limitation of the previous one.

1. **Autoencoders** can reconstruct their input but cannot generate *new* examples — the latent space is unstructured, so sampling a random latent vector usually produces garbage.
2. **VAEs** fix this by forcing the latent space to be a known distribution (Gaussian). You can sample a random latent vector and decode it into a valid new example. But VAE samples are often blurry — the Gaussian assumption and KL regularization smooth out high-frequency detail.
3. **GANs** fix the blurriness by replacing the reconstruction loss with an adversarial game. A discriminator network tries to distinguish real from generated; the generator tries to fool it. GAN samples are sharp and realistic. But GANs are notoriously hard to train — mode collapse (generating only a few types of examples) and training instability are persistent problems.
4. **Diffusion models** fix the training instability by replacing the adversarial game with a gradual denoising process. The model learns to reverse a noise-adding process, and generation is the iterative removal of noise. Diffusion models are stable to train, produce state-of-the-art quality, and underlie DALL-E 3, Stable Diffusion, and Sora. They are the current state of the art for image generation.

By the end of the area, you will understand why each family exists, what it fixes, and what it cannot do — and you will be ready to read modern papers in generative AI.

## See also

- [[Attention and Transformers MOC]] — decoder-only models for text generation, and the text encoders used for conditional generation
- [[Information Bottleneck and Latent Space]] — the encoder-decoder paradigm these models instantiate
- [[Artificial Neural Networks]] — the neural-network prerequisite this area builds on
- [[Decoder-Only Architecture]] — the other half of the generative family tree: text
- [[CLIP]] — the contrastive text encoder that conditions modern text-to-image diffusion
- [[DiT and FLUX]] — where diffusion went next: Transformer backbones and flow matching for image generation
