---
title: Guardrails
type: concept
aliases: [Guardrails, NeMo Guardrails, Guardrails AI, Input Output Filtering]
tags: [production, guardrails, safety, filtering, nemo]
sources: [04 — Guardrails]
created_index: 23
---

Guardrails are input and output filters that enforce safety, format, and policy constraints on LLM applications: input guardrails screen the request before the model sees it, and output guardrails screen the response before it reaches the user. They exist because language models are unreliable by design — they hallucinate, they can be tricked by prompt injection, they produce toxic content, and they leak information from their context — so production systems cannot trust raw model output. The two main frameworks are NeMo Guardrails and Guardrails AI, and the essential stance is defense-in-depth: multiple guardrails at different layers, because no single guardrail is sufficient. This note covers the check families on each side of the model, the frameworks, the layering strategy, the recurring handling patterns, and the limitations that shape real deployments; [[Inference and Production MOC]] orients the wider area.

> [!info] TL;DR
> Guardrails are input/output filters that enforce safety, format, and policy constraints on LLM applications. Input guardrails detect prompt injection, PII, and disallowed topics before the LLM sees the request. Output guardrails detect hallucination, toxicity, and policy violations before the response reaches the user. The two main frameworks are NeMo Guardrails (NVIDIA, open-source) and Guardrails AI (library with typed validators). Defense-in-depth — multiple guardrails at different layers — is essential because no single guardrail is sufficient.

## Why guardrails

LLMs are unreliable by design: they hallucinate (see [[Hallucination]]), they can be tricked by prompt injection, they produce toxic content, and they leak information from their context. In production, you cannot trust the LLM's output directly — you need filters that catch failures before they reach users.

Guardrails serve three purposes:

1. **Safety**: prevent harmful, toxic, or policy-violating outputs.
2. **Reliability**: enforce output format, catch hallucinations, validate facts.
3. **Compliance**: redact PII, enforce data residency, log for audit.

Without guardrails, a single bad output can cause real harm (medical misinformation, leaked PII, hate speech) and legal/compliance issues, which is why guardrail design is a first-class production concern rather than an afterthought.

## Input and output guardrails

Guardrails split into two families by position in the request path: those that run before the LLM sees the request, and those that run after the LLM produces a response but before it reaches the user.

### Input guardrails

Input guardrails run *before* the LLM sees the request. They filter, transform, or reject the input, and the common checks are:

- **Prompt injection detection**: classify the input for known injection patterns ("ignore previous instructions", "system override", etc.). The threat itself is covered in [[LLM Security and Prompt Injection]].
- **PII detection and redaction**: detect SSNs, credit card numbers, emails, phone numbers; redact or hash before sending to the LLM.
- **Topic filtering**: reject queries about disallowed topics (medical advice, legal advice, weapons, etc.) based on your application's scope.
- **Length limiting**: truncate overly long inputs to control cost and prevent context overflow.
- **Language detection**: route non-supported languages or translate before processing.
- **Toxicity detection**: reject abusive or harassing inputs.

A typical input pipeline chains these checks so that suspected injections are rejected outright, out-of-scope queries never reach the model, and only cleaned, length-bounded input consumes model context:

```mermaid
graph TD
  Input[User input] --> InjCheck[Prompt injection check]
  InjCheck -->|suspected| Reject1[Reject: injection suspected]
  InjCheck -->|clean| PIICheck[PII detection + redaction]
  PIICheck --> TopicCheck[Topic filter]
  TopicCheck -->|disallowed| Reject2[Reject: out of scope]
  TopicCheck -->|allowed| LengthCheck[Length limit]
  LengthCheck --> LLM[LLM processing]
```

### Output guardrails

Output guardrails run *after* the LLM produces a response, before it reaches the user. The common checks are:

