---
title: Multimodal AI Overview
type: overview
aliases: [Multimodal AI Overview, Multimodal AI, Multimodal AI survey]
tags: [multimodal, vision-language, llava, clip, diffusion, audio, video, overview]
sources: ["01 - Multimodal AI Overview"]
created_index: 11
---

Multimodal AI combines text, images, audio, and video, and this note is the survey of that field within the [[Foundation Models and Multimodal MOC]] area. It tours the modalities and the model families that serve them — vision-language models (CLIP, LLaVA, Qwen-VL, GPT-4V/4o, Claude, Gemini), diffusion-based image generation (Stable Diffusion, FLUX, DALL-E 3, Midjourney), audio (Whisper, TTS engines, speech-to-speech), and video (Sora, Veo, Runway Gen-3, Pika) — and then goes below the catalog: the three architectural patterns for multimodal LLMs, the cost and latency profile of image tokens, a vision-language task taxonomy, the multimodal-vs-text-only decision rule, and worked examples for both inference and document RAG with vision.

> [!info] TL;DR
> Multimodal AI combines text, images, audio, and video. Vision-language models (CLIP, LLaVA, GPT-4V) handle image+text. Diffusion models (Stable Diffusion, FLUX) generate images. Whisper handles speech. The frontier is native multimodal models (GPT-4o, Gemini) that handle all modalities in one model.

## The modalities

Multimodal AI starts with an inventory of the modalities, each with its own model families:

- **Text**: LLMs.
- **Image**: ViT, CLIP, Stable Diffusion, FLUX, SAM.
- **Audio (speech)**: Whisper (ASR), Bark / ElevenLabs (TTS).
- **Video**: Sora, Runway, Veo.
- **Code**: special case of text but worth distinguishing — the specialized models are covered in [[Code Models]].

Most of what follows is about combining these modalities in one system rather than handling any single one; the notes linked throughout this survey are the deep dives for each combination.

## Vision-language models

Vision-language models handle image+text, and they are the center of gravity of multimodal AI. The vision encoders they build on are covered in [[Vision Foundation Models]], and the model families below get their full per-model treatment in [[Multimodal Foundation Models]].

### CLIP (Radford et al. 2021)

Two encoders (image + text) trained contrastively. Foundation for many multimodal systems. The full treatment of the contrastive alignment is in [[CLIP]].

### LLaVA (Liu et al. 2023)

Open-source multimodal LLM: ViT/CLIP image encoder + projector + Llama LLM.

```text
Image → CLIP encoder → image tokens → projector (MLP) → LLM
```

Variants: LLaVA-1.5, LLaVA-NeXT (higher resolution, better performance), LLaVA-OneVision. The architecture walkthrough lives in [[LLaVA]].

### Qwen-VL

Alibaba's multimodal model. Strong on document understanding and Chinese.

### GPT-4V / GPT-4o (OpenAI)

Closed-source. GPT-4o is **native multimodal** — one model handles text, image, and audio tokens directly (not separate encoders stitched together).

### Claude (Anthropic)

Multimodal since Claude 3 (Mar 2024). Strong on document analysis and chart reading.

### Gemini (Google)

Native multimodal from the start. Gemini 1.5 Pro handles 1M+ tokens of mixed text/image/video/audio.

## Image generation: diffusion

Image generation is dominated by diffusion models, with open-source and closed-source options splitting the field:

### Stable Diffusion / FLUX

Open-source image generation. Diffusion Transformers (DiT) power FLUX and SD3 — see [[DiT and FLUX]].

### DALL-E 3 (OpenAI)

Closed-source image generation; integrated with ChatGPT.

### Midjourney

Closed-source, strong aesthetic quality.

## Audio

The audio modality covers recognition, generation, and full-duplex conversation:

### Whisper (OpenAI, 2022)

Open-source ASR. Whisper-large-v3 is the standard. Multilingual. The deep dive is [[Whisper]].

### TTS: ElevenLabs, Bark, OpenAI TTS

Voice generation. ElevenLabs is the commercial leader; Bark is open-source.

### Speech-to-speech

Real-time voice-to-voice conversation. GPT-4o is the frontier.

## Video

### Sora (OpenAI, 2024)

Text-to-video generation. Minutes-long, high quality.

### Veo (Google), Runway Gen-3, Pika

Competing video models.

## Worked example: LLaVA via HuggingFace

A minimal LLaVA inference loop — load the model, attach an image, prompt with the chat template:

