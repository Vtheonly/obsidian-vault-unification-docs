---
title: Training Dynamics and Mode Collapse
type: concept
aliases: ["Mode Collapse", "GAN Training Instability", "GAN Failure Modes", "Adversarial Training Instability"]
tags: [gans, mode-collapse, training-instability, vanishing-gradients, gan-evaluation]
sources: ["02. Training Dynamics and Mode Collapse"]
created_index: 8
---

The adversarial game has a clean theoretical endpoint — a generator producing perfect samples and a discriminator stuck at 50% accuracy — but reaching it is another matter: GAN training is unstable, sensitive to hyperparameters, and prone to a handful of characteristic failure modes. This note covers the three main pathologies (mode collapse, training instability, and evaluation difficulty), why each arises, and the standard fixes. It closes with the deeper lesson behind all of them: adversarial training is fundamentally harder than supervised training, which is why the field eventually moved toward diffusion models.

> [!warning] Keep the game balanced
> The adversarial loss only provides a gradient when the generator and the discriminator are roughly balanced, and that is a narrow regime. Most GAN training tricks — loss variants, update ratios, Wasserstein objectives — exist to hold the two networks inside it.

## Mode collapse

**Mode collapse** is when the generator produces only a small subset of the possible outputs, ignoring the rest of the data distribution. The symptom is unmistakable: you sample 100 different noise vectors $z_1, \ldots, z_{100}$ and feed them to the generator, and instead of 100 diverse samples you get the same image (or a small handful of images) repeated 100 times. The generator has found a single output that fools the discriminator and produces it for every input.

The root cause is that the discriminator judges individual samples — "is *this* sample real?" — not the *diversity* of samples. The generator can therefore win the game by producing one perfect sample and replicating it without covering the full distribution, and the discriminator has no way to penalize this, because each individual sample looks real. An analogy: a student trying to pass an exam by memorizing one perfect answer and writing it for every question, regardless of what the question asks. If the grader only checks "is this a good answer?" (not "does this answer the question?"), the student passes.

### Fixes for mode collapse

Three remedies attack the problem from different angles:

- **Minibatch discrimination:** the discriminator looks at *batches* of samples, not individuals, and can penalize lack of diversity.
- **Unrolled GANs:** the generator is trained to fool the discriminator *after the discriminator has adapted* to the generator's current strategy, preventing the generator from exploiting transient discriminator weaknesses.
- **Wasserstein GANs:** replace the JS-divergence-based loss with the Wasserstein distance, which provides smoother gradients and reduces mode collapse (see [[Wasserstein GANs and Modern Variants]]).

The first two change what the discriminator can see or how far ahead the generator plans; the third changes the loss geometry itself.

## Training instability

GAN training often **oscillates** rather than converging. The generator improves, the discriminator improves to catch it, the generator improves again, the discriminator improves again — and the system never settles. Or worse, one network "wins" decisively (the discriminator becomes perfect, or the generator finds an exploit), and the other's gradients vanish, halting progress.

### Why the game does not converge

The minimax game is **not convex** and has no convergence guarantee. The two networks chase each other through a complex loss landscape, and small changes in one can cause large changes in the other's optimal response. There is no Lyapunov function (a quantity that monotonically decreases) ensuring convergence.

### The vanishing gradient problem

If the discriminator becomes **too good** (e.g., $D(x) = 1$ for real, $D(G(z)) = 0$ for fake), then the generator's loss $\log(1 - D(G(z))) = \log(1) = 0$, and the gradient is zero — the generator cannot learn. Conversely, if the generator becomes too good, the discriminator's loss is uninformative. This is the opposite of the VAE, where the reconstruction loss always provides a gradient. The adversarial loss only provides a gradient when the two networks are roughly balanced, which is a narrow regime.

### Fixes for instability

Three standard countermeasures:

- **Alternate training ratios:** update the discriminator more often than the generator (e.g., 5:1), to keep the discriminator "one step ahead" without becoming perfect.
- **Saturating vs non-saturating loss:** the original GAN loss $\log(1 - D(G(z)))$ saturates (vanishing gradient) when the generator is doing badly. The non-saturating variant $-\log D(G(z))$ provides stronger gradients early in training.
- **Wasserstein loss:** provides non-vanishing gradients even when the discriminator is good, which stabilizes training.

The non-saturating trick patches the early-training regime, update ratios manage the ongoing balance, and the Wasserstein loss removes the saturation problem at its source.

## Evaluation difficulty

There is no clean metric for "how good are these generated samples?" Reconstruction-based models (VAEs, autoencoders) can measure reconstruction error, but GANs generate from noise — there is no "ground truth" to compare against. The field has settled on two defaults:

- **Inception Score (IS):** use a pretrained Inception classifier on generated samples; high score if the classifier is confident (samples look like distinct classes) and the class distribution is diverse.
- **Fréchet Inception Distance (FID):** compute the Inception features of real and generated samples, then measure the Fréchet distance between their Gaussian fits. Lower is better — the standard metric for GAN quality.

Both metrics have known flaws (they depend on the Inception classifier, which may not capture all relevant qualities), but they are the field's defaults.

## The deeper lesson: adversarial training is hard

GANs' difficulties are not just engineering annoyances — they reflect a deeper challenge: **adversarial training is fundamentally harder than supervised training.** In supervised learning, the loss is fixed (e.g., cross-entropy against true labels), and the model optimizes against it. In adversarial training, the "loss" is itself a network being trained, so the optimization target moves as you train.

This is why the field has moved toward **non-adversarial** generative models: diffusion models replace the adversarial game with a stable denoising objective (see [[Score-Based and Latent Diffusion]] and [[The Reverse Process]]), and modern state-of-the-art image generators (Stable Diffusion, DALL-E 3) are diffusion-based, not GAN-based. But GANs remain important: they are faster at inference (one forward pass, vs diffusion's iterative denoising), and they are still used in domains where speed matters (real-time style transfer, super-resolution, interactive editing).

## Key takeaways

The pathologies in brief:

1. **Mode collapse:** the generator produces only a few outputs, ignoring the rest of the distribution. Caused by the discriminator judging individual samples, not diversity.
2. **Training instability:** the adversarial game is non-convex with no convergence guarantee. Networks oscillate or one wins decisively, causing vanishing gradients.
3. **Vanishing gradients:** if the discriminator is too good, the generator's loss saturates and gradients vanish. The non-saturating loss variant helps.
4. **Evaluation:** Inception Score and FID are the standard (imperfect) metrics for GAN quality.
5. Adversarial training is fundamentally harder than supervised training — the optimization target moves as you train. This is why the field has moved toward diffusion models for state-of-the-art generation.

## See also

- [[12 - Generative Models/Chapter Overview|Chapter Overview]] — the map of the generative models area.
- [[The Adversarial Game]] — the minimax objective whose dynamics break down here.
- [[Wasserstein GANs and Modern Variants]] — the loss-level fix for vanishing gradients and instability.
- [[Score-Based and Latent Diffusion]] — the non-adversarial successor for state-of-the-art quality.
- [[The Reverse Process]] — the iterative denoising that trades GAN speed for stability.
