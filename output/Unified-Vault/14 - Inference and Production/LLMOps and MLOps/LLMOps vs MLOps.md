---
title: LLMOps vs MLOps
type: concept
aliases: [LLMOps vs MLOps, LLMOps Differences, LLMOps versus MLOps]
tags: [llmops, mlops, comparison, pipelines, deployment, monitoring]
sources: ["01 — LLMOps vs MLOps"]
created_index: 17
---

LLMOps is what classical MLOps becomes when the system under management is an LLM application rather than a single trained model. The pipeline stages still look familiar — train, register, deploy, monitor — but every stage acquires LLM-specific concerns: prompts, adapters, and tool schemas join the model as versioned artifacts; hallucination, prompt injection, and provider drift join accuracy drift as failure modes; and tokens replace compute as the dominant, unbounded cost driver. This note maps the differences stage by stage, catalogues the new failure modes with detection and mitigation for each, and works through the deployment-unit model, eval-driven development, provider drift, cost engineering, monitoring, and a full CI/CD-style pipeline — the practices a team misses when it treats an LLM application like a classical ML deployment. It anchors the operations side of [[Inference and Production MOC]].

> [!info] TL;DR
> LLMOps extends MLOps with new artifact types (prompts, adapters, system messages), new failure modes (hallucination, prompt injection), and new cost drivers (tokens, not just compute). The pipelines look similar — train, register, deploy, monitor — but every stage has LLM-specific concerns. Treating an LLM application like a classical ML deployment leads to predictable production failures.

## The core difference

Classical MLOps was built around one artifact: a trained model. You version the model, version the features, deploy the model, and monitor the predictions for drift. The pipeline is conceptually simple because the model is the only thing that changes.

LLMOps instead has *four* coupled artifacts that can change independently:

1. **Base model** — the pretrained or fine-tuned LLM (GPT-4o, Claude, Llama-3, etc.).
2. **Adapter** — a [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]] or similar PEFT module that modifies the base model's behavior.
3. **Prompt** — system prompt, few-shot examples, output format instructions.
4. **Tools / RAG context** — the function schemas, retrieval indexes, and knowledge bases the LLM can access.

A "model deployment" in LLMOps is really a deployment of *all four*. Changing the prompt can have as much impact as changing the model, which makes versioning, rollback, and A/B testing significantly more complex.

## Side-by-side comparison

The practical differences between the two disciplines compress into a single table:

| Aspect                  | Classical ML                              | LLMOps                                                  |
|-------------------------|-------------------------------------------|---------------------------------------------------------|
| Primary artifact        | One trained model                         | Base model + adapter + prompt + tools                   |
| Training frequency      | Weekly / monthly                          | Continuous (prompts), occasional (model)                |
| Evaluation              | Held-out accuracy / F1                    | Benchmarks + LLM-as-judge + human eval                  |
| Cost driver             | Compute (training + inference)            | Tokens (per-request, scales with usage)                 |
| Latency characteristic  | ms-scale, predictable                     | 100ms–10s, variable (output length, reasoning steps)    |
| Failure modes           | Drift, accuracy drop                      | Hallucination, prompt injection, cost spikes, refusals  |
| Ground truth            | Available (labeled data)                  | Often unavailable (open-ended generation)               |
| Retraining signal       | Drift detection on features/labels        | Quality regression on eval set + user feedback          |
| Reproducibility         | High (fixed model + features)             | Low (model providers silently update; nondeterminism)   |
| Telemetry               | Predictions, confidence, latency          | Predictions, prompt, tool calls, token counts, cost     |

Three rows do most of the damage in practice: the artifact row (four things to version instead of one), the ground-truth row (no labels means evaluation must be designed rather than computed), and the reproducibility row (the model can change under you). The rest of this note unpacks those consequences.

## The new failure modes

LLMOps inherits the classical failure modes — drift, latency, errors — and adds several LLM-specific ones. Each has a detection strategy and a mitigation strategy.

### Hallucination

The model confidently produces false statements. There is no analog in classical ML — a classifier either predicts the right label or it doesn't, but it doesn't invent new labels (see [[Hallucination]]). Detection relies on fact-checking against a knowledge base, LLM-as-judge verification, and citation faithfulness checks. Mitigation combines RAG grounding, structured outputs that force the model to cite sources, [[Guardrails]], and lower temperature.

### Prompt injection

A malicious user embeds instructions in the input that override the system prompt. Classical ML has no analog — model inputs are numbers, not natural language (see [[LLM Security and Prompt Injection]]). Detection uses input classification and output monitoring for policy violations. Mitigation layers input sanitization, output filtering, defense-in-depth (multiple guardrails), and separate privileges for tool-calling.

### Cost spikes

