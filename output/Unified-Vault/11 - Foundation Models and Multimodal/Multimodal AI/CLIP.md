---
title: CLIP
type: concept
aliases: [CLIP, Contrastive Language-Image Pretraining, Contrastive Language-Image Pre-training]
tags: [multimodal, clip, vision-language, contrastive-learning]
sources: [02 — CLIP]
created_index: 7
---

> [!info] TL;DR
> CLIP (Contrastive Language-Image Pre-training) trained a vision encoder and a text encoder jointly on 400M image-caption pairs, using a contrastive loss that pulls matching image-text pairs together in embedding space and pushes non-matching pairs apart. The result: a single model that can match images to text, classify images into arbitrary categories (zero-shot), and produce embeddings useful for retrieval, generation, and downstream tasks. CLIP became the default visual encoder for multimodal LLMs (LLaVA, Flamingo, BLIP) and remains one of the most influential multimodal models.

CLIP (Contrastive Language-Image Pre-training) is the contrastive vision-language model that made natural language the supervision signal for vision. This note covers the problem it solved, its two-encoder architecture, the contrastive training objective, zero-shot classification and the prompt engineering that unlocks it, its key results, limitations, and successors. It closes with CLIP's impact on multimodal AI — as the default visual encoder for vision-language models and as the foundation of text-to-image generation. The area orientation is [[Foundation Models and Multimodal MOC]]; the wider multimodal context is in [[Multimodal AI Overview]].

## Citation

Radford, A., Kim, J. W., Hallacy, C., Ramesh, A., Goh, G., Agarwal, S., Sastry, G., Clark, J., Eck, D., Sutskever, I., & Chen, M. (2021). *Learning Transferable Visual Models From Natural Language Supervision*. ICML 2021. arXiv:2103.00020.

## The problem being solved

Before CLIP, vision models were trained on fixed label sets (ImageNet's 1000 classes, COCO's 80 classes). This limited them to recognizing categories seen during training. To recognize a new category (e.g., a novel animal species), you needed to collect labeled examples and fine-tune — expensive and slow.

CLIP's insight: train on natural language captions rather than fixed labels. Captions provide unlimited supervision — every image on the web comes with surrounding text that describes it. A model trained on image-caption pairs learns to associate visual concepts with their textual descriptions, enabling zero-shot classification: to recognize a new category, just provide its textual description.

This was a paradigm shift. Instead of training a classifier for each task, you train one model on web-scale image-text data and use it for any task by specifying the categories as text.

## The architecture

CLIP has two encoders that map into one shared space.

### Image encoder

A vision model (ResNet or ViT) that takes an image and produces a fixed-dimensional embedding. The ResNet variants are ResNet-50, ResNet-101, RN50x4, RN50x16, and RN50x64 (scaled versions); the ViT variants are ViT-B/32, ViT-B/16, ViT-L/14, and ViT-L/14@336 (higher resolution) — the ViT design itself is covered in [[ViT Architecture]]. The image encoder outputs a single embedding vector (e.g., 512 or 768 dimensions).

### Text encoder

A Transformer encoder that takes a text prompt (up to 77 tokens) and produces an embedding of the same dimension as the image encoder. The text encoder is a standard Transformer (similar to GPT-2 architecture) with a `[CLS]`-style pooling token.

### Projection heads

Both encoders have linear projection heads that map their outputs to a shared embedding space (typically 512 or 768 dimensions). This shared space is where image and text embeddings are compared.

```mermaid
graph LR
  Img[Image] --> ViT[Vision Encoder: ViT/ResNet]
  ViT --> ImgEmb[Image embedding: 512-d]
  ImgEmb --> Proj1[Linear projection]
  Proj1 --> ImgVec[Shared space: 512-d]
  
  Text[Text: "a photo of a cat"] --> TextEnc[Text Encoder: Transformer]
  TextEnc --> TextEmb[Text embedding: 512-d]
  TextEmb --> Proj2[Linear projection]
  Proj2 --> TextVec[Shared space: 512-d]
  
  ImgVec --> Sim[Cosine similarity]
  TextVec --> Sim
```

## The training objective: contrastive learning

CLIP is trained on a batch of N image-caption pairs. The contrastive loss works in four steps: encode all N images and N captions; compute the N×N similarity matrix (cosine similarity between every image and every caption); require the diagonal (matching pairs) to have high similarity and the off-diagonal (non-matching) to have low; and apply a symmetric cross-entropy, where the "correct" class for each image is its matching caption (and vice versa).

```python
# For a batch of N pairs:
logits = (image_embeddings @ text_embeddings.T) / temperature  # N×N
labels = arange(N)  # the diagonal is correct

loss_images = cross_entropy(logits, labels)       # image-to-text
loss_texts = cross_entropy(logits.T, labels)      # text-to-image
loss = (loss_images + loss_texts) / 2
```

The `temperature` parameter controls the sharpness of the similarity distribution. It's learned during training (typically converges to ~0.01).

The key requirement is large batch sizes. The contrastive loss only works well when there are many "negative" (non-matching) pairs in the batch. CLIP used batch size 32,768 — requiring significant compute and memory.

## Zero-shot classification

CLIP's killer feature: zero-shot classification. To classify an image into arbitrary categories, encode the categories as text, encode the image, and pick the category with the highest similarity:

```python
# Define the categories as text prompts
categories = ["a photo of a dog", "a photo of a cat", "a photo of a bird"]
text_embeddings = encode_text(categories)  # 3×512

# Encode the image
image_embedding = encode_image(image)  # 1×512

# Compute similarities
similarities = (image_embedding @ text_embeddings.T)  # 1×3

# Predict the category with highest similarity
predicted = categories[similarities.argmax()]
```

