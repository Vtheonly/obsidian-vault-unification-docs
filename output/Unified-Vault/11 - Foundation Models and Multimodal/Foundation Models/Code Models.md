---
title: Code Models
type: concept
aliases: [Code Models, Codex, StarCoder, Code Llama, DeepSeek-Coder, Qwen-Coder]
tags: [foundation-models, code-models, codex, starcoder, code-llama, deepseek-coder, qwen-coder, fill-in-the-middle, code-completion]
sources: ["04 — Code Models"]
created_index: 2
---

Code models are LLMs specialized for software engineering tasks: code generation, code completion, code review, bug fixing, and code translation. They are pretrained on massive corpora of source code (GitHub, GitLab, public repositories) and often further trained on code-related instruction data. The major families are **Codex** (OpenAI, closed), **StarCoder** (BigCode, open), **Code Llama** (Meta, open), **DeepSeek-Coder** (DeepSeek, open), and **Qwen-Coder** (Alibaba, open), and they sit alongside the other foundation-model domains collected in [[Foundation Models and Multimodal MOC]]. What distinguishes them from general LLMs is a set of domain-specific design choices — fill-in-the-middle (FIM) training objectives, byte-level tokenizers, and large context windows for repositories — which this note covers together with the model families, evaluation benchmarks, production usage patterns, and current strengths and limitations.

## Why code models are different

Code is structurally different from natural language in ways that matter for model design, and the differences come in four flavors. First, code has **formal syntax**: it must parse, and a missing bracket or wrong indentation breaks execution, whereas models trained on natural language tolerate minor grammar errors — code models must respect syntax. Second, code carries **long-range dependencies**: a function defined in one file may be called in another, so repository-level understanding requires long context (32K-128K tokens). Third, completion demands **bidirectional context**: filling in the middle of a function means the model sees both the prefix (function signature) and the suffix (closing brace), which is the **fill-in-the-middle (FIM)** objective, distinct from standard left-to-right language modeling. Fourth, code contains **sparse, repetitive patterns** — more repeated patterns (boilerplate, common idioms) than natural language — which byte-level tokenizers help capture without fragmentation. The practical upshot: a general LLM fine-tuned on code works okay, but a model designed from scratch for code works much better.

## The major code model families

### Codex (OpenAI, closed)

Codex (2021) was the first major code model, described in the paper "Evaluating Large Language Models Trained on Code" (Chen et al., 2021), and it powered the original GitHub Copilot. It was not publicly released: the model is accessible only via OpenAI's API (as the `code-*` models) and via Copilot. Architecturally it is a GPT-3 derivative — a descendant of the [[GPT Family]] — trained on 159GB of code from GitHub. As of 2026, Codex as a distinct model name is deprecated; OpenAI's current code-capable models (GPT-4o, o1, o3) inherit Codex's code training but are general-purpose.

### StarCoder and StarCoder 2 (BigCode, open)

StarCoder (2023) was the first major open-weights code model with permissive licensing, and BigCode — the collaboration behind it between HuggingFace and ServiceNow — made its data practices as open as its weights. StarCoder 1 has 15.5B parameters and 8K context; StarCoder 2 comes in 3B/7B/15B sizes with 16K context and fill-in-the-middle. Both generations were trained on 80+ programming languages from The Stack, a curated GitHub dump with per-file license attribution. The family's strengths are transparent data provenance, an opt-out for repository authors, and strong performance on less-common languages. The Stack v2, used for StarCoder 2, contains 4x more data than v1.

### Code Llama (Meta, open)

Code Llama (2023) is a Llama 2 derivative fine-tuned on code. It ships in 7B/13B/34B/70B parameters with 16K context, extendable to 100K with RoPE scaling, and was trained on 500B tokens of code. It inherits Llama's strong language understanding and is available in three flavors: base, Python-specialized, and Instruct. The 70B version was competitive with GPT-4 on HumanEval at release. Licensing follows the Llama 2 community license, with usage caps for very large commercial deployments.

### DeepSeek-Coder (DeepSeek, open)

DeepSeek-Coder (2024) is a code-focused model from DeepSeek. It comes in 1.3B/6.7B/33B parameters with 16K context, trained on 2T tokens (87% code, 13% natural language). It is strong on math+code benchmarks, particularly the 33B version, and was released under a permissive license (MIT for code, DeepSeek license for weights). DeepSeek-Coder-V2 (2024) adds a MoE architecture — see [[Mixture of Experts]] — and supports 33K+ languages.

### Qwen-Coder (Alibaba, open)

Qwen-Coder (2024) is a code-specialized variant of the Qwen model family. It comes in 1.5B/7B/32B parameters with 32K+ context, trained on a curated code corpus with emphasis on practical software engineering (not just algorithmic problems). Its strength is real-world coding tasks (debugging, refactoring) rather than just competitive programming, and the smaller models carry a permissive Apache 2.0 license.

## Key design choices

### Fill-in-the-middle (FIM)

Standard LMs are left-to-right: given the prefix, predict the next token. But code completion often requires filling in the middle: given the function signature and the code after the cursor, predict what's in between. FIM reformulates training to support this. The training example `(prefix, middle, suffix)` is transformed into one of two formats:

- **PSM** (Prefix-Suffix-Middle): `<fim_prefix>prefix<fim_suffix>suffix<fim_middle>middle`
- **SPM** (Suffix-Prefix-Middle): `<fim_suffix>suffix<fim_prefix>prefix<fim_middle>middle`

The model is trained on both formats with equal probability. At inference, the IDE provides the prefix and suffix; the model generates the middle. Without FIM, code completion is limited to "predict the next token given what's before the cursor." With FIM, the model uses both before-cursor and after-cursor context, dramatically improving completion quality.

### Byte-level tokenizers