```python
from transformers import LlavaForConditionalGeneration, AutoProcessor
from PIL import Image
import torch

model_id = "llava-hf/llava-v1.6-mistral-7b-hf"
model = LlavaForConditionalGeneration.from_pretrained(
    model_id, torch_dtype=torch.bfloat16, device_map="auto",
)
processor = AutoProcessor.from_pretrained(model_id)

image = Image.open("photo.jpg")
prompt = "USER: <image>\nWhat's in this image?\nASSISTANT:"

inputs = processor(text=prompt, images=image, return_tensors="pt").to(model.device)
output = model.generate(**inputs, max_new_tokens=200)
print(processor.decode(output[0], skip_special_tokens=True))
```

## Why this matters

Multimodal AI is **the** 2024–2026 frontier, and the reasons are concrete:

- Most major model releases are multimodal.
- For RAG with images (PDFs with figures, screenshots, diagrams), multimodal models can extract information that text-only models can't.
- For agents, multimodal enables computer-use (Claude Computer Use, OpenAI Operator) — agents that "see" the screen.
- For creative applications, image/video generation opens entirely new product categories.

## Production implications

The defaults for putting multimodal models to work:

- **For document-heavy RAG**, multimodal models (Qwen-VL, LLaVA-NeXT, Claude 3.5) can extract info from figures, charts, scanned PDFs.
- **For image generation**, FLUX and Stable Diffusion 3 are the open-source standards.
- **For speech**, Whisper-large-v3 for ASR, ElevenLabs for TTS.
- **Latency**: multimodal is slower than text-only (more tokens to process). Plan accordingly.
- **Cost**: image tokens cost more than text tokens. For GPT-4o, an image is ~750 tokens (depending on resolution).

## Common pitfalls

Four failure modes recur in multimodal projects, and all four are avoidable with discipline:

- **Wrong image resolution** — multimodal models expect specific resolutions. Resize correctly.
- **Forgetting to handle multiple images** — most multimodal models support multiple images, but the chat template differs.
- **Treating multimodal as "LLM + image"** — native multimodal (GPT-4o, Gemini) is fundamentally different from stitched (LLaVA).
- **Not testing on real images** — benchmarks use clean images; production images are noisy.

## Architectural patterns for multimodal LLMs

There are three architectural patterns for combining vision with language models, in increasing order of integration:

### Pattern 1: stitched (LLaVA-style)

```text
Image → ViT/CLIP encoder → image tokens → MLP projector → LLM token space → LLM
```

- Vision encoder is frozen (pretrained separately).
- Projector is a small MLP (1-2 layers) that maps vision encoder dim to LLM dim.
- LLM is fine-tuned (LoRA or full SFT) to consume image tokens alongside text.
- Pros: simple, modular, cheap to train (only projector + LLM adapter).
- Cons: limited cross-modal interaction; vision encoder can't see text context.

Examples: LLaVA-1.5, LLaVA-NeXT, MiniGPT-4,早期的 Qwen-VL.

### Pattern 2: cross-attention (BLIP-2-style)

```text
Image → ViT encoder → image features → Q-Former (cross-attention) → compressed image tokens → LLM (via cross-attn)
```

- Q-Former is a small Transformer with cross-attention to image features, producing a fixed number (e.g., 32) of "query tokens" that summarize the image.
- LLM gets image info via cross-attention layers, not by treating image tokens as input.
- Pros: compressed image representation (fewer tokens), better cross-modal fusion.
- Cons: more complex; Q-Former needs pretraining.

Examples: BLIP-2, InstructBLIP, MiniGPT-v2.

### Pattern 3: native multimodal (GPT-4o-style)

```text
Image patches → patch embedding → interleaved with text tokens → unified Transformer
```

- No separate vision encoder. Image patches and text tokens are processed by the same Transformer.
- Trained end-to-end on interleaved image+text+audio data.
- Pros: maximum cross-modal integration; no information bottleneck at a projector.
- Cons: requires massive multimodal training data; expensive to train from scratch.

Examples: GPT-4o, Gemini 2.5, Qwen2-VL (partial).

The trend is from Pattern 1 → Pattern 2 → Pattern 3. Most 2026 open-source VLMs are Pattern 1 (LLaVA-NeXT) or Pattern 2 (BLIP-2 derivatives); closed models are Pattern 3. The fusion mechanism behind the cross-attention pattern is covered in [[Cross-Modal Attention]].

