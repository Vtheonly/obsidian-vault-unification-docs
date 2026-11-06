---
title: Multimodal Foundation Models
type: concept
aliases: [Multimodal Foundation Models, VLM, MLLM, Vision-Language Models]
tags: [foundation-models, multimodal, gpt-4v, gemini, llama-vision]
sources: [05 — Multimodal Foundation Models]
created_index: 12
---

> [!info] TL;DR
> Multimodal foundation models process more than one modality — typically text + images, but increasingly text + images + audio + video. The major families are **GPT-4V/4o/5** (OpenAI, closed), **Gemini** (Google, closed), **Claude 3/3.5/4 Sonnet & Opus** (Anthropic, closed), **Llama 3.2 Vision / Llama 4** (Meta, open), **Qwen-VL / Qwen2-VL** (Alibaba, open), and **InternVL** (Shanghai AI Lab, open). Two architectural paradigms dominate: **multimodal-native** (trained from scratch on interleaved multimodal data, e.g., Gemini) and **bolt-on** (vision encoder added to a pretrained LLM, e.g., LLaVA, Llama-Vision). Each has different capability profiles and training costs.

Multimodal foundation models process more than one modality — typically text and images, but increasingly text, images, audio, and video together — and they are the models that can read documents, watch video, and listen. This note maps the territory: the two dominant architectural paradigms, the major model families from closed and open labs, and the components every vision-language model shares (vision encoders, projection modules, image tokenization, position embeddings). It then walks through the standard three-stage training recipe, the evaluation benchmarks that separate frontier models from early ones, and the strengths and limitations that matter in practice. A text-only LLM is blind to half of the world's information; these models close that gap. The area orientation is [[Foundation Models and Multimodal MOC]], and the wider multimodal context is in [[Multimodal AI Overview]].

## Why multimodal foundation models matter

Most real-world information is multimodal. Documents have text and figures. Web pages have text and images. Conversations have speech and gestures. A text-only LLM is blind to half of this information.

Multimodal foundation models close this gap. They can answer questions about images ("What's in this picture?", "Read the text on this sign."), understand documents (parse PDFs with text, tables, and figures), reason about UIs ("Click the submit button" — the foundation of UI agents), process video (summarize, answer questions, detect events), and transcribe and translate speech (end-to-end speech-to-text and speech-to-speech translation).

The economic significance is large: document AI, accessibility tools, robotics, autonomous vehicles, and content moderation all rely on multimodal understanding.

## Two architectural paradigms

### Multimodal-native (trained from scratch)

The model is trained from initialization on interleaved multimodal data: sequences that mix text tokens, image patches, and audio frames. The attention mechanism operates across modalities from the start. The upside is tight cross-modal integration — the model learns joint representations rather than late fusion. The downsides: it requires massive multimodal training data from the start, it is expensive, and it can't reuse a pretrained text-only LLM. Examples: Gemini (Google), GPT-4o (OpenAI). Status: officially confirmed for Gemini; strongly inferred for GPT-4o.

In a multimodal-native model, the modalities share the same transformer blocks. An image patch and a text token attend to each other in every layer. This produces deeper integration than bolt-on approaches.

### Bolt-on (vision encoder + pretrained LLM)

The model starts with a pretrained LLM and adds a vision encoder ([[CLIP]], SigLIP, etc.). A projection module maps vision features into the LLM's embedding space, and the LLM is then fine-tuned on image-text data. The upside: it reuses expensive pretrained components (the LLM and the vision encoder) and is fast to train (hours-days vs. months). The downside: looser cross-modal integration — vision features enter the LLM as "soft tokens" that the LLM must learn to interpret. Examples: LLaVA, Llama 3.2 Vision, Qwen-VL, InternVL.

The bolt-on approach dominates open-weights VLMs because it's tractable without massive compute. See [[LLaVA]] for the canonical recipe.

### Hybrid (mostly bolt-on, partially native)

Some models (GPT-4V, Claude 3.5 Sonnet) appear to use a hybrid: a pretrained LLM core with vision added early in training, but not from initialization. Status: strongly inferred — neither OpenAI nor Anthropic has disclosed architecture details.

## The major model families

### GPT-4V / GPT-4o / GPT-5 (OpenAI, closed)

