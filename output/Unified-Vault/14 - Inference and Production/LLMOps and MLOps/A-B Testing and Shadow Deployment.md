---
title: A-B Testing and Shadow Deployment
type: concept
aliases: [A/B Testing, A-B Testing, A/B Testing for LLMs, Shadow Deployment, Canary Deployment]
tags: [llmops, ab-testing, deployment, canary, shadow, rollout]
sources: ["07 — A/B Testing and Shadow Deployment"]
created_index: 14
---

A/B testing an LLM application inherits the goal of classical web experimentation — prove a new variant is safe before full exposure — while violating its core assumptions: LLM outputs are non-deterministic, quality is multi-dimensional, feedback is slow, and mistakes are expensive. The standard answer is a three-stage rollout pipeline of shadow deployment, canary, and gradual ramp, with LLM-as-judge and human review as gates at each stage. This note covers why LLM A/B testing is hard, the three rollout stages, the statistical considerations, shadow traffic analysis, rollback strategy, common pitfalls, and the tooling. It is part of the operations side of [[Inference and Production MOC]].

> [!info] TL;DR
> LLM A/B testing differs from classical web A/B testing because LLM outputs are non-deterministic, multi-dimensional, and slow to evaluate. The standard pipeline uses **shadow deployment** (run new model in parallel, compare offline) → **canary** (small traffic percentage) → **full rollout**, with LLM-as-judge and human review gates at each stage. Without this pipeline, you ship regressions to all users at once.

## Why LLM A/B testing is hard

Classical web A/B testing is well-understood: split users into control and treatment, measure a conversion metric, run a t-test. The assumptions are that the treatment is deterministic (the same user always sees the same variant), the metric is clear (click-through, conversion), and effects are measurable within hours.

LLM A/B testing violates all three assumptions, and adds a fourth problem of stakes.

### Non-determinism

The same prompt can produce different outputs on different requests (especially at temperature > 0). A user in the treatment group might get a great answer on one try and a bad answer on the next. This adds variance that classical A/B testing does not handle.

### Multi-dimensional metrics

"Quality" is not a single number. A response can be correct but verbose, helpful but slow, accurate but tone-deaf. You need multiple metrics (correctness, helpfulness, latency, cost) and a way to combine them into a rollout decision.

### Slow feedback

For many LLM applications, the "conversion" (did the user find the answer helpful?) takes hours or days to manifest. You cannot run a 1-hour A/B test and conclude anything about quality.

### Cost asymmetry

A bad classical A/B test wastes some users' time. A bad LLM A/B test can cost thousands of dollars (if the new model is more expensive) or cause real harm (if the new model hallucinates medical advice). The stakes for safe rollout are higher.

## The three-stage rollout pipeline

```mermaid
graph TD
  NewModel[New model/prompt candidate] --> Shadow[Stage 1: Shadow deployment]
  Shadow -->|1-7 days, offline comparison| Decision1{Regression?}
  Decision1 -->|Yes| Block1[Block: iterate]
  Decision1 -->|No| Canary[Stage 2: Canary deployment]
  Canary -->|5-10% traffic, 3-7 days| Decision2{Metrics OK?}
  Decision2 -->|No| Rollback1[Rollback]
  Decision2 -->|Yes| Ramp[Stage 3: Ramp to 50%]
  Ramp -->|3-7 days| Decision3{Metrics OK?}
  Decision3 -->|No| Rollback2[Rollback]
  Decision3 -->|Yes| Full[Full rollout: 100%]
```

### Stage 1: shadow deployment

Run the new model in parallel with the current production model. For every production request, send it to the production model (which serves the user), send it to the shadow model (output discarded, or logged for offline comparison), and log both outputs for later analysis.

Shadow deployment lets you see what the new model *would have* done, without exposing users to it. The cost is 2× (you pay for both models), but the safety is invaluable.

After 1–7 days of shadow traffic, run LLM-as-judge on a sample of paired outputs, compute aggregate metrics (latency, cost, refusal rate), and look for regressions on specific user segments or query types. If the shadow model is statistically worse on any critical metric, block the rollout and iterate.

### Stage 2: canary deployment

Serve the new model to a small percentage of users (typically 5–10%). Monitor real user feedback (thumbs up/down, follow-up corrections), latency, cost, and error rates; LLM-as-judge on sampled outputs; and refusal rate and safety classifier alerts.

Canary duration depends on traffic volume, because statistical power takes time to accumulate:

- High-traffic (10K+ requests/day): 3–5 days.
- Medium-traffic (1K–10K): 5–7 days.
- Low-traffic (<1K): 1–2 weeks (need more time to accumulate statistical power).

If any metric regresses, roll back. If all metrics are stable, ramp to 50%.

### Stage 3: ramp to 50% then 100%

Increase traffic gradually, treating each step as a checkpoint: 5% → 25% → 50% → 100%, monitoring metrics for 1–3 days at each step, with rollback always available.

The gradual ramp catches issues that only appear at scale — for example, a model that handles 100 requests/minute fine but breaks at 1000 requests/minute due to batching effects.

