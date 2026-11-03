---
title: What Is AI Engineering
type: concept
aliases: [AI Engineering, AI Engineering Discipline, AI Engineer Role, "01 - What Is AI Engineering"]
tags: [ai-foundations, ai-engineering, orientation, career]
sources: ["01 - What Is AI Engineering"]
created_index: 2
---

AI engineering is the discipline of building production systems whose core component is a trained neural model — usually a Transformer-based LLM. It sits at the intersection of ML engineering, software engineering, distributed systems, and product, and its center of gravity is not inventing new models but shipping reliable products on top of pretrained ones. This note covers what the discipline actually is, the skill stack it draws on, what makes it hard, how it differs from adjacent fields, a maturity model, common mistakes, career paths into the field, and a day-in-the-life view.

## What AI engineering actually is

AI engineering is the **applied engineering discipline** of taking pretrained AI models — mostly LLMs, but also embedding models, vision models, audio models, and diffusion models — and building useful, reliable, cost-effective systems on top of them. The job is rarely to invent new architectures; it is almost always to combine existing components — models, retrieval, tools, infrastructure — into a coherent product. In one line: it is not "training GPT-5 from scratch" — it's "shipping reliable products on top of pretrained models."

Concretely, an AI engineer's day-to-day includes:

- **Prompting and fine-tuning** models for specific tasks.
- **Designing retrieval pipelines** (RAG) to ground model outputs in real data.
- **Building agent systems** that use tools and iterate toward goals.
- **Serving models at scale** with low latency and acceptable cost.
- **Monitoring production systems** for drift, hallucination, and abuse.
- **Integrating AI features** into existing software systems.
- **Evaluating model outputs** systematically (offline + online).
- **Managing cost**: token budgets, model routing, caching.
- **Building data pipelines** for fine-tuning, evaluation, and continuous improvement.
- **Working with product and design** to translate model capabilities into user value.