GPT-4V (2023) was OpenAI's first multimodal model, added to GPT-4. GPT-4o (2024) is "omnimodal" — natively handles text, image, and audio. GPT-5 (if released) is presumed to extend this. Architecture: not officially disclosed; strongly inferred to be multimodal-native, based on GPT-4o's low latency for audio, which suggests end-to-end audio processing without a separate ASR step. Strengths: broad capability, excellent OCR, strong visual reasoning. Status as of 2026: GPT-4o and successors are the default multimodal API for most developers.

### Gemini (Google, closed)

Gemini 1.0 (2023) was Google's first multimodal-native model. Gemini 1.5 Pro (2024) added a 1M-2M token context window. Gemini 2.0 (late 2024) and 2.5 (2025) improved reasoning. Architecture: multimodal-native, with MoE (Mixture-of-Experts) in some versions (see [[Mixture of Experts]]). The multimodal-native property is officially confirmed (Gemini 1 paper, 2023). Strengths: massive context, native video understanding, strong document AI.

### Claude 3 / 3.5 / 4 (Anthropic, closed)

Claude 3 (2024) added vision to Claude. Claude 3.5 Sonnet (2024) significantly improved visual reasoning. Claude 4 / Opus (2025) extended this. Architecture: not officially disclosed; strongly inferred to be a bolt-on or hybrid vision approach. Strengths: strong document understanding, careful refusals, good handwriting OCR. Anthropic publishes less about architecture than Google but more about capabilities.

### Llama 3.2 Vision / Llama 4 (Meta, open)

Llama 3.2 Vision (2024) shipped as 11B and 90B parameter vision-language models based on Llama 3.1 text. Llama 4 (2025, if released) extends to multimodal-native. Architecture: bolt-on (vision encoder + adapter on Llama 3.1). Strengths: open weights, strong performance, reusable for fine-tuning. Licensing: Llama community license.

### Qwen-VL / Qwen2-VL / Qwen2.5-VL (Alibaba, open)

Qwen-VL (2023) was the first-generation vision-language model from Alibaba. Qwen2-VL (2024) is significantly improved and supports dynamic resolution (variable image sizes). Qwen2.5-VL (2025) brings further improvements and is strong on document AI. Architecture: bolt-on (ViT + adapter on Qwen2). Strengths: excellent OCR, dynamic resolution, permissive licensing. It is the best open-weights VLM for many use cases as of 2025.

### InternVL (Shanghai AI Lab, open)

InternVL (2024) is a family of VLMs from Shanghai AI Lab. It uses a large ViT (6B parameters in InternVL-Chat-V1.5) for richer vision features. Architecture: bolt-on with an oversized vision encoder. Strengths: strong on fine-grained visual detail (small text, distant objects). Permissive MIT license.

## Key architectural components

### Vision encoders

Most VLMs use one of a small set of encoders. [[CLIP]] (OpenAI, 2021) is the original vision-language encoder. SigLIP (Google, 2023) uses a sigmoid loss instead of softmax and is better at scale. DINOv2 (Meta, 2023) is a self-supervised vision encoder with richer features for some tasks. And some labs train custom large ViTs: InternVL uses a 6B-parameter ViT, and some Gemini versions reportedly use custom vision encoders.

The vision encoder matters more than people initially expected. LLaVA-1.5 with SigLIP outperforms LLaVA-1.5 with CLIP, even with identical LLMs and projections. The encoder landscape is covered in [[Vision Foundation Models]].

### Projection modules

Four projection designs dominate. A **linear** projection is the simplest, used in LLaVA-1; it works okay but has limited capacity. An **MLP** (a 2-layer MLP with GELU), used in LLaVA-1.5+, is significantly better than linear. A **Perceiver Resampler** is a small cross-attention module that compresses N vision tokens to K (e.g., 576 → 64); used in Flamingo and Qwen-VL, it reduces the LLM's vision-token burden. **Pixel Shuffle** rearranges spatial dimensions into channels, reducing the number of vision tokens; used in Qwen2-VL.

### Tokenization of images

**Patch embeddings** are the standard ViT approach: the image is split into 14×14 (or 16×16) patches, each embedded into a vector. **Dynamic resolution** — instead of resizing all images to 336×336, the model accepts variable image sizes and tiles large images into multiple 336×336 patches — is used in Qwen2-VL, LLaVA-NeXT, and InternVL. **Multi-scale** models process the image at multiple resolutions in parallel.

Dynamic resolution is the most important recent innovation. It allows VLMs to read small text in high-resolution images — a capability the original LLaVA completely lacked.

### Position embeddings for vision