Code contains many out-of-vocabulary tokens for natural-language tokenizers: variable names, camelCase/snake_case identifiers, special symbols. Byte-level tokenizers (like GPT-2's BPE on UTF-8 bytes — see [[BPE]]) handle any character without an `<unk>` token. StarCoder uses a byte-level BPE with 49K tokens, which handles all programming languages uniformly, including those with non-ASCII identifiers (Chinese variable names, emoji in comments).

### Long context for repository understanding

Modern code models support 16K-128K context, which enables repository-level tasks such as "given this entire codebase, refactor the auth module": the model sees the imports, the type definitions, and the call sites — not just the file being edited. Three techniques deliver that range:

- **RoPE scaling** (Code Llama): extend the RoPE base frequency to attend over longer distances ([[RoPE]]).
- **YaRN** (some Qwen-Coder variants): a more sophisticated RoPE extension ([[YaRN and NTK-Aware Scaling]]).
- **Training on long sequences**: StarCoder 2 explicitly trains on long-context examples.

### Repository-level training data

Beyond single files, modern code models train on repository-level context: multiple files from the same repo, so the model learns how files relate. DeepSeek-Coder and StarCoder 2 both use repository-aware data sampling.

## Evaluation

Code models are evaluated on a ladder of benchmarks, each probing a different slice of coding ability:

| Benchmark | What it is |
| --- | --- |
| HumanEval (OpenAI, 2021) | 164 hand-written Python problems. Each problem has a function signature and docstring; the model must implement the function. Pass@1 is the standard metric. Limitation: small, easy, Python-only. |
| HumanEval+ / MBPP+ | Expanded versions with more test cases, which catch more bugs. |
| MBPP (Google, 2021) | 974 Python problems, mostly beginner-level. |
| MultiPL-E | HumanEval translated into 18 languages; tests multilingual code capability. |
| LiveCodeBench | Problems scraped from LeetCode/AtCoder with timestamps, so you can test on problems released after the model's training cutoff; prevents contamination. |
| BigCodeBench | Harder, practical tasks requiring library usage. |
| SWE-bench | Real GitHub issues with the corresponding PRs; the model must produce a patch that resolves the issue. Tests repository-level understanding. |

Pass@1 on HumanEval is the most commonly reported number, but it is saturated (models achieve 90%+) and contaminated (many models saw HumanEval during training). LiveCodeBench and SWE-bench are more reliable for comparing 2026-era models.

## How code models are used in production

### IDE integration (Copilot, Cursor, Continue)

The dominant production use case is inline completion in the IDE: the user types; the model suggests the rest of the line or the next few lines. FIM is essential here — the model uses both before-cursor and after-cursor context. Latency matters as much as quality: suggestions must appear in <300ms or users disable them, which drives serving optimizations such as small models, prefix caching, and [[Speculative Decoding]].

### Chat-based coding (ChatGPT, Claude, Cursor Chat)

For complex tasks ("refactor this module", "debug this error"), users interact conversationally. The model sees the code, the error, and the conversation history. This is closer to general LLM use, but with code-specialized models.

### Agentic coding (Devin, SWE-Agent, OpenDevin)

The frontier use case is agentic coding — agents that autonomously navigate a codebase, make changes, run tests, and iterate. Doing this well requires:

- **Long context**, to hold the repo structure.
- **Tool use**: file operations, shell commands, test runners.
- **Planning**: decompose "implement feature X" into steps.
- **Self-correction**: when tests fail, diagnose and fix.

Code models that perform well on HumanEval often struggle with agentic tasks, which require multi-step reasoning and tool use. SWE-bench is the relevant benchmark.

## Strengths and limitations

### Strengths

Algorithmic problem-solving is the headline strength: top models solve 90%+ of HumanEval. Multi-language support is nearly as broad, with top models handling 80+ languages. Repository-level context is standard equipment — 128K+ context windows — and tool integration is built in: production models support function calling for IDE integration.

### Limitations

The limitations are just as consistent. Models hallucinate APIs — suggesting APIs that don't exist or have wrong signatures — a code-specific face of [[Hallucination]]. Outdated library knowledge: libraries evolve, and models trained a year ago may not know current APIs. Language coverage is uneven: models are strong on Python/JavaScript/Java but weaker on Rust, Zig, and niche DSLs. Debugging ability is limited: models can write code but struggle to systematically diagnose bugs in unfamiliar codebases. And security remains a live risk: models produce code with common vulnerabilities (SQL injection, XSS) unless explicitly trained not to.

## Future directions

Five directions stand out. **Repository-aware models** would maintain a persistent representation of the codebase across queries. **Execution-aware training** would train models not just on code text but on execution traces — what does this code do when run? **Test-time compute for code** applies reasoning-model techniques (chain-of-thought, self-reflection) to code generation, borrowing from [[Reasoning Models]]. **Multimodal code models** would understand code + screenshots + diagrams, for UI work and data science. And **better agentic evaluation** remains open: SWE-bench is improving, but benchmarks for long-horizon coding tasks (multi-day projects) are still needed.

## See also

- [[Foundation Models and Multimodal MOC]] — the orientation note for this area.
- [[Vision Foundation Models]] — the sister domain on the vision side.
- [[Embedding Models for Retrieval]] — the sister domain for retrieval-oriented models.
- [[Reasoning Models]] — the sister domain whose techniques feed test-time compute for code.
- [[Multimodal Foundation Models]] — the sister domain a multimodal code model would join.
- [[Decoder-Only Architecture]] — the underlying architecture of most code model families.
- [[Large Language Models MOC]] — general LLM background.
- [[Speculative Decoding]] — one of the serving tricks behind sub-300ms completions.
- [[Hallucination]] — the general failure mode behind hallucinated APIs.
