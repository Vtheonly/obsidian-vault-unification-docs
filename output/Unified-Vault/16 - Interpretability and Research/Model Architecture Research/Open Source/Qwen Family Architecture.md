---
title: Qwen Family Architecture
type: concept
aliases: [Qwen Family Architecture, Qwen Architecture, Qwen Family, Qwen 2 2.5 3 Architecture]
tags: [model-architecture, qwen, multilingual, open-source]
sources: ["05 - Qwen Family Architecture"]
created_index: 23
---

Qwen (Alibaba) is the leading Chinese open-weights LLM family, notable for strong multilingual capability (especially Chinese), a large vocabulary (151K+), and early adoption of MoE. Architecturally similar to Llama (GQA, RoPE, SwiGLU, RMSNorm), Qwen differentiates through multilingual data, larger vocabularies, and MoE variants (Qwen 2.5 MoE, Qwen 3). Across generations the family has moved from dense MHA models to GQA with a 151K vocabulary, and then to MoE with hybrid attention.

> [!info] Source status
> All claims are **officially confirmed** — documented in Alibaba's Qwen technical reports (Qwen, Qwen 1.5, Qwen 2, Qwen 2.5) and model cards on HuggingFace.

## The Qwen lineage

| Version | Release    | Key architectural features                     |
|---------|------------|-------------------------------------------------|
| Qwen 1  | 2023       | MHA, 32K vocab, RoPE, SwiGLU                   |
| Qwen 1.5 | Early 2024 | GQA, 151K vocab, larger context                |
| Qwen 2  | Mid 2024   | GQA, 151K vocab, up to 128K context            |
| Qwen 2.5 | Late 2024  | GQA, 151K vocab, MoE variants, up to 128K context |
| Qwen 3  | 2025       | MoE, hybrid attention, larger sizes            |

## Qwen 2 / 2.5 architecture

### Standard (dense) variants

| Property  | Qwen 2.5 7B | Qwen 2.5 14B | Qwen 2.5 32B | Qwen 2.5 72B |
|-----------|-------------|--------------|--------------|--------------|
| Parameters | 7.6B       | 14.7B        | 32.8B        | 72.7B        |
| Layers     | 28          | 40           | 64           | 80           |
| d_model    | 3584        | 5120         | 5120         | 8192         |
| Heads      | 28          | 40           | 40           | 64           |
| KV heads   | 4 (GQA)     | 8 (GQA)      | 8 (GQA)      | 8 (GQA)      |
| Context    | 128K        | 128K         | 128K         | 128K         |
| Vocab      | 151K        | 151K         | 151K         | 151K         |
| RoPE base  | 1000000     | 1000000      | 1000000      | 1000000      |

### Key architectural choices