What an AI engineer does **not** typically do is just as defining: train foundation models from scratch (that's research at frontier labs), invent new neural network architectures (that's ML research), build the GPU hardware (that's systems engineering), label training data (that's data ops), or train diffusion models for image generation (unless that's their specific focus).

## The skill stack

A working AI engineer needs roughly six things:

1. **Software engineering** — Python, APIs, databases, version control, testing, deployment. This is non-negotiable; without it, nothing ships. [[The Modern AI Stack]] shows where these skills land in a production system.
2. **ML fundamentals** — what models are, how they're trained, what they can and can't do. [[Introduction to Machine Learning]] is the entry point; [[Mathematics MOC]] and [[Neural Network Foundations MOC]] carry the underlying theory.
3. **Transformer / LLM specifics** — attention, tokenization, sampling, fine-tuning, evaluation; see [[Attention and Transformers MOC]] and [[Large Language Models MOC]].
4. **Inference engineering** — KV cache, batching, quantization, serving frameworks; see [[Inference and Production MOC]].
5. **Applied AI patterns** — RAG, agents, memory, tool use.
6. **Production systems** — infrastructure, observability, cost, security; see [[Production AI Stack]].

You don't need to be an expert in all six before starting. Most working AI engineers are deep in 2–3 and competent in the rest.

### The T-shaped AI engineer

The "T-shaped" model applies well to AI engineering. The horizontal bar is breadth — enough understanding of all six areas to make architectural decisions, communicate with specialists, and integrate components. The vertical bar is depth in one area. Common specializations:

- **Inference engineer**: serving, quantization, kernel optimization.
- **RAG engineer**: retrieval, embeddings, evaluation.
- **Agent engineer**: agent frameworks, tool use, multi-agent systems.
- **Fine-tuning engineer**: [[13 - Training and Adaptation/Fine-Tuning/LoRA|LoRA]], [[RLHF with PPO|RLHF]], dataset curation.
- **AI infra engineer**: GPU clusters, distributed training, Kubernetes.
- **Applied ML engineer**: the model-product gap, prompt engineering, evaluation.

Pick a depth area based on your background and interests; breadth comes with time.

## What makes AI engineering hard

Traditional software engineering is hard because of complexity, scale, and changing requirements. AI engineering adds several further dimensions.

### Non-determinism

The same input can produce different outputs. A model might answer correctly 95% of the time and fail mysteriously the other 5%, which breaks traditional testing, monitoring, and debugging approaches. You can't write a unit test that says `assert model.answer("2+2") == "4"` because the model might say "4", "four", "The answer is 4", or "2+2=4".

The implications run through everything: tests become probabilistic — "the model should answer correctly 95%+ of the time on this eval set" — monitoring tracks distributions rather than points (token usage, latency percentiles, faithfulness scores), and debugging requires tracing. Why did the model produce *this* output *this* time? The answer lives in the prompt, the retrieved context, the temperature, and the model version.

### Capability shifts

A model that worked great in January might be replaced by a better one in March, but the new one behaves differently — different prompt formats, different failure modes, different cost. You're building on a moving foundation. The practical responses: pin model versions in production and don't auto-upgrade; build an abstraction layer over model providers (LiteLLM, an internal gateway) so you can swap models without rewriting application code; run your eval set on every model upgrade, because a "better" model may regress on your specific use case; and track model behavior over time — latency, cost, failure modes, user satisfaction.

### Evaluation is hard

For a CRUD app, you can write tests: "create user → user exists." For an LLM feature, what's the test? "Summarize this article" has no single right answer. You need new evaluation techniques — LLM-as-judge, golden datasets, human review, online [[A-B Testing and Shadow Deployment|A/B tests]].

That means building an eval set early (even 50 hand-labeled examples are better than nothing), using multiple evaluation methods (automated metrics, [[LLM-as-Judge Evaluation|LLM-as-judge]], human spot-checks, user feedback), and treating evaluation as a first-class engineering problem, not an afterthought. Online metrics — user satisfaction, thumbs up/down, retention — are the ultimate ground truth, but they lag behind deployment.

### Cost is variable and unpredictable

A traditional API call costs the same whether the input is 10 bytes or 10KB. An LLM call costs proportional to input + output tokens, which can vary 10× across requests; a single "summarize this 100K-token document" call costs 100× a normal call. The countermeasures: set per-request token budgets, cache aggressively (query cache, semantic cache), route easy queries to cheaper models and hard queries to expensive ones, and monitor token usage in real time with alerts on spikes. These are the levers developed in [[Cost Optimization]].

### Latency is variable

LLM latency varies with output length, model load, and prompt complexity — a "summarize this" request might take 500ms or 5s, and users notice. The countermeasures: stream outputs to mask latency, set per-request timeouts, use [[Speculative Decoding|speculative decoding]] or smaller models for low-latency paths, and monitor p50, p95, and p99 latency separately.

## How AI engineering differs from adjacent fields

The field overlaps with several neighbors, to varying degrees:

| Field                  | Focus                                            | Overlap with AI engineering                        |
|------------------------|--------------------------------------------------|----------------------------------------------------|
| ML Engineering         | Training models on data                          | High — same math, same code, different scale       |
| Data Science           | Insights from data; statistics                   | Medium — DS informs what models should do          |
| Software Engineering   | Building reliable software                       | High — AI features ship in software                |
| MLOps                  | Pipelines, deployment, monitoring for ML         | High — LLMOps is the LLM-specific variant          |
| Data Engineering       | Building data pipelines                          | Medium — RAG needs good data pipelines             |
| DevOps / SRE           | Operating distributed systems                    | Medium — AI systems run on distributed infra       |
| AI Research            | Inventing new architectures, training new models | Low overlap; high inspiration                      |
| Product Engineering    | Building user-facing products                    | High — AI features must serve user needs           |

### Concrete distinctions

Three distinctions come up most often:

- **AI engineer vs. ML engineer**: ML engineers train models on data (often tabular, often smaller scale); AI engineers build systems on top of pretrained foundation models. The skills overlap — both know PyTorch, both understand ML — but the day-to-day is different. ML engineers worry about feature engineering, model selection, and hyperparameter tuning; AI engineers worry about retrieval, prompting, evaluation, and serving.
- **AI engineer vs. data scientist**: Data scientists extract insights from data, often with statistical methods; AI engineers build production systems. Data scientists inform what the AI should do — see [[Data Science Definition and Philosophy]] for that mindset — and AI engineers make it work in production.
- **AI engineer vs. MLOps engineer**: MLOps engineers build pipelines for training, deploying, and monitoring ML models, and LLMOps (the LLM variant) is a subset of that. AI engineers do some LLMOps but also build the application logic, retrieval, and agent systems on top.

## The AI engineering maturity model

Organizations and individuals progress through maturity levels:

### Level 1: prompt engineering

At this level someone can call an LLM API and get a response, writes effective prompts (few-shot, chain-of-thought), uses a single model for everything, and builds prototypes rather than production systems.

### Level 2: RAG and basic production

Builds RAG pipelines with vector databases, uses multiple models (different sizes for different tasks), implements caching, rate limiting, and basic monitoring, and ships AI features to production — with manual monitoring.

### Level 3: fine-tuning and evaluation

Fine-tunes models with LoRA/[[QLoRA]] for specific tasks, builds systematic evaluation pipelines, implements cost optimization (model routing, quantization), and has automated monitoring with alerts.

### Level 4: agents and multi-model systems

Builds agent systems with tool use, orchestrates multiple models (router + specialists), implements human-in-the-loop for high-stakes actions, and has comprehensive observability (traces, metrics, logs).

### Level 5: AI platform engineering

Builds internal AI platforms (model serving, fine-tuning, eval, monitoring), supports multiple AI product teams, implements advanced techniques (speculative decoding, custom kernels), and sets organizational standards for AI reliability and cost.

Most working AI engineers are at Level 2–3; senior engineers and tech leads are at Level 3–4; platform teams operate at Level 5.

## Common mistakes

The same mistakes recur:

### Treating AI engineering as prompt engineering

Prompting is a small part. The bulk of the work is the system around the model — retrieval, tools, memory, monitoring, cost control — and engineers who focus only on prompts ship fragile systems.

### Skipping evaluation

"I tested it on 3 examples and it worked" is not evaluation. Without a systematic eval set, you can't tell if changes help or hurt, can't catch regressions, and can't communicate quality to stakeholders.

### Over-engineering

Adding graph RAG, agentic loops, and multi-model routing when simple vector RAG would suffice. Start simple, measure, add complexity only when needed.

### Under-investing in data

Fine-tuning on low-quality data makes the model worse. RAG on garbage documents retrieves garbage. Data quality is the #1 determinant of AI system quality.

### Ignoring cost

LLM costs add up fast: a feature that costs $0.05 per query and gets 1M queries/month costs $50K/month. Without cost monitoring and optimization, AI features become unsustainable.

### Treating the LLM as a database

LLMs [[Hallucination|hallucinate]]; they are not authoritative sources of facts. Use RAG to ground them in real data, and don't trust model outputs for factual claims without verification.

### Not pinning model versions

"Use GPT-4" is not a spec. "Use `gpt-4-0613`" is. Models change behavior between versions, so pin versions in production and test upgrades carefully.

### Building instead of buying

For many use cases, off-the-shelf tools (LangChain, LlamaIndex, [[14 - Inference and Production/Inference/vLLM|vLLM]], RAGAS) are good enough. Don't rebuild these from scratch unless you have a specific need.

## A day in the life

A typical day for a mid-level AI engineer at a product company runs in four blocks. In the **morning (9-11am)**: check overnight monitoring — latency, cost, error rates, faithfulness scores; triage user feedback (thumbs-down reviews, support tickets); standup — share progress, raise blockers. **Midday (11am-2pm)**: work on the current feature (maybe adding reranking to the RAG pipeline); write code, run evals, iterate; pair with a product manager on requirements for the next feature. **Afternoon (2-5pm)**: code review for a teammate's PR; investigate a production issue (why did the agent loop forever on this query?); read a paper or blog post on a new technique — continuous learning is essential. **Late afternoon (5-6pm)**: deploy a small improvement to staging; document what you learned today (internal wiki or personal notes).

This varies by team and seniority, but the rhythm — monitoring, building, evaluating, deploying — is consistent.

## Why this matters

Understanding the discipline's scope prevents two common mistakes. The first is **trying to learn everything** — there's too much, so pick a depth area and breadth the rest. The second is **treating AI engineering as "prompt engineering"** — prompting is a small part, and the bulk of the work is the system around the model: retrieval, tools, memory, monitoring, cost control.

## Production implications

Four points dominate once you build for production:

- The AI engineer's value is in the **system**, not the prompt. A great prompt with a bad system fails; a mediocre prompt with a great system can succeed.
- Most production AI features spend 80% of effort on infrastructure, evaluation, and monitoring — not on the model itself.
- The pace of change means **learning velocity** matters more than current knowledge. Build the habit of reading papers and trying new tools continuously.
- **Reliability is harder than capability**. Getting an LLM to do something once is easy. Getting it to do something reliably 99.9% of the time, at acceptable cost and latency, with monitoring and rollback — that's the job.

## Career paths into AI engineering

The broader role landscape is covered in [[Roles and Careers in Data and AI]]; the common entry routes into AI engineering specifically:

### From software engineering

Path: SWE → SWE with AI features → AI Engineer → Senior AI Engineer. Strengths: production systems, testing, deployment. Gaps to fill: ML fundamentals, Transformer specifics, evaluation methodologies. Time: 6-12 months of focused learning to transition.

### From ML engineering or data science

Path: ML Engineer → ML Engineer with LLM focus → AI Engineer. Strengths: ML fundamentals, experimentation, statistics. Gaps to fill: production software engineering, distributed systems, modern serving stacks. Time: 3-9 months to fill the software engineering gaps.

### From research

Path: PhD/Postdoc → Applied Researcher → AI Engineer. Strengths: deep ML knowledge, ability to read papers. Gaps to fill: production engineering, product thinking, moving fast. Time: 6-12 months; the cultural shift from "thorough" to "shipped" is the hardest part.

### From adjacent fields (DevOps, data engineering, etc.)

Path: DevOps → MLOps → LLMOps → AI Engineer. Strengths: infrastructure, operations. Gaps to fill: ML fundamentals, application logic. Time: 9-18 months; the ML learning curve is steep.

## Interview questions

Five questions that recur in AI engineering interviews, with the answers:

- **What's the difference between AI engineering and ML engineering?** ML engineers train models on data; AI engineers build systems on top of pretrained foundation models. The skills overlap, but the day-to-day is different.
- **How would you decide between RAG and fine-tuning for a new feature?** Use RAG for knowledge that changes frequently, for attribution, and for multi-tenancy. Use fine-tuning for style, behavior, and domain-specific patterns. They're complementary — fine-tune the model's behavior, then RAG for facts.
- **How do you evaluate an LLM feature?** Build an eval set with (input, expected output) pairs. Use automated metrics (faithfulness, relevance) for fast iteration, LLM-as-judge for nuanced quality, and human review for ground truth. Track online metrics (user satisfaction, retention) as the ultimate signal.
- **How do you handle model upgrades in production?** Pin model versions. Run your eval set on the new version before deploying. Use shadow deployment (run the new model in parallel, compare outputs). Roll out gradually (canary, A/B test). Have a rollback plan.
- **What's the hardest part of production AI?** Reliability at scale. Getting an LLM to do something once is easy. Getting it to do it 99.9% of the time, at acceptable cost and latency, with monitoring and rollback — that's the job.

## Further reading

- Andrej Karpathy, *Software 2.0* (essay) — the shift from explicit code to learned models.
- Eugene Yan, *Machine Learning Systems Design*.
- Chip Huyen, *Designing Machine Learning Systems*.
- Hannes Hapke, *Machine Learning Engineering in Action*.

## See also

- [[Foundations MOC]]
- [[The Modern AI Stack]]
- [[AI vs ML vs DL]]
- [[History and Evolution of AI]]
- [[Roles and Careers in Data and AI]]
- [[Data Science Definition and Philosophy]]
