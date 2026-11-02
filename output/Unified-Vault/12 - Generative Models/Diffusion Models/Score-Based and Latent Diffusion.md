---
title: Score-Based and Latent Diffusion
type: concept
aliases: [Score-based diffusion, Latent diffusion, Latent diffusion model, LDM, Score-based generative modeling]
tags: [diffusion, generative-models, score-based-models, latent-diffusion, text-to-image, classifier-free-guidance]
sources: ["03. Score-Based and Latent Diffusion"]
created_index: 4
---

Two innovations turned diffusion models from a working proof of concept into the dominant generative architecture: the score-based formulation, which unified diffusion theory with continuous-time stochastic processes, and latent diffusion, which moved the entire procedure into a compressed latent space and made high-resolution generation computationally practical. Together with text conditioning and classifier-free guidance, these ideas underpin modern text-to-image systems such as Stable Diffusion. This note builds on [[The Forward Process]] and [[The Reverse Process]] — it assumes the noise-prediction mechanics covered there — and treats the score view of the denoiser, the latent-space trick and its VAE underpinnings, the text-to-image architecture, and the current state of the art across modalities.

> [!info] TL;DR
> Score-based theory shows that the diffusion denoiser approximates the score of the data distribution, unifying discrete DDPM with continuous-time sampling and enabling fast samplers. Latent diffusion runs the whole process in a VAE-compressed latent space (~48× cheaper), which is what lets Stable Diffusion run on a single consumer GPU. Text-to-image adds cross-attention to text embeddings plus classifier-free guidance for prompt fidelity.

## Two key innovations that made diffusion practical

The original DDPM (Ho et al. 2020) demonstrated that diffusion works, but two subsequent innovations made it the dominant generative architecture: **score-based formulation** (unified the theory) and **latent diffusion** (made it computationally practical for high-resolution images). The sections that follow treat each in turn, then show how they come together with conditioning in text-to-image generation and where the field stands today.

## Score-based diffusion: the deeper theory

The noise-prediction objective $\|\epsilon - \epsilon_\theta(x_t, t)\|^2$ used to train the reverse process is equivalent to training the network to approximate the **score** of the data distribution at noise level $t$:

$$s_\theta(x_t, t) \approx \nabla_{x_t} \log q_t(x_t)$$

The score is the gradient of the log-density — it points in the direction of increasing probability density. By following the score (via Langevin dynamics or probability flow ODEs), you can sample from the distribution.

**Song et al. (2021)** unified the discrete-step DDPM with continuous-time diffusion (score-based generative models, SDE-based). The unified view:

- The forward process is a stochastic differential equation (SDE) that adds noise.
- The reverse process is the reverse SDE, which requires the score.
- The score is approximated by a neural network trained on the noise-prediction objective.

This unification is theoretically elegant and enabled several practical advances:

- **Continuous-time sampling** (any number of steps, not just the training $T$).
- **Deterministic sampling** (probability flow ODE — no stochasticity, faster).
- **Better samplers** (DPM-Solver, EDM) that achieve high quality in 10-20 steps.

You do not need the full SDE theory to use diffusion models, but it underlies the modern samplers that make diffusion fast.

## Latent diffusion: the computational breakthrough

The original DDPM operates in **pixel space** — the U-Net processes full-resolution images (e.g., $256 \times 256 \times 3$). This is expensive: each of the 1000 denoising steps requires a full U-Net forward pass at full resolution. Generating a single $256 \times 256$ image takes minutes on a high-end GPU.

**Latent diffusion** (Rombach et al. 2022 — the Stable Diffusion paper) moves the diffusion process into a **compressed latent space**, using a VAE-like encoder as the compression stage:

1. **Train a VAE** (see [[From Autoencoder to VAE]]) to compress images into a low-dimensional latent space. For $512 \times 512 \times 3$ images, the VAE encoder produces $64 \times 64 \times 4$ latent vectors — a 48× compression with minimal perceptual loss.
2. **Train the diffusion U-Net in latent space** — denoise $64 \times 64 \times 4$ latents instead of $512 \times 512 \times 3$ pixels. This is 48× cheaper per step.
3. **Generate by**: sample noise in latent space, denoise with the U-Net, decode the final latent back to pixel space with the VAE decoder.

This reduces the computational cost by ~48×, making high-resolution diffusion practical on consumer GPUs. **Stable Diffusion is a latent diffusion model** — this is why it can run on a single GPU while pixel-space diffusion models require clusters.

### Why latent space works

The VAE's latent space captures the **perceptually meaningful** structure of the image while throwing away high-frequency noise that is not semantically important. Diffusing in this space is sufficient because the latent already encodes the image's content; the VAE decoder reconstructs the details.