- **Hallucination detection**: verify claims against retrieved documents (for RAG) or a knowledge base.
- **Toxicity detection**: classify the output for hate speech, harassment, explicit content.
- **PII leakage detection**: scan for PII that shouldn't be in the output (e.g., other users' data leaked via RAG).
- **Format validation**: ensure the output matches the expected schema (JSON, specific fields, length constraints).
- **Fact-checking**: verify factual claims against trusted sources.
- **Sentiment / tone filtering**: ensure the output meets tone guidelines (professional, empathetic, etc.).
- **Citation verification**: for RAG, verify that cited sources actually support the claims.

Where the input pipeline mostly rejects, the output pipeline can also repair: an invalid format triggers a retry with instructions, toxicity triggers a rejection plus logging, leaked PII triggers redaction, and a suspected hallucination triggers a retry with grounding:

```mermaid
graph TD
  LLM[LLM output] --> FormatCheck[Format validation]
  FormatCheck -->|invalid| Retry1[Retry with format instruction]
  FormatCheck -->|valid| ToxicCheck[Toxicity check]
  ToxicCheck -->|toxic| Reject1[Reject + log]
  ToxicCheck -->|clean| PIICheck[PII leakage check]
  PIICheck -->|leak| Redact[Redact + log]
  PIICheck -->|clean| HallucCheck[Hallucination check]
  HallucCheck -->|suspected| Retry2[Retry with grounding]
  HallucCheck -->|grounded| User[Send to user]
```

PII leakage — the model emitting data that should never have reached it, such as another user's documents pulled in through retrieval — is the output-side face of [[PII and Data Leakage]].

## Guardrail frameworks

The two main frameworks are NeMo Guardrails for programmable, flow-based control and Guardrails AI for typed validators with automatic retry; around them sit two ready-made safety classifiers, Llama Guard and the OpenAI Moderation API, plus the custom guardrails many teams build for their own domain.

### NeMo Guardrails (NVIDIA)

NeMo Guardrails is an open-source framework for adding programmable guardrails to LLM applications. It uses Colang, a domain-specific language, to define guardrail flows. Its key features:

- **Colang flows**: declarative definitions of input/output checks and actions.
- **Pre-built guardrails**: topic control, jailbreak detection, hallucination prevention, moderation.
- **Integration**: works with LangChain, LlamaIndex, OpenAI SDK.
- **Action executors**: custom Python functions for complex checks.

A minimal Colang config recognizes two phrasings of a medical-advice request and answers with a fixed refusal:

```python
# Example NeMo Guardrails config
define user ask medical advice
  "How should I treat my illness?"
  "What medicine should I take?"

define bot refuse medical advice
  "I'm not able to provide medical advice. Please consult a healthcare professional."

define flow medical advice
  user ask medical advice
  bot refuse medical advice
```

Use case: enterprise applications needing fine-grained control over conversation flows and topic restrictions.

### Guardrails AI

Guardrails AI is an open-source Python library with typed validators for common guardrail patterns. Its key features:

- **Validators**: pre-built checks (toxicity, PII, hallucination, format, length, regex).
- **Custom validators**: write your own with a simple decorator.
- **Schemas**: define expected output structure; guardrails validate against it.
- **Retry logic**: if validation fails, automatically retry with corrective instructions.

A guard that chains a toxicity validator (threshold 0.5, fixing on failure) and a PII filter (email and phone entities, filtering on failure) around an OpenAI call:

```python
from guardrails import Guard
from guardrails.hub import ToxicLanguage, PIIFilter

guard = Guard().use_many(
    ToxicLanguage(threshold=0.5, on_fail="fix"),
    PIIFilter(pii_entities=["EMAIL_ADDRESS", "PHONE_NUMBER"], on_fail="filter"),
)

response = guard(
    llm_api=openai.chat.completions.create,
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": user_input}],
)
```

Use case: applications needing programmatic guardrails with automatic retry.

### Llama Guard (Meta)

Llama Guard is a fine-tuned Llama model specifically for safety classification. It classifies inputs and outputs as safe or unsafe across categories (violence, hate, sexual content, etc.). Use case: lightweight safety filtering, especially for open-source deployments.

