---
title: Prompt Management
type: concept
aliases: [Prompt Management, Prompt Versioning, Prompt Registry, PromptOps]
tags: [llmops, prompts, prompt-engineering, versioning, ab-testing, evaluation]
sources: ["02 — Prompt Management"]
created_index: 20
---

Prompts are the most frequently edited artifact in an LLM application, and every edit can shift quality, break output formats, inflate token cost, or open security holes as surely as a code change. Prompt management is the discipline that treats prompts as versioned configuration — drafted, reviewed, evaluated, staged, and rolled back with the same rigor code receives — rather than hardcoded strings buried in source files. This note covers why hardcoded prompts fail in production, what a versioned prompt artifact bundles, the lifecycle that carries a draft safely to production, and the tooling, coupling trade-offs, and pitfalls along the way; [[Inference and Production MOC]] orients the wider area.

> [!info] TL;DR
> Prompts are first-class artifacts in LLMOps: they need versioning, review, testing, and rollback just like code. A mature prompt-management system treats prompts as configuration (not source code), separates them from application logic, and integrates them into CI/CD pipelines with automated evaluation gates.

## Why prompts need management

In the early days of LLM apps, prompts were hardcoded strings in source files. This works for prototypes but breaks down in production:

- **Iteration friction**: changing a prompt requires a code deploy. If you want to A/B test 5 prompt variants, that is 5 deploys.
- **No audit trail**: who changed the prompt last week, and why? Without version history, you cannot answer.
- **No rollback**: if a prompt change degrades quality, reverting is painful (find the old version in git history, redeploy).
- **No separation of concerns**: prompts are written by PMs, subject-matter experts, or prompt engineers — not necessarily the developers who own the code. Hardcoded prompts force these teams to interact through pull requests.
- **No testing**: a prompt change can break the model's output format, fail to handle edge cases, or trigger refusals. Without an automated eval pipeline, you find out in production.

Mature LLMOps treats prompts as **configuration**: a separate artifact, versioned independently of code, deployed independently, and tested against an eval suite before going live.

## The anatomy of a prompt artifact

A "prompt" in a production system is more than a string. It typically includes:

1. **System message** — defines the model's role, tone, and constraints.
2. **User message template** — the variable-filled template for the actual user input.
3. **Few-shot examples** — demonstrations of expected input/output pairs.
4. **Tool descriptions** — schemas for any tools the model can call.
5. **Output format specification** — JSON schema, regex, or natural-language description of the expected response shape.
6. **Model parameters** — temperature, top_p, max_tokens, stop sequences.
7. **Model identifier** — which model (and version) this prompt is designed for.

A prompt artifact bundles all of these together so they version as a unit: changing the temperature is a prompt change; changing the model is a prompt change; changing the system message is a prompt change. The message-level conventions build on [[Instruction Tuning and Chat Templates]], and the prompt artifact itself becomes a component of the deployment unit described in [[Model Registry and Versioning]].

## The prompt management lifecycle

A candidate prompt moves through a pipeline with the same shape as a code release:

```mermaid
graph LR
  Draft[Draft prompt] --> Review[Review: PM + eng]
  Review --> Test[Run eval suite]
  Test -->|pass| Stage[Stage: shadow traffic]
  Stage -->|no regression| Canary[Canary: 5% traffic]
  Canary -->|metrics OK| Prod[Production: 100%]
  Canary -->|metrics bad| Rollback[Rollback to previous]
  Test -->|fail| Draft
  Prod --> Monitor[Monitor quality + cost]
  Monitor -->|drift| Draft
```

### Draft

Prompt engineers draft candidate prompts, often experimenting in a notebook or playground. Tools like LangSmith, PromptLayer, and Helicone provide a playground for iterating on prompts with immediate eval feedback.

### Review

Prompts are reviewed by both product (for behavior) and engineering (for correctness, edge cases, security). The review asks four questions: does the prompt follow the model's best practices (clear instructions, examples, format)? Does it handle edge cases (empty inputs, adversarial inputs, very long inputs)? Does it have prompt-injection defenses (if user input is included)? Does it match the model's known strengths and weaknesses?

### Test

The candidate prompt runs against an eval suite — a set of test inputs with expected outputs (or LLM-as-judge criteria, detailed in [[LLM-as-Judge Evaluation]]). The suite must cover:

- **Golden cases**: known-good inputs with expected outputs.
- **Edge cases**: empty inputs, very long inputs, malformed inputs.
- **Adversarial cases**: prompt-injection attempts, attempts to extract the system prompt.
- **Diverse cases**: varied languages, tones, lengths.

If the candidate prompt's eval score is below the current production prompt's, it does not ship.

