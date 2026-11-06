---
title: Failure Modes and Graceful Degradation
type: concept
aliases: [Failure Modes, Graceful Degradation, LLM Reliability]
tags: [production, reliability, failure-modes, graceful-degradation, resilience]
sources: ["06 — Failure Modes and Graceful Degradation"]
created_index: 21
---

Production AI systems fail in predictable ways: provider outages, latency spikes, cost overruns, quality regressions, hallucination spikes, prompt injection attacks, and security incidents. Graceful degradation is the design discipline that keeps the system functioning — possibly at reduced quality — when a component fails, instead of crashing entirely. This note walks through each failure mode with its impact, detection signals, and mitigations, then the patterns that make degradation graceful (fallbacks, circuit breakers, bulkheads, timeouts, retries, caching), and the incident-response and post-mortem culture that surrounds them.

> [!info] TL;DR
> Production AI systems fail in predictable ways: provider outages, latency spikes, cost overruns, quality regressions, and security incidents. Graceful degradation means the system continues to function (possibly at reduced quality) when components fail, rather than crashing entirely. The key patterns are: fallbacks (try A, fall back to B), circuit breakers (stop trying if A keeps failing), bulkheads (isolate failures to prevent cascading), and timeouts (don't wait forever). Without these patterns, a single provider outage takes down the entire application.

## Common failure modes

### LLM provider outages

Third-party LLM providers (OpenAI, Anthropic) experience outages — API errors, rate limits, network issues. These can last from seconds to hours. The impact: requests fail, users see errors, and if the failure is not handled the application appears broken. Detection comes from HTTP 5xx errors, timeouts, and rate limit responses (429). The standard mitigations:

- **Fallback to alternative provider**: route to a backup model (different provider or self-hosted).
- **Retry with backoff**: retry transient failures (network errors, 429s) with exponential backoff.
- **Circuit breaker**: if a provider fails repeatedly, stop trying for a period (avoid wasting requests).
- **Cache fallback**: return a cached response (possibly stale) if available.

### Latency spikes

LLM inference latency is variable — from 200ms to 30+ seconds depending on prompt length, model load, and provider conditions. p99 latency can be 10× p50. Users experience slow responses, synchronous handlers may time out, and downstream services may block. Detection is latency monitoring with p50/p95/p99 tracking and alerting on p99 spikes. Mitigations:

- **Timeouts**: set per-request timeouts (e.g., 10s for interactive, 60s for batch). Don't wait forever.
- **Streaming**: stream responses so users see progress; reduces perceived latency.
- **Async processing**: for non-interactive workloads, queue requests and process asynchronously.
- **Load shedding**: if the system is overloaded, reject low-priority requests to protect high-priority ones.
- **Capacity planning**: monitor queue depth; autoscale to handle spikes.

### Cost overruns

LLM costs are unbounded — a single long-context request can cost dollars, and bugs (infinite loops, overly long prompts, runaway agents) can rack up thousands of dollars quickly. The impact is budget exhaustion and unexpected bills; in multi-tenant systems, one tenant's runaway usage can affect others. Detection: per-request cost tracking, daily/monthly budget alerts, and per-tenant cost monitoring. Mitigations:

- **Per-request cost cap**: reject requests that would exceed a threshold (e.g., $0.50 per request).
- **Per-tenant budget caps**: enforce daily/monthly limits; reject or degrade when exceeded.
- **Max tokens limit**: always set `max_tokens` to prevent runaway generation.
- **Agent iteration limits**: cap the number of tool calls per agent run.
- **Model routing**: route expensive requests to cheaper models when possible.

### Quality regressions

LLM quality can regress without warning. The recurring causes: the provider silently updates the model (closed-model providers do this regularly); prompt changes have unintended effects on edge cases; RAG index updates introduce conflicting or low-quality documents; and fine-tuned models drift over time. Users receive worse answers, the hallucination rate increases, and user satisfaction drops. Detection: LLM-as-judge on sampled production traffic, benchmark regression tests, and user feedback (thumbs down rate). Mitigations:

- **Pin model versions**: use specific model identifiers (`gpt-4o-2024-08-06`) rather than aliases (`gpt-4o`).
- **Shadow deployment**: run new models in parallel, compare quality before switching traffic.
- **Canary deployment**: route a small percentage of traffic to the new model, monitor, ramp gradually.
- **Rollback**: maintain the previous model version; revert quickly if a regression is detected.

[[LLM-as-Judge Evaluation]] covers the judge side of detection; [[A-B Testing and Shadow Deployment]] covers the deployment mechanics.

### Hallucination spikes

The model suddenly produces more hallucinated content. Causes: knowledge base changes, prompt changes, model updates, or adversarial inputs. Users receive false information, and for high-stakes applications (medical, legal) this can cause real harm. Detection: faithfulness checking (LLM-as-judge on RAG outputs), fact-checking against trusted sources, and user feedback. Mitigations:

- **Grounding requirements**: require citations; verify citations support claims.
- **Lower temperature**: reduce randomness for factual tasks.
- **Fallback to "I don't know"**: if the model can't find supporting evidence, refuse rather than hallucinate.
- **Human review**: for high-stakes outputs, route to a human before sending to the user.

[[Hallucination]] treats the phenomenon itself; this note is about detecting and blunting the operational spike.

### Prompt injection attacks

Malicious users craft inputs that override the system prompt, causing the model to behave in unintended ways (leak the system prompt, call harmful tools, produce disallowed content). The impact is a security breach: data leakage, harmful outputs, reputational damage. Detection: input classification for known injection patterns, output monitoring for policy violations, and a spike in unusual tool calls. Mitigations:

- **Input sanitization**: filter known injection patterns.
- **Output validation**: verify outputs meet policy before sending to users.
- **Tool call allowlists**: restrict which tools can be called in which contexts.
- **Human-in-the-loop**: require approval for high-risk tool calls.
- **Rate limiting**: limit how often a user can trigger unusual patterns.

The full threat model and defense-in-depth stack are in [[LLM Security and Prompt Injection]] and [[Guardrails]].

### Security incidents

Data breaches, unauthorized access, PII leakage, model exfiltration. The impact: regulatory penalties (GDPR, HIPAA), loss of user trust, legal liability. Detection: audit log review, anomaly detection on access patterns, and user reports. Mitigations:

- **Incident response plan**: documented procedures for security incidents.
- **Audit logs**: comprehensive logging of all data access.
- **Access control**: enforce least privilege; audit permissions regularly.
- **Encryption**: encrypt data at rest and in transit.
- **Penetration testing**: regularly test for vulnerabilities.

[[PII and Data Leakage]] covers the leakage paths and their defenses.

## Graceful degradation patterns

> [!warning]
> Without fallbacks, circuit breakers, bulkheads, and timeouts, a single provider outage takes down the entire application. Every pattern below exists to keep some level of service alive while something is broken.

### Fallbacks

Try the primary; if it fails, try a secondary; if that fails, try a tertiary:

```python
def generate_with_fallback(prompt):
    models = [
        ("gpt-4o", openai_client),
        ("claude-3-5-sonnet", anthropic_client),
        ("llama-3.1-70b", vllm_client),
    ]
    for model_name, client in models:
        try:
            return client.generate(model_name, prompt, timeout=10)
        except (TimeoutError, APIError, RateLimitError) as e:
            log.warning(f"{model_name} failed: {e}")
            continue
    return "I'm sorry, I'm unable to respond right now. Please try again later."
```

The tertiary tier here is a self-hosted model served with [[14 - Inference and Production/Inference/vLLM|vLLM]] — a common last line of defense because it removes the third-party dependency entirely.

**Key principle**: always have a final fallback that returns *something* (even if it's just an apology), rather than an error.

### Circuit breakers

If a service fails repeatedly, stop trying for a period. This prevents cascading failures and wasted requests:

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failures = 0
        self.last_failure = None
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout

    def can_call(self):
        if self.failures < self.failure_threshold:
            return True
        if time.time() - self.last_failure > self.recovery_timeout:
            self.failures = 0  # reset, try again
            return True
        return False

    def record_failure(self):
        self.failures += 1
        self.last_failure = time.time()

    def record_success(self):
        self.failures = 0
```

When the circuit is open (too many failures), return a fallback immediately rather than trying and failing.

### Bulkheads

Isolate components so that a failure in one doesn't take down others. Use separate thread pools, processes, or services for different functions:

```python
# Separate thread pools for different features
chat_executor = ThreadPoolExecutor(max_workers=20)
rag_executor = ThreadPoolExecutor(max_workers=10)
agent_executor = ThreadPoolExecutor(max_workers=5)

# A failure in agents (which might hang) doesn't exhaust chat capacity
```

Without bulkheads, a single slow feature can exhaust all threads and take down the entire application.

### Timeouts

Never wait forever. Set timeouts at every layer:

- HTTP client timeout: 10s for interactive, 60s for batch.
- Database query timeout: 5s.
- Tool execution timeout: 30s (configurable per tool).
- Agent loop timeout: 60s total.

```python
def call_llm_with_timeout(prompt, timeout=10):
    try:
        return openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            timeout=timeout,
        )
    except TimeoutError:
        return fallback_response("The request took too long. Please try a simpler query.")
```

### Retries with backoff

Transient failures (network errors, 429s) often succeed on retry. Use exponential backoff to avoid overwhelming the provider:

```python
import time

def call_with_retry(fn, max_retries=3, base_delay=1.0):
    for attempt in range(max_retries):
        try:
            return fn()
        except (TimeoutError, RateLimitError) as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)  # 1s, 2s, 4s
            time.sleep(delay)