Vision encoders use 2D positional embeddings (sinusoidal or learned) to encode patch positions. When the vision features are projected into the LLM, the LLM's 1D position embeddings take over. Some VLMs (Qwen2-VL) use 2D-aware position embeddings even in the LLM, preserving spatial information.

## Training recipes

### Stage 1: projection pretraining

Train only the projection (the MLP mapping vision features to LLM space) on image-caption pairs, with the vision encoder and LLM frozen. This teaches the projection to translate vision features into the LLM's vocabulary. Data: ~500K image-caption pairs (e.g., CC3M, LAION-COCO). Compute: hours on a single GPU. Result: a model that can describe images but doesn't follow instructions well.

### Stage 2: instruction tuning

Train the projection and (optionally) the LLM on image-text instruction data. The LLM is usually fine-tuned with [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]] to keep parameter count manageable; the general recipe is covered in [[Instruction Tuning and Chat Templates]]. Data: ~500K image-instruction-response triples (e.g., LLaVA-Instruct). Compute: days on a single GPU, or hours on multi-GPU. Result: a model that follows instructions about images.

### Stage 3: multimodal RLHF (optional)

Some VLMs (GPT-4V, Gemini) undergo RLHF with multimodal preferences: the reward model scores image-text responses on helpfulness, harmlessness, and hallucination. The underlying method is covered in [[RLHF with PPO]], and the failure mode it guards against in [[Hallucination]]. Status: rarely done in open-weights VLMs due to the cost of collecting multimodal preference data.

## Evaluation

Multimodal models are evaluated on a battery of benchmarks: **VQA** (visual question answering — answer questions about images), **GQA** (a more rigorous VQA with structured question types), **MMMU** (Massive Multi-discipline Multimodal Understanding — college-level questions requiring visual reasoning across disciplines), **MMBench** (a multilingual multimodal benchmark), **DocVQA** (question answering about document images), **ChartQA** (question answering about charts), **MMMU-Pro** (a harder version of MMMU designed to defeat pattern-matching), and **Video-MME** (a video understanding benchmark).

The frontier benchmarks (MMMU, MMMU-Pro) are where 2026-era models differentiate. Early VLMs scored 30-40% on MMMU; current frontier models score 60-70%.

## Strengths and limitations

### Strengths

Image captioning is largely solved: most VLMs produce fluent, accurate captions for common images. Document understanding — reading text in images, parsing tables, understanding forms — is a core strength. Visual reasoning (answering questions that require spatial reasoning, object relationships, and common sense) is strong. And for OCR, modern VLMs rival dedicated OCR systems for printed text and exceed them for handwriting.

### Limitations

**Hallucination**: VLMs sometimes describe objects that aren't in the image. Mitigation: train on negative examples ("What's in this image?" → "Nothing relevant"). **Counting**: VLMs are unreliable at counting more than ~5 objects. **Spatial reasoning**: "left of", "behind" are often wrong, especially in complex scenes. **Fine-grained recognition**: identifying specific breeds of dog, models of car, etc. remains hard. **Video understanding**: temporal reasoning in video is much weaker than image understanding. **Audio understanding**: only GPT-4o-class models handle audio natively; most VLMs are text+image only.

## Future directions

Five directions dominate the agenda. True omnimodal models would handle text + image + audio + video, all natively. Better long-video understanding is needed: current models handle ~1 minute of video; we need 1-hour. Embodied AI would put VLMs in control of robots, understanding the world through cameras. 3D understanding — depth, occlusion, and 3D structure from 2D images — remains open. And multimodal reasoning — models that reason across modalities ("this graph shows X, therefore Y") — is the frontier.

## See also

- [[Foundation Models and Multimodal MOC]] — orientation for this area.
- [[Multimodal AI Overview]] — the wider multimodal context.
- [[CLIP]] — the vision encoder most VLMs use.
- [[Cross-Modal Attention]] — fusion architectures.
- [[LLaVA]] — the simplest VLM recipe.
- [[DiT and FLUX]] — the generative side of multimodality.
- [[Whisper]] — audio understanding.
- [[Vision Foundation Models]] — the vision encoders VLMs use.
- [[Embedding Models for Retrieval]] — sister domain.
- [[Reasoning Models]] and [[Code Models]] — sister domains.
- [[Embedding Model Training]] — related training approach.
- [[Hallucination]], [[RLHF with PPO]], and [[Instruction Tuning and Chat Templates]] — training and failure-mode background.
- [[Build a Vision-Language Model]]