No fine-tuning required. The model classifies into any set of categories defined by text.

### Prompt engineering for zero-shot

The choice of text prompt affects accuracy. "a photo of a {category}" works better than just "{category}". More sophisticated prompts ("a satellite photo of a {category}", "a sketch of a {category}") can further improve accuracy for specific domains.

CLIP's zero-shot accuracy on ImageNet (1000 classes) was 76.2% — competitive with supervised ResNet-50 (77.4%), without seeing any ImageNet labels. This was a landmark result: zero-shot matching supervised performance.

## Key results

| Task                          | Previous SOTA | CLIP (zero-shot) |
|-------------------------------|---------------|------------------|
| ImageNet (zero-shot)          | —             | 76.2%            |
| ImageNet (linear probe)       | 88.3%         | 83.8%            |
| ObjectNet (zero-shot)         | ~30%          | 72.3%            |
| Satellite imagery (zero-shot) | —             | ~60%             |

CLIP showed strong robustness to distribution shift — it outperformed supervised models on ObjectNet (images with different viewpoints, backgrounds, styles) because it learned general visual concepts rather than dataset-specific features.

## Why it worked

### Natural language supervision is unlimited

Web-scale image-caption data (400M pairs in CLIP's case) provides supervision for an unlimited number of concepts. No label set can match this coverage.

### Contrastive learning aligns modalities

The contrastive loss directly aligns image and text embeddings in a shared space. This makes the embeddings useful for cross-modal retrieval (find images matching this text, find text matching this image).

### Shared embedding space enables composition

Because images and text live in the same space, you can compose them: find images similar to this text, then find text similar to those images, etc. This enables applications like text-to-image retrieval, image-based search, and visual question answering.

### Zero-shot generalization

The model learns to associate visual concepts with their textual descriptions, not just to classify into fixed categories. This enables recognition of novel categories at inference time.

## Limitations

### Biased training data

CLIP was trained on web data, which contains biases (demographic, cultural, geographic). The model inherits these biases — it performs worse on non-Western concepts and can produce stereotyped classifications.

### Counting and spatial reasoning

CLIP struggles with counting ("how many objects?") and spatial reasoning ("what is to the left of the cup?"). The contrastive loss doesn't explicitly teach these skills.

### Fine-grained classification

For fine-grained tasks (e.g., distinguishing bird species), CLIP underperforms specialized supervised models. The web-scale training data is too noisy for fine-grained concepts.

### Limited text length

CLIP's text encoder accepts only 77 tokens. This limits the complexity of text prompts and prevents using CLIP for long-form text-image tasks.

## Successors

**OpenCLIP** is an open-source reproduction of CLIP with various model sizes and datasets, widely used in research and production. **SigLIP** (Google, 2023) replaces the softmax-based contrastive loss with a sigmoid loss — simpler, more scalable, and slightly better performance; it is used in many 2024+ multimodal models. **EVA-CLIP** is an improved CLIP variant with a better training recipe and larger scale, delivering stronger zero-shot performance. **DINOv2** (Meta, 2023) is a self-supervised vision encoder (no text) that produces features matching or exceeding CLIP for many tasks, especially dense prediction. **MobileCLIP** is optimized for mobile deployment — smaller, faster, with minimal quality loss.

## Impact and legacy

CLIP reshaped computer vision and multimodal AI in five ways. First, it became the **default visual encoder for multimodal LLMs**: LLaVA, Flamingo, BLIP, and most vision-language models use CLIP (or a successor) as the visual encoder, because the shared embedding space makes it natural to fuse visual and textual information. Second, it established **zero-shot classification as a paradigm** — CLIP demonstrated that specifying categories as text is practical, and this became a standard evaluation mode for vision models. Third, it became a **foundation for text-to-image generation**: DALL-E, Stable Diffusion, and Midjourney use CLIP's text encoder (or a similar model) to encode the text prompt that guides image generation; without CLIP, text-to-image models would need a separate text encoder. Fourth, it powers **vision-language retrieval**: CLIP embeddings drive image search, visual search, and content moderation systems, where matching images and text in a shared space is foundational. Fifth, it popularized **contrastive learning as a training paradigm** for multimodal alignment — the same loss function appears in audio-text, video-text, and other multimodal models.

For AI engineers, CLIP is foundational infrastructure. If you're building a multimodal application (image search, visual Q&A, content moderation), CLIP or a successor is likely your visual encoder. Understanding CLIP clarifies how visual and textual information are aligned and how to leverage this alignment for downstream tasks.

## Further reading

The original paper is arXiv:2103.00020. OpenCLIP lives at github.com/mlfoundations/open_clip, and SigLIP is arXiv:2303.15343.

## See also

- [[Foundation Models and Multimodal MOC]] — orientation for this area.
- [[Multimodal AI Overview]] — the wider multimodal context.
- [[Cross-Modal Attention]] — how aligned embeddings get consumed downstream.
- [[LLaVA]] — the simplest VLM built on a CLIP-style encoder.
- [[Multimodal Foundation Models]] — the model families that use CLIP or its successors.
- [[DiT and FLUX]] — text-to-image generation with CLIP-style text conditioning.
- [[ViT Architecture]] — the vision backbone of CLIP's ViT variants.
- [[Vision Foundation Models]] — the encoder landscape, including DINOv2.
- [[Embedding Models for Retrieval]] — retrieval over contrastive embeddings.
- [[Embedding Model Training]] — training objectives for embedding models.
- [[Vision Transformer]]