## Statistical considerations

### Sample size

LLM outputs have high variance. To detect a 5% quality difference with 80% power, you typically need 1,000–10,000 examples per variant. For low-traffic features, this means canary periods of weeks.

### Multiple testing

If you measure 20 metrics, one will appear statistically significant by chance. Use Bonferroni correction (divide α by 20) or focus on a small number of pre-registered primary metrics.

### Sequential testing

Classical A/B testing assumes you test once, after a fixed sample size. In practice, teams check metrics daily, which inflates false positives. Use sequential testing methods (always-valid p-values, group sequential designs) to avoid this.

### Heterogeneous effects

A model might be better on average but worse for a specific user segment. Always segment the analysis by user type (new vs. returning, free vs. paid), query type (easy vs. hard, short vs. long), and language / region.

## Shadow traffic analysis

The most valuable part of the pipeline is the shadow stage, because it lets you compare models on the *same* inputs. Two analysis patterns matter.

### Paired comparison

For each shadowed request, you have the production output and the shadow output for the same input. Run an LLM-as-judge pairwise comparison:

```text
For the question {question}:
  Response A (production): {response_a}
  Response B (shadow): {response_b}

  Which is better?
```

Paired comparisons are much more powerful than unpaired ones, because you eliminate input variance. With 500–1000 paired examples, you can detect 2–3% quality differences.

### Failure mode analysis

Identify requests where the shadow model failed but the production model succeeded (and vice versa), then look for patterns. Does the shadow model fail on a specific query type? Does it fail on long inputs? Short inputs? Code? Math? Are there specific topics where it's worse?

This analysis often reveals issues that aggregate metrics miss. A model might be "5% better on average" but catastrophically worse on a critical query type — which aggregate metrics hide.

## Rollback strategy

Rollback must be fast and reliable. The requirements:

- **One-command rollback**: a single API call or config change that reverts traffic to the previous version.
- **No data loss**: in-flight requests complete on the new model; new requests go to the old model. No user-visible errors.
- **Versioned artifacts**: the previous model + prompt + adapter are still in the registry, ready to serve.
- **Tested rollback**: run a rollback drill before you need it. Many teams discover their rollback is broken only during a real incident.

The rollback target should be the previous *known-good* version, not just any previous version. If you've had two consecutive bad deploys, rolling back to the immediately previous one is not enough — you need to roll back to the last known-good.

> [!warning]
> Without pre-registered success criteria, you can rationalize any result. Before the canary starts, write down: "We will roll out if metric X is ≥ baseline and metric Y is ≤ baseline + Z%." Stick to it.

## Common pitfalls

### Skipping shadow for "small" changes

A prompt tweak seems small, but it can break edge cases that only appear in production traffic. Always shadow, even for changes that look trivial.

### Insufficient canary duration

3 days is the minimum for high-traffic features; 1 day is not enough. Weekday/weekend traffic patterns differ, and you need both to make a confident decision.

### Ignoring long-tail metrics

Mean latency looks fine, but p99 latency regressed. Users notice the slow requests, not the average. Always look at percentiles, not just means.

### Not segmenting by user type

A model that's better on average but worse for paying customers is a bad trade. Always segment by user value.

### No pre-registered success criteria

Without pre-registered criteria, you can rationalize any result. Write the rollout conditions down before the canary starts, and stick to them.

### Trusting LLM-as-judge without human validation

LLM-as-judge scores can be biased. Always validate a sample of canary outputs with human review before rolling out.

## Tooling

### Feature flag systems

- **LaunchDarkly** — commercial feature flagging with traffic-percentage controls.
- **Statsig** — experimentation platform with LLM-aware features.
- **GrowthBook** — open-source experimentation.
- **Eppo** — experimentation platform with statistical rigor.

### LLM-specific tools

- **LangSmith** — built-in A/B testing for LLMs.
- **Helicone** — observability with experiment tracking.
- **Parea AI** — experiment + eval pipeline.
- **Braintrust** — prompt + model experimentation.

### Custom pipelines

Most mature teams build a custom pipeline: a feature flag for traffic routing (percentage + user-segment), a shadow traffic logger that writes paired outputs to S3/BigQuery, an offline analysis job that runs LLM-as-judge and computes metrics, a dashboard (Grafana, Metabase) showing the comparison, and a rollback button that reverts traffic with one API call.

## See also

- [[Inference and Production MOC]] — orientation for the inference and production area.
- [[LLM-as-Judge Evaluation]] — the scoring engine behind every gate in the pipeline.
- [[Model Registry and Versioning]] — versioned artifacts ready for rollback.
- [[Production Monitoring]] — the metrics watched at every stage.
- [[LLMOps vs MLOps]] — why the deployment unit has four artifacts to roll out.
- [[Prompt Management]] — the most common "small" change that needs shadowing.
- [[Gateway and Router Patterns]] — traffic routing and fallbacks at the serving layer.
- [[Observability Stack]] — dashboards for canary and shadow comparisons.