A single long-context request can cost dollars, not cents, and a bug that causes the model to produce 10k-token outputs instead of 500-token outputs multiplies cost by 20×. Classical ML costs are bounded per request; LLM costs are unbounded. Detection depends on per-request cost tracking and anomaly alerts on token usage. Mitigation means max_tokens limits, prompt caching, model routing (a cheap model for easy queries), and budget caps per user/tenant.

### Refusal and bias

The model refuses benign requests (over-alignment) or produces biased outputs. These are not bugs in the traditional sense — the model is doing what it was trained to do, but the policy is wrong for your use case. Detection uses refusal-rate monitoring and demographic-bias testing. Mitigation is prompt engineering, system-prompt adjustments, and model selection, since different models have different policies.

### Provider drift

Closed-model providers (OpenAI, Anthropic) silently update their models, so the same `gpt-4o` API call can produce different outputs this week versus last week. This breaks reproducibility in a way classical ML never dealt with — your own model never silently changes. Detection runs eval-set regression on a schedule (daily/weekly), comparing current outputs to baselines. Mitigation pins to specific model versions (e.g., `gpt-4o-2024-08-06`), maintains fallback models, and runs canary tests before deploying.

## The pipeline stages compared

The pipeline shape is shared, but each stage manages different artifacts and produces different telemetry.

### Data and prompt management

Where classical ML manages a feature store, schema enforcement, and data versioning (DVC), LLMOps manages a prompt registry, prompt versioning (LangSmith, PromptLayer), few-shot example management, and evaluation datasets. The versioned material is instructions and examples rather than features.

### Training and fine-tuning

Classical ML runs a training job on labeled data with hyperparameter tuning. LLMOps runs SFT, DPO, or RLHF; LoRA adapter training; benchmark evaluation; and LLM-as-judge evaluation. "Training" becomes one of several ways to change behavior, and often not the most frequent one.

### Model registry

Classical ML registers a model file + metadata + schema. LLMOps registers base model + adapter + prompt + system message + tool schemas, all versioned together as a single "deployment unit."

### Deployment

Classical ML deploys a model server (TF Serving, Triton) with a canary rollout. LLMOps deploys a model server (vLLM, TGI) plus a prompt loader, tool executor, and guardrails, with a canary that runs shadow traffic.

### Monitoring

Classical ML monitors prediction drift, feature drift, and accuracy when labels arrive. LLMOps monitors token usage, cost per request, latency per output token, refusal rate, hallucination rate (via sampling + verification), and prompt-injection alerts.

### Evaluation

Classical ML computes held-out accuracy, F1, and AUC. LLMOps combines benchmarks (MMLU, GPQA) + LLM-as-judge on the eval set + human eval on a sample + task-specific metrics (e.g., retrieval faithfulness for RAG).

## The four-artifact deployment unit

The fundamental LLMOps shift is that "the model" is no longer the only artifact — a production LLM deployment is a tuple of four coupled artifacts:

```mermaid
graph TD
  Base[Base model<br/>e.g. Llama-3-70B-Instruct]
  Adapter[PEFT adapter<br/>e.g. LoRA rank 16]
  Prompt[System prompt +<br/>few-shot examples]
  Tools[Tool schemas +<br/>RAG indexes]
  Base --> Bundle[Deployment Unit v1.4.2]
  Adapter --> Bundle
  Prompt --> Bundle
  Tools --> Bundle
  Bundle --> Deploy[Deploy to production]
```

Each artifact can change independently, and each change carries a different risk profile:

- **Base model change**: usually a major version bump (Llama 3 → Llama 4). Breaks compatibility; needs full re-eval.
- **Adapter change**: routine LoRA fine-tune update. Needs eval on regression set.
- **Prompt change**: a single word can break behavior. The most common production failure mode; needs eval + canary.
- **Tools change**: adding/removing tools or changing schemas. Needs eval for tool-calling accuracy.

Versioning all four together as a single "deployment unit" is essential. Without it, you can't reproduce behavior — you don't know which artifact caused a regression.

## Eval-driven development for LLMs

Classical ML has a clean train/test split: train on training data, evaluate on held-out test. LLMs don't have this — outputs are open-ended, ground truth is often unavailable, and "quality" is multi-dimensional. The LLMOps solution is **eval-driven development**:

1. **Build an eval set** (50-500 examples covering the task distribution).
2. **Define metrics** (LLM-as-judge for quality, exact match for verifiable, BLEU/ROUGE for translation, retrieval faithfulness for RAG).
3. **Run evals on every change** (prompt tweak, adapter update, base model swap).
4. **Compare to baseline** (statistical significance, not single-run noise).
5. **Canary in production** (5% traffic, monitor key metrics).