```

### Caching as fallback

If the LLM is unavailable, return a cached response (even if stale). This is better than no response:

```python
def generate_with_cache_fallback(prompt):
    try:
        response = llm.generate(prompt, timeout=10)
        cache.set(prompt, response, ttl=3600)
        return response
    except (TimeoutError, APIError):
        cached = cache.get(prompt)
        if cached:
            return cached + " [cached response — live model unavailable]"
        return "I'm unable to respond right now. Please try again later."
```

## Incident response

### Detection

Three detection channels, in the order they usually fire. Automated alerts monitor key metrics (error rate, latency, cost, quality) and alert on anomalies. User reports come next — users notice failures before monitoring does, so have a clear reporting channel. Log analysis — periodic review of error logs for patterns — catches the slow-burn issues the other two miss.

### Response

The response lifecycle has six steps: **acknowledge** (confirm the incident is real, not a false alarm), **mitigate** (apply immediate fixes — rollback, failover, rate limit), **communicate** (inform affected users; provide status updates), **investigate** (determine root cause), **remediate** (fix the underlying issue), and **post-mortem** (document what happened, what worked, what didn't; update procedures).

### Post-mortem culture

Treat incidents as learning opportunities, not blame opportunities. The goal is to improve the system, not to find someone to punish. Document every incident with:

- Timeline of events.
- Impact (users affected, cost, downtime).
- Root cause.
- Mitigations applied.
- Long-term fixes.
- Lessons learned.

## Common pitfalls

> [!warning]
> Most production outages trace back to one of these six omissions.

**No fallbacks.** Single-provider setups fail completely when the provider has an outage. Always have a fallback, even if it's a self-hosted backup model.

**No timeouts.** A hung request blocks a worker forever. Always set timeouts at every layer.

**Cascading failures.** A failure in one component exhausts resources (threads, memory) and takes down other components. Use bulkheads to isolate failures.

**No monitoring.** Without monitoring, you discover failures from user complaints. Monitor key metrics and alert proactively.

**No rollback plan.** Deploying a new model version without a rollback plan means a regression takes hours to fix (redeploy the old version). Maintain previous versions; test rollback procedures.

**No incident response plan.** When an incident happens, everyone scrambles to figure out what to do. Document procedures in advance; run drills.

## See also

- [[Inference and Production MOC]] — orientation for the production-AI family.
- [[Gateway and Router Patterns]] — fallback chains, routing, and cost caps implemented at the gateway.
- [[LLM Security and Prompt Injection]] — the injection failure mode in depth.
- [[PII and Data Leakage]] — the leakage paths behind security incidents.
- [[Guardrails]] — input/output filtering that catches many failure modes early.
- [[Production Monitoring]] — the detection layer for all of these modes.
- [[Observability Stack]] — the metrics, logs, and traces that power the alerts.
- [[A-B Testing and Shadow Deployment]] — safe rollout and rollback mechanics.
- [[LLM-as-Judge Evaluation]] — quality-regression detection.
- [[Cost Optimization]] — the cost-overrun countermeasures.
- [[Hallucination]] — the phenomenon behind hallucination spikes.
- [[Reference Production Architectures]] — where these patterns sit in a full stack.
