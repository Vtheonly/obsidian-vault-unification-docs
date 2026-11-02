---
title: Inductive Bias
type: concept
aliases:
  - inductive biases
  - architectural prior
  - "CNNs vs ViTs"
  - "Inductive Bias — CNNs vs ViTs"
tags:
  - inductive-bias
  - vision-transformer
  - cnn
  - sample-efficiency
  - data-scaling
sources:
  - "03. Inductive Bias — CNNs vs ViTs and Why ViTs Need More Data"
created_index: 36
---

Inductive bias is the set of assumptions an architecture builds in about the data, independent of anything it sees during training. The CNN-versus-ViT comparison is the cleanest illustration in modern deep learning: a CNN hard-codes locality, translation equivariance, and hierarchical composition, while a ViT assumes almost nothing about images and must learn those priors from data. This tradeoff between built-in assumptions and data-driven learning explains why ViTs need more data than CNNs — and why they win once data is abundant. It is a tradeoff that runs through all of modern deep learning.

## What is inductive bias?

**Inductive bias** is the set of assumptions built into a model's architecture that constrain what it can learn, independent of the data. It is the "prior knowledge" the designer bakes in.

A CNN has strong inductive biases. First, **locality**: each convolutional neuron sees only a small local neighborhood (the kernel), not the whole image — the assumption that nearby pixels are more related than distant ones. Second, **translation equivariance**: the same kernel is applied at every spatial position — the assumption that a pattern that appears in the top-left is the same pattern if it appears in the bottom-right. Third, **hierarchical composition**: stacking layers expands the receptive field, so early layers detect edges, middle layers detect textures/parts, and late layers detect objects — the assumption that visual concepts are built hierarchically from simpler components.

These assumptions are **correct for natural images**. Locality holds (pixels correlate with their neighbors), translation equivariance holds (a cat is a cat regardless of position), and hierarchical composition holds (edges → textures → parts → objects is how the visual cortex works). By baking these correct assumptions into the architecture, CNNs can learn from relatively small datasets: the architecture already "knows" what kind of patterns to look for, so it only needs the data to fill in the details. The CNN design philosophy is laid out in [[06 - Computer Vision/CNN Foundations and Philosophy/Introduction and Foundations of CNNs|Introduction and Foundations of CNNs]].

A ViT has almost **no** inductive biases about images. There is **no locality** — every patch can attend to every other patch from the first layer, with no built-in assumption that nearby patches are more related. There is **no translation equivariance** — the patches sit at fixed positions with learned positional embeddings, with no weight sharing across spatial translations. And there is **no hierarchical composition** — the "receptive field" is global from layer 1, with no built-in progression from local to global features. The ViT's only image-specific prior is the patch extraction step, which is a single convolution (see [[Patch Tokenization]]). Everything else — the spatial relationships, the locality, the hierarchy — must be **learned from data**.

## The tradeoff: inductive bias vs data

This sets up a fundamental tradeoff:

| | Strong inductive bias (CNN) | Weak inductive bias (ViT) |
| :--- | :--- | :--- |
| Sample efficiency | High — needs less data to learn | Low — needs more data to learn the priors |
| Ceiling on performance | Limited by the bias (if the bias is wrong, the model cannot escape it) | Higher — can learn any pattern the data supports |
| Best regime | Small-to-medium datasets | Large-to-massive datasets |

The CNN's inductive bias is a **constraint**. If the bias is correct (and for natural images it largely is), the constraint helps — it focuses learning on the right kinds of patterns and prevents the model from wasting capacity exploring irrelevant ones. But if the bias is wrong or too rigid, the constraint hurts — the model cannot learn patterns that violate the bias.

The ViT's lack of inductive bias is **freedom**. The model can learn any pattern the data supports, including patterns that violate CNN priors (e.g., long-range spatial dependencies that CNNs handle poorly). But this freedom comes at a cost: the model must learn the priors from data, which requires a lot of data.

## The empirical evidence: the JFT-300M result

The original ViT paper (Dosovitskiy et al. 2020) demonstrated this tradeoff cleanly by training ViTs and ResNets on datasets of increasing size:

- **ImageNet-1K** (1.3M images): ResNet **dominates**. ViT underperforms — it does not have enough data to learn the spatial priors that ResNet gets for free.
- **ImageNet-21K** (14M images): ResNet still wins, but the gap narrows.
- **JFT-300M** (300M images): ViT **overtakes** ResNet. With enough data, the ViT's freedom to learn any pattern beats the ResNet's constrained-but-correct priors.

The crossover happens around 14–100M images. Below that, CNNs win; above that, ViTs win. This is why the original ViT paper's headline result was "ViT beats SOTA on ImageNet" — but only after pretraining on JFT-300M. Without the massive pretraining, ViT loses to ResNet.

## Why the crossover happens