## Cost and latency of multimodal models

Multimodal models are more expensive than text-only because images consume many tokens:

| Model                | Image resolution | Image tokens | Cost per image (relative) |
|----------------------|------------------|--------------|---------------------------|
| GPT-4V               | 512×512          | ~465         | 1× (baseline)             |
| GPT-4o               | 1024×1024        | ~750         | 1.5×                      |
| Claude 3.5 Sonnet    | 1024×1024        | ~1,600       | 2.5×                      |
| LLaVA-NeXT (7B self) | 672×672          | ~2,000       | ~0.1× (self-host)         |
| Qwen2-VL (7B self)   | Dynamic          | ~1,000-4,000 | ~0.1× (self-host)         |

Latency: image processing adds 100-500ms per image on top of text-only latency. For multi-image queries (e.g., analyzing a 10-page document), latency can reach 5-10s.

Production patterns:

- **Tile large images**: split 4K images into 4-16 tiles, process each separately, combine results. Avoids huge token counts.
- **Cache image embeddings**: for repeated images (e.g., product photos), cache the embedded representation.
- **Use smaller vision encoder**: DINOv2-Small instead of Large for non-critical tasks.
- **Skip images for simple queries**: classify whether the query needs vision; skip image processing if not.

## Vision-language task taxonomy

The recurring vision-language tasks, with the models that currently do each best:

| Task                         | Description                                          | Best Models                          |
|------------------------------|------------------------------------------------------|--------------------------------------|
| Image captioning             | Describe image in text                               | LLaVA, Qwen-VL, Claude               |
| Visual question answering    | Answer questions about an image                      | LLaVA, Qwen-VL, GPT-4V               |
| Image-text retrieval         | Find images matching text (or vice versa)            | CLIP, SigLIP, DINOv2                 |
| Document understanding       | Extract info from scanned documents, charts          | Qwen2-VL, Donut, Claude              |
| OCR                          | Extract text from images                             | PaddleOCR, Tesseract, Qwen2-VL       |
| Visual reasoning             | Multi-step reasoning over images (e.g., diagram)     | GPT-4o, Claude 3.5, o1               |
| Image generation             | Text → image                                          | FLUX, SD3, DALL-E 3                  |
| Image editing                | Modify image per text instructions                   | InstructPix2Pix, FLUX-edit           |
| Video understanding          | Answer questions about video                         | GPT-4o, Qwen2-VL (frames), LLaVA-Video |
| Visual grounding             | Identify where in image a concept is                 | GroundingDINO, Qwen2-VL              |
| Chart/figure understanding   | Extract data from charts                             | Claude 3.5, GPT-4V, Qwen2-VL         |

## When to use multimodal vs text-only

Use multimodal when:

1. The input contains images, charts, diagrams, or scanned documents.
2. The task requires visual reasoning (spatial, color, layout).
3. The user experience benefits from image input (e.g., "what's in this photo?").
4. You need to extract structured data from visual sources (PDFs, screenshots).

Use text-only when:

1. The input is pure text.
2. You can pre-extract text from images via OCR (cheaper).
3. Latency and cost are critical.
4. The task is purely linguistic (translation, summarization of text).

**Rule of thumb**: don't use a VLM if OCR + text LLM suffices. VLMs are 5-10× more expensive than text LLMs per token; only use them when the visual content adds value beyond extractable text.

## Production worked example: document RAG with vision

The standard pattern for PDFs whose value lives in figures and charts — convert pages to images, extract per page with a VLM, aggregate the hits:

```python
from transformers import LlavaForConditionalGeneration, AutoProcessor
from PIL import Image
import pdf2image  # for PDF → images
import torch

class DocumentVisionRAG:
    def __init__(self):
        self.model_id = "llava-hf/llava-v1.6-mistral-7b-hf"
        self.model = LlavaForConditionalGeneration.from_pretrained(
            self.model_id, torch_dtype=torch.bfloat16, device_map="auto",
        )
        self.processor = AutoProcessor.from_pretrained(self.model_id)

    def extract_from_pdf(self, pdf_path: str, query: str) -> str:
        # Convert PDF pages to images
        images = pdf2image.convert_from_path(pdf_path, dpi=200)
        results = []
        for page_num, image in enumerate(images, 1):
            prompt = f"USER: <image>\nOn this page, find information about: {query}\nIf not present, say 'NOT FOUND'.\nASSISTANT:"
            inputs = self.processor(text=prompt, images=image, return_tensors="pt").to(self.model.device)
            output = self.model.generate(**inputs, max_new_tokens=300)
            response = self.processor.decode(output[0], skip_special_tokens=True)
            if "NOT FOUND" not in response:
                results.append({"page": page_num, "content": response})
        return results

# Usage
rag = DocumentVisionRAG()
results = rag.extract_from_pdf("financial_report.pdf", "total revenue for Q4 2024")
```