### Stage, canary, and production

The prompt promotes through shadow traffic (run alongside the current prompt, outputs not served to users) → canary (small percentage of traffic) → full production. At each stage, metrics — quality, cost, latency, refusal rate — are compared against the baseline. This is the same staged-traffic discipline behind [[A-B Testing and Shadow Deployment]].

### Rollback

If any stage shows regression, the system rolls back to the previous prompt version. Because prompts are versioned, rollback is a config change, not a code deploy.

## Tooling

### Prompt registries

The prompt-registry category includes **LangSmith** (LangChain) for prompt management, eval, and tracing; **PromptLayer** for prompt versioning + review workflow; **Helicone** for observability with prompt history; **Parea AI** for prompt testing and versioning; and **Weave** (Weights & Biases) for prompt + eval tracking.

These tools provide a central registry for prompts (separate from code), version history with diffs, review workflows (PRs for prompts), eval integration (run a prompt against a test set with one click), and A/B testing infrastructure.

### Prompt templating

Most production prompts use a templating language to separate static text from dynamic variables. A common pattern:

```python
# Jinja2 template
SYSTEM = """
You are a helpful assistant. Answer the user's question about {{product}}.
If you don't know, say so. Do not make up information.

Examples:
{% for ex in examples %}
Q: {{ex.question}}
A: {{ex.answer}}
{% endfor %}
"""
```

The template is versioned; the variables (`product`, `examples`) are filled at runtime. This lets you change the prompt structure without changing the application code.

### Prompt and code coupling

A subtle design decision: should prompt templates live in the codebase (git-tracked, deployed with code) or in a prompt registry (deployed independently)? In code is simpler and version-controlled, but iteration requires deploys; in a registry enables faster iteration but introduces a runtime dependency on the registry service. Most teams start with prompts in code, then migrate to a registry once prompt iteration becomes a bottleneck — typically when non-developers need to edit prompts.

## Common pitfalls

**Hardcoding prompts in source** is the #1 mistake: prompts in source files become invisible configuration — no one knows they exist until they break. Move prompts to a dedicated location (registry or config files) as soon as the project moves beyond prototype. **No eval before deploying**: changing a prompt without running the eval suite is like deploying code without running tests — it will work for the cases you mentally checked, and break for the cases you didn't. **Mixing prompt and logic**: if the prompt includes business logic (e.g., "if the user is a premium customer, do X"), that logic should probably be in code, not in the prompt — prompts are best for shaping behavior; code is best for enforcing it. **Ignoring token cost**: a verbose prompt costs more per request, a prompt that asks for "detailed reasoning" costs more than one that asks for a short answer, and prompt changes can silently double your cost — always measure token cost as part of the eval ([[Cost Optimization]]). **No pinning of model versions**: a prompt written for `gpt-4o-2024-08-06` may behave differently on `gpt-4o-2024-11-20` — always pin the model version in the prompt artifact, and re-run evals when upgrading.

## Best practices

Seven practices summarize the discipline:

1. **Treat prompts as configuration**: separate from code, versioned independently, deployed via config changes.
2. **Maintain an eval suite**: golden cases, edge cases, adversarial cases. Run before every prompt deploy.
3. **Use a registry for non-trivial projects**: enables iteration without deploys, review workflows, A/B testing.
4. **Pin model versions**: never use unpinned model identifiers in production.
5. **Track cost per prompt variant**: a "better" prompt that costs 2× more may not be worth it.
6. **Document prompt intent**: each prompt should have a comment explaining what behavior it's designed to elicit. Without this, future prompt editors won't know what they're preserving.
7. **Review prompts for security**: any prompt that includes user input is prompt-injection-vulnerable. Add defenses (input sanitization, output validation, system-prompt hardening) — [[LLM Security and Prompt Injection]] and [[Guardrails]] cover the toolkit.

Together these keep prompt iteration fast, safe, auditable, and correctly priced.

## See also

- [[Inference and Production MOC]] — orientation for the area
- [[Model Registry and Versioning]] — the deployment unit the prompt lives in
- [[LLM-as-Judge Evaluation]] — judging candidate prompts
- [[A-B Testing and Shadow Deployment]] — shadow and canary promotion
- [[Production Monitoring]] — the drift signals that send prompts back to draft
- [[LLM Security and Prompt Injection]] — the threat model for prompts with user input
- [[Guardrails]] — input sanitization and output validation as defenses
- [[Cost Optimization]] — the token-cost dimension of prompt changes
- [[Instruction Tuning and Chat Templates]] — system message and chat template conventions
- [[LLMOps vs MLOps]] — the wider context