### OpenAI Moderation API

The OpenAI Moderation API is a free API that classifies content for hate, harassment, sexual content, violence, and self-harm. It is fast and reliable for English content. Use case: simple toxicity filtering for OpenAI-based applications.

### Custom guardrails

Many production teams build custom guardrails tailored to their domain rather than relying only on the packaged frameworks:

- **Domain-specific fact-checkers**: verify claims against internal knowledge bases.
- **Compliance filters**: enforce industry-specific regulations (HIPAA, GDPR, FINRA).
- **Brand voice validators**: ensure outputs match brand tone and style guidelines.

## Defense in depth

No single guardrail is sufficient, so production systems use multiple layers:

1. **Input layer**: prompt injection detection, PII redaction, topic filtering.
2. **LLM layer**: system prompt with safety instructions, function calling constraints, tool use limits.
3. **Output layer**: toxicity detection, hallucination checking, format validation.
4. **Application layer**: business logic validation, user confirmation for high-stakes actions.
5. **Monitoring layer**: content sampling, LLM-as-judge quality monitoring, alerting on anomalies.

Each layer catches different failure modes. Prompt injection might bypass the input filter but get caught by the output toxicity check. Hallucination might pass the format check but fail the fact-checker. Multiple layers ensure that failures in one guardrail don't reach the user. The monitoring layer closes the loop in production — [[Production Monitoring]] and [[LLM-as-Judge Evaluation]] cover how.

## Common guardrail patterns

When a guardrail triggers, what happens next matters as much as the detection itself; four patterns cover most production behavior.

### The safe response pattern

When a guardrail triggers, don't just reject — provide a safe fallback response. Injection detected: "I can only help with [topic]. How can I assist you with that?" Hallucination detected: "I'm not confident in my answer. Could you rephrase or provide more context?" Toxicity detected: "I can't help with that. Let's talk about something else." This is much better than a bare error message, which frustrates users.

### The retry with correction pattern

When an output fails validation (e.g., wrong format, contains PII), retry the LLM call with corrective instructions. Format failure: "Your response must be valid JSON. Please retry." PII failure: "Your response contained personal information. Please retry without including PII." This often succeeds on the second try without user-visible failure.

### The human review pattern

For high-stakes outputs (medical, legal, financial), route flagged responses to a human reviewer before sending to the user. Adds latency but ensures safety for critical applications.

### The citation requirement pattern

For RAG applications, require the model to cite sources. If a claim lacks a citation, or the citation doesn't support the claim, reject or retry. This dramatically reduces hallucination.

## Limitations

Guardrails are neither free nor foolproof; five limitations recur in practice.

### Guardrails add latency

Each guardrail adds latency (typically 50–500ms). With 5 guardrails, that's 250ms–2.5s of overhead. Balance thoroughness with latency requirements.

### Guardrails can be bypassed

Sophisticated prompt injection can sometimes bypass input filters. Always combine with output guardrails and monitoring.

### False positives

Overly strict guardrails reject legitimate inputs, frustrating users. Tune thresholds based on real traffic.

### Maintenance burden

Guardrails need continuous tuning as new attack patterns emerge and application requirements change. Budget ongoing engineering effort.

### Cost

Some guardrails (LLM-based fact-checking, hallucination detection) require additional LLM calls, adding cost. Use cheaper models for guardrails when possible.

## See also

- [[Inference and Production MOC]] — orientation for the area
- [[LLM Security and Prompt Injection]] — the threat model input guardrails detect
- [[PII and Data Leakage]] — the data-protection problem behind redaction
- [[Hallucination]] — the failure mode output guardrails catch
- [[LLM-as-Judge Evaluation]] — the evaluator behind monitoring-layer checks
- [[Production Monitoring]] — the outermost defense-in-depth layer
- [[Gateway and Router Patterns]] — the request path guardrails sit on
- [[Reference Production Architectures]] — the systems these filters protect
- [[Failure Modes and Graceful Degradation]] — graceful behavior when guardrails trigger