At small data sizes, the CNN's inductive bias is doing real work. The model does not need to learn that "nearby pixels are related" — the architecture already encodes this, so the model only needs to learn *what* the local patterns are (edges, textures, parts), which is a much smaller learning problem. The ViT, by contrast, must learn both the spatial priors *and* the patterns from the data, which is a harder problem that requires more data.

At large data sizes, the CNN's inductive bias becomes a **ceiling**. The model is constrained to express only patterns that respect locality, translation equivariance, and hierarchical composition. If the task requires patterns that violate these — e.g., "this pixel in the top-left is related to that pixel in the bottom-right because they are the same color in a globally-coordinated pattern" — the CNN cannot represent them well. The ViT, with its global attention from layer 1, can represent any pattern, and with enough data it learns the relevant ones.

This is the same phenomenon as in NLP: RNNs (which encode the prior "the past influences the future, in order") dominated NLP until Transformers (which encode almost no prior) were trained on enough data to learn the order-related patterns themselves — the arc traced in [[From RNNs to Attention]]. The trajectory is **architectural priors → data-driven learning**, and the crossover happens when data becomes abundant enough.

## The modern resolution: hybrid approaches

The ViT's data hunger was a real limitation in 2020, when JFT-300M was a proprietary dataset most researchers could not access. The field has since developed several approaches to get ViT-like performance on smaller datasets.

### Hybrid CNN+ViT

Use a CNN for the early layers (to provide the locality and translation equivariance priors cheaply) and a ViT for the later layers (to provide the global attention and flexibility). The CNN front-loads the patches with good low-level features, so the ViT does not need to learn them from scratch. Examples include CoaT, BoTNet, and "Early Convolutions Help Transformers See Further."

### Strong augmentation and self-supervised pretraining

Train the ViT on ImageNet-1K with heavy data augmentation (RandAugment, Mixup, CutMix — see [[05 - Neural Network Foundations/Training Dynamics and Stability/Data Augmentation|Data Augmentation]]) and self-supervised objectives (MAE, DINO, MoCo). The augmentation effectively multiplies the dataset; the self-supervised objective provides a richer learning signal than supervised classification. With these tricks, ViTs can match ResNets on ImageNet-1K without massive pretraining.

### Hierarchical architectures (Swin, PVT)

Modify the ViT to have a hierarchical structure (small patches early, merged into larger patches later), reintroducing some of the CNN's multi-scale prior. The Swin Transformer (Liu et al. 2021) uses shifted-window attention to make this efficient. These architectures combine the flexibility of attention with the data efficiency of hierarchical priors, and they match or beat both CNNs and plain ViTs on a wide range of dataset sizes.

### Knowledge distillation from CNNs

Train a CNN teacher on the dataset, then distill its knowledge into a ViT student. The CNN teacher's inductive bias is "transferred" to the ViT through the distillation loss, effectively giving the ViT access to the CNN's priors without baking them into the architecture. DeiT (Touvron et al. 2021) uses this to train competitive ViTs on ImageNet-1K alone.

## The deeper lesson: priors vs data

The CNN-vs-ViT tradeoff is one instance of a recurring pattern in deep learning. **RNNs vs Transformers**: RNNs encode the prior "the past influences the future, in order," while Transformers encode almost no prior and need more data to learn order-related patterns; Transformers won when data scaled. **Hand-crafted features vs learned features**: pre-deep-learning computer vision used SIFT, HOG, SURF — features designed by humans based on assumptions about what visual patterns matter — and deep learning replaced them with learned features, which need more data but scale better; deep learning won when data and compute scaled. **Symbolic AI vs neural networks**: symbolic AI encodes human knowledge as rules, while neural networks learn from data; neural networks won when data and compute scaled.

The pattern: **as data and compute scale, models with less inductive bias and more flexibility win, because they can learn the priors from data rather than being constrained by designer-specified ones.** The ViT is the vision instance of this pattern; the Transformer is the NLP instance. Both won when data scaled.

This does not mean inductive bias is always bad — for small-data regimes (medical imaging, scientific domains), CNNs or even hand-crafted features may still be the right choice. But for the data-rich regimes that dominate modern AI, the trend is clear: **less prior, more data, more flexibility.**

## See also

- [[Attention and Transformers MOC]] — area overview
- [[ViT Architecture]] — the model whose data hunger this note explains
- [[Patch Tokenization]] — the ViT's one image-specific prior
- [[CLS Token]] — the readout mechanism of the same model
- [[The Transformer]] — the NLP instance of the weak-prior pattern
- [[From RNNs to Attention]] — the RNN-to-Transformer crossover this mirrors
- [[06 - Computer Vision/CNN Foundations and Philosophy/Introduction and Foundations of CNNs|Introduction and Foundations of CNNs]] — the CNN design philosophy
- [[06 - Computer Vision/Architecture and Connectivity/Evolution of CNN Architectures|Evolution of CNN Architectures]] — the CNN lineage ViT competes with
- [[05 - Neural Network Foundations/Training Dynamics and Stability/Data Augmentation|Data Augmentation]] — the augmentation toolset that substitutes for data