This pattern (PDF → images → VLM extraction → aggregate) is the standard for vision-based document RAG in 2026, used by products like Google NotebookLM, Claude's PDF analysis, and various enterprise document AI platforms.

## Further reading

- Radford et al. (2021), *CLIP*.
- Liu et al. (2023), *LLaVA*.
- Rombach et al. (2022), *Stable Diffusion* (Latent Diffusion).
- OpenAI (2024), *Sora Technical Report*.

## Interview questions

1. **Q: Compare stitched, cross-attention, and native multimodal architectures.**
   A: Stitched (LLaVA): frozen vision encoder + MLP projector + LLM; simple, modular, cheap to train; limited cross-modal interaction. Cross-attention (BLIP-2): Q-Former compresses image into few query tokens, LLM gets them via cross-attention; better fusion, more complex. Native (GPT-4o): image patches and text tokens in one Transformer; maximum integration, requires massive multimodal training data. Trend is stitched → cross-attention → native.

2. **Q: Why are multimodal models more expensive than text-only?**
   A: Images consume many tokens (500-4000 per image depending on resolution and model). At GPT-4o pricing, a 1024×1024 image adds ~750 tokens, costing ~$0.002 per image on top of text. For document-heavy applications with 10+ images per query, costs add up fast. Mitigations: tile large images, cache image embeddings, use smaller vision encoders, skip images for simple queries.

3. **Q: When would you use a VLM vs OCR + text LLM?**
   A: Use VLM when (1) the visual content adds value beyond extractable text (charts, diagrams, handwriting), (2) the task requires visual reasoning (spatial, color, layout), (3) the user experience benefits from image input. Use OCR + text LLM when (1) the input is mostly text in images (scanned documents), (2) latency and cost are critical, (3) the task is purely linguistic. VLMs are 5-10× more expensive; only use them when visual content adds value.

4. **Q: How does LLaVA work, and what are its limitations?**
   A: LLaVA = frozen CLIP-ViT vision encoder + MLP projector + Llama LLM. The projector maps CLIP's patch features to LLM's embedding space; the LLM is fine-tuned (LoRA or full SFT) to consume image tokens alongside text. Limitations: (1) vision encoder can't see text context (no cross-modal attention in the encoder), (2) high resolution is expensive (many tokens), (3) struggles with dense text in images (use Qwen2-VL or document-specialized models instead).

5. **Q: How would you build a document RAG system that handles PDFs with charts?**
   A: Two paths. Path 1 (text-only): extract text via PyPDF/pdfplumber, embed and index, retrieve chunks for RAG. Cheap but misses chart data. Path 2 (vision): convert PDF pages to images, use a VLM (LLaVA, Qwen2-VL, Claude) to extract structured info per page, embed the extracted text, retrieve for RAG. More expensive but captures charts and figures. Most production systems use Path 2 for high-value documents (financial reports, scientific papers) and Path 1 for high-volume text-heavy documents.

6. **Q: What's the difference between GPT-4o's native multimodality and LLaVA's stitched approach?**
   A: GPT-4o processes image patches and text tokens in one Transformer, trained end-to-end on interleaved multimodal data. No information bottleneck — vision and language interact at every layer. LLaVA has a frozen vision encoder that produces image tokens, which are then projected into the LLM. The vision encoder can't see text context, and the LLM sees vision only through the projected tokens. Native multimodality is more capable but requires massive multimodal training data and unified training; stitching is cheaper and modular.

## See also

- [[Foundation Models and Multimodal MOC]] — the area map this survey belongs to.
- [[Multimodal Foundation Models]] — the vision-language model families in depth.
- [[CLIP]] — contrastive image-text alignment.
- [[LLaVA]] — the open-source VLM and the stitched-pattern template.
- [[Whisper]] — speech recognition.
- [[DiT and FLUX]] — image generation.
- [[Cross-Modal Attention]] — fusion mechanisms.
- [[Vision Foundation Models]] — the vision encoders.
- [[ViT Architecture]] — the underlying vision architecture.