The tooling — LangSmith, Langfuse, Braintrust, Promptfoo, OpenAI Evals — provides eval set management, multi-metric evaluation, and comparison views. The eval set itself is a living artifact: add examples from production failures, edge cases, and adversarial inputs. A mature eval set has 200-2000 examples covering the task's full distribution.

## Provider drift: the hidden LLMOps challenge

Closed-model providers (OpenAI, Anthropic, Google) silently update their models. The same `gpt-4o` API call can produce different outputs this week versus last week. This is fundamentally different from classical ML, where your own model never changes without your action.

### The drift problem

```mermaid
graph LR
  Deploy[Deploy app on gpt-4o-2024-08-06] --> Eval[Eval: 92% quality]
  Eval --> Production[Production: 92%]
  Production --> Update[OpenAI silently updates gpt-4o]
  Update --> Regression[Quality drops to 87%]
  Regression --> Alert[Eval set alerts on regression]
```

The drift happens because providers update model weights without version bumps, because they change tokenization, system prompts, or safety classifiers, and because they change rate limits, latency, or availability.

### Mitigations

1. **Pin to specific versions**: use `gpt-4o-2024-08-06`, not `gpt-4o`. This locks you to a specific snapshot.
2. **Run regression evals daily**: even pinned versions can change (providers may deprecate or update).
3. **Maintain fallback models**: if OpenAI deprecates your version, fall back to Anthropic or self-hosted.
4. **Track behavior over time**: log inputs and outputs; periodically re-run old inputs to detect drift.
5. **SLA contracts with providers**: for enterprise, demand advance notice of model changes.

## Cost engineering

LLM costs are unbounded in a way classical ML costs are not. A single long-context request can cost dollars; a bug that causes 10K-token outputs multiplies cost 20×. Cost engineering is a first-class LLMOps discipline.

### Per-request cost tracking

Every request must be attributed:

- User ID (for billing and quotas).
- Tenant ID (for multi-tenant cost allocation).
- Model used (for routing analysis).
- Input/output token counts (for actual cost).
- Tool calls made (for tool-attributed cost).
- Latency (for SLO analysis).

This data feeds dashboards for cost per user, cost per tenant, cost per model, and cost per request type.

### Cost reduction techniques ranked by impact

| Technique                          | Cost Reduction | Quality Impact    | Implementation Difficulty |
|------------------------------------|----------------|-------------------|---------------------------|
| Model routing (cheap for easy)     | 50-80%         | <1%               | Medium                    |
| Prompt caching (shared prefixes)   | 30-60%         | 0%                | Low (server-side)         |
| Quantization (INT8/FP8)            | 50-75%         | ~1%               | Medium                    |
| Continuous batching                | 2-5× throughput| 0%                | Use vLLM (free)           |
| Response caching (exact match)     | 10-30%         | 0%                | Low                       |
| Max token limits                   | Variable       | Caps tail quality | Trivial                   |
| Smaller model fine-tuned for task  | 80-95%         | -1 to +3%         | High (needs fine-tuning)  |
| Distillation to smaller model      | 90-99%         | -2 to -5%         | Very high                 |

Most production teams stack 3-5 of these. The first three (model routing, prompt caching, quantization) give 80%+ cost reduction with minimal quality loss.

## Monitoring stack for LLMs

LLM monitoring is richer than classical ML monitoring:

| Metric Category   | Specific Metrics                                        | Alert Threshold           |
|-------------------|---------------------------------------------------------|---------------------------|
| Latency           | P50, P95, P99 latency per endpoint/model                | P95 > 2× baseline         |
| Throughput        | Requests/sec, tokens/sec                                | Sustained drop > 20%      |
| Error rate        | HTTP 5xx, LLM errors, timeout rate                      | > 1% sustained            |
| Cost              | Cost per request, cost per tenant, cost per day         | Daily cost > 1.5× baseline|
| Token usage       | Input/output tokens per request, p99 output length      | p99 output > 5× baseline  |
| Quality (sampled) | LLM-as-judge score, hallucination rate                  | Quality drop > 5%         |
| Safety            | Refusal rate, prompt-injection alerts                   | Refusal rate > 2× baseline|
| Provider health   | API error rate, latency, deprecation warnings           | Provider 5xx > 5%         |

Each metric needs a real-time dashboard, a historical trend, an alerting threshold, and an incident response runbook.

## Worked example: an LLMOps pipeline for a chat product

```mermaid
graph TD
  Dev[Developer changes prompt] --> EvalLocal[Local eval: 200 examples]
  EvalLocal --> |pass| PR[Pull request]
  PR --> CIEval[CI: full eval set 1000 examples]
  CIEval --> |pass| Staging[Deploy to staging]
  Staging --> CanaryEvals[Staging evals + smoke tests]
  CanaryEvals --> |pass| Canary[Canary: 5% production traffic]
  Canary --> Monitor[Monitor: latency, cost, quality]
  Monitor --> |OK| FullDeploy[Full deploy]
  Monitor --> |regression| Rollback[Rollback]
  FullDeploy --> Continuous[Continuous monitoring + daily evals]
  Continuous --> |drift detected| Alert[Alert + investigate]
```