Qwen uses a 151K vocabulary (vs Llama's 32K–128K). The larger vocabulary better supports Chinese (each character can be a token, vs being split into multiple bytes), better supports other non-Latin scripts (Arabic, Korean, Japanese), and reduces sequence length for non-English text (fewer tokens per sentence). The trade-off is a larger embedding matrix (151K × d_model), which adds parameters and memory.

Qwen's GQA is aggressive: very few KV heads (4 for the 7B model — only 1/7 of query heads). This is more aggressive than Llama 3 (8 KV heads) and gives larger KV cache reduction, at some quality cost. The trade-off works for Qwen's use cases (high-volume serving). See [[GQA MQA and MLA]].

Qwen uses RoPE base 1,000,000 (vs Llama's 10,000–500,000). The higher base gives better length extrapolation — Qwen can handle 128K context from a model trained on shorter sequences. See [[RoPE]].

SwiGLU and RMSNorm are standard choices, same as Llama/Mistral.

### Qwen 2.5 MoE variants

| Property          | Qwen 2.5 MoE-A14B | Qwen 2.5 MoE-A3B |
|-------------------|-------------------|------------------|
| Total parameters  | 57B (A14B)        | 36B (A3B)        |
| Active per token  | 14B               | 3B               |
| Experts           | 60+               | 16               |
| Active experts    | 4-8               | 2-4              |
| Context           | 128K              | 128K             |

Qwen's MoE variants use more experts than Mixtral (60+ vs 8), with fewer active per token. This gives finer-grained specialization but more complex routing. See [[Mistral and Mixtral Architecture]] for Mixtral's coarser-grained approach and [[Mixture of Experts]] for the general pattern.

## Qwen 3 (2025)

> [!info] Source status
> Qwen 3 architecture details are **officially confirmed** in Alibaba's announcements, but full technical details may not be completely published. This note reflects publicly available information as of mid-2025.

Key changes from Qwen 2.5: MoE as default (not just a variant), hybrid attention (linear + full attention, similar to Kimi Linear), larger sizes (up to 480B+ total parameters), and native multimodal (vision-language). Qwen 3 aligns with the 2025 trend toward MoE + hybrid architectures for long context and efficiency. See [[Kimi Linear]] and [[Qwen 3.8 Architecture]].

## Multilingual capability

Qwen's standout feature is multilingual quality, especially for Chinese.

### Why Qwen excels at Chinese

Three factors reinforce each other. Training data: Qwen is trained on a large Chinese corpus (Alibaba has access to Chinese web data, books, and proprietary content). Tokenizer: the 151K vocabulary includes many Chinese characters as single tokens, reducing sequence length and improving Chinese understanding. Fine-tuning: Qwen chat models are fine-tuned with Chinese instruction data.

### Multilingual benchmarks

Qwen consistently outperforms Llama and Mistral on Chinese benchmarks (C-Eval, CMMLU) and is competitive on multilingual benchmarks (MGSM, FLORES). For Chinese-language applications, Qwen is often the best open-weights choice.

## Qwen variants

### Qwen-VL (vision-language)

Qwen-VL pairs a visual encoder (ViT) with a Qwen LLM. It is pretrained on image-text pairs and is strong on document understanding, chart reading, and multilingual OCR. See [[LLaVA]] for the general VLM pattern.

### Qwen-Coder

Qwen-Coder is fine-tuned on code data (Starcoder-style). It is strong on code generation, completion, and understanding, and supports many programming languages.

### Qwen-Math

Qwen-Math is fine-tuned on mathematical reasoning data. It is strong on math benchmarks (MATH, GSM8K) and uses chain-of-thought reasoning. See [[Chain of Thought]].

### Qwen-Long

Qwen-Long is optimized for long-context applications, with 10M+ token context (with file-based retrieval). It targets document analysis use cases.

## Why Qwen matters

### Chinese AI sovereignty

Qwen is China's leading open-weights LLM. It demonstrates that frontier-quality LLMs can be developed in China, despite US export controls on advanced GPUs. This has geopolitical implications — China's AI capability is a strategic concern, and Qwen shows that capability is real.

### Multilingual representation

Most LLM research is English-centric. Qwen's strong Chinese (and other language) capability provides an alternative for non-English applications, reducing dependence on English-centric models.

### MoE innovation

Qwen's MoE variants (especially Qwen 3) push MoE design — more experts, finer-grained routing, hybrid attention. This contributes to the broader MoE research community.

### Open weights despite geopolitics

Alibaba releases Qwen weights openly (Apache 2.0 for most variants), even as US-China tech tensions escalate. This makes Qwen accessible globally, not just in China.

## Comparison to other families

| Family   | Vocab   | Chinese quality | MoE?      | Notable feature           |
|----------|---------|-----------------|-----------|----------------------------|
| Llama    | 32-128K | Moderate        | Llama 4   | Conservative baseline      |
| Mistral  | 32K     | Weak            | Mixtral   | SWA + MoE                  |
| Qwen     | 151K    | Excellent       | Qwen 2.5+ | Multilingual + MoE          |
| DeepSeek | 100K    | Excellent       | V2+       | MLA, auxiliary-loss-free    |
| Gemma    | 256K    | Moderate        | No        | Large vocab, GQA            |

Qwen and DeepSeek are the top choices for Chinese-language applications. See [[DeepSeek Architecture]] and [[Llama Mistral Qwen Comparison]].

## Impact and legacy

Qwen's architectural influence shows in four ways. It shaped multilingual LLM design: Qwen's large vocabulary and multilingual training data showed how to build LLMs that genuinely work across languages, not just English. It enabled a Chinese open-weights ecosystem: Qwen gave Chinese developers access to frontier-quality open weights, parallel to the Western ecosystem. It expanded MoE variety: Qwen's MoE variants (many experts, fine routing) expanded the MoE design space beyond Mixtral's 8-expert approach. And it applied competitive pressure: Qwen's quality (especially Qwen 2.5 72B matching Llama 3.1 70B) pushed other labs to improve, accelerating the entire field.

For AI engineers, Qwen is the top choice for Chinese-language applications and a strong alternative to Llama/Mistral for multilingual use cases. Understanding Qwen's architecture clarifies how to build multilingual LLMs and how MoE design is evolving.

## Further reading

Primary sources for the claims in this note:

- Qwen technical report: arXiv:2309.16609 (Qwen 1)
- Qwen 2: qwenlm.github.io/blog/qwen2/
- Qwen 2.5: qwenlm.github.io/blog/qwen2.5/
- [[Llama Mistral Qwen Comparison]] — comparison note.

## See also

- [[Interpretability and Research MOC]] — orientation for the interpretability and research area.
- [[Llama Family Architecture]] — the template Qwen varies.
- [[Mistral and Mixtral Architecture]] — the coarse-grained MoE comparison.
- [[Gemma Architecture]] — the other large-vocab family.
- [[Llama Mistral Qwen Comparison]] — cross-family comparison.
- [[Qwen 3.8 Architecture]] — the Qwen 3.8 deep dive.
- [[DeepSeek Architecture]] — the other top Chinese choice.
- [[GQA MQA and MLA]] — Qwen's aggressive GQA in context.
- [[Mixture of Experts]] — the MoE pattern.
- [[RoPE]] — the high-base positional encoding.
- [[Kimi Linear]] — the hybrid-attention comparison for Qwen 3.
- [[LLaVA]] — the VLM pattern behind Qwen-VL.
