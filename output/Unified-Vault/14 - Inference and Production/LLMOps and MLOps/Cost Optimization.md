---
title: Cost Optimization
type: concept
aliases: [Cost Optimization, Token Economics, LLM Cost Management]
tags: [llmops, cost, optimization, token-economics, caching, model-routing]
sources: ["06 — Cost Optimization"]
created_index: 15
---

Cost in an LLM application is dominated by tokens rather than compute, and it is not a fixed per-request value — it varies by 100× with prompt length, output length, and model choice. This note explains why LLM cost behaves so differently from classical ML cost, develops the five reduction levers (model routing, prompt compression, caching, output length control, and batching), works through a complete token-economics example from a naive to an optimized deployment, and covers the monitoring, common pitfalls, and build-versus-buy decisions that keep the bill predictable. It is part of the operations side of [[Inference and Production MOC]].

> [!info] TL;DR
> LLM cost is dominated by tokens, not compute. A single misconfigured prompt can multiply cost 10×. The five levers for cost reduction are: **model routing** (cheap model for easy queries), **prompt compression** (shorter prompts), **caching** (reuse previous results), **output length control** (max_tokens, structured outputs), and **batching** (offline processing for non-interactive workloads). A mature cost strategy combines all five and typically achieves 5–10× reduction vs. a naive deployment.

## Why LLM cost is different

In classical ML, cost is dominated by compute: training is expensive, inference is cheap. A trained model runs at a fixed cost per request — milliseconds of GPU time.

In LLMOps, cost is dominated by **tokens**:

- **Closed-model APIs** charge per token: $0.01–$0.06 per 1K tokens for input, $0.03–$0.15 per 1K tokens for output (GPT-4-class pricing, 2024).
- **Self-hosted models** charge per GPU-hour, but the GPU-hours per request scale with token count.
- **Output tokens cost more than input tokens** (typically 3× for closed models, because generation is sequential and slower than prefill).

The implication: cost is not a fixed per-request value. It varies by 100× depending on prompt length, output length, and model choice. A single 10k-token prompt with a 5k-token output costs 50× more than a 200-token prompt with a 100-token output on the same model. This variability makes cost engineering a first-class concern — teams that ignore it routinely run 5–10× over budget.

> [!warning]
> Output tokens are priced roughly 3× input tokens on most APIs. A prompt that doubles input tokens but halves output tokens may be a net win. Always calculate net cost, not raw token counts.

## The five cost levers

### Model routing

Not every request needs the strongest model. A routing layer classifies each request by difficulty and sends it to the appropriate model:

```mermaid
graph TD
  Req[Incoming request] --> Router[Router LLM or classifier]
  Router -->|easy: 70% of traffic| Cheap[Cheap model: Haiku/Mini]
  Router -->|medium: 25%| Mid[Mid model: Sonnet/Flash]
  Router -->|hard: 5%| Strong[Strong model: Opus/GPT-4o]
```

There are four implementation options, trading latency against routing sophistication:

- **LLM router**: a small LLM (or the same model with a routing prompt) classifies the request. Adds latency but enables sophisticated routing.
- **Classifier**: a fine-tuned BERT or similar classifies by difficulty. Fast but less accurate.
- **Cascade**: try the cheap model first; if the response is low-confidence (e.g., refusal, uncertain), retry with the strong model. Adds latency for the failed cases but maximally cheap.
- **Feature-based**: route based on input features (length, language, topic). Simplest, but coarse.

Typical savings: 50–70% versus always using the strong model, with minimal quality impact if the router is well-tuned.

### Prompt compression

Longer prompts cost more — directly (input tokens) and indirectly (slower prefill). Five strategies work in practice:

- **System prompt compression**: review your system prompt for redundancy. Cut anything that does not change behavior. A 2000-token system prompt often compresses to 500 tokens with no quality loss.
- **Few-shot example selection**: instead of always including 10 examples, retrieve the 2–3 most relevant per query.
- **Context pruning**: for long conversations, periodically summarize older turns rather than including them verbatim.
- **Tool description compression**: tool schemas can be verbose. Minimize descriptions to what the model needs to choose correctly.
- **Prompt caching**: many providers (Anthropic, OpenAI, [[14 - Inference and Production/Inference/vLLM|vLLM]]) now support prefix caching — if multiple requests share a prefix, the cached prefix is charged at a discount (often 50–90% off).

Typical savings: 30–60% on input cost.

### Caching

LLM outputs are deterministic at temperature 0, and approximately deterministic at low temperatures, so you can cache aggressively. Three levels exist, from shallowest to deepest:

- **Exact-match cache**: if the same prompt was asked recently, return the cached response. Hit rate depends on the use case (5–30% for general chat, 50–80% for FAQ-style queries).
- **Semantic cache**: embed the prompt, retrieve similar past prompts, and return the cached response if similarity is above a threshold. Higher hit rate but risks returning wrong answers.
- **Prefix cache**: for requests sharing a system prompt or few-shot prefix, cache the prefix's KV state. This is the deepest level — the model literally resumes from the cached state.

Cache hit rates of 20–50% are typical in production. Combined with provider-side prefix caching (which discounts cached tokens), this can halve effective cost.

### Output length control

Output tokens cost 3× input tokens on most APIs, so controlling output length is the highest-leverage cost optimization. The levers:

- **`max_tokens`**: always set this. Without it, a model can generate 4000+ tokens for a simple question.
- **Structured outputs**: ask for JSON or a specific format. Models produce more concise outputs when constrained.
- **"Be concise" in the prompt**: explicitly tell the model to be brief. Effects vary by model but can reduce output length 30–50%.
- **Stop sequences**: if you only need the answer (not the reasoning), use a stop sequence to terminate generation early.
- **For reasoning models** (o1, R1): use the smallest reasoning effort that solves the problem. Reasoning tokens are charged like output tokens and can dominate cost.

Typical savings: 40–80% on output cost.

### Batching

For non-interactive workloads (data labeling, bulk summarization, classification), use batch APIs:

- **OpenAI Batch API**: 50% discount, 24-hour turnaround.
- **Anthropic Message Batches**: 50% discount, async processing.
- **Self-hosted batching**: with [[14 - Inference and Production/Inference/vLLM|vLLM]], continuous batching processes many requests in parallel, dramatically improving throughput.

Batching trades latency for cost. For workloads where 24-hour latency is acceptable (most offline processing), the 50% discount is free money.

## Token economics: a worked example

Consider a customer support chatbot handling 10,000 conversations per day, average 5 turns each, average 500 input tokens + 200 output tokens per turn.

**Naive deployment** (GPT-4o at $5/Mtok input, $15/Mtok output):

- Daily input tokens: 10,000 × 5 × 500 = 25M tokens → $125/day
- Daily output tokens: 10,000 × 5 × 200 = 10M tokens → $150/day
- Daily cost: $275/day → **$100,375/year**

**Optimized deployment**:

- Model routing: 70% on Haiku ($0.25/Mtok in, $1.25/Mtok out), 30% on GPT-4o.
- Prompt compression: cut input from 500 → 300 tokens.
- Output control: cut output from 200 → 120 tokens via "be concise" + max_tokens.
- Caching: 30% cache hit rate on inputs.
- Batching: not applicable (interactive).

Calculation:

- Routed to Haiku (70%): 7,000 × 5 turns × (300 in × 0.7 cache-adjusted + 120 out) = 7,300 × 5 × (210 + 120) = 7,300 × 5 × 330 = 12M tokens
  - Input: 7,665K × $0.25/M = $1.92
  - Output: 4,380K × $1.25/M = $5.48
- Routed to GPT-4o (30%): 3,000 × 5 × (210 + 120) = 5M tokens
  - Input: 3,150K × $5/M = $15.75
  - Output: 1,800K × $15/M = $27.00
- **Total: $50.15/day → $18,305/year**

That is a **5.5× cost reduction** from a reasonable set of optimizations. The full optimization stack (caching + routing + compression + output control) routinely achieves 5–10× in production.

## Cost monitoring

You cannot optimize what you cannot measure. A cost monitoring stack should track:

- **Per-request cost** — input + output, by model.
- **Per-tenant cost** — which customers are expensive?
- **Per-feature cost** — which features consume the most budget?
- **Cost trends** — is daily cost increasing? Why?
- **Cost per successful outcome** — not just per request. If a feature has 50% retry rate, the cost per successful answer is 2× the per-request cost.

The alerting side matters just as much. Alert when daily cost exceeds budget, when per-request cost exceeds a threshold (often a bug), and when cost per tenant spikes (often abuse or a tenant-side bug).

## Common pitfalls

### No max_tokens

A model generating 4000 tokens for a yes/no question is the canonical waste pattern. Always set `max_tokens` based on the expected response length.

### Verbose system prompts

System prompts that say "You are a helpful, friendly, knowledgeable assistant who is also patient and concise..." cost tokens for every request without changing behavior. Cut aggressively.

### Always using the strongest model

GPT-4o for "what's the weather?" is wasteful. Route easy queries to cheaper models.

### No caching

Asking the same question twice and paying both times. Implement at least exact-match caching; semantic caching for higher hit rates.

### Not using batch APIs for offline work

If you're processing 100K documents overnight, use the batch API and save 50%.

### Ignoring output token cost

Input and output tokens are priced differently. A prompt that doubles input tokens but halves output tokens may be a net win (output is 3× more expensive). Always calculate net cost.

## The build-vs-buy decision

Many teams build custom cost optimization (routing, caching, semantic dedup). Before building, evaluate the existing options:

- **LiteLLM** — open-source proxy with routing, caching, fallbacks.
- **Portkey** — commercial LLM gateway with cost optimization.
- **OpenRouter** — multi-model routing as a service.
- **Cloud provider gateways** — AWS Bedrock, Azure AI, and Google Vertex AI all offer routing + caching.

Building custom makes sense when you have unusual requirements (specialized routing logic, tight latency constraints, custom caching). For most teams, a gateway is sufficient and much faster to deploy.

## See also

- [[Inference and Production MOC]] — orientation for the inference and production area.
- [[LLMOps vs MLOps]] — why tokens, not compute, are the LLMOps cost driver.
- [[Prompt Management]] — the artifact that prompt compression tunes.
- [[Production Monitoring]] — where per-request cost telemetry lives.
- [[A-B Testing and Shadow Deployment]] — verifying that cost levers don't regress quality.
- [[LLM-as-Judge Evaluation]] — the quality signal when routing to cheaper models.
- [[14 - Inference and Production/Inference/vLLM|vLLM]] — prefix caching and continuous batching for self-hosted serving.
- [[Continuous Batching]] — the throughput engine behind self-hosted batching.