This is the same insight as the autoencoder's bottleneck (see [[The Autoencoder]]) — compression forces the representation to capture meaning, and operating in the compressed space is cheaper.

## Conditional generation: text-to-image

The most visible application of diffusion is **text-to-image generation** (Stable Diffusion, DALL-E, Midjourney). The architecture:

1. **Text encoder:** a Transformer (CLIP or T5) encodes the text prompt into a sequence of embeddings.
2. **Latent diffusion U-Net:** the denoiser, with **cross-attention** to the text embeddings at each layer. This lets the denoiser "see" the text while denoising, guiding generation toward the described content.
3. **VAE decoder:** decodes the final latent back to pixel space.

The cross-attention is the key mechanism: at each denoising step, the U-Net attends to the text embeddings, so the denoising is guided by the text. This is structurally identical to the Transformer decoder's cross-attention to the encoder (see [[Transformer Decoder Block]]) — the text plays the role of the encoder output.

### Classifier-free guidance

A critical technique for text-to-image quality is **classifier-free guidance** (Ho and Salimans 2022). At inference, the model is run twice — once with the text condition, once without — and the final prediction extrapolates away from the unconditional:

$$\hat{\epsilon}_{guided} = \epsilon_\theta(x_t, t, \emptyset) + w \cdot (\epsilon_\theta(x_t, t, c) - \epsilon_\theta(x_t, t, \emptyset))$$

where $c$ is the text condition, $\emptyset$ is the null condition, and $w$ is the guidance scale (typically 7-10). This amplifies the text's influence, producing images that more closely match the prompt (at the cost of some diversity). Without guidance, text-to-image models produce generic, weakly-aligned images; with guidance, they produce the striking, prompt-faithful images that made Stable Diffusion famous.

> [!warning] Guidance trades diversity for prompt fidelity
> The same extrapolation that sharpens alignment with the prompt narrows the variety of outputs — a higher guidance scale buys faithfulness at the cost of some diversity.

## The current state of the art

As of 2024-2025, diffusion models are the state of the art for:

- **Image generation:** Stable Diffusion 3, DALL-E 3, Midjourney v6, Flux.
- **Video generation:** Sora, Runway Gen-3, Kling.
- **Audio generation:** AudioLDM, Stable Audio.
- **3D generation:** DreamFusion, Magic3D (text-to-3D).
- **Molecular generation:** Diffusion-based drug design.

The field is moving fast, with active research on:

- **Faster sampling:** consistency models, rectified flow (1-step generation).
- **Better architectures:** DiT (Diffusion Transformer — replaces U-Net with a Transformer), used in Sora and SD3.
- **Control:** ControlNet, IP-Adapter (precise spatial/structural control).
- **Editing:** instruction-based editing, inpainting, outpainting.

Diffusion has unified generative AI across modalities, just as Transformers unified sequence modeling. The combination (diffusion for generation, Transformers for understanding) is the foundation of modern AI. The Diffusion Transformer line is covered in [[DiT and FLUX]], and the CLIP text encoder in [[CLIP]].

## Summary

**Score-based formulation** unified diffusion theory: the denoiser approximates the score (gradient of log-density), and generation follows the score via reverse SDE — this enabled continuous-time sampling and fast samplers. **Latent diffusion** moves the process into a VAE-compressed latent space, reducing computational cost by ~48× and making high-resolution diffusion practical; Stable Diffusion is a latent diffusion model. **Text-to-image** uses cross-attention from the U-Net to text embeddings, guiding denoising by the text prompt, and classifier-free guidance amplifies the text's influence, producing prompt-faithful images. Diffusion is the state of the art for image, video, audio, 3D, and molecular generation — it has unified generative AI across modalities — and the combination of diffusion (for generation) and Transformers (for understanding) is the foundation of modern AI.

With diffusion, the four major families of generative models are complete: autoencoders (compression), VAEs (probabilistic generation), GANs (adversarial generation), and diffusion (iterative denoising). In the source course's reading order, the next steps after generative models are the expansion phases: evaluation metrics, math foundations, classical ML, and de-duplication.

## See also

- [[12 - Generative Models/Chapter Overview|Chapter Overview]] — orientation for the generative-models area.
- [[The Forward Process]] — the fixed noising process that latent diffusion runs in compressed space.
- [[The Reverse Process]] — the noise-prediction denoiser whose score-based interpretation is developed here.
- [[From Autoencoder to VAE]] — the VAE that supplies the compressed latent space.
- [[The Autoencoder]] — the bottleneck insight behind compressing before generating.
- [[DiT and FLUX]] — the Diffusion Transformer line that replaces the U-Net.
- [[CLIP]] — the contrastive text encoder that conditions text-to-image diffusion.
- [[Transformer Decoder Block]] — the cross-attention mechanism the U-Net reuses for text conditioning.