This pipeline is the LLMOps equivalent of a classical ML CI/CD pipeline, but every stage has LLM-specific concerns. Local eval means the developer runs an eval set on their machine before pushing. CI eval runs the full eval set on every PR and blocks merge on regression. Staging deploys to a staging environment, runs smoke tests, and samples LLM-as-judge. The canary sends 5% of production traffic and monitors key metrics for 1 hour. Full deploy ramps to 100% if the canary is clean. The continuous stage runs daily regression evals to detect provider drift and alerts on quality regression.

## Why this matters

For AI engineers, the practical implication is that LLMOps is *not* just "MLOps with a bigger model." It requires new tooling, new metrics, and new skills:

- **Prompt engineering as a first-class discipline**, not an afterthought.
- **Cost engineering** — token economics is a critical skill; teams without it routinely run 10× over budget.
- **Eval-driven development** — because there is no held-out test set with ground-truth labels, you need a robust LLM-as-judge pipeline to iterate safely.
- **Defense-in-depth security** — prompt injection is a real attack surface, not a theoretical concern.

Teams that treat LLMOps like MLOps typically discover the gap the hard way: a cost surprise, a hallucination incident, or a security breach.

## Interview questions

These distinctions are frequent interview material, and the short-form answers are worth knowing cold.

**What are the four artifacts in an LLMOps deployment unit?** Base model, PEFT adapter (LoRA), prompt (system + few-shot), and tools/RAG context. All four can change independently and each can affect behavior. Version them together as a single deployment unit; without this, you can't reproduce behavior or diagnose regressions.

**How is LLMOps different from MLOps?** Three core differences: (1) four coupled artifacts instead of one model, (2) new failure modes (hallucination, prompt injection, cost spikes, provider drift), and (3) cost is per-token and unbounded, not per-prediction and bounded. The pipelines look similar (train, register, deploy, monitor) but every stage has LLM-specific concerns.

**What is provider drift, and how do you mitigate it?** Provider drift is when a closed-model provider (OpenAI, Anthropic) silently updates their model, changing your application's behavior without your action. Mitigations: pin to specific versions (`gpt-4o-2024-08-06`), run daily regression evals, maintain fallback models, track behavior over time, and demand SLA contracts for enterprise.

**How do you evaluate an LLM application in production?** Eval-driven development. Build a 200-2000 example eval set covering the task distribution. Define multi-dimensional metrics (LLM-as-judge for quality, exact match for verifiable, retrieval faithfulness for RAG). Run evals on every change (prompt, adapter, base model). Compare to baseline with statistical significance. Canary in production (5% traffic, monitor for 1 hour). Continuous monitoring with daily regression evals.

**How do you attribute cost in an LLM application?** Per-request attribution: log user ID, tenant ID, model, input/output token counts, tool calls, and latency for every request. Aggregate into dashboards: cost per user, cost per tenant, cost per model, cost per request type. Use these to identify optimization opportunities (e.g., 80% of cost from one tenant suggests a custom solution; 50% of cost from one model suggests routing to a cheaper model).

**What's the LLMOps equivalent of a CI/CD pipeline?** Local eval → PR with CI eval (full eval set) → staging deploy with smoke tests → canary (5% production traffic) → full deploy → continuous monitoring with daily regression evals. Each stage has LLM-specific concerns: local eval uses the developer's eval subset, CI uses the full set, staging runs LLM-as-judge, canary monitors cost/latency/quality, and continuous monitoring catches provider drift.

## See also

- [[Inference and Production MOC]] — orientation for the inference and production area.
- [[Cost Optimization]] — the token-economics discipline LLMOps adds.
- [[LLM-as-Judge Evaluation]] — the evaluation methodology that replaces held-out accuracy.
- [[A-B Testing and Shadow Deployment]] — safe rollout patterns for the deployment unit.
- [[Model Registry and Versioning]] — versioning the four-artifact deployment unit.
- [[Production Monitoring]] — the monitoring stack in production.
- [[Prompt Management]] — prompts as first-class versioned artifacts.
- [[Production AI Stack]] — the infrastructure LLMOps operates on.
- [[LLM Security and Prompt Injection]] — the new security concerns.
- [[Hallucination]] — the failure mode monitoring must detect.
- [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]] — the adapter artifact.
- [[14 - Inference and Production/Inference/vLLM|vLLM]] — the LLM-side model server.
- [[Quantization]] — the INT8/FP8 row of the cost-reduction table.
- [[Continuous Batching]] — the throughput lever in the cost-reduction table.
